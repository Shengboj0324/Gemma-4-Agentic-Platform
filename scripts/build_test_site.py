"""Build the test-time site-packages a subprocess sandbox needs, from the official wheels.

swegemma's subprocess sandbox installs nothing into a task's venv: it exposes
the evaluating interpreter's site-packages through a `.pth` file and expects
the host to provide the repository's runtime and test dependencies, pytest
included (the Docker path gets them from its image plus the task wheels). This
installs the competition's own task wheels (`<devset>/wheels`) into a separate
`.../site-packages` directory, choosing per distribution the highest version
compatible with *this* interpreter — swegemma's `_deduplicate_wheels` rule,
with its Python 3.13 filter replaced by the running interpreter's tags.
`run_official_eval.py --test-site` puts it on the worker's path so sandboxes
see it. Offline only: `pip --no-index --no-deps` from the given files.

The official sandbox image (`<devset>/docker/Dockerfile.sandbox`) also
pip-installs a few packages and copies two compatibility modules (`imp.py`,
`telnetlib.py`) into site-packages. --docker-dir copies every `.py` file the
Dockerfile COPYs into site-packages; --extra-wheel NAME=SHA256=PATH adds a
wheel the task wheels lack (pytest-timeout==2.1.0), refused unless its
digest matches.

--fidelity-lock (requirements/test-site-fidelity.json) with --fidelity-wheels
reproduces what the subprocess sandbox skips and the scorer does: the editable
install that makes a `src/` package (requests) the imported copy, setup.py's
workspace_paths.pth, and date-pinned test dependencies (Pygments by base-commit
date; fastapi's inline_snapshot/dirty_equals/typing_inspection). Each pinned
wheel goes, digest-checked, into its own `_fidelity/<name>-<version>` directory;
`zenithsync/test_site_shim.py` is copied in as `apport_python_hook.py` and
chooses per sandbox. Refused unless this interpreter's sitecustomize imports
apport_python_hook (Ubuntu's does), since nothing else would run the shim.
--fidelity-requirements LOCK prints one `name==version` per pinned wheel (for
`pip download --no-deps`) and exits.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record


def select_wheels(wheels, supported):
    """Highest compatible version per normalized distribution name."""
    from packaging.utils import parse_wheel_filename
    chosen = {}
    for path in wheels:
        name, version, _, tags = parse_wheel_filename(path.name)
        if not tags & supported:
            continue
        key = re.sub(r'[-_.]+', '_', str(name)).lower()
        if key not in chosen or version > chosen[key][0]:
            chosen[key] = (version, path)
    return [chosen[key][1] for key in sorted(chosen)]


def dockerfile_modules(docker_dir):
    """The .py files Dockerfile.sandbox COPYs into site-packages."""
    text = (docker_dir / 'Dockerfile.sandbox').read_text()
    names = re.findall(r'^COPY\s+(\S+\.py)\s+\S*/site-packages/\S+$', text, re.M)
    return [docker_dir / name for name in names]


def normalize(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def load_fidelity_lock(path):
    """The fidelity lock, validated: dates, versions, wheel names and digests are explicit."""
    from datetime import date
    from packaging.utils import parse_wheel_filename
    lock = json.loads(Path(path).read_text())
    if lock.get('schema_version') != 1 or not lock.get('groups'):
        raise ValueError(f'{path}: schema_version 1 with groups required')
    for group, dists in lock['groups'].items():
        if group != '*' and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', group):
            raise ValueError(f'{path}: group {group!r} is neither * nor an import name')
        for dist, entries in dists.items():
            if not entries:
                raise ValueError(f'{path}: {group}/{dist} has no entries')
            dates = [e['from'] for e in entries]
            for value in dates:
                date.fromisoformat(value)
            if dates != sorted(set(dates)):
                raise ValueError(f'{path}: {group}/{dist} dates must be unique and ascending')
            for e in entries:
                name, version, _, _ = parse_wheel_filename(e['wheel'])
                if normalize(str(name)) != normalize(dist) or str(version) != e['version']:
                    raise ValueError(f'{path}: {e["wheel"]} is not {dist}=={e["version"]}')
                if not re.fullmatch(r'[0-9a-f]{64}', e['sha256']):
                    raise ValueError(f'{path}: {e["wheel"]} needs a sha256 digest')
    return lock


def fidelity_requirements(lock):
    return sorted({f'{dist}=={e["version"]}' for dists in lock['groups'].values()
                   for dist, entries in dists.items() for e in entries})


def shim_trigger(find_spec=None):
    """Origin of this interpreter's sitecustomize if it imports apport_python_hook, else None."""
    import importlib.util
    spec = (find_spec or importlib.util.find_spec)('sitecustomize')
    try:
        source = Path(spec.origin).read_text() if spec and spec.origin else ''
    except OSError:
        source = ''
    return spec.origin if 'apport_python_hook' in source else None


def pip_install(wheel, target):
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', '--no-index', '--no-deps',
                    '--target', str(target), str(wheel)], check=True)


