import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.select_candidate import paired_durations, rank, sign_test, touches_tests

ROOT = Path(__file__).resolve().parents[1]


def write(results, name, outcomes):
    d = results / name
    (d / 'patches').mkdir(parents=True)
    rows = []
    for tid, (resolved, patch, error, seconds) in outcomes.items():
        rows.append({'instance_id': tid, 'repo': 'o/' + tid[0], 'resolved': resolved,
                     'agent_patch_size': len(patch), 'error': error, 'duration_seconds': seconds})
        if patch:
            (d / 'patches' / f'{tid}.patch').write_text(patch)
    (d / 'task_results.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))


class SelectCandidateTests(unittest.TestCase):
    def test_test_file_detection(self):
        patch = '+++ b/src/app.py\n+++ b/tests/test_app.py\n+++ b/pkg/conftest.py\n'
        self.assertEqual(touches_tests(patch), ['tests/test_app.py', 'pkg/conftest.py'])

    def test_sign_test_and_paired_durations(self):
        self.assertEqual(sign_test(0, 0), 1.0)
        self.assertAlmostEqual(sign_test(23, 14), 0.1877, places=3)
        ref = {'a': {'duration_seconds': 100}, 'b': {'duration_seconds': 600}, 'c': {'duration_seconds': 300}}
        rows = {'a': {'duration_seconds': 50}, 'b': {'duration_seconds': 600}, 'c': {'duration_seconds': 302}}
        self.assertEqual(paired_durations(rows, ref), {'median_difference_s': 0, 'faster': 1, 'slower': 0,
                                                       'sign_test_p': 1.0})

    def test_rank_order_and_winner_rule(self):
        summaries = {'a': {'resolved': 5, 'budget_exhausted_no_patch': 2, 'median_duration_s': 100},
                     'b': {'resolved': 5, 'budget_exhausted_no_patch': 1, 'median_duration_s': 300},
                     'c': {'resolved': 6, 'budget_exhausted_no_patch': 9, 'median_duration_s': 900}}
        self.assertEqual(rank(summaries), ['c', 'b', 'a'])

    def test_end_to_end_reference_kept_when_nothing_beats_it(self):
        with tempfile.TemporaryDirectory() as d:
            results = Path(d) / 'results'
            p = 'diff --git a/x b/x\n+++ b/src/x.py\n'
            write(results, 'base', {'a1': (True, p, None, 100), 'a2': (False, p, None, 600), 'b1': (True, p, None, 200)})
            write(results, 'worse', {'a1': (True, p, None, 90), 'a2': (False, '', 'Agent exceeded session timeout (10 min)', 600),
                                     'b1': (False, p, None, 300)})
            out = Path(d) / 'report.json'
            run = subprocess.run([sys.executable, str(ROOT / 'scripts/select_candidate.py'), '--results-root', str(results),
                                  '--reference', 'base', '--cap-minutes', '8', '--output', str(out)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads(out.read_text())
            self.assertEqual(report['winner'], 'base')
            worse = report['candidates']['worse']
            self.assertEqual({k: v for k, v in worse['vs_reference'].items() if k != 'paired_durations'},
                             {'candidate_only': 0, 'reference_only': 1, 'exact_mcnemar_p': 1.0,
                              'worse_in_repositories': ['o/b']})
            self.assertEqual(worse['vs_reference']['paired_durations']['slower'], 1)
            self.assertEqual(worse['budget_exhausted_no_patch'], 1)
            # mean of min(d, 480) + 45 over (90, 600, 300) = (135 + 525 + 345) / 3 = 335 s, x120 tasks
            self.assertAlmostEqual(worse['projected_sequential_hours'], 335 * 120 / 3600)


if __name__ == '__main__':
    unittest.main()
