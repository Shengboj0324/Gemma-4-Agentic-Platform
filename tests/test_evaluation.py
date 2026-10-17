import tempfile
import unittest
from pathlib import Path

from zenithsync.evaluation import compare_junit, junit_outcomes


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def report(self, filename, contents):
        path = self.root / filename
        path.write_text(contents)
        return path

    def test_preserves_failure_error_and_skip_transitions(self):
        before = self.report('before.xml', '''<testsuite tests="3">
          <testcase classname="C" name="a"><failure/></testcase>
          <testcase classname="C" name="b"><error/></testcase>
          <testcase classname="C" name="c"><skipped/></testcase>
        </testsuite>''')
        after = self.report('after.xml', '''<testsuite tests="3">
          <testcase classname="C" name="c"><skipped/></testcase>
          <testcase classname="C" name="a"/>
          <testcase classname="C" name="b"><failure/></testcase>
        </testsuite>''')
        result = compare_junit(before, after)
        self.assertEqual(result['baseline_counts'], {'failed': 1, 'error': 1, 'skipped': 1})
        self.assertEqual(result['candidate_counts'], {'failed': 1, 'passed': 1, 'skipped': 1})
        self.assertEqual(result['changed_cases'], [
            {'test': 'C::a', 'baseline': 'failed', 'candidate': 'passed'},
            {'test': 'C::b', 'baseline': 'error', 'candidate': 'failed'}])

    def test_rejects_missing_or_ambiguous_evidence(self):
        fixtures = [
            '<testsuite tests="0"/>',
            '<testsuite tests="2"><testcase classname="C" name="a"/></testsuite>',
            '<testsuite tests="1"><testcase name="a"/></testsuite>',
            '<testsuite tests="2"><testcase classname="C" name="a"/><testcase classname="C" name="a"/></testsuite>',
            '<testsuite tests="1"><testcase classname="C" name="a"><failure/><skipped/></testcase></testsuite>',
        ]
        for index, content in enumerate(fixtures):
            with self.subTest(index=index), self.assertRaises(ValueError):
                junit_outcomes(self.report(str(index) + '.xml', content))

    def test_does_not_compare_different_test_sets(self):
        before = self.report('before.xml', '<testsuite tests="1"><testcase classname="C" name="a"/></testsuite>')
        after = self.report('after.xml', '<testsuite tests="1"><testcase classname="C" name="b"/></testsuite>')
        with self.assertRaisesRegex(ValueError, 'Unpaired'):
            compare_junit(before, after)

    def test_rejects_contradictory_outcome_counts(self):
        for attribute, outcome in [('failures', 'failure'), ('errors', 'error'),
                                   ('skipped', 'skipped')]:
            for declared, body in [('1', ''), ('0', '<' + outcome + '/>')]:
                with self.subTest(attribute=attribute, declared=declared):
                    contents = (f'<testsuite tests="1" {attribute}="{declared}">'
                                f'<testcase classname="C" name="a">{body}</testcase></testsuite>')
                    with self.assertRaisesRegex(ValueError, 'Declared ' + attribute):
                        junit_outcomes(self.report('conflict.xml', contents))

    def test_checks_aggregate_and_nested_suite_counts(self):
        suite = ('<testsuite tests="1" failures="1" errors="0" skipped="0">'
                 '<testcase classname="C" name="a"><failure/></testcase></testsuite>')
        valid = f'<testsuites tests="1" failures="1">{suite}</testsuites>'
        self.assertEqual(junit_outcomes(self.report('valid.xml', valid)), {'C::a': 'failed'})
        for contents in [f'<testsuites tests="2">{suite}</testsuites>',
                         f'<testsuites failures="0">{suite}</testsuites>',
                         f'<testsuite tests="1" failures="0">{suite}</testsuite>']:
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                junit_outcomes(self.report('aggregate.xml', contents))

    def test_rejects_noncanonical_summary_numbers(self):
        for declared in ['-1', '+0', '0.0', ' 0', '\u0660']:
            contents = (f'<testsuite tests="1" failures="{declared}">'
                        '<testcase classname="C" name="a"/></testsuite>')
            with self.subTest(declared=declared), self.assertRaises(ValueError):
                junit_outcomes(self.report('number.xml', contents))


if __name__ == '__main__':
    unittest.main()