def pin_dir(dist, entry):
    return f'{normalize(dist)}-{entry["version"]}'


def selection_table(lock):
    """The sandbox's view of the lock: per group and distribution, (from date, directory)."""
    return {group: {dist: [{'from': e['from'], 'dir': pin_dir(dist, e)} for e in entries]
                    for dist, entries in dists.items()}
            for group, dists in lock['groups'].items()}


def build_fidelity(site, lock, wheel_dir, install=pip_install):
    """Install every pinned wheel into its own directory under site/_fidelity, write the
    sandbox's selection table and the shim. Returns the record for test-site.json."""
    shim_target = site / 'apport_python_hook.py'
    if shim_target.exists():
        raise FileExistsError(shim_target)
    wheels = {}
    for dists in lock['groups'].values():
        for dist, entries in dists.items():
            for e in entries:
                directory = pin_dir(dist, e)
                if directory in wheels:
                    continue
                path = Path(wheel_dir) / e['wheel']
                if hashlib.sha256(path.read_bytes()).hexdigest() != e['sha256']:
                    raise ValueError(f'{path}: digest differs from the pinned {e["sha256"]}')
                install(path, site / '_fidelity' / directory)
                wheels[directory] = file_record(path) | {'name': path.name}
    groups = selection_table(lock)
    (site / '_fidelity' / 'selection.json').write_bytes(canonical_json({'schema_version': 1, 'groups': groups}))
    shim_source = ROOT / 'zenithsync' / 'test_site_shim.py'
    shim_target.write_bytes(shim_source.read_bytes())
    return {'selection': groups, 'wheels': [wheels[k] for k in sorted(wheels)],
            'shim': file_record(shim_target) | {'name': shim_target.name}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheels', type=Path)
    parser.add_argument('--output', type=Path, help='a directory named site-packages')
    parser.add_argument('--docker-dir', type=Path, help='<devset>/docker, for the image\'s site modules')
    parser.add_argument('--extra-wheel', action='append', default=[], help='NAME=SHA256=PATH')
    parser.add_argument('--fidelity-lock', type=Path, help='requirements/test-site-fidelity.json')
    parser.add_argument('--fidelity-wheels', type=Path, help='directory holding the lock\'s wheels')
    parser.add_argument('--fidelity-requirements', type=Path, help='print the lock\'s name==version lines and exit')
    args = parser.parse_args()
    if args.fidelity_requirements:
        print('\n'.join(fidelity_requirements(load_fidelity_lock(args.fidelity_requirements))))
        return
    if args.wheels is None or args.output is None:
        parser.error('--wheels and --output are required')
    lock = None
    if args.fidelity_lock:
        if args.fidelity_wheels is None:
            parser.error('--fidelity-lock needs --fidelity-wheels')
        lock = load_fidelity_lock(args.fidelity_lock)
        trigger = shim_trigger()
        if trigger is None:
            raise SystemExit('This interpreter\'s sitecustomize does not import apport_python_hook; '
                             'the fidelity shim would never run in sandboxes')
    if args.output.name != 'site-packages':
        raise ValueError('The sandbox only exposes directories whose path contains site-packages')
    if args.output.exists():
        raise FileExistsError(args.output)
    from packaging.tags import sys_tags
    wheels = sorted(args.wheels.glob('*.whl'))
    selected = select_wheels(wheels, set(sys_tags()))
    extras = []
    for spec in args.extra_wheel:
        name, digest, path = spec.split('=', 2)
        path = Path(path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'{path}: digest differs from the pinned {digest}')
        if any(re.sub(r'[-_.]+', '_', w.name.split('-')[0]).lower() == name for w in selected):
            raise ValueError(f'{name} is already provided by the task wheels')
        extras.append(path)
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', '--no-index', '--no-deps',
                    '--target', str(args.output), *map(str, selected + extras)], check=True)
    modules = dockerfile_modules(args.docker_dir) if args.docker_dir else []
    for module in modules:
        target = args.output / module.name
        if target.exists():
            raise FileExistsError(target)
        shutil.copyfile(module, target)
    record = {'schema_version': 1, 'python': sys.version.split()[0], 'available': len(wheels),
              'selected': [file_record(path) | {'name': path.name} for path in selected],
              'extra_wheels': [file_record(path) | {'name': path.name} for path in extras],
              'image_modules': [file_record(path) | {'name': path.name} for path in modules]}
    if lock is not None:
        record['fidelity'] = build_fidelity(args.output, lock, args.fidelity_wheels) | {
            'lock': file_record(args.fidelity_lock), 'sitecustomize': trigger}
    (args.output.parent / 'test-site.json').write_bytes(canonical_json(record))
    print(json.dumps({'available': len(wheels), 'selected': len(selected), 'extra_wheels': len(extras),
                      'image_modules': [m.name for m in modules],
                      'fidelity_wheels': len(record['fidelity']['wheels']) if lock is not None else 0}))


if __name__ == '__main__':
    main()
