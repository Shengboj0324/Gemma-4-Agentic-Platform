"""Observe each selected task's licence file at its pinned commit, then judge it.

The pool screens on a licence *label* carried by dataset metadata. This fetches
the licence file from each task's repository at that task's own base commit,
hashes the bytes, and compares the text against the label. Per commit, not per
repository: a licence can change, and a file observed at one commit says nothing
about another.

Only tasks whose observed text is the declared family become eligible. A
mismatch, an unrecognised text and a missing file are three different failures
and are reported as three, each naming its tasks, because a count cannot be
acted on.

The fetched licence texts are staged and published to R2 like any other
artifact; nothing is kept locally. Reads only public repository files over HTTPS
and sends no credentials to GitHub.

Exit codes: 0 every observation confirmed; 1 at least one task withheld (the
normal outcome, and not an error); 2 bad arguments; 3 the run failed and no
receipt exists.
"""
import argparse
import concurrent.futures as futures
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, inventory, load_json
from zenithsync.rights_review import (CONFIRMED, LICENCE_FILENAMES,
                                      NOTICE_FILENAMES, review_observation,
                                      summarise)

SOURCES = ['scripts/review_pool_rights.py', 'zenithsync/rights_review.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']

EXIT_ALL_CONFIRMED = 0
EXIT_TASKS_WITHHELD = 1
EXIT_BAD_ARGUMENTS = 2
EXIT_RUN_FAILED = 3

RAW = 'https://raw.githubusercontent.com'
#: A licence file is a licence file. Anything larger is not one, and fetching it
#: would spend bandwidth on something that cannot be the thing we want.
MAX_LICENCE_BYTES = 1024 * 1024


