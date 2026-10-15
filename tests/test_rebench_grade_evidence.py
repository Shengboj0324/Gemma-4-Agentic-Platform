"""Reject misleading grade summaries even when their top-level flags pass."""
import copy
from pathlib import Path
import tempfile
import unittest

from zenithsync.artifacts import canonical_json, file_record
from zenithsync.pytest_controls import compare_candidate
from zenithsync.rebench_grade_evidence import verify_rebench_outcomes


class GradeEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.documents = {}
        for role in ('base', 'reference', 'candidate'):
            document = {'collected': ['test.py::case'], 'collection_errors': [],
                        'exitstatus': 1 if role == 'base' else 0,
                        'reports': [{'nodeid': 'test.py::case', 'when': phase,
                                     'outcome': 'failed' if role == 'base' and phase == 'call'
                                     else 'passed'} for phase in ('setup', 'call', 'teardown')]}
            self.documents[role] = document
            self.write(role + '/outcomes.json', document)
        self.write('metadata.json', {'FAIL_TO_PASS': ['test.py::case'],
                                    'PASS_TO_PASS': [], 'FAIL_TO_FAIL': [], 'PASS_TO_FAIL': []})
        self.grade = {'inputs': {'bindings': {
            str(self.root / name): file_record(self.root / name)
            for name in ('metadata.json', 'base/outcomes.json', 'reference/outcomes.json')}},
            'outcomes': file_record(self.root / 'candidate/outcomes.json'),
            'grading': compare_candidate(self.documents['reference'], self.documents['candidate'])}

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json(value))

    def test_complete_evidence_returns_four_bound_files(self):
        self.assertEqual(len(verify_rebench_outcomes(self.grade, self.root)), 4)

    def test_missing_bindings_and_ambiguous_metadata_fail(self):
        with self.assertRaisesRegex(ValueError, 'Bound publisher'):
            verify_rebench_outcomes({'inputs': {}}, self.root)
        self.grade['inputs']['bindings'][str(self.root / 'other/metadata.json')] = {}
        with self.assertRaisesRegex(ValueError, 'Unique bound'):
            verify_rebench_outcomes(self.grade, self.root)

    def test_changed_candidate_bytes_fail_even_with_passing_summary(self):
        self.write('candidate/outcomes.json', self.documents['base'])
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            verify_rebench_outcomes(self.grade, self.root)

    def test_rehashed_failure_cannot_retain_passing_summary(self):
        self.write('candidate/outcomes.json', self.documents['base'])
        self.grade['outcomes'] = file_record(self.root / 'candidate/outcomes.json')
        with self.assertRaisesRegex(ValueError, 'recomputed outcomes'):
            verify_rebench_outcomes(self.grade, self.root)

    def test_declared_failure_is_recomputed_without_becoming_pass(self):
        self.write('candidate/outcomes.json', self.documents['base'])
        self.grade['outcomes'] = file_record(self.root / 'candidate/outcomes.json')
        self.grade['grading'] = compare_candidate(self.documents['reference'], self.documents['base'])
        self.assertEqual(len(verify_rebench_outcomes(self.grade, self.root)), 4)
        self.assertFalse(self.grade['grading']['all_cases_match_reference'])

    def test_publisher_transition_must_match_base_and_reference(self):
        metadata = {'FAIL_TO_PASS': [], 'PASS_TO_PASS': ['test.py::case'],
                    'FAIL_TO_FAIL': [], 'PASS_TO_FAIL': []}
        self.write('metadata.json', metadata)
        self.grade['inputs']['bindings'][str(self.root / 'metadata.json')] = file_record(self.root / 'metadata.json')
        with self.assertRaises(ValueError):
            verify_rebench_outcomes(self.grade, self.root)

    def test_extra_claim_in_summary_is_not_silently_accepted(self):
        grade = copy.deepcopy(self.grade)
        grade['grading']['training_approved'] = True
        with self.assertRaisesRegex(ValueError, 'recomputed outcomes'):
            verify_rebench_outcomes(grade, self.root)
