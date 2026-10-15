import copy
import json
import unittest

from zenithsync.mocha_controls import compare_mocha_publisher, compare_mocha_runs, mocha_outcomes


def report(failing=False):
    first = {'title': 'repair', 'fullTitle': 'suite repair', 'currentRetry': 0,
             'duration': 1, 'err': {'message': 'mismatch'} if failing else {}}
    second = {'title': 'stable', 'fullTitle': 'suite stable', 'currentRetry': 0,
              'duration': 0, 'err': {}}
    return {'stats': {'tests': 2, 'passes': 1 if failing else 2,
                      'failures': int(failing), 'pending': 0},
            'tests': [first, second], 'passes': [second] if failing else [first, second],
            'failures': [first] if failing else [], 'pending': []}


class MochaControlsTests(unittest.TestCase):
    def test_complete_transition_and_same_short_titles(self):
        runs = {role: {'text': json.dumps(report(role == 'base')),
                       'exit_code': int(role == 'base')}
                for role in ('base', 'reference', 'candidate')}
        result = compare_mocha_runs(runs, fail_to_pass=['suite repair'],
                                    pass_to_pass=['suite stable'])
        self.assertEqual(result['test_count'], 2)
        self.assertFalse(result['training_approved'])
        value = report()
        value['tests'][1]['title'] = 'repair'
        value['tests'][1]['fullTitle'] = 'other repair'
        self.assertEqual(len(mocha_outcomes(json.dumps(value), exit_code=0)['tests']), 2)

    def test_malformed_json_duplicate_fields_and_nonfinite_numbers(self):
        for text in ('{}', '[]', '{} trailing', '{"stats":{},"stats":{}}',
                     '{"stats":NaN}', '{"stats":Infinity}', ''):
            with self.subTest(text=text), self.assertRaises(ValueError):
                mocha_outcomes(text, exit_code=0)

    def test_counts_partition_and_identity_corruption(self):
        variants = []
        value = report(); value['stats']['tests'] = True; variants.append(value)
        value = report(); value['stats']['passes'] = 3; variants.append(value)
        value = report(); value['passes'] = []; variants.append(value)
        value = report(); value['tests'].append(copy.deepcopy(value['tests'][0])); variants.append(value)
        value = report(); value['passes'] = copy.deepcopy(value['passes'])
        value['passes'][0]['duration'] = 2; variants.append(value)
        value = report(); value['tests'][0]['fullTitle'] = 'wrong'; variants.append(value)
        value = report(); value['tests'][0]['currentRetry'] = 1; variants.append(value)
        value = report(); value['tests'][0]['err'] = {'message': 'hidden'}; variants.append(value)
        value = report(True); value['tests'][0]['err'] = {}; variants.append(value)
        value = report(); value['tests'][0]['duration'] = -1; variants.append(value)
        value = report(); value['tests'][0]['duration'] = True; variants.append(value)
        value = report(); value['stats']['pending'] = 1; variants.append(value)
        value = report(); value['pending'] = [value['tests'][0]]; variants.append(value)
        for value in variants:
            with self.subTest(value=value), self.assertRaises(ValueError):
                mocha_outcomes(json.dumps(value), exit_code=0)

    def test_hook_only_failure_and_exit_mismatch(self):
        value = report(True)
        value['failures'] = [{'title': 'before all', 'fullTitle': 'suite before all',
                              'currentRetry': 0, 'err': {'message': 'hook failed'}}]
        with self.assertRaises(ValueError):
            mocha_outcomes(json.dumps(value), exit_code=1)
        for code in (True, -1, 256, 1, None):
            with self.subTest(code=code), self.assertRaises(ValueError):
                mocha_outcomes(json.dumps(report()), exit_code=code)
        with self.assertRaises(ValueError):
            mocha_outcomes(json.dumps(report(True)), exit_code=0)

    def test_coverage_and_regression_cannot_be_hidden(self):
        runs = {role: {'text': json.dumps(report(role == 'base')),
                       'exit_code': int(role == 'base')}
                for role in ('base', 'reference', 'candidate')}
        for fail, passed in [([], ['suite stable']), (['suite repair'], []),
                             (['repair'], ['suite stable']),
                             (['suite repair'], ['suite repair', 'suite stable'])]:
            with self.subTest(fail=fail), self.assertRaises(ValueError):
                compare_mocha_runs(runs, fail_to_pass=fail, pass_to_pass=passed)
        runs['candidate'] = runs['base']
        with self.assertRaises(ValueError):
            compare_mocha_runs(runs, fail_to_pass=['suite repair'],
                               pass_to_pass=['suite stable'])

    def test_publisher_ambiguity_requires_all_matching_passes(self):
        runs = {}
        for role in ('base', 'reference', 'candidate'):
            value = report(role == 'base')
            extra = copy.deepcopy(value['tests'][1])
            extra['fullTitle'] = 'other stable'
            value['tests'].append(extra)
            value['passes'].append(extra)
            value['stats']['tests'] += 1
            value['stats']['passes'] += 1
            runs[role] = {'text': json.dumps(value), 'exit_code': int(role == 'base')}
        result = compare_mocha_publisher(runs, fail_to_pass=['repair'], pass_to_pass=['stable'])
        self.assertEqual(result['ambiguous_pass_titles']['stable'], ['other stable', 'suite stable'])
        self.assertEqual(result['pass_to_pass_count'], 2)
        for fail, passed in [(['missing'], ['stable']), (['stable'], ['repair']),
                             (['repair'], ['stable', 'stable'])]:
            with self.subTest(fail=fail), self.assertRaises(ValueError):
                compare_mocha_publisher(runs, fail_to_pass=fail, pass_to_pass=passed)


if __name__ == '__main__':
    unittest.main()
