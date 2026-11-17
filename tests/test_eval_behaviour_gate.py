import json
from pathlib import Path
import tempfile
import unittest

from scripts.eval_behaviour_gate import evaluate, step_rates


def step(text, cmd):
    return {'source': 'agent', 'message': text,
            'tool_calls': [{'function_name': 'run_command', 'arguments': {'command': cmd}}]}


class BehaviourGateTests(unittest.TestCase):
    def test_rates(self):
        trace = {'steps': [{'source': 'user', 'message': 'task'}, step('think', 'a'), step('', 'b'), step('', 'b'),
                           {'source': 'agent', 'message': 'done'}]}
        r = step_rates([trace])
        self.assertEqual(r['tool_steps'], 3)
        self.assertAlmostEqual(r['no_thinking'], 2 / 3)
        self.assertAlmostEqual(r['repeat_call'], 1 / 3)
        # a repeat is only within one trace
        self.assertEqual(step_rates([{'steps': [step('x', 'a')]}, {'steps': [step('x', 'a')]}])['repeat_call'], 0.0)

    def write(self, d, rows, traces):
        (d / 'traces').mkdir(parents=True)
        (d / 'task_results.jsonl').write_text(''.join(json.dumps({'instance_id': r}) + '\n' for r in rows))
        for name, t in traces.items():
            (d / 'traces' / f'trace_{name}.json').write_text(json.dumps(t))

    def test_verdicts(self):
        healthy = {'steps': [step('think', 'a'), step('think', 'b')]}
        collapsed = {'steps': [step('', 'a'), step('', 'a'), step('', 'a')]}
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / 'c'
            self.write(d, ['x', 'y'], {'x': healthy, 'y': collapsed})
            self.assertEqual(evaluate(d, min_tasks=3, max_no_thinking=0.05, max_repeat=0.05)['verdict'], 'pending')
            self.assertEqual(evaluate(d, min_tasks=2, max_no_thinking=0.05, max_repeat=0.05)['verdict'], 'fail')
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / 'c'
            self.write(d, ['x', 'z'], {'x': healthy, 'z': healthy})
            self.assertEqual(evaluate(d, min_tasks=2, max_no_thinking=0.05, max_repeat=0.05)['verdict'], 'pass')
        self.assertEqual(evaluate(Path('/nonexistent'), min_tasks=1, max_no_thinking=0.05, max_repeat=0.05)['verdict'],
                         'pending')


if __name__ == '__main__':
    unittest.main()
