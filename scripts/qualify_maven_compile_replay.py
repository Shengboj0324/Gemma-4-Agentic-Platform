"""Grade a frozen replay with an explicit Maven compilation-barrier profile.

Publisher patches stay in disposable evaluator containers. This receipt does not
admit data to training or reconcile malformed publisher per-test labels.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.maven_compile_controls import compare_compile_barrier_runs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('attempt', 'snapshot', 'task', 'profile', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    probe = ROOT / 'scripts/run_maven_grade_probe.py'
    paths = [args.attempt / 'receipt.json', args.attempt / 'submitted.patch',
             args.snapshot / 'receipt.json', args.snapshot / 'snapshot.json',
             args.snapshot / 'verification.json', args.snapshot / 'input-bindings.json',
             args.task, args.profile, probe, Path(__file__),
             ROOT / 'zenithsync/maven_compile_controls.py', ROOT / 'zenithsync/junit_controls.py',
             ROOT / 'zenithsync/artifacts.py']
    bindings = {str(path.resolve()): file_record(path) for path in paths}
    attempt = load_json(args.attempt / 'receipt.json')
    snapshot = load_json(args.snapshot / 'snapshot.json')
    verification = load_json(args.snapshot / 'verification.json')
    snapshot_run = load_json(args.snapshot / 'receipt.json')
    for name, expected in load_json(args.snapshot / 'input-bindings.json').items():
        if file_record(Path(name)) != expected:
            raise ValueError('Snapshot verification binding drift')
        bindings[str(Path(name).resolve())] = expected
    task, profile = load_json(args.task), load_json(args.profile)
    if (attempt['status'] != 'replayed_not_graded' or not attempt['cleanup']['removed']
            or attempt['patch'] != file_record(args.attempt / 'submitted.patch')
            or attempt['image'] != snapshot_run['image_id']
            or verification['tracked_manifest_matches'] is not True
            or verification['reachable_commits'] != 1
            or any(snapshot_run[key] != 0 for key in ('returncode', 'copy_returncode', 'cleanup_returncode'))
            or any(task[key] != attempt['task'][key] for key in ('repo', 'instance_id', 'base_commit'))
            or task['base_commit'] != snapshot['base_commit']):
        raise ValueError('Frozen replay and verified source snapshot required')
    image = attempt['image']
    if subprocess.check_output(['docker', 'image', 'inspect', image, '--format', '{{.Id}}'], text=True).strip() != image:
        raise ValueError('Image identity changed')
    args.output.mkdir(parents=True, exist_ok=False)
    runs, artifacts, cleanup_records = {}, {}, {}
    for role in ('base', 'reference', 'candidate'):
        directory = args.output / role
        directory.mkdir()
        (directory / 'tests.patch').write_text(task['test_patch'])
        if role == 'reference':
            (directory / 'repair.patch').write_text(task['patch'])
        elif role == 'candidate':
            shutil.copyfile(args.attempt / 'submitted.patch', directory / 'repair.patch')
        config = {'snapshot': snapshot, 'tests_patch': file_record(directory / 'tests.patch'),
                  'repair_patch': None if role == 'base' else file_record(directory / 'repair.patch')}
        (directory / 'config.json').write_bytes(canonical_json(config))
        cid = subprocess.check_output(['docker', 'create', '--platform', 'linux/amd64',
            '--network', 'none', '--cap-drop', 'ALL', '--memory', '3g', '--cpus', '2',
            '--entrypoint', '/usr/local/bin/python', image, '/tmp/probe.py', '/tmp/config.json'], text=True).strip()
        try:
            copies = [(probe, 'probe.py'), (directory / 'config.json', 'config.json'),
                      (directory / 'tests.patch', 'tests.patch')]
            if role != 'base':
                copies.append((directory / 'repair.patch', 'repair.patch'))
            for path, name in copies:
                subprocess.run(['docker', 'cp', str(path), cid + ':/tmp/' + name], check=True, capture_output=True)
            with (directory / 'probe.stdout').open('wb') as stdout, (directory / 'probe.stderr').open('wb') as stderr:
                process = subprocess.run(['docker', 'start', '-a', cid], stdout=stdout, stderr=stderr, timeout=270)
            state_bytes = subprocess.check_output(['docker', 'inspect', cid, '--format', '{{json .State}}'])
            (directory / 'container-state.json').write_bytes(state_bytes)
            copy = subprocess.run(['docker', 'cp', cid + ':/audit', str(directory / 'audit')], capture_output=True)
        finally:
            cleanup = subprocess.run(['docker', 'rm', '-f', cid], capture_output=True)
            cleanup_records[role] = {'container_id': cid, 'removed': cleanup.returncode == 0}
            (directory / 'cleanup.json').write_bytes(canonical_json(cleanup_records[role]))
        state = load_json(directory / 'container-state.json')
        if (process.returncode or copy.returncode or cleanup.returncode or state['ExitCode']
                or state['OOMKilled'] or state['Status'] != 'exited'):
            raise ValueError('Grading probe, audit copy or cleanup failed')
        audit = directory / 'audit'
        runtime = load_json(audit / 'runtime.json')
        for name, key in (('tracked-before.json', 'tracked_before'), ('tracked-after.json', 'tracked_after'),
                          ('stdout.log', 'stdout'), ('stderr.log', 'stderr')):
            if file_record(audit / name) != runtime[key]:
                raise ValueError('Runtime artifact drift')
        if (runtime['tracked_before'] != runtime['tracked_after']
                or runtime['snapshot'] != snapshot or runtime['reports_initially_absent'] is not True
                or runtime['command'] != ['mvn', '-o', '-B', '-ntp', 'test']
                or (audit / 'tracked-before.patch').read_bytes() != (audit / 'tracked-after.patch').read_bytes()
                or runtime['applied'] != {key: value for key, value in (
                    ('tests.patch', config['tests_patch']), ('repair.patch', config['repair_patch'])) if value is not None}):
            raise ValueError('Grading source or execution contract drift')
        report_paths = sorted((audit / 'reports').iterdir()) if (audit / 'reports').exists() else []
        if {p.name: file_record(p) for p in report_paths} != runtime['reports']:
            raise ValueError('Report inventory drift')
        runs[role] = {'stdout': (audit / 'stdout.log').read_text(), 'exit_code': runtime['maven_exit'],
                      'reports': {p.name: p.read_bytes() for p in report_paths if p.suffix == '.xml'}}
        artifacts[role] = {str(p.relative_to(args.output)): file_record(p)
                           for p in sorted(directory.rglob('*')) if p.is_file()}
        print(role, 'Maven exit', runtime['maven_exit'], 'XML reports', len(runs[role]['reports']), flush=True)
    comparison = compare_compile_barrier_runs(runs, **profile)
    if any(file_record(Path(name)) != expected for name, expected in bindings.items()):
        raise ValueError('Input changed during grading')
    receipt = {'status': 'qualified_compile_barrier_controls', 'image': image, 'inputs': bindings,
               'artifacts': artifacts, 'cleanup': cleanup_records, 'comparison': comparison,
               'evaluator_kind': 'maven_compile_barrier_v1', 'sanitized_snapshot': True,
               'training_approved': False,
               'scope': 'Fresh offline phase controls; production admission integration and publisher-label review remain separate.'}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print('Fresh source-bound Maven controls verified.')


if __name__ == '__main__':
    main()
