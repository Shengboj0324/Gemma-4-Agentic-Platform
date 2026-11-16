import unittest

from scripts.trace_to_history import trace_history
from zenithsync.conversation import normalize_history

ALLOWED = {'run_command', 'read_file', 'submit_patch'}


def trace(*agent_steps):
    return {'steps': [{'step_id': 1, 'source': 'system', 'message': 'SYS'},
                      {'step_id': 2, 'source': 'user', 'message': 'TASK'}, *agent_steps]}


def agent(message, calls=None, observation=None, event='thinking'):
    step = {'source': 'agent', 'message': message, 'extra': {'event_type': event}}
    if calls is not None:
        step['tool_calls'] = calls
        step['observation'] = observation
    return step


def call(cid, name, args):
    return {'tool_call_id': cid, 'function_name': name, 'arguments': args}


class TraceHistoryTests(unittest.TestCase):
    def test_round_trip_is_a_valid_native_history(self):
        messages = trace_history(trace(
            agent('look', [call('c1', 'read_file', {'filepath': 'a.py'})], {'content': '{"status": "ok"}'}),
            agent('', [call('c2', 'submit_patch', {})], {'content': '{"status": "ok"}'}),
            agent('done', event='final')), ALLOWED)
        self.assertEqual([m['role'] for m in messages], ['system', 'user', 'assistant', 'tool', 'assistant', 'tool', 'assistant'])
        self.assertEqual(messages[2]['reasoning'], 'look')
        self.assertNotIn('reasoning', messages[4])
        self.assertEqual(messages[2]['tool_calls'][0]['function']['arguments'], '{"filepath": "a.py"}')
        self.assertEqual(messages[-1], {'role': 'assistant', 'content': 'done'})
        normalize_history(messages, allowed_tools=ALLOWED)

    def test_refusals(self):
        with self.assertRaises(ValueError):
            trace_history(trace(agent('x', [call('c1', 'read_file', {}), call('c2', 'read_file', {})],
                                      {'content': 'one result only'})), ALLOWED)
        with self.assertRaises(ValueError):
            trace_history(trace(agent('x', [call('c1', 'write_file', {})], {'content': 'r'})), ALLOWED)
        with self.assertRaises(ValueError):
            trace_history(trace(agent('x', [call('c1', 'read_file', {})], {'content': 'r'}),
                                agent('y', [call('c1', 'read_file', {})], {'content': 'r'})), ALLOWED)

    def test_trailing_reasoning_fragment_is_dropped(self):
        messages = trace_history(trace(
            agent('a', [call('c1', 'run_command', {'command': 'ls'})], {'content': 'out'}),
            agent('thinking only')), ALLOWED)
        self.assertEqual(messages[-1]['role'], 'tool')


if __name__ == '__main__':
    unittest.main()
