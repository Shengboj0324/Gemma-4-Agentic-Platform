import json
import unittest

from zenithsync.go_test_controls import compare_go_runs, go_outcomes


def event(action, test=None, package='example/p'):
    value = {'Action': action, 'Package': package}
    if test is not None:
        value['Test'] = test
    return value


def stream(events):
    return '\n'.join(json.dumps(value) for value in events) + '\n'


def sample(outcome='pass', package='example/p'):
    return [event('start', package=package), event('run', 'TestFix', package),
            event(outcome, 'TestFix', package), event(outcome, package=package)]


class GoTestControlsTests(unittest.TestCase):
    def parse(self, events, code=0, empty=None):
        return go_outcomes(stream(events), exit_code=code, no_test_packages=empty or [])

    def test_parallel_interleaving_and_explicit_empty_package(self):
        rows = [event('start'), event('run', 'TestFix'), event('pause', 'TestFix'),
                *sample(package='example/q'), event('cont', 'TestFix'),
                event('pass', 'TestFix'), event('pass'),
                event('start', package='example/empty'), event('skip', package='example/empty')]
        result = self.parse(rows, empty=['example/empty'])
        self.assertEqual(len(result['tests']), 2)
        self.assertEqual(result['packages']['example/empty'], 'skip')

    def test_duplicates_and_incomplete_lifecycles(self):
        rows = sample()
        variants = [rows[:-1], rows[:2], rows[:2] + rows[1:],
                    rows[:3] + rows[2:], rows[:1] + rows, rows[1:],
                    [rows[0], rows[2], rows[3]]]
        for value in variants:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.parse(value)

    def test_skip_and_unsupported_events_rejected(self):
        for action in ('skip', 'bench', 'cont', 'unknown'):
            with self.subTest(action=action), self.assertRaises(ValueError):
                self.parse([event('start'), event('run', 'TestFix'),
                            event(action, 'TestFix'), event('pass')])

    def test_package_and_process_failures_cannot_be_hidden(self):
        for rows, code in [(sample('fail'), 0), (sample(), 1),
                           (sample('fail')[:-1] + [event('pass')], 1),
                           (sample()[:-1] + [event('fail')], 1),
                           ([event('start'), event('fail')], 1)]:
            with self.subTest(rows=rows, code=code), self.assertRaises(ValueError):
                self.parse(rows, code)
        for code in (True, -9, 2):
            with self.assertRaises(ValueError):
                self.parse(sample(), code)

    def test_empty_package_requires_exact_allowlist(self):
        rows = sample() + [event('start', package='empty'), event('skip', package='empty')]
        for empty in ([], ['missing'], ['empty', 'empty']):
            with self.assertRaises(ValueError):
                self.parse(rows, empty=empty)
        with self.assertRaises(ValueError):
            self.parse(sample(), empty=['example/p'])

    def test_malformed_and_duplicate_json_rejected(self):
        for text in ('', 'null\n', '{}\n', stream(sample()) + '\n',
                     '{"Action":"start","Action":"pass","Package":"p"}\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                go_outcomes(text, exit_code=0, no_test_packages=[])

    def test_invalid_output_and_build_failure_rejected(self):
        for row in ({**event('output'), 'Output': 3}, event('output', 'Unstarted'),
                    {**event('output'), 'Output': '', 'FailedBuild': 'p'}):
            with self.assertRaises(ValueError):
                self.parse([event('start'), row, *sample()[1:]])

    def test_valid_output_is_not_parsed_as_test_evidence(self):
        rows = sample()
        rows.insert(2, {**event('output', 'TestFix'), 'Output': 'FAIL fake\n'})
        self.assertEqual(self.parse(rows)['exit_code'], 0)

    def compare(self, base, reference, candidate, expectations=None):
        def run(rows):
            return {'stdout': stream(rows), 'exit_code': int(any(
                row['Action'] == 'fail' and 'Test' not in row for row in rows))}
        return compare_go_runs(run(base), run(reference), run(candidate), expectations or {
            'FAIL_TO_PASS': ['TestFix'], 'PASS_TO_PASS': [],
            'FAIL_TO_FAIL': [], 'PASS_TO_FAIL': []}, no_test_packages=[])

    def test_subtest_parent_consistency(self):
        valid = [event('start'), event('run', 'TestFix'),
                 event('run', 'TestFix/child'), event('fail', 'TestFix/child'),
                 event('fail', 'TestFix'), event('fail')]
        self.assertEqual(len(self.parse(valid, 1)['tests']), 2)
        for rows in (valid[:1] + valid[2:],
                     valid[:4] + [event('pass', 'TestFix'), event('fail')],
                     valid[:3] + [event('pass', 'TestFix')] + valid[3:]):
            with self.assertRaises(ValueError):
                self.parse(rows, 1)

    def test_transition_and_candidate_disagreement(self):
        self.assertTrue(self.compare(sample('fail'), sample(), sample())['all_cases_match_reference'])
        result = self.compare(sample('fail'), sample(), sample('fail'))
        self.assertFalse(result['all_cases_match_reference'])
        self.assertEqual(result['disagreements'][0]['nodeid'], 'example/p::TestFix')
        with self.assertRaises(ValueError):
            self.compare(sample(), sample(), sample())

    def test_ambiguous_names_and_unequal_coverage_rejected(self):
        for before, after, candidate in [
                (sample('fail') + sample('fail', 'q'), sample() + sample(package='q'),
                 sample() + sample(package='q')),
                (sample('fail'), sample(), sample() + sample(package='q'))]:
            with self.assertRaises(ValueError):
                self.compare(before, after, candidate)

    def test_missing_duplicate_and_extra_publisher_expectations(self):
        for names in ([], ['TestFix', 'TestFix'], ['Missing'], ['TestFix', 'Missing']):
            with self.assertRaises(ValueError):
                self.compare(sample('fail'), sample(), sample(), {
                    'FAIL_TO_PASS': names, 'PASS_TO_PASS': [],
                    'FAIL_TO_FAIL': [], 'PASS_TO_FAIL': []})


if __name__ == '__main__':
    unittest.main()
