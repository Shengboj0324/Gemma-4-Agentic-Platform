"""Derive a training-only lock from the serving lock, keeping its exact digests.

The training image installs `serving-linux-py312-httpfix.lock.txt`, which is the
serving environment. Auditing that lock against the index found four pins that
would fail a `--require-hashes` install: `vllm` (the locked digest matches none
of the files the index serves for that version) and three competition-private
packages absent from the public index. None of the four is needed to train.
`runtime_preflight.REQUIRED_PACKAGES` names what the worker actually demands —
torch, transformers, compressed-tensors, peft — so a lock built from those roots
and their dependencies is both smaller and installable.

Versions and digests are copied from the source lock, never re-resolved, so this
cannot introduce a version nobody audited. A transitive dependency the source
lock does not pin is a hard failure, not an omission: a lock missing one
installs a different environment than it claims to.

Markers are evaluated for the declared target environment with no extras, which
is what `pip install` does for a plain requirement.

Exit codes: 0 derived; 2 bad arguments; 3 the run failed and nothing was written.
Deriving a lock is not building an image, and this makes no GPU claim.
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
from zenithsync.lock_audit import parse_lock, render_lock, resolve_closure
from zenithsync.runtime_preflight import REQUIRED_PACKAGES

SOURCES = ['scripts/derive_training_lock.py', 'zenithsync/lock_audit.py',
           'zenithsync/runtime_preflight.py', 'zenithsync/artifacts.py']

EXIT_DERIVED = 0
EXIT_BAD_ARGUMENTS = 2
EXIT_RUN_FAILED = 3

DEFAULT_INDEX = 'https://pypi.org/pypi'
#: The environment the training image targets, asserted by the worker itself.
TARGET_ENVIRONMENT = {'python_version': '3.12', 'python_full_version': '3.12.3',
                      'sys_platform': 'linux', 'platform_system': 'Linux',
                      'platform_machine': 'x86_64',
                      'implementation_name': 'cpython',
                      'platform_python_implementation': 'CPython',
                      'os_name': 'posix'}


def normalise(name):
    return name.lower().replace('_', '-').replace('.', '-')


def requirements_for(index, name, version, *, timeout, attempts=4):
    """Return the dependency names this version needs in the target env."""
    from packaging.markers import InvalidMarker, Marker
    from packaging.requirements import InvalidRequirement, Requirement

    url = f'{index}/{name}/{version}/json'
    delay = 1.0
    payload = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url, headers={'User-Agent': 'zenithsync-lock-derive',
                          'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode('utf-8'))
            break
        except urllib.error.HTTPError as error:
            if error.code == 404:
                # Not on the public index: the private packages are exactly the
                # ones this derivation drops, so an empty dependency list is the
                # right answer rather than a failure.
                return []
            if error.code not in (403, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        if attempt + 1 == attempts:
            raise RuntimeError(f'Gave up querying {name}=={version}')
        time.sleep(delay)
        delay *= 2
    needed = []
    for raw in (payload.get('info', {}).get('requires_dist') or []):
        try:
            requirement = Requirement(raw)
        except InvalidRequirement:
            raise ValueError(f'{name}=={version} declares an unparseable '
                             f'requirement: {raw!r}')
        if requirement.marker is not None:
            try:
                # No extras are requested, so a marker mentioning `extra`
                # evaluates false and the optional dependency is left out.
                if not requirement.marker.evaluate(
                        {**TARGET_ENVIRONMENT, 'extra': ''}):
                    continue
            except (InvalidMarker, Exception) as error:
                raise ValueError(f'{name}=={version} marker {raw!r} could not '
                                 f'be evaluated: {error}')
        needed.append(normalise(requirement.name))
    return sorted(set(needed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-lock', type=Path, required=True)
    parser.add_argument('--source-lock-sha256', required=True)
    parser.add_argument('--extra-lock', type=Path, action='append', default=[],
                        help='Further hash-locked files whose pins may satisfy '
                             'dependencies; repeatable')
    parser.add_argument('--root', action='append', default=[],
                        help='Additional root package; the worker-required four '
                             'are always roots')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--lock-name', default='training-linux-py312.lock.txt')
    parser.add_argument('--index', default=DEFAULT_INDEX)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--timeout', type=float, default=30.0)
    args = parser.parse_args()
    if not args.source_lock.is_file():
        parser.error('--source-lock is not a readable file')
    for path in args.extra_lock:
        if not path.is_file():
            parser.error(f'{path} is not a readable file')
    if args.workers < 1:
        parser.error('--workers must be a positive integer')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')

    identity = file_record(args.source_lock)
    if identity['sha256'] != args.source_lock_sha256:
        raise ValueError('Source lock identity differs from the expected digest')
    pins = parse_lock(args.source_lock.read_text(encoding='utf-8'))
    extras = {}
    for path in args.extra_lock:
        for pin in parse_lock(path.read_text(encoding='utf-8')):
            if pin['name'] in {row['name'] for row in pins}:
                raise ValueError(f'{pin["name"]!r} is pinned in both '
                                 f'{args.source_lock} and {path}')
            extras[pin['name']] = {'pin': pin, 'lock': str(path)}
    all_pins = pins + [value['pin'] for value in extras.values()]
    available = {pin['name'] for pin in all_pins}
    roots = sorted({normalise(name) for name in REQUIRED_PACKAGES}
                   | {normalise(name) for name in args.root})

    sources = {name: file_record(ROOT / name) for name in SOURCES}
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        dependencies = {}
        with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            pending = {pool.submit(requirements_for, args.index, pin['name'],
                                   pin['version'], timeout=args.timeout):
                       pin['name'] for pin in all_pins}
            for future in futures.as_completed(pending):
                dependencies[pending[future]] = future.result()
        closure = resolve_closure(roots, dependencies, available)
        if closure['gaps']:
            raise ValueError(
                'Dependencies required but not pinned in any supplied lock: '
                + '; '.join(f'{name} (needed by {", ".join(users)})'
                            for name, users in closure['gaps'].items()))
        header = (f'Training-only lock derived from {args.source_lock.name} '
                  f'(sha256 {identity["sha256"]}).\n'
                  f'Roots: {", ".join(roots)}.\n'
                  'Versions and digests are copied from the source lock, not '
                  're-resolved.\n'
                  'Target: Linux x86_64 / CPython 3.12, no extras.\n'
                  'Derived by scripts/derive_training_lock.py; never built or '
                  'GPU-tested by that script.')
        text = render_lock(all_pins, closure['keep'], header=header)
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during the derivation')
        if file_record(args.source_lock) != identity:
            raise RuntimeError('Source lock changed during the derivation')
        lock_path = args.output / args.lock_name
        lock_path.write_text(text, encoding='utf-8')
        dropped = sorted(available - set(closure['keep']))
        receipt = {'schema_version': 1, 'status': 'training_lock_derived',
                   'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                   'sources': sources,
                   'source_lock': {**identity, 'path': str(args.source_lock)},
                   'extra_locks': sorted({value['lock'] for value
                                          in extras.values()}),
                   'index': args.index,
                   'target_environment': TARGET_ENVIRONMENT,
                   'roots': roots,
                   'source_pins': len(all_pins),
                   'kept_pins': len(closure['keep']),
                   'dropped_pins': len(dropped),
                   'dropped': dropped,
                   'derived_lock': file_record(lock_path),
                   'image_built': False, 'training_approved': False,
                   'scope': 'A dependency closure over the source lock\'s own '
                            'pins, with markers evaluated for the declared '
                            'target. Not a build and not an install: it does '
                            'not establish that these wheels resolve together '
                            'or work on a GPU.'}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
        (args.output / 'dependencies.json').write_bytes(
            canonical_json(dependencies))
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    print({'status': receipt['status'], 'roots': roots,
           'source_pins': receipt['source_pins'],
           'kept_pins': receipt['kept_pins'],
           'dropped_pins': receipt['dropped_pins'],
           'lock': str(lock_path)})
    raise SystemExit(EXIT_DERIVED)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Training lock derivation failed ({type(error).__name__}: '
              f'{error}); nothing written.', file=sys.stderr)
        raise SystemExit(EXIT_RUN_FAILED)
