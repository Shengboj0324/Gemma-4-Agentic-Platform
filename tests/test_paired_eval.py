import json
from pathlib import Path
import tempfile
import unittest

from zenithsync.paired_eval import (bootstrap_difference, compare, exact_mcnemar,
                                    load_task_results, wilson)


def row(tid, resolved, **extra):
    return {'instance_id': tid, 'repo': 'r/' + tid[0], 'resolved': resolved,
            'agent_patch_size': 10, 'error': None, 'duration_seconds': 60.0,
            'tool_calls': 5, 'total_llm_calls': 7, **extra}


class StatisticsTests(unittest.TestCase):
    def test_reference_values_from_the_protocol(self):
        # docs/05: b=23, c=10 gives exact McNemar p ≈ 0.03508.
        self.assertAlmostEqual(exact_mcnemar(23, 10), 0.03508, places=5)
        self.assertEqual(exact_mcnemar(0, 0), 1.0)
        self.assertEqual(exact_mcnemar(5, 5), 1.0)
        self.assertAlmostEqual(exact_mcnemar(0, 6), 2 / 64)
        # docs/05: 39/129 -> [22.97%, 38.63%], 52/129 -> [32.24%, 48.94%].
        low, high = wilson(39, 129)
        self.assertAlmostEqual(low, 0.2297, places=4)
        self.assertAlmostEqual(high, 0.3863, places=4)
        low, high = wilson(52, 129)
        self.assertAlmostEqual(low, 0.3224, places=4)
        self.assertAlmostEqual(high, 0.4894, places=4)
        self.assertIsNone(wilson(0, 0))

    def test_bootstrap_is_seeded_and_brackets_the_estimate(self):
        pairs = [(False, True)] * 8 + [(True, False)] * 3 + [(True, True)] * 10 + [(False, False)] * 20
        first = bootstrap_difference(pairs, seed='x', resamples=2000)
        self.assertEqual(first, bootstrap_difference(pairs, seed='x', resamples=2000))
        self.assertLess(first[0], 5 / 41)
        self.assertGreater(first[1], 5 / 41)


class CompareTests(unittest.TestCase):
    def test_denominator_never_shrinks_and_outcomes_are_classified(self):
        cohort = ['a1', 'a2', 'a3', 'a4', 'b1']
        repos = {t: 'r/' + t[0] for t in cohort}
        base = {'a1': row('a1', True), 'a2': row('a2', False), 'a3': row('a3', False, error='timeout'),
                'b1': row('b1', False, agent_patch_size=0)}
        cand = {'a1': row('a1', True), 'a2': row('a2', True), 'a3': row('a3', False),
                'a4': row('a4', True)}
        result = compare(cohort, base, cand, repos=repos)
        self.assertEqual(result['tasks'], 5)
        self.assertEqual(result['base']['resolved'], 1)
        self.assertEqual(result['candidate']['resolved'], 3)
        self.assertEqual(result['base']['outcomes'], {'resolved': 1, 'patch_failed_verification': 1,
                                                      'error': 1, 'missing_result': 1, 'no_patch': 1})
        self.assertEqual(result['candidate']['outcomes']['missing_result'], 1)
        self.assertEqual(result['paired'], {**result['paired'], 'candidate_only': 2, 'base_only': 0,
                                            'both': 1, 'neither': 2, 'difference': 0.4})
        self.assertEqual(result['paired']['exact_mcnemar_p'], 0.5)
        self.assertEqual(result['by_repository']['r/a'], {'tasks': 4, 'base_resolved': 1, 'candidate_resolved': 3})
        self.assertEqual(result['base']['results_present'], 4)

    def test_results_outside_the_cohort_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'outside the frozen cohort'):
            compare(['a1'], {'a1': row('a1', True)}, {'zz': row('zz', True)}, repos={'a1': 'r/a'})
        with self.assertRaises(ValueError):
            compare([], {}, {}, repos={})

    def test_jsonl_loading_is_strict(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'task_results.jsonl'
            path.write_text(json.dumps(row('a1', True)) + '\n\n' + json.dumps(row('a2', False)) + '\n')
            self.assertEqual(sorted(load_task_results(path)), ['a1', 'a2'])
            path.write_text(json.dumps(row('a1', True)) + '\n' + json.dumps(row('a1', False)) + '\n')
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                load_task_results(path)
            path.write_text(json.dumps(row('a1', 'yes')) + '\n')
            with self.assertRaisesRegex(ValueError, 'Non-boolean'):
                load_task_results(path)


if __name__ == '__main__':
    unittest.main()
