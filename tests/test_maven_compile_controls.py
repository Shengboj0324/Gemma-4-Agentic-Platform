import copy
import unittest

from zenithsync.maven_compile_controls import compare_compile_barrier_runs, missing_symbol_test_compile
from tests.test_junit_controls import report


DIAGNOSTIC = {'file': '/testbed/src/test/java/Test.java', 'line': 12, 'column': 3,
              'symbol': 'method missing()', 'location': 'variable subject of type Example'}
LOG = '''[INFO] --- compiler:3.1:testCompile (default-testCompile) @ project ---
[ERROR] COMPILATION ERROR :
[INFO] -------------------------------------------------------------
[ERROR] /testbed/src/test/java/Test.java:[12,3] cannot find symbol
  symbol:   method missing()
  location: variable subject of type Example
[INFO] 1 error
[INFO] -------------------------------------------------------------
[INFO] BUILD FAILURE
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.1:testCompile (default-testCompile) on project project: Compilation failure
'''


class MavenCompileTests(unittest.TestCase):
    def parse(self, text=LOG, **kwargs):
        values = {'exit_code': 1, 'reports': {}, 'expected': [DIAGNOSTIC]}
        values.update(kwargs)
        return missing_symbol_test_compile(text, **values)

    def test_expected_compile_failure_does_not_invent_test_outcomes(self):
        result = self.parse()
        self.assertEqual(result['diagnostics'], [DIAGNOSTIC])
        self.assertIsNone(result['runtime_case_outcomes'])
        self.assertFalse(result['training_approved'])

    def test_wrong_phase_status_or_reports_reject(self):
        for values in ({'exit_code': 0}, {'exit_code': True}, {'exit_code': 137},
                       {'reports': {'stale.xml': b'<testsuite/>'}}, {'reports': None}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.parse(**values)
        for text in (LOG.replace(':testCompile ', ':compile '), LOG + '[INFO] BUILD SUCCESS\n',
                     LOG + 'Tests run: 1\n', LOG + '[INFO] --- surefire:2.16:test ---\n',
                     LOG + '[INFO] Tests run: 1\n', '[ERROR] prior failure\n' + LOG,
                     LOG + '[ERROR] COMPILATION ERROR :\n', LOG.replace('BUILD FAILURE', 'BUILD SUCCESS')):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_missing_changed_and_additional_diagnostics_reject(self):
        for before, after in (('method missing()', 'method unrelated()'),
                              ('[12,3]', '[13,3]'), ('[INFO] 1 error', '[INFO] 2 errors'),
                              ('  location: variable subject of type Example\n', ''),
                              ('[INFO] BUILD FAILURE', '[ERROR] dependency resolution failed\n[INFO] BUILD FAILURE')):
            with self.subTest(before=before), self.assertRaises(ValueError):
                self.parse(LOG.replace(before, after))

    def test_invalid_expectations_and_encoded_logs_reject(self):
        for expected in ([], [DIAGNOSTIC, DIAGNOSTIC], ['class-only-label'], [{}]):
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                self.parse(expected=expected)
        for key, value in (('line', True), ('column', -1), ('symbol', '\nforged'), ('file', '../Test.java')):
            row = copy.deepcopy(DIAGNOSTIC); row[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.parse(expected=[row])
        for text in ('\0' + LOG, '\x1b[31m' + LOG):
            with self.assertRaises(ValueError):
                self.parse(text)

    def test_summary_repeats_match_and_extra_footer_errors_reject(self):
        repeat = ('[ERROR] /testbed/src/test/java/Test.java:[12,3] cannot find symbol\n'
                  '[ERROR]   symbol:   method missing()\n'
                  '[ERROR]   location: variable subject of type Example\n')
        self.assertIsNone(self.parse(LOG + repeat)['runtime_case_outcomes'])
        for tail in (repeat.replace('missing()', 'unrelated()'),
                     repeat + '[ERROR] another failure\n', repeat + repeat,
                     '[ERROR] build plugin crashed\n'):
            with self.subTest(tail=tail), self.assertRaises(ValueError):
                self.parse(LOG + tail)

    def test_compile_barrier_comparison_preserves_unknown_base_cases(self):
        runs = {'base': {'stdout': LOG, 'exit_code': 1, 'reports': {}}}
        for role in ('reference', 'candidate'):
            runs[role] = {'stdout': '', 'exit_code': 0, 'reports': {'suite.xml': report()}}
        expectations = {'expected_diagnostics': [DIAGNOSTIC],
                        'passing_cases': [['C', 'repair'], ['C', 'stable']],
                        'skipped_cases': [['C', 'optional']]}
        result = compare_compile_barrier_runs(runs, **expectations)
        self.assertTrue(result['compile_to_test_phase_change_verified'])
        self.assertFalse(result['runtime_fail_to_pass_transitions_verified'])
        self.assertIsNone(result['base']['runtime_case_outcomes'])
        self.assertFalse(result['training_approved'])
        for mutation in ('missing_role', 'base_report', 'wrong_symbol', 'missing_case',
                         'unexpected_skip', 'candidate_failure', 'duplicate', 'overlap'):
            changed, expected = copy.deepcopy(runs), copy.deepcopy(expectations)
            if mutation == 'missing_role': del changed['reference']
            elif mutation == 'base_report': changed['base']['reports'] = {'stale.xml': report()}
            elif mutation == 'wrong_symbol': changed['base']['stdout'] = LOG.replace('missing()', 'other()')
            elif mutation == 'missing_case': expected['passing_cases'].pop()
            elif mutation == 'unexpected_skip': expected['skipped_cases'] = []
            elif mutation == 'candidate_failure':
                changed['candidate'] = {'stdout': '', 'exit_code': 1,
                    'reports': {'suite.xml': report([('C', 'repair', 'fail'),
                        ('C', 'stable', 'pass'), ('C', 'optional', 'skip')])}}
            elif mutation == 'duplicate': expected['passing_cases'].append(['C', 'repair'])
            else: expected['skipped_cases'].append(['C', 'repair'])
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                compare_compile_barrier_runs(changed, **expected)


if __name__ == '__main__':
    unittest.main()
