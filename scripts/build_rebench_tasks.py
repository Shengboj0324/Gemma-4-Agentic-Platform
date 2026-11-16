"""Convert SWE-rebench-V2 cohort tasks into swegemma tasks, one repository at a time.

For each selected repository this writes, under OUTPUT/<repo_slug>/:

  tasks.jsonl          swegemma rows: instance_id, repo, base_commit, patch,
                       test_patch, problem_statement, hints_text, created_at
  snapshots/<id>.tgz   the official snapshot format: a fresh repository built by
                       `git fast-export` up to base_commit (no future history),
                       branch `main` checked out, archived from its root
  wheels/              empty (the dependencies live in the test site instead)
  site/site-packages   the repository's runtime and test dependencies, installed
                       by the task's own `install_config.install` commands into a
                       throwaway venv, with the repository's own distribution
                       removed afterwards (swegemma installs /workspace itself),
                       plus the official image's build backends and pytest pins
  build.json           what was done per task and per command, with exit codes

The site is built once per repository, at the newest selected base commit; tasks
whose tests then fail with the reference patch are removed later by gold/empty
qualification (`qualify_verifier.py`), not here. Network is used only while
building, before any guard. The cohort gate refuses a confirmation-cohort task.

Commands that need a system package manager or a toolchain download (apt-get,
curl | sh, rustup, conda) are skipped and recorded; a task that needed them will
fail qualification and be dropped, which is the honest outcome.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
SKIP = re.compile(r'^\s*(apt-get|apt |sudo |curl |wget |conda |mamba |rustup|export DEBIAN|source |\. )')
IMAGE_PACKAGES = ['pytest', 'pytest-timeout==2.1.0', 'typer', 'pdm-backend', 'setuptools', 'wheel',
                  'poetry-core', 'hatchling', 'flit-core', 'editables']
ROW_KEYS = ('instance_id', 'repo', 'base_commit', 'patch', 'test_patch', 'problem_statement', 'created_at')


def run(cmd, *, cwd=None, env=None, timeout=1800, shell=False):
    started = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, shell=shell, capture_output=True, text=True, timeout=timeout)
        code, tail = p.returncode, (p.stdout[-1500:] + p.stderr[-1500:])
    except subprocess.TimeoutExpired:
        code, tail = 'timeout', ''
    return {'cmd': cmd if isinstance(cmd, str) else ' '.join(cmd), 'exit': code,
            'seconds': round(time.monotonic() - started, 1), 'tail': tail}


def slug(repo):
    return repo.replace('/', '__')


def select(rows, cohort_ids, *, repos, per_repo, only_repos):
    by_repo = {}
    for r in rows:
        if r['instance_id'] in cohort_ids:
            by_repo.setdefault(r['repo'], []).append(r)
    names = sorted(by_repo)
    if only_repos:
        names = [n for n in names if n in set(only_repos)]
    names = names[:repos] if repos else names
    return {n: sorted(by_repo[n], key=lambda r: r['created_at'])[-per_repo:] if per_repo else
            sorted(by_repo[n], key=lambda r: r['created_at']) for n in names}


def snapshot(source, commit, dest_tgz, work):
    """Official format: fast-export up to `commit` into a fresh repository on `main`."""
    new = work / 'snap'
    shutil.rmtree(new, ignore_errors=True)
    new.mkdir(parents=True)
    steps = [run(['git', '-C', str(source), 'branch', '-f', 'export_ref', commit])]
    steps.append(run(['git', 'init', '-q', '-b', 'main', str(new)]))
    export = subprocess.Popen(['git', '-C', str(source), 'fast-export', '--reencode=yes', '--signed-tags=strip',
                               '--tag-of-filtered-object=drop', 'export_ref'], stdout=subprocess.PIPE)
    imp = subprocess.run(['git', '-C', str(new), 'fast-import', '--quiet'], stdin=export.stdout,
                         capture_output=True, text=True)
    export.wait()
    steps.append({'cmd': 'fast-export | fast-import', 'exit': export.returncode or imp.returncode,
                  'tail': imp.stderr[-800:]})
    steps.append(run(['git', '-C', str(new), 'branch', '-f', 'main', 'export_ref']))
    steps.append(run(['git', '-C', str(new), 'checkout', '-q', '-f', 'main']))
    head = run(['git', '-C', str(new), 'rev-parse', 'HEAD'])
    tree_src = run(['git', '-C', str(source), 'rev-parse', f'{commit}^{{tree}}'])
    tree_new = run(['git', '-C', str(new), 'rev-parse', 'HEAD^{tree}'])
    same_tree = tree_src['exit'] == 0 and tree_src['tail'].strip() == tree_new['tail'].strip()
    future = run(['git', '-C', str(new), 'log', '--all', '--format=%H'])
    if not same_tree or any(s['exit'] != 0 for s in steps):
        return {'ok': False, 'steps': steps, 'same_tree': same_tree}
    with tarfile.open(dest_tgz, 'w:gz') as tar:
        tar.add(new, arcname='.')
    digest = hashlib.sha256(dest_tgz.read_bytes()).hexdigest()
    return {'ok': True, 'same_tree': True, 'commits': len(future['tail'].split()), 'sha256': digest,
            'size_bytes': dest_tgz.stat().st_size, 'head': head['tail'].strip()}


def build_site(source, commit, install, out_dir, work, python):
    """Install the task's dependencies into a venv, drop the repository itself, keep site-packages."""
    tree = work / 'tree'
    shutil.rmtree(tree, ignore_errors=True)
    log = [run(['git', '-C', str(source), 'worktree', 'add', '-f', '--detach', str(tree), commit])]
    venv = out_dir / 'venv'
    shutil.rmtree(venv, ignore_errors=True)
    log.append(run([python, '-m', 'venv', str(venv)]))
    pip = str(venv / 'bin' / 'pip')
    log.append(run([pip, 'install', '-q', '--upgrade', 'pip'], timeout=600))
    env = {'PATH': f"{venv / 'bin'}:/usr/local/bin:/usr/bin:/bin", 'HOME': str(work), 'VIRTUAL_ENV': str(venv),
           'PIP_DISABLE_PIP_VERSION_CHECK': '1', 'GIT_TERMINAL_PROMPT': '0'}
    for command in install:
        if SKIP.search(command):
            log.append({'cmd': command, 'exit': 'skipped'})
            continue
        log.append(run(command, cwd=tree, env=env, shell=True, timeout=2400))
    log.append(run([pip, 'install', '-q', *IMAGE_PACKAGES], timeout=900))
    # The repository's own distribution, editable or copied, would shadow /workspace: find it by its
    # PEP 610 direct_url pointing at the build tree, and remove it.
    own = []
    try:
        report = json.loads(subprocess.run([pip, 'inspect'], capture_output=True, text=True, timeout=300).stdout)
        own = sorted({d['metadata']['name'] for d in report.get('installed', [])
                      if str((d.get('direct_url') or {}).get('url', '')).startswith(f'file://{tree}')})
    except (ValueError, KeyError, subprocess.TimeoutExpired):
        log.append({'cmd': 'pip inspect', 'exit': 'unparsed'})
    for name in own:
        log.append(run([pip, 'uninstall', '-y', name]))
    site = next((venv / 'lib').glob('python3*/site-packages'))
    target = out_dir / 'site' / 'site-packages'
    shutil.rmtree(target.parent, ignore_errors=True)
    shutil.copytree(site, target, symlinks=True)
    for pth in target.glob('__editable__*'):
        pth.unlink()
    log.append(run(['git', '-C', str(source), 'worktree', 'remove', '--force', str(tree)]))
    shutil.rmtree(venv, ignore_errors=True)
    failed = [s for s in log if s['exit'] not in (0, 'skipped')]
    return {'removed_own': own, 'failed_commands': len(failed), 'log': log}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--parquet', type=Path, required=True)
    parser.add_argument('--cohorts', type=Path, default=ROOT / 'evidence/data/task-pool-v2-python-001/cohorts.json')
    parser.add_argument('--cohort', choices=('train', 'development'), default='train')
    parser.add_argument('--freeze', type=Path, default=ROOT / 'evidence/data/confirmation-cohort-freeze-001/freeze.json')
    parser.add_argument('--repos', type=int, default=0, help='first N repositories by name (0 = all)')
    parser.add_argument('--only-repo', action='append', default=[])
    parser.add_argument('--per-repo', type=int, default=0, help='newest N tasks per repository (0 = all)')
    parser.add_argument('--shard', default='0/1', help='K/N: build only repositories with index %% N == K')
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import pyarrow.parquet as pq
    cohorts = json.loads(args.cohorts.read_text())
    ids = set(next(c for c in cohorts['cohorts'] if c['name'] == args.cohort)['instance_ids'])
    frozen = json.loads(args.freeze.read_text())
    reserved = set()
    for key in ('reserved_tasks', 'instance_ids', 'tasks'):
        value = frozen.get(key) or frozen.get('body', {}).get(key)
        if isinstance(value, list):
            reserved |= {v if isinstance(v, str) else v.get('instance_id') for v in value}
    confirmation = set(next(c for c in cohorts['cohorts'] if c['name'] == 'confirmation')['instance_ids'])
    if ids & (reserved | confirmation):
        raise SystemExit('refused: selection overlaps the frozen confirmation cohort')
    columns = list(ROW_KEYS) + ['install_config']
    rows = pq.read_table(args.parquet, columns=columns).to_pylist()
    chosen = select(rows, ids, repos=args.repos, per_repo=args.per_repo, only_repos=args.only_repo)
    k, n = (int(x) for x in args.shard.split('/'))
    args.output.mkdir(parents=True, exist_ok=True)
    for index, (repo, tasks) in enumerate(sorted(chosen.items())):
        if index % n != k:
            continue
        out = args.output / slug(repo)
        if (out / 'build.json').exists():
            continue
        work = Path('/tmp/rebench-work') / slug(repo)
        shutil.rmtree(work, ignore_errors=True)
        (out / 'snapshots').mkdir(parents=True, exist_ok=True)
        (out / 'wheels').mkdir(exist_ok=True)
        work.mkdir(parents=True)
        source = work / 'src.git'
        record = {'repo': repo, 'tasks': {}, 'started': time.time()}
        clone = run(['git', 'clone', '-q', '--bare', f'https://github.com/{repo}.git', str(source)], timeout=3600)
        record['clone'] = clone
        if clone['exit'] != 0:
            (out / 'build.json').write_text(json.dumps(record, indent=1))
            print(json.dumps({'repo': repo, 'clone': 'failed'}), flush=True)
            continue
        good = []
        for task in tasks:
            snap = snapshot(source, task['base_commit'], out / 'snapshots' / f"{task['instance_id']}.tgz", work)
            record['tasks'][task['instance_id']] = {'snapshot': snap}
            if snap['ok']:
                good.append(task)
        if good:
            newest = good[-1]
            record['site'] = build_site(source, newest['base_commit'], newest['install_config'].get('install') or [],
                                        out, work, args.python)
            record['site']['built_at_commit'] = newest['base_commit']
            with open(out / 'tasks.jsonl', 'w') as handle:
                for task in good:
                    row = {key: task[key] for key in ROW_KEYS}
                    row['created_at'] = str(row['created_at'])
                    row['hints_text'] = ''
                    handle.write(json.dumps(row) + '\n')
        record['finished'] = time.time()
        (out / 'build.json').write_text(json.dumps(record, indent=1))
        shutil.rmtree(work, ignore_errors=True)
        print(json.dumps({'repo': repo, 'tasks': len(tasks), 'snapshots': len(good),
                          'site_failed_commands': record.get('site', {}).get('failed_commands'),
                          'seconds': round(record['finished'] - record['started'])}), flush=True)


if __name__ == '__main__':
    main()
