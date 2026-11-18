import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.qualify_verifier import census, compare_census

ROOT = Path(__file__).resolve().parents[1]


def receipt(tasks, gold, empty):
    return {'tasks': tasks, 'gold': {'resolved': gold}, 'empty': {'resolved': empty},
            'gold_resolved': f'{len(gold)}/{len(tasks)}', 'empty_resolved': f'{len(empty)}/{len(tasks)}'}


TASKS = ['requests_7309', 'requests_7315', 'rich_3130', 'rich_3278', 'fastapi_14246']
CONTROL = receipt(TASKS, ['requests_7309', 'requests_7315', 'rich_3278'], ['requests_7309', 'requests_7315'])
FIXED = receipt(TASKS, ['requests_7315', 'rich_3130', 'fastapi_14246'], [])


class CensusTests(unittest.TestCase):
    def test_a_task_is_gradable_only_if_gold_resolves_and_empty_does_not(self):
        self.assertEqual(census(CONTROL), {'rich_3278'})
        self.assertEqual(census(FIXED), {'requests_7315', 'rich_3130', 'fastapi_14246'})

    def test_comparison_reports_gains_and_regressions_per_repository(self):
        out = compare_census(FIXED, CONTROL)
        self.assertEqual(out['valid'], {'fixed': 3, 'control': 1})
        self.assertEqual(out['newly_valid'], ['fastapi_14246', 'requests_7315', 'rich_3130'])
        self.assertEqual(out['regressed'], ['rich_3278'])
        self.assertEqual(out['valid_by_repo']['fixed'], {'fastapi': 1, 'requests': 1, 'rich': 1})
        self.assertEqual(out['empty_resolved']['control'], ['requests_7309', 'requests_7315'])

    def test_receipts_over_different_tasks_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'different tasks'):
            compare_census(receipt(TASKS[:2], [], []), CONTROL)

    def test_compare_mode_needs_no_harness(self):
        with tempfile.TemporaryDirectory() as d:
            paths = []
            for name, value in (('fixed', FIXED), ('control', CONTROL)):
                paths.append(Path(d) / f'{name}.json')
                paths[-1].write_text(json.dumps(value))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'qualify_verifier.py'), '--compare',
                                     *map(str, paths)], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)['regressed'], ['rich_3278'])


if __name__ == '__main__':
    unittest.main()
