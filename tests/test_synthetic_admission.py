import copy
import unittest

from zenithsync.replay_history import native_replay_history
from zenithsync.synthetic_admission import validate_synthetic_projection


class SyntheticProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tools = [{'function': {'name': name}} for name in ('run_command', 'submit_patch')]
        self.events = []
        for index, name in enumerate(('run_command', 'submit_patch')):
            result = {'status': 'ok', 'stdout': 'observed'}
            self.events.append({'source_index': index, 'kind': 'synthetic', 'result': result,
                                'native_calls': [{'name': name, 'arguments': {}, 'result': result}]})
        self.messages = native_replay_history(self.events, system='system', problem='issue',
                                              allowed_tools={'run_command', 'submit_patch'})['messages']
        self.messages.append({'role': 'assistant', 'content': 'Bounded conclusion.'})

    def test_exact_projection_accepts_and_does_not_mutate(self):
        before = copy.deepcopy((self.events, self.messages, self.tools))
        self.assertEqual(validate_synthetic_projection(self.events, self.messages, self.tools, 1), 1)
        self.assertEqual(before, (self.events, self.messages, self.tools))

    def test_fabricated_observation_rejected(self):
        self.messages[3]['content'] = 'invented success'
        with self.assertRaisesRegex(ValueError, 'differs from captured'):
            validate_synthetic_projection(self.events, self.messages, self.tools, 1)

    def test_boolean_call_count_rejected(self):
        with self.assertRaisesRegex(ValueError, 'call count'):
            validate_synthetic_projection(self.events, self.messages, self.tools, True)

    def test_missing_or_tool_bearing_final_prose_rejected(self):
        for final in ({'role': 'assistant', 'content': ''},
                      {'role': 'assistant', 'content': 'done', 'tool_calls': []}):
            with self.subTest(final=final), self.assertRaisesRegex(ValueError, 'final prose'):
                validate_synthetic_projection(self.events, self.messages[:-1] + [final], self.tools, 1)

    def test_teacher_kind_and_duplicate_schema_rejected(self):
        self.events[0]['kind'] = 'shell'
        with self.assertRaisesRegex(ValueError, 'synthetic events'):
            validate_synthetic_projection(self.events, self.messages, self.tools, 1)
        self.events[0]['kind'] = 'synthetic'
        with self.assertRaisesRegex(ValueError, 'Unique tool schemas'):
            validate_synthetic_projection(self.events, self.messages, self.tools + self.tools[:1], 1)

    def test_failed_submission_rejected_even_when_history_agrees(self):
        self.events[-1]['result']['status'] = 'error'
        messages = native_replay_history(self.events, system='system', problem='issue',
                                        allowed_tools={'run_command', 'submit_patch'})['messages']
        with self.assertRaisesRegex(ValueError, 'Successful terminal'):
            validate_synthetic_projection(self.events, messages + self.messages[-1:], self.tools, 1)


if __name__ == '__main__':
    unittest.main()
