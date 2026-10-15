"""Synthetic receipt mutations test consistency, not execution authenticity."""
import copy
from pathlib import Path
import tempfile
import unittest

from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.maven_compile_controls import compare_compile_barrier_runs
from zenithsync.maven_grade_bundle import verify_maven_grade_bundle
from tests.test_junit_controls import report
from tests.test_maven_compile_controls import DIAGNOSTIC, LOG


class MavenBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.grade = self.root / 'grade'; self.grade.mkdir()
        self.attempt = self.root / 'attempt'; self.attempt.mkdir()
        (self.attempt / 'submitted.patch').write_text('candidate patch')
        self.task = {'base_commit': 'base', 'test_patch': 'test patch', 'patch': 'reference patch'}
        self.snapshot = {'base_commit': 'base', 'exact_tree_preserved': True, 'reachable_commits': 1}
        self.save(self.root / 'snapshot.json', self.snapshot)
        self.profile = self.root / 'profile.json'
        self.save(self.profile, {'expected_diagnostics': [DIAGNOSTIC],
            'passing_cases': [['C', 'repair'], ['C', 'stable']], 'skipped_cases': [['C', 'optional']]})
        self.grading = {'status': 'qualified_compile_barrier_controls', 'image': 'fixture-image',
            'evaluator_kind': 'maven_compile_barrier_v1', 'training_approved': False,
            'inputs': {str(p): file_record(p) for p in (self.profile, self.root / 'snapshot.json')},
            'artifacts': {}, 'cleanup': {}}
        runs = {}
        for role in ('base', 'reference', 'candidate'):
            directory = self.grade / role; audit = directory / 'audit'; audit.mkdir(parents=True)
            (directory / 'tests.patch').write_text(self.task['test_patch'])
            repair = None
            if role != 'base':
                (directory / 'repair.patch').write_text(self.task['patch'] if role == 'reference' else 'candidate patch')
                repair = file_record(directory / 'repair.patch')
            config = {'snapshot': self.snapshot, 'tests_patch': file_record(directory / 'tests.patch'), 'repair_patch': repair}
            self.save(directory / 'config.json', config)
            cleanup = {'container_id': role, 'removed': True}
            self.grading['cleanup'][role] = cleanup
            self.save(directory / 'cleanup.json', cleanup)
            self.save(directory / 'container-state.json', {'ExitCode': 0, 'OOMKilled': False, 'Status': 'exited'})
            for when in ('before', 'after'):
                self.save(audit / ('tracked-' + when + '.json'),
                          [{'path': 'source.java', 'mode': '100644', 'sha256': 'a' * 64, 'size_bytes': 10}])
                (audit / ('tracked-' + when + '.patch')).write_text('same diff')
            (audit / 'stdout.log').write_text(LOG if role == 'base' else '')
            (audit / 'stderr.log').write_text('')
            reports = {}
            if role != 'base':
                (audit / 'reports').mkdir()
                (audit / 'reports/suite.xml').write_bytes(report())
                reports['suite.xml'] = file_record(audit / 'reports/suite.xml')
            applied = {'tests.patch': config['tests_patch']}
            if repair is not None: applied['repair.patch'] = repair
            runtime = {'snapshot': self.snapshot, 'applied': applied, 'reports_initially_absent': True,
                'command': ['mvn', '-o', '-B', '-ntp', 'test'], 'reports': reports,
                'maven_exit': int(role == 'base'), 'tracked_before': file_record(audit / 'tracked-before.json'),
                'tracked_after': file_record(audit / 'tracked-after.json'),
                'stdout': file_record(audit / 'stdout.log'), 'stderr': file_record(audit / 'stderr.log')}
            self.save(audit / 'runtime.json', runtime)
            self.refresh(role)
            runs[role] = {'stdout': LOG if role == 'base' else '', 'exit_code': runtime['maven_exit'],
                          'reports': {} if role == 'base' else {'suite.xml': report()}}
        self.grading['comparison'] = compare_compile_barrier_runs(runs, **load_json(self.profile))

    @staticmethod
    def save(path, value):
        path.write_bytes(canonical_json(value))

    def refresh(self, role):
        self.grading['artifacts'][role] = {str(p.relative_to(self.grade)): file_record(p)
            for p in (self.grade / role).rglob('*') if p.is_file()}

    def verify(self):
        def resolve(value):
            p = Path(value).resolve(strict=True)
            if not p.is_relative_to(self.root): raise ValueError('Outside fixture')
            return p
        def verify(path, identity):
            if file_record(resolve(path)) != identity: raise ValueError('Identity drift')
        return verify_maven_grade_bundle(grade=self.grade, grading=self.grading,
            grading_profile=self.profile, replay={'image': 'fixture-image'}, task=self.task,
            attempt=self.attempt, read=lambda p: load_json(resolve(p)), verify=verify,
            record=lambda p: file_record(resolve(p)), path=resolve)

    def test_consistent_fixture_retains_phase_distinction(self):
        value = self.verify()
        self.assertTrue(value['all_cases_match_reference'])
        self.assertFalse(value['phase_comparison']['runtime_fail_to_pass_transitions_verified'])
        self.assertFalse(value['training_approved'])

    def test_patch_change_rejected_even_with_updated_inventory(self):
        (self.grade / 'candidate/repair.patch').write_text('different repair')
        self.refresh('candidate')
        with self.assertRaises(ValueError): self.verify()

    def test_source_mutation_rejected_with_updated_artifact_hashes(self):
        p = self.grade / 'candidate/audit/tracked-after.json'
        self.save(p, [{'path': 'changed.java'}])
        runtime_path = self.grade / 'candidate/audit/runtime.json'
        runtime = load_json(runtime_path); runtime['tracked_after'] = file_record(p)
        self.save(runtime_path, runtime); self.refresh('candidate')
        with self.assertRaises(ValueError): self.verify()

    def test_missing_report_not_hidden_by_updated_inventory(self):
        (self.grade / 'candidate/audit/reports/suite.xml').unlink()
        p = self.grade / 'candidate/audit/runtime.json'
        runtime = load_json(p); runtime['reports'] = {}; self.save(p, runtime)
        self.refresh('candidate')
        with self.assertRaises(ValueError): self.verify()

    def test_cleanup_and_oom_cannot_be_relabelled_as_passes(self):
        p = self.grade / 'candidate/container-state.json'
        state = load_json(p); state['OOMKilled'] = True; self.save(p, state)
        self.refresh('candidate')
        with self.assertRaises(ValueError): self.verify()

    def test_profile_and_comparison_binding(self):
        old = copy.deepcopy(self.grading)
        del self.grading['inputs'][str(self.profile)]
        with self.assertRaises(ValueError): self.verify()
        self.grading = old
        self.grading['comparison']['runtime_fail_to_pass_transitions_verified'] = True
        with self.assertRaises(ValueError): self.verify()

    def test_undeclared_artifact_and_cross_role_path(self):
        (self.grade / 'base/extra').write_text('not inventoried')
        with self.assertRaises(ValueError): self.verify()
        (self.grade / 'base/extra').unlink()
        self.grading['artifacts']['base']['candidate/repair.patch'] = file_record(self.grade / 'candidate/repair.patch')
        with self.assertRaises(ValueError): self.verify()

    def test_malformed_source_inventory_rejected_even_when_both_copies_match(self):
        for change in ({'path': '../outside'}, {'mode': '120000'}, {'sha256': 'invalid'},
                       {'size_bytes': True}, {'size_bytes': -1}):
            with self.subTest(change=change):
                row = {'path': 'source.java', 'mode': '100644', 'sha256': 'a' * 64, 'size_bytes': 10}
                row.update(change)
                runtime_path = self.grade / 'candidate/audit/runtime.json'
                runtime = load_json(runtime_path)
                for when in ('before', 'after'):
                    p = self.grade / 'candidate/audit' / ('tracked-' + when + '.json')
                    self.save(p, [row])
                    runtime['tracked_' + when] = file_record(p)
                self.save(runtime_path, runtime)
                self.refresh('candidate')
                with self.assertRaises(ValueError):
                    self.verify()


if __name__ == '__main__':
    unittest.main()
