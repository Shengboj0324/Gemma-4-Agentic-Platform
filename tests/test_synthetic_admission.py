import copy
import unittest

from zenithsync.replay_history import native_replay_history
from zenithsync.synthetic_admission import validate_synthetic_projection, validate_synthetic_task_binding


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

    def test_status_inspection_is_recorded_but_not_charged(self):
        self.tools.append({'function': {'name': 'get_status'}})
        result = {'status':'ok','tool_calls_used':1}
        self.events.insert(1, {'source_index':1,'kind':'synthetic','result':result,
            'native_calls':[{'name':'get_status','arguments':{},'result':result}]})
        self.events[-1]['source_index'] = 2
        messages = native_replay_history(self.events,system='system',problem='issue',
            allowed_tools={'run_command','get_status','submit_patch'})['messages'] + self.messages[-1:]
        self.assertEqual(validate_synthetic_projection(self.events,messages,self.tools,1),1)
        with self.assertRaisesRegex(ValueError,'call count mismatch'):
            validate_synthetic_projection(self.events,messages,self.tools,2)

    def test_failed_submission_rejected_even_when_history_agrees(self):
        self.events[-1]['result']['status'] = 'error'
        messages = native_replay_history(self.events, system='system', problem='issue',
                                        allowed_tools={'run_command', 'submit_patch'})['messages']
        with self.assertRaisesRegex(ValueError, 'Successful terminal'):
            validate_synthetic_projection(self.events, messages + self.messages[-1:], self.tools, 1)

    def test_post_submission_calls_cannot_hide_failed_or_stale_submission(self):
        for submission_status in ('ok', 'error'):
            for following_tool in ('run_command', 'get_status'):
                with self.subTest(submission=submission_status, following=following_tool):
                    events = copy.deepcopy(self.events)
                    events[-1]['result']['status'] = submission_status
                    result = {'status': 'ok', 'stdout': 'later observation'}
                    events.append({'source_index': 2, 'kind': 'synthetic', 'result': result,
                        'native_calls': [{'name': following_tool, 'arguments': {}, 'result': result}]})
                    tools = self.tools + [{'function': {'name': 'get_status'}}]
                    charged = 1 + (following_tool == 'run_command')
                    with self.assertRaisesRegex(ValueError, 'Native submission exchange required'):
                        validate_synthetic_projection(events, self.messages, tools, charged)



class SyntheticTaskBindingTests(unittest.TestCase):
    def setUp(self):
        capture = SyntheticProjectionTests()
        capture.setUp()
        self.inputs = dict(messages=capture.messages, events=capture.events, tools=capture.tools,
            task={'base_commit':'base', 'problem_statement':'issue'},
            snapshot={'base_commit':'base', 'snapshot_commit':'snapshot'}, image='image',
            patch_identity={'sha256':'patch'}, history_identity={'sha256':'history'},
            tools_identity={'sha256':'tools'})
        self.inputs['receipt'] = dict(kind='synthetic_native_trajectory', author='assistant',
            reference_informed=True, source_observations_reused=False, new_model_evaluated=False,
            training_approved=False, status='captured_not_graded', cleanup={'removed':True},
            snapshot=copy.deepcopy(self.inputs['snapshot']), image='image', tool_calls=1,
            patch={'sha256':'patch'}, history={'sha256':'history'}, tools={'sha256':'tools'})

    def test_bound_capture_accepts_without_mutation(self):
        before = copy.deepcopy(self.inputs)
        self.assertEqual(validate_synthetic_task_binding(**self.inputs), 1)
        self.assertEqual(self.inputs, before)

    def test_provenance_and_cleanup_cannot_be_relabelled(self):
        changes = {'kind':'teacher', 'author':'teacher', 'reference_informed':False,
            'source_observations_reused':True, 'new_model_evaluated':True,
            'training_approved':True, 'status':'replayed_not_graded','cleanup':{'removed':False}}
        for key, value in changes.items():
            data = copy.deepcopy(self.inputs)
            data['receipt'][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError,'explicitly synthetic'):
                validate_synthetic_task_binding(**data)

    def test_changed_artifact_or_snapshot_rejected(self):
        for key in ('patch', 'history', 'tools', 'snapshot', 'image'):
            data = copy.deepcopy(self.inputs)
            data['receipt'][key] = 'changed'
            with self.subTest(key=key), self.assertRaisesRegex(ValueError,'artifact binding'):
                validate_synthetic_task_binding(**data)
        self.inputs['task']['base_commit'] = 'other'
        with self.assertRaisesRegex(ValueError,'artifact binding'):
            validate_synthetic_task_binding(**self.inputs)

    def test_wrong_issue_and_fabricated_transcript_rejected(self):
        data = copy.deepcopy(self.inputs)
        data['task']['problem_statement'] = 'another issue'
        with self.assertRaisesRegex(ValueError,'issue differs'):
            validate_synthetic_task_binding(**data)
        self.inputs['messages'][3]['content'] = 'invented observation'
        with self.assertRaisesRegex(ValueError,'differs from captured'):
            validate_synthetic_task_binding(**self.inputs)


if __name__ == '__main__':
    unittest.main()
