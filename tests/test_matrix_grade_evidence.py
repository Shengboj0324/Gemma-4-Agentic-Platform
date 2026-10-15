"""Synthetic evidence fixtures; these are not recorded agent executions."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from zenithsync.artifacts import canonical_json, file_record
from zenithsync.matrix_grade_evidence import verify_matrix_outcomes
from zenithsync.pytest_matrix import compare_publisher_matrix
from tests.test_pytest_matrix import document


SOURCE = '''import django
import pytest
@pytest.mark.skipif(django.VERSION >= (3, 2), reason="old only")
def test_old():
    pass
@pytest.mark.skipif(django.VERSION < (3, 2), reason="new only")
def test_new():
    pass
def test_common():
    pass
'''


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.counter = 0
        self.expected = dict(FAIL_TO_PASS=['tests/test_versions.py::test_new'],
                             FAIL_TO_FAIL=[], PASS_TO_PASS=[], PASS_TO_FAIL=[])
        self.supplemental = ['tests/test_versions.py::test_old',
                             'tests/test_versions.py::test_common']
        matrix, applicability, environments = {}, {}, {}
        for name, version, active in [('old', [3, 1, 14, 'final', 0], ['old', 'common']),
                                      ('new', [3, 2, 25, 'final', 0], ['new', 'common'])]:
            image = 'sha256:' + ('a' if name == 'old' else 'b') * 64
            roles, matrix[name] = {}, {}
            for role in ('base', 'reference', 'candidate'):
                result = document(active, ['new'] if name == 'new' and role == 'base' else [])
                result['collected'] = [self.node(n) for n in result['collected']]
                for row in result['reports']:
                    row['nodeid'] = self.node(row['nodeid'])
                matrix[name][role] = result
                roles[role] = dict(receipt=self.write({'image_id': image}), outcomes=self.write(result))
            applicability[name] = [self.node(n) for n in active]
            environments[name] = dict(version=self.write({'version': version}),
                                      source=self.write(SOURCE), receipt=self.write({'image_id': image}),
                                      roles=roles)
        self.bundle = dict(metadata=self.write(self.expected),
                           obligations=self.write(dict(publisher_expectations=self.expected,
                                                       supplemental_pass_to_pass=self.supplemental)),
                           module_path='tests/test_versions.py', environments=environments,
                           expected=compare_publisher_matrix(matrix, applicability, self.expected,
                                                             supplemental_pass_to_pass=self.supplemental))

    @staticmethod
    def node(name):
        return 'tests/test_versions.py::test_' + name

    def write(self, value):
        self.counter += 1
        path = self.root / str(self.counter)
        path.write_bytes(value.encode() if isinstance(value, str) else canonical_json(value))
        return {'path': str(path), 'identity': file_record(path)}

    def test_recomputes_without_mutating_or_granting_admission(self):
        before = deepcopy(self.bundle)
        result = verify_matrix_outcomes(self.bundle)
        self.assertEqual(result['grading'], self.bundle['expected'])
        self.assertFalse(result['training_approved'])
        self.assertEqual(self.bundle, before)

    def test_tampered_bytes_and_claimed_result_reject(self):
        bad = deepcopy(self.bundle)
        bad['expected']['outcome_contract_passed'] = False
        with self.assertRaisesRegex(ValueError, 'summary differs'):
            verify_matrix_outcomes(bad)
        Path(self.bundle['metadata']['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            verify_matrix_outcomes(self.bundle)

    def test_version_source_and_image_substitutions_reject(self):
        for field, value in [('version', {'version': [3, 2, 25, 'final', 0]}),
                             ('source', SOURCE.replace('>= (3, 2)', '>= (3, 0)')),
                             ('receipt', {'image_id': 'sha256:' + 'c' * 64})]:
            with self.subTest(field=field):
                bad = deepcopy(self.bundle)
                bad['environments']['old'][field] = self.write(value)
                with self.assertRaises(ValueError):
                    verify_matrix_outcomes(bad)

    def test_missing_roles_and_changed_obligations_reject(self):
        bad = deepcopy(self.bundle)
        del bad['environments']['new']['roles']['candidate']
        with self.assertRaises(ValueError):
            verify_matrix_outcomes(bad)
        bad = deepcopy(self.bundle)
        bad['obligations'] = self.write(dict(publisher_expectations=self.expected,
                                             supplemental_pass_to_pass=[]))
        with self.assertRaises(ValueError):
            verify_matrix_outcomes(bad)
