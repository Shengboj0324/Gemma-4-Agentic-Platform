"""Reconstruct Maven phase controls from bound artifacts; never admit training."""
from pathlib import Path, PurePosixPath

from .artifacts import relative_path
from .contracts import digest, natural
from .maven_compile_controls import compare_compile_barrier_runs


def verify_maven_grade_bundle(*, grade, grading, grading_profile, replay, task,
                             attempt, read, verify, record, path):
    """Use the admission caller's confined, drift-checking filesystem accessors."""
    if (grading.get('status') != 'qualified_compile_barrier_controls'
            or grading.get('image') != replay['image']
            or grading.get('evaluator_kind') != 'maven_compile_barrier_v1'
            or grading.get('training_approved') is not False):
        raise ValueError('Qualified Maven phase-control receipt required')
    if grading_profile is None:
        raise ValueError('Explicit bound Maven grading profile required')
    inputs = {str(path(name)): identity for name, identity in grading['inputs'].items()}
    if inputs.get(str(path(grading_profile))) != record(grading_profile):
        raise ValueError('Grading profile not bound to execution')
    profile = read(grading_profile)
    roles = {'base', 'reference', 'candidate'}
    if set(grading['artifacts']) != roles or set(grading['cleanup']) != roles:
        raise ValueError('Exactly three grading controls required')
    snapshots = [read(name) for name in grading['inputs'] if Path(name).name == 'snapshot.json']
    if not snapshots or any(value != snapshots[0] for value in snapshots):
        raise ValueError('Consistent bound snapshot metadata required')
    snapshot = snapshots[0]
    if (snapshot['base_commit'] != task['base_commit'] or snapshot['exact_tree_preserved'] is not True
            or snapshot['reachable_commits'] != 1):
        raise ValueError('Exact source snapshot required')
    runs = {}
    for role in sorted(roles):
        directory = path(grade / role)
        declared = grading['artifacts'][role]
        for name, identity in declared.items():
            relative = PurePosixPath(name)
            if (relative.is_absolute() or '..' in relative.parts or len(relative.parts) < 2
                    or relative.parts[0] != role or '\\' in name):
                raise ValueError('Unsafe grading artifact path')
            verify(grade / name, identity)
        entries = list(directory.rglob('*'))
        if any(entry.is_symlink() for entry in entries):
            raise ValueError('Symlink grading artifacts are unsupported')
        actual = {str(entry.relative_to(path(grade))): record(entry)
                  for entry in entries if entry.is_file()}
        if actual != declared:
            raise ValueError('Incomplete or changed role artifact inventory')
        cleanup = read(directory / 'cleanup.json')
        state = read(directory / 'container-state.json')
        if (cleanup != grading['cleanup'][role] or cleanup.get('removed') is not True
                or type(state.get('ExitCode')) is not int or state['ExitCode'] != 0
                or state.get('OOMKilled') is not False or state.get('Status') != 'exited'):
            raise ValueError('Unclean or failed grading container')
        config = read(directory / 'config.json')
        tests_patch = directory / 'tests.patch'
        if path(tests_patch).read_bytes() != task['test_patch'].encode('utf-8'):
            raise ValueError('Publisher tests differ from bound task')
        verify(tests_patch, config['tests_patch'])
        applied = {'tests.patch': config['tests_patch']}
        repair = directory / 'repair.patch'
        if role == 'base':
            if config['repair_patch'] is not None or repair.exists():
                raise ValueError('Base cannot receive a repair')
        else:
            expected_patch = (task['patch'].encode('utf-8') if role == 'reference'
                              else path(attempt / 'submitted.patch').read_bytes())
            if path(repair).read_bytes() != expected_patch:
                raise ValueError('Repair patch differs from reference or frozen replay')
            verify(repair, config['repair_patch'])
            applied['repair.patch'] = config['repair_patch']
        audit = directory / 'audit'
        runtime = read(audit / 'runtime.json')
        if (config['snapshot'] != snapshot or runtime['snapshot'] != snapshot
                or runtime['applied'] != applied or runtime['reports_initially_absent'] is not True
                or runtime['command'] != ['mvn', '-o', '-B', '-ntp', 'test']):
            raise ValueError('Maven execution contract mismatch')
        for filename, key in (('tracked-before.json', 'tracked_before'), ('tracked-after.json', 'tracked_after'),
                              ('stdout.log', 'stdout'), ('stderr.log', 'stderr')):
            verify(audit / filename, runtime[key])
        if (runtime['tracked_before'] != runtime['tracked_after']
                or record(audit / 'tracked-before.patch') != record(audit / 'tracked-after.patch')):
            raise ValueError('Tests changed tracked source')
        before = read(audit / 'tracked-before.json')
        if (not isinstance(before, list) or not before
                or any(not isinstance(row, dict) or set(row) != {'path', 'mode', 'sha256', 'size_bytes'}
                       for row in before)):
            raise ValueError('Complete tracked-source records required')
        for row in before:
            relative_path(row['path'])
            digest(row['sha256'])
            natural(row['size_bytes'], 'tracked source size')
            if row['mode'] not in ('100644', '100755'):
                raise ValueError('Unsupported tracked source mode')
        if len(before) != len({row['path'] for row in before}):
            raise ValueError('Nonempty unique tracked-source inventory required')
        report_dir = audit / 'reports'
        report_paths = sorted(report_dir.iterdir()) if report_dir.exists() else []
        if any(not item.is_file() or item.suffix not in ('.xml', '.txt') for item in report_paths):
            raise ValueError('Unexpected report artifact')
        if {item.name: record(item) for item in report_paths} != runtime['reports']:
            raise ValueError('Report inventory differs from runtime')
        runs[role] = {'stdout': path(audit / 'stdout.log').read_text(),
                      'exit_code': runtime['maven_exit'],
                      'reports': {item.name: path(item).read_bytes()
                                  for item in report_paths if item.suffix == '.xml'}}
    comparison = compare_compile_barrier_runs(runs, **profile)
    if comparison != grading['comparison']:
        raise ValueError('Maven grading summary contradicts raw evidence')
    return {'all_cases_match_reference': True, 'phase_comparison': comparison,
            'training_approved': False}
