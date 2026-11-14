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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheels', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='a directory named site-packages')
    parser.add_argument('--docker-dir', type=Path, help='<devset>/docker, for the image\'s site modules')
    parser.add_argument('--extra-wheel', action='append', default=[], help='NAME=SHA256=PATH')
    args = parser.parse_args()
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
    (args.output.parent / 'test-site.json').write_bytes(canonical_json(record))
    print(json.dumps({'available': len(wheels), 'selected': len(selected), 'extra_wheels': len(extras),
                      'image_modules': [m.name for m in modules]}))


if __name__ == '__main__':
    main()