def fetch(url, *, timeout, max_bytes, attempts=4):
    """Return (bytes, None) for 200, (None, reason) for a definite absence.

    A 404 is an answer — the file is not there at that commit — so it returns
    rather than retries. A 403, 429 or 5xx is the service asking for patience,
    so it backs off; exhausting the attempts raises, because treating a
    throttled fetch as "no licence file" would withhold tasks for a network
    reason and call it a rights finding.
    """
    delay = 1.0
    for attempt in range(attempts):
        request = urllib.request.Request(
            url, headers={'User-Agent': 'zenithsync-rights-review'})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read(max_bytes + 1)
                if len(payload) > max_bytes:
                    return None, f'exceeds {max_bytes} bytes'
                return payload, None
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None, 'not found'
            if error.code not in (403, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        if attempt + 1 == attempts:
            raise RuntimeError(f'Gave up fetching {url} after {attempts} attempts')
        time.sleep(delay)
        delay *= 2
    raise AssertionError('unreachable')


def observe(row, *, staging, timeout, max_bytes):
    """Fetch and judge one task's licence, writing the bytes into staging."""
    repo, commit = row['repo'], row['base_commit']
    text = path = notice_path = notice_digest = None
    for name in LICENCE_FILENAMES:
        payload, _ = fetch(f'{RAW}/{repo}/{commit}/{name}',
                           timeout=timeout, max_bytes=max_bytes)
        if payload is not None:
            text, path = payload, name
            break
    result = review_observation(row['license'],
                               None if text is None else text, path=path)
    digest = None
    if text is not None:
        digest = hashlib.sha256(text).hexdigest()
        # Content-addressed: one copy per distinct licence text, however many
        # tasks observed it. 2,966 observations over 508 repositories would
        # otherwise stage the same bytes hundreds of times.
        target = staging / 'licences' / f'{digest}.txt'
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text)
    if result['outcome'] == CONFIRMED and row['license'] == 'Apache-2.0':
        # Apache-2.0 section 4(d) makes an existing NOTICE part of what a
        # redistributor carries. Absence is not a defect; silence about it is.
        for name in NOTICE_FILENAMES:
            payload, _ = fetch(f'{RAW}/{repo}/{commit}/{name}',
                               timeout=timeout, max_bytes=max_bytes)
            if payload is not None:
                notice_path = name
                notice_digest = hashlib.sha256(payload).hexdigest()
                target = staging / 'notices' / f'{notice_digest}.txt'
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(payload)
                break
    return {'instance_id': row['instance_id'], 'repo': repo,
            'base_commit': commit, 'owner': row['owner'],
            'repository_group': row['repository_group'],
            'licence_sha256': digest,
            'licence_bytes': None if text is None else len(text),
            'notice_path': notice_path, 'notice_sha256': notice_digest,
            **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', type=Path, required=True,
                        help="selection.json from the pool bundle")
    parser.add_argument('--selection-sha256', required=True,
                        help='A selection you did not pin cannot be reviewed')
    parser.add_argument('--staging', type=Path, required=True,
                        help='New directory for the fetched texts; published '
                             'to R2 and not a durable home')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reviewer', required=True,
                        help='Accountable identity recorded in the receipt')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--timeout', type=float, default=30.0)
    parser.add_argument('--max-licence-bytes', type=int,
                        default=MAX_LICENCE_BYTES)
    parser.add_argument('--limit', type=int,
                        help='Review only the first N tasks; a partial review '
                             'is recorded as partial and clears nothing')
    args = parser.parse_args()
    if not args.selection.is_file():
        parser.error('--selection is not a readable file')
    for value, name in ((args.workers, '--workers'),
                        (args.max_licence_bytes, '--max-licence-bytes')):
        if value < 1:
            parser.error(f'{name} must be a positive integer')
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be a positive integer')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    for path, name in ((args.output, '--output'), (args.staging, '--staging')):
        if path.exists() or path.is_symlink():
            parser.error(f'{name} already exists')

    identity = file_record(args.selection)
    if identity['sha256'] != args.selection_sha256:
        raise ValueError('Selection identity differs from the expected digest')
    rows = load_json(args.selection)
    if not isinstance(rows, list) or not rows:
        raise ValueError('Selection must be a nonempty JSON list')
    total = len(rows)
    if args.limit is not None:
        rows = rows[:args.limit]

    sources = {name: file_record(ROOT / name) for name in SOURCES}
    args.staging.mkdir(parents=True, exist_ok=False)
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        observations = [None] * len(rows)
        with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            pending = {pool.submit(observe, row, staging=args.staging,
                                   timeout=args.timeout,
                                   max_bytes=args.max_licence_bytes): index
                       for index, row in enumerate(rows)}
            done = 0
            for future in futures.as_completed(pending):
                observations[pending[future]] = future.result()
                done += 1
                if done % 100 == 0:
                    print(f'observed {done}/{len(rows)}', flush=True)
        summary = summarise(observations)
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during the review')
        if file_record(args.selection) != identity:
            raise RuntimeError('Selection changed during the review')
        (args.output / 'observations.json').write_bytes(
            canonical_json(observations))
        (args.output / 'summary.json').write_bytes(canonical_json(summary))
        staged = inventory(args.staging, kind='candidate',
                           source='zenithsync-pool-licences', revision='001')
        (args.output / 'staged-manifest.json').write_bytes(
            canonical_json(staged))
        receipt = {'schema_version': 1,
                   'status': ('pool_rights_reviewed' if not summary['withheld_tasks']
                              else 'pool_rights_reviewed_with_withheld_tasks'),
                   'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                   'sources': sources, 'reviewer': args.reviewer,
                   'selection_file': identity,
                   'selection_tasks_total': total,
                   'reviewed_tasks': len(rows),
                   'partial_review': len(rows) != total,
                   'outcome_counts': summary['outcome_counts'],
                   'eligible_tasks': summary['eligible_tasks'],
                   'withheld_tasks': summary['withheld_tasks'],
                   'distinct_licence_texts': len(
                       {row['licence_sha256'] for row in observations
                        if row['licence_sha256']}),
                   'staged_files': len(staged['files']),
                   'staged_bytes': sum(r['size_bytes'] for r in staged['files']),
                   'rights_cleared': False, 'training_approved': False,
                   'scope': summary['scope']}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    print({key: receipt[key] for key in
           ('status', 'reviewed_tasks', 'partial_review', 'outcome_counts',
            'eligible_tasks', 'withheld_tasks', 'distinct_licence_texts',
            'staged_files', 'staged_bytes')})
    raise SystemExit(EXIT_ALL_CONFIRMED if not summary['withheld_tasks']
                     else EXIT_TASKS_WITHHELD)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Pool rights review failed ({type(error).__name__}: {error}); '
              'no receipt written.', file=sys.stderr)
        raise SystemExit(EXIT_RUN_FAILED)
