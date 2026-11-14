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
"""
import argparse
import json
from pathlib import Path
import re
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheels', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='a directory named site-packages')
    args = parser.parse_args()
    if args.output.name != 'site-packages':
        raise ValueError('The sandbox only exposes directories whose path contains site-packages')
    if args.output.exists():
        raise FileExistsError(args.output)
    from packaging.tags import sys_tags
    wheels = sorted(args.wheels.glob('*.whl'))
    selected = select_wheels(wheels, set(sys_tags()))
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', '--no-index', '--no-deps',
                    '--target', str(args.output), *map(str, selected)], check=True)
    record = {'schema_version': 1, 'python': sys.version.split()[0], 'available': len(wheels),
              'selected': [file_record(path) | {'name': path.name} for path in selected]}
    (args.output.parent / 'test-site.json').write_bytes(canonical_json(record))
    print(json.dumps({'available': len(wheels), 'selected': len(selected)}))


if __name__ == '__main__':
    main()
