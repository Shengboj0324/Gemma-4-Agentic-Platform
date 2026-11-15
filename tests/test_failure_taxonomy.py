import json
from pathlib import Path
import tempfile
import unittest

from scripts.failure_taxonomy import analyse, classify


class ClassifyTests(unittest.TestCase):
    def test_commands_are_classified_in_order(self):
        cases = {'pip install -r requirements-tests.txt': 'pip', 'python -m pytest tests/test_x.py': 'test',
                 'grep -rn "def get" fastapi': 'search', 'cat fastapi/routing.py | grep x': 'search',
                 'sed -n 1,40p a.py': 'inspect', 'python3 -c "import fastapi"': 'python', 'make': 'other_command'}
        for command, kind in cases.items():
            self.assertEqual(classify('run_command', {'command': command}), kind, command)
        self.assertEqual(classify('edit_file', {}), 'edit')
        self.assertEqual(classify('submit_patch', {}), 'submit')


class AnalyseTests(unittest.TestCase):
    def test_runs_join_traces_and_outcomes(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'traces').mkdir()
            rows = [{'instance_id': 'a', 'resolved': True, 'agent_patch_size': 10, 'error': None, 'duration_seconds': 100},
                    {'instance_id': 'b', 'resolved': False, 'agent_patch_size': 0,
                     'error': 'Agent exceeded session timeout (10 min)', 'duration_seconds': 600}]
            (d / 'task_results.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
            steps = [{'tool_calls': [{'function_name': 'read_file', 'arguments': {'filepath': 'x'}}],
                      'metrics': {'completion_tokens': 50}},
                     {'tool_calls': [{'function_name': 'edit_file', 'arguments': {}},
                                     {'function_name': 'run_command', 'arguments': '{"command": "pytest -q"}'}],
                      'metrics': {'completion_tokens': 70}},
                     {'tool_calls': [{'function_name': 'submit_patch', 'arguments': {}}]}]
            (d / 'traces' / 'trace_a.json').write_text(json.dumps({'steps': steps}))
            runs, summary = analyse(d)
            a = runs[0]
            self.assertEqual((a['calls'], a['first_edit_call'], a['first_test_call'], a['submitted'],
                              a['completion_tokens']), (4, 2, 3, True, 120))
            self.assertFalse(runs[1]['trace_present'])
            self.assertEqual(summary['resolved']['runs'], 1)
            self.assertEqual(summary['budget_exhausted_no_patch']['runs'], 1)


if __name__ == '__main__':
    unittest.main()
