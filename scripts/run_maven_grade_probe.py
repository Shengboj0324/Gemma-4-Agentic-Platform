"""Container-only offline Maven grading probe with source and report inventories."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('/testbed')
OUT = Path('/audit')


def identity(path):
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}


def git(*arguments):
    return subprocess.check_output(['git', '-C', str(ROOT), *arguments])


def tracked():
    rows = []
    for raw in git('ls-files', '--stage', '-z').split(b'\0'):
        if not raw:
            continue
        metadata, name = raw.decode('utf-8').split('\t', 1)
        mode, _, stage = metadata.split()
        path = ROOT / name
        if (stage != '0' or mode not in ('100644', '100755') or path.is_symlink()
                or not path.is_file() or not path.resolve().is_relative_to(ROOT)):
            raise ValueError('Unsupported or escaping source entry')
        rows.append({'path': name, 'mode': mode, **identity(path)})
    return rows


def save(name, value):
    (OUT / name).write_text(json.dumps(value, sort_keys=True) + '\n')


def main():
    config = json.loads(Path(sys.argv[1]).read_text())
    if set(config) != {'snapshot', 'tests_patch', 'repair_patch'}:
        raise ValueError('Exact grading configuration required')
    OUT.mkdir(exist_ok=False)
    snapshot = json.loads(Path('/opt/zenithsync/source-snapshot.json').read_text())
    if snapshot != config['snapshot']:
        raise ValueError('Snapshot metadata drift')
    if (git('rev-parse', 'HEAD').decode().strip() != snapshot['snapshot_commit']
            or git('rev-parse', 'HEAD^{tree}').decode().strip() != snapshot['source_tree']
            or git('rev-list', '--all', '--count').strip() != b'1'
            or git('remote').strip() or git('status', '--porcelain', '--untracked-files=all').strip()
            or (ROOT / 'target').exists() or (ROOT / 'target').is_symlink()):
        raise ValueError('Unclean or incorrect baseline')
    applied = {}
    for name, expected in (('repair.patch', config['repair_patch']), ('tests.patch', config['tests_patch'])):
        if expected is None:
            continue
        path = Path('/tmp') / name
        if identity(path) != expected:
            raise ValueError('Input patch drift')
        subprocess.run(['git', '-C', str(ROOT), 'apply', str(path)], check=True)
        applied[name] = expected
    # Include any newly added patch files in before/after source accounting.
    subprocess.run(['git', '-C', str(ROOT), 'add', '--intent-to-add', '--all'], check=True)
    before = tracked()
    save('tracked-before.json', before)
    (OUT / 'tracked-before.patch').write_bytes(git('diff', '--binary', 'HEAD', '--'))
    command = ['mvn', '-o', '-B', '-ntp', 'test']
    with (OUT / 'stdout.log').open('wb') as stdout, (OUT / 'stderr.log').open('wb') as stderr:
        result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=240)
    after = tracked()
    save('tracked-after.json', after)
    (OUT / 'tracked-after.patch').write_bytes(git('diff', '--binary', 'HEAD', '--'))
    if before != after or (OUT / 'tracked-before.patch').read_bytes() != (OUT / 'tracked-after.patch').read_bytes():
        raise ValueError('Tests changed source files')
    reports = ROOT / 'target/surefire-reports'
    inventory, total = {}, 0
    if reports.exists():
        if reports.is_symlink() or not reports.is_dir() or not reports.resolve().is_relative_to(ROOT):
            raise ValueError('Unsafe report directory')
        (OUT / 'reports').mkdir()
        for path in sorted(reports.iterdir()):
            if path.is_symlink() or not path.is_file() or path.suffix not in ('.xml', '.txt'):
                raise ValueError('Unexpected report artifact or JVM crash dump')
            record = identity(path)
            total += record['size_bytes']
            if total > 16 * 1024**2:
                raise ValueError('Report inventory exceeds budget')
            shutil.copyfile(path, OUT / 'reports' / path.name)
            inventory[path.name] = record
    save('runtime.json', {'command': command, 'maven_exit': result.returncode,
         'reports_initially_absent': True, 'reports': inventory, 'applied': applied,
         'tracked_before': identity(OUT / 'tracked-before.json'),
         'tracked_after': identity(OUT / 'tracked-after.json'),
         'stdout': identity(OUT / 'stdout.log'), 'stderr': identity(OUT / 'stderr.log'),
         'snapshot': snapshot, 'training_approved': False})


if __name__ == '__main__':
    main()
