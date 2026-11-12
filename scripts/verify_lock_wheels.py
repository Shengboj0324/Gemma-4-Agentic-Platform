"""Check every pin in a hash-locked requirements file against the package index.

The training image has never been built. Its largest single risk is that one of
its pins cannot be installed on the target platform at all — a wheel never
published for cp312, a version yanked since the lock was resolved, or a package
absent from the public index. A `docker build` discovers that after downloading
gigabytes; this discovers it from the index in a couple of minutes, before a pod
is paid for.

A pin passes only when the index serves a file whose SHA-256 is exactly the
locked digest, which is the same thing `pip install --require-hashes` demands.

Exit codes: 0 every pin satisfied; 1 at least one pin would fail an install;
2 bad arguments; 3 the run failed and no receipt exists.

Passing is not a build. It does not establish that the wheels resolve together,
that they import, or that any of them works on a GPU.
"""
import argparse
import concurrent.futures as futures
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync.lock_audit import judge_pin, parse_lock, summarise_lock

SOURCES = ['scripts/verify_lock_wheels.py', 'zenithsync/lock_audit.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']

EXIT_ALL_SATISFIED = 0
EXIT_PINS_FAILING = 1
EXIT_BAD_ARGUMENTS = 2
EXIT_RUN_FAILED = 3

DEFAULT_INDEX = 'https://pypi.org/pypi'


def release_files(index, name, version, *, timeout, attempts=4):
    """Return the index's files for one version, [] or None when absent."""
    url = f'{index}/{name}/{version}/json'
    delay = 1.0
    for attempt in range(attempts):
        request = urllib.request.Request(
            url, headers={'User-Agent': 'zenithsync-lock-audit',
                          'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode('utf-8')).get('urls', [])
        except urllib.error.HTTPError as error:
            if error.code == 404:
                # Distinguish "no such version" from "no such package", since
                # the first is a lock to correct and the second a wheelhouse to
                # supply.
                try:
                    probe = urllib.request.Request(
                        f'{index}/{name}/json',
                        headers={'User-Agent': 'zenithsync-lock-audit'})
                    with urllib.request.urlopen(probe, timeout=timeout):
                        return []
                except urllib.error.HTTPError as inner:
                    if inner.code == 404:
                        return None
                    raise
            if error.code not in (403, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        if attempt + 1 == attempts:
            raise RuntimeError(f'Gave up querying {name}=={version} after '
                               f'{attempts} attempts')
        time.sleep(delay)
        delay *= 2
    raise AssertionError('unreachable')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, action='append', required=True,
                        help='Hash-locked requirements file; repeatable')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--index', default=DEFAULT_INDEX)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--timeout', type=float, default=30.0)
    args = parser.parse_args()
    for path in args.lock:
        if not path.is_file():
            parser.error(f'{path} is not a readable file')
    if args.workers < 1:
        parser.error('--workers must be a positive integer')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')

    sources = {name: file_record(ROOT / name) for name in SOURCES}
    locks = {}
    for path in args.lock:
        locks[str(path)] = {'identity': file_record(path),
                            'pins': parse_lock(path.read_text(encoding='utf-8'))}

    args.output.mkdir(parents=True, exist_ok=False)
    try:
        results = {}
        for label, lock in locks.items():
            pins = lock['pins']
            rows = [None] * len(pins)
            with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                pending = {pool.submit(release_files, args.index, pin['name'],
                                       pin['version'], timeout=args.timeout): index
                           for index, pin in enumerate(pins)}
                for future in futures.as_completed(pending):
                    position = pending[future]
                    rows[position] = judge_pin(pins[position], future.result())
            results[label] = {'identity': lock['identity'],
                              'rows': rows, 'summary': summarise_lock(rows)}
            print(f'{label}: {results[label]["summary"]["satisfied"]}'
                  f'/{len(rows)} satisfied', flush=True)
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during the audit')
        for label, lock in locks.items():
            if file_record(Path(label)) != lock['identity']:
                raise RuntimeError(f'{label} changed during the audit')
        (args.output / 'pins.json').write_bytes(canonical_json(
            {label: value['rows'] for label, value in results.items()}))
        installable = all(value['summary']['installable']
                          for value in results.values())
        receipt = {'schema_version': 1,
                   'status': ('lock_pins_satisfied' if installable
                              else 'lock_pins_failing'),
                   'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                   'sources': sources, 'index': args.index,
                   'locks': {label: {'file': value['identity'],
                                     **{key: value['summary'][key] for key in
                                        ('pins', 'outcome_counts',
                                         'artifact_counts', 'satisfied',
                                         'failing_pins', 'yanked_pins',
                                         'installable')}}
                             for label, value in results.items()},
                   'installable': installable,
                   'image_built': False, 'training_approved': False,
                   'scope': 'Index availability and digest match for each pin. '
                            'Not a build: it does not establish that the wheels '
                            'resolve together, that they import, or that any of '
                            'them works on a GPU.'}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    print({'status': receipt['status'], 'installable': installable,
           'locks': {label: {'pins': value['summary']['pins'],
                             'satisfied': value['summary']['satisfied'],
                             'failing': len(value['summary']['failing_pins']),
                             'artifacts': value['summary']['artifact_counts']}
                     for label, value in results.items()}})
    raise SystemExit(EXIT_ALL_SATISFIED if installable else EXIT_PINS_FAILING)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Lock wheel audit failed ({type(error).__name__}: {error}); '
              'no receipt written.', file=sys.stderr)
        raise SystemExit(EXIT_RUN_FAILED)
