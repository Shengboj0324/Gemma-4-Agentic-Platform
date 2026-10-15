import unittest
from zenithsync.pytest_applicability import applicable_nodes

SOURCE = '''import django
import pytest
import rest_framework_api_key
@pytest.mark.skipif(django.VERSION < (3, 2), reason="new branch")
def test_new():
    assert True
@pytest.mark.skipif(django.VERSION >= (3, 2), reason="old branch")
def test_old():
    assert True
'''
NODES = ['tests/compat.py::test_new', 'tests/compat.py::test_old', 'tests/other.py::test_extra']


class ApplicabilityTests(unittest.TestCase):
    def run_source(self, source=SOURCE, version=(3, 2, 25, 'final', 0), nodes=None):
        return applicable_nodes(source, module_path='tests/compat.py',
                                collected=NODES if nodes is None else nodes, version=version)

    def test_boundary_and_other_module_preservation(self):
        self.assertEqual(self.run_source(version=(3, 1, 14, 'final', 0)), NODES[1:])
        self.assertEqual(self.run_source(), [NODES[0], NODES[2]])
        self.assertEqual(self.run_source(version=(3, 2, 0, 'alpha', 1)), [NODES[0], NODES[2]])

    def test_full_python_tuple_semantics(self):
        # Django VERSION has five components: equality with a three-tuple is false.
        source = SOURCE.replace('django.VERSION < (3, 2)', 'django.VERSION == (3, 2, 0)')
        self.assertIn(NODES[0], self.run_source(source, (3, 2, 0, 'final', 0)))
        source = source.replace('== (3, 2, 0)', '> (3, 2, 0)')
        self.assertNotIn(NODES[0], self.run_source(source, (3, 2, 0, 'final', 0)))

    def test_comparison_operators_against_python(self):
        for operator in ('<', '<=', '>', '>=', '==', '!='):
            source = SOURCE.replace('django.VERSION < (3, 2)', f'django.VERSION {operator} (3, 2)')
            for version in ((3, 1, 14, 'final', 0), (3, 2, 0, 'alpha', 1), (4, 0, 0, 'final', 0)):
                a, b = version, (3, 2)
                expected = {'<': a < b, '<=': a <= b, '>': a > b, '>=': a >= b, '==': a == b, '!=': a != b}[operator]
                self.assertEqual(NODES[0] not in self.run_source(source, version), expected)

    def test_unsupported_expressions_and_decorators_reject(self):
        for expression in ('True', 'django.VERSION[0] < 3', 'django.VERSION < (3, 2) or True',
                           'django.VERSION < (True, 2)', 'django.VERSION < tuple([3, 2])',
                           'other.VERSION < (3, 2)', 'django.VERSION is (3, 2)'):
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                self.run_source(SOURCE.replace('django.VERSION < (3, 2)', expression))
        with self.assertRaises(ValueError):
            self.run_source(SOURCE.replace('@pytest.mark.skipif', '@pytest.mark.skip'))

    def test_alias_rebinding_executable_definition_and_node_drift_reject(self):
        for source in (SOURCE.replace('import django', 'import django as d'),
                       SOURCE + '\ndjango.VERSION = (0, 0)\n',
                       SOURCE.replace('def test_new():', 'def test_new(x=print("bad")):'),
                       SOURCE.replace('def test_new():', 'def test_new(*x: print("bad")):'),
                       SOURCE.replace('def test_new():', 'def test_new(x: print("bad")):'),
                       SOURCE.replace('def test_old():', 'def test_new():')):
            with self.assertRaises(ValueError): self.run_source(source)
        with self.assertRaises(ValueError): self.run_source(nodes=NODES[:-1] + ['tests/compat.py::missing'])

    def test_incomplete_or_ambiguous_runtime_version_rejects(self):
        for version in ((3, 2), (3, 2, 0), (True, 2, 0, 'final', 0),
                        (3, 2, 0, 'unknown', 0), (3, 2, 0, 'final', -1)):
            with self.assertRaises(ValueError): self.run_source(version=version)
