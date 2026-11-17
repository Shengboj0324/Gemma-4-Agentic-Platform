"""Build, qualify and ship converted task packs in batches (CPU pod, root).

For each batch of repositories: (1) build packs with `build_rebench_tasks.py`, several
processes in parallel, while the network is open; (2) install the egress guard and run
gold/empty qualification for every pack as the non-root evaluator (`qualify_verifier.py`,
test site appended: the site's shim gives it precedence inside the sandbox only); (3)
remove the guard, keep only qualified tasks (gold resolves, empty does not), archive each
pack and PUT it to the presigned URL for its repository, then delete it from disk.

The guard blackholes DNS for the whole pod, so building and uploading never overlap a
qualification phase. Every shipped pack is recorded in OUTPUT/shipped.jsonl with its
sha256, md5 (the R2 ETag of a single PUT) and size, which are checked from outside by a
HEAD request; nothing is downloaded to verify. Packs with no qualified task are recorded
and not shipped.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
GUARD = [sys.executable, str(ROOT / 'scripts' / 'egress_guard.py')]


def log(**fields):
    print(json.dumps({'t': time.strftime('%H:%M:%S'), **fields}), flush=True)


def qualified_ids(receipt_path):
    receipt = json.loads(Path(receipt_path).read_text())
    gold, empty = set(receipt['gold']['resolved']), set(receipt['empty']['resolved'])
    return sorted(gold - empty)


def prune_pack(pack, keep):
    """Drop snapshots and rows of unqualified tasks; write qualified.json."""
    rows = [json.loads(l) for l in (pack / 'tasks.jsonl').read_text().splitlines() if l.strip()]
    kept = [r for r in rows if r['instance_id'] in set(keep)]
    with open(pack / 'tasks.jsonl', 'w') as handle:
        for row in kept:
            handle.write(json.dumps(row) + '\n')
    for snap in (pack / 'snapshots').glob('*.tgz'):
        if snap.name[:-4] not in set(keep):
            snap.unlink()
    (pack / 'qualified.json').write_text(json.dumps(sorted(keep)))
    return len(rows), len(kept)


SINGLE_PUT_LIMIT = 4_800_000_000  # R2 refuses a single PUT over 5 GiB; stay clear of it


def archive(pack, out, limit=SINGLE_PUT_LIMIT):
    """Plain tar; gzip (level 1) when the plain archive would exceed a single PUT. `tar xf` detects either."""
    with tarfile.open(out, 'w') as tar:
        tar.add(pack, arcname=pack.name)
    if out.stat().st_size > limit:
        with tarfile.open(out, 'w:gz', compresslevel=1) as tar:
            tar.add(pack, arcname=pack.name)
    sha, md5, size = hashlib.sha256(), hashlib.md5(), 0
    with open(out, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            sha.update(block)
            md5.update(block)
            size += len(block)
    return sha.hexdigest(), md5.hexdigest(), size


def put(path, url, size, attempts=5):
    for attempt in range(attempts):
        try:
            with open(path, 'rb') as handle:
                request = urllib.request.Request(url, data=handle, method='PUT',
                                                 headers={'Content-Length': str(size)})
                with urllib.request.urlopen(request, timeout=1800) as response:
                    return response.status, response.headers.get('ETag', '').strip('"')
        except Exception as error:  # retried; the last failure is reported
            last = f'{type(error).__name__}: {error}'
            time.sleep(10 * (attempt + 1))
    return None, last


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parquet', type=Path, required=True)
    parser.add_argument('--repos-file', type=Path, required=True, help='JSON list of owner/name, in order')
    parser.add_argument('--cohort', choices=('train', 'development'), default='train')
    parser.add_argument('--uploads', type=Path, required=True, help='JSON {slug: presigned PUT url}')
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--sandbox-dir', type=Path, required=True, help='<devset>/sandbox')
    parser.add_argument('--docker-dir', type=Path, required=True, help='<devset>/docker')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runs', type=Path, required=True, help='evaluator-writable directory')
    parser.add_argument('--evaluator', default='evaluator')
    parser.add_argument('--batch', type=int, default=24)
    parser.add_argument('--build-procs', type=int, default=8)
    parser.add_argument('--qualify-procs', type=int, default=4)
    parser.add_argument('--qualify-concurrency', type=int, default=3)
    parser.add_argument('--eval-python', default='/root/venv/bin/python')
    parser.add_argument('--build-python', default='/root/pq/bin/python')
    args = parser.parse_args()
    repos = json.loads(args.repos_file.read_text())
    uploads = json.loads(args.uploads.read_text())
    key = lambda repo: repo.replace('/', '__').lower()  # upload keys come from lower-case instance ids
    missing = [r for r in repos if key(r) not in uploads]
    if missing:
        raise SystemExit(f'no upload URL for {missing[:5]}')
    args.output.mkdir(parents=True, exist_ok=True)
    shipped_path = args.output / 'shipped.jsonl'
    done = {json.loads(l)['slug'] for l in shipped_path.read_text().splitlines()} if shipped_path.exists() else set()
    todo = [r for r in repos if key(r) not in done]
    packs_root = args.output / 'packs'
    as_eval = ['setpriv', f'--reuid={args.evaluator}', f'--regid={args.evaluator}', '--init-groups', 'env', '-i',
               f'HOME=/home/{args.evaluator}', f'USER={args.evaluator}', 'PATH=/usr/local/bin:/usr/bin:/bin']
    for start in range(0, len(todo), args.batch):
        batch = todo[start:start + args.batch]
        log(phase='build', batch=start // args.batch, repos=len(batch))
        only = [x for r in batch for x in ('--only-repo', r)]
        procs = [subprocess.Popen([args.build_python, str(ROOT / 'scripts' / 'build_rebench_tasks.py'),
                                   '--parquet', str(args.parquet), '--cohort', args.cohort, *only,
                                   '--shard', f'{k}/{args.build_procs}',
                                   '--python', '/usr/bin/python3', '--output', str(packs_root)],
                                  stdout=open(args.output / f'build-{start}-{k}.log', 'w'), stderr=subprocess.STDOUT)
                 for k in range(args.build_procs)]
        for p in procs:
            p.wait()
        ready = []
        for repo in batch:
            pack = packs_root / repo.replace('/', '__')
            if (pack / 'tasks.jsonl').exists():
                shutil.copytree(args.sandbox_dir, pack / 'sandbox', dirs_exist_ok=True)
                for name in ('imp.py', 'telnetlib.py'):
                    if (args.docker_dir / name).exists():
                        shutil.copy(args.docker_dir / name, pack / 'site' / 'site-packages' / name)
                ready.append(pack)
        subprocess.run(['chmod', '-R', 'a+rX', str(packs_root), str(args.submission)], check=True)
        log(phase='qualify', batch=start // args.batch, packs=len(ready))
        subprocess.run([*GUARD, 'install'], check=True, stdout=subprocess.DEVNULL)
        try:
            check = subprocess.run([*as_eval, *GUARD, 'check'], capture_output=True, text=True)
            if '"external_reachable": false' not in check.stdout:
                raise SystemExit('egress guard check failed: ' + check.stdout[-500:])

            def qualify(pack):
                ids = [json.loads(l)['instance_id'] for l in (pack / 'tasks.jsonl').read_text().splitlines() if l.strip()]
                out = args.runs / f'qual-{pack.name}'
                if out.exists():
                    return pack, out
                subprocess.run([*as_eval, args.eval_python, str(ROOT / 'scripts' / 'qualify_verifier.py'),
                                '--tasks', str(pack / 'tasks.jsonl'), '--data-root', str(pack),
                                '--submission', str(args.submission), *[x for i in ids for x in ('--task-id', i)],
                                '--concurrency', str(args.qualify_concurrency),
                                '--test-site', str(pack / 'site' / 'site-packages'), '--test-site-order', 'append',
                                '--isolation', 'egress-guard', '--output', str(out)],
                               stdout=open(args.output / f'qual-{pack.name}.log', 'w'), stderr=subprocess.STDOUT,
                               timeout=3 * 3600)
                return pack, out
            with ThreadPoolExecutor(args.qualify_procs) as pool:
                results = list(pool.map(qualify, ready))
        finally:
            subprocess.run([*GUARD, 'remove'], check=True, stdout=subprocess.DEVNULL)
        log(phase='ship', batch=start // args.batch)
        for repo in batch:
            slug = key(repo)
            pack = packs_root / repo.replace('/', '__')
            out = args.runs / f'qual-{pack.name}'
            record = {'slug': slug, 'repo': repo}
            if not (pack / 'tasks.jsonl').exists() or not (out / 'receipt.json').exists():
                record.update(status='not_built' if not (pack / 'tasks.jsonl').exists() else 'qualification_failed')
            else:
                keep = qualified_ids(out / 'receipt.json')
                total, kept = prune_pack(pack, keep)
                shutil.copy(out / 'receipt.json', pack / 'qualification-receipt.json')
                record.update(tasks=total, qualified=kept)
                if kept:
                    tar_path = args.output / f'{slug}.tar'
                    sha, md5, size = archive(pack, tar_path)
                    if size > 5 * 1024 ** 3:
                        status, etag = None, 'too_large_for_single_put'
                    else:
                        status, etag = put(tar_path, uploads[slug], size)
                    record.update(sha256=sha, md5=md5, size=size, http=status, etag=etag,
                                  status='shipped' if status == 200 and etag == md5 else 'upload_failed')
                    tar_path.unlink()
                else:
                    record['status'] = 'none_qualified'
            if pack.exists():
                shutil.rmtree(pack)
            with open(shipped_path, 'a') as handle:
                handle.write(json.dumps(record) + '\n')
            log(**{k: record.get(k) for k in ('slug', 'status', 'tasks', 'qualified', 'size')})
    log(phase='done')


if __name__ == '__main__':
    main()
