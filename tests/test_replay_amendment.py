import copy
import hashlib
import unittest

from zenithsync.artifacts import canonical_json
from zenithsync.replay_amendment import amend_actions, amended_replay_history


def identity(value):
    data = canonical_json(value)
    return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}


class ActionAmendmentTests(unittest.TestCase):
    def event_fixture(self):
        actions, plan = self.fixture()
        derived = amend_actions(actions, plan)['actions']
        events = []
        for action in derived:
            if action['kind'] == 'create':
                name, args = 'write_file', {'filepath': action['path'],
                    'content': action['arguments']['file_text']}
            elif action['kind'] == 'shell':
                name, args = 'run_command', {'command': action['command']}
            else:
                name, args = 'submit_patch', {}
            result = {'status': 'ok', 'exit_code': 0}
            events.append({'source_index': action['index'], 'kind': action['kind'],
                           'result': result, 'native_calls': [{'name': name,
                           'arguments': args, 'result': result}]})
        return actions, plan, events

    def project(self, actions, plan, events, completion=None):
        return amended_replay_history(events, actions=actions, plan=plan,
            system='Repair the issue.', problem='Reported defect.',
            allowed_tools={'write_file', 'run_command', 'submit_patch'},
            completion_plan=completion)

    def test_projection_preserves_observations_and_marks_changed_authorship(self):
        actions, plan, events = self.event_fixture()
        original = copy.deepcopy(events)
        result = self.project(actions, plan, events)
        self.assertEqual(events, original)
        self.assertEqual(result['mapping'][0]['author'], 'assistant')
        self.assertEqual(result['mapping'][0]['amendment']['action_index'], 0)
        self.assertNotIn('amendment', result['mapping'][1])
        self.assertIn(plan['amendments'][0]['after'], str(result['messages']))
        self.assertFalse(result['training_approved'])

    def test_projection_rejects_original_call_missing_event_and_changed_path(self):
        for variant in ('original_call', 'missing_event', 'changed_path', 'wrong_order'):
            actions, plan, events = self.event_fixture()
            if variant == 'original_call':
                events[0]['native_calls'][0]['arguments']['content'] = plan['amendments'][0]['before']
            elif variant == 'missing_event':
                del events[1]
            elif variant == 'changed_path':
                events[0]['native_calls'][0]['arguments']['filepath'] = 'other.py'
            else:
                events[0], events[1] = events[1], events[0]
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                self.project(actions, plan, events)

    def test_completion_requires_derived_binding_and_keeps_separate_authorship(self):
        actions, plan, events = self.event_fixture()
        result = {'status': 'ok', 'exit_code': 0}
        events.insert(-1, {'source_index': None, 'adapter_authored': True,
            'kind': 'completion', 'result': result, 'native_calls': [{
                'name': 'run_command', 'arguments': {'command': 'verify'}, 'result': result}]})
        completion = {'schema_version': 1, 'author': 'assistant', 'reason': 'Verify',
            'source_actions': plan['derived_actions'], 'final_patch': identity('patch'),
            'commands': [{'command': 'verify', 'expected_exit_code': 0}]}
        projected = self.project(actions, plan, events, completion)
        self.assertTrue(projected['mapping'][-2]['adapter_authored'])
        self.assertIsNone(projected['mapping'][-2]['source_index'])
        self.assertNotIn('amendment', projected['mapping'][-2])
        completion['source_actions'] = plan['source_actions']
        with self.assertRaises(ValueError):
            self.project(actions, plan, events, completion)

    def fixture(self):
        actions = [
            {'index': 3, 'kind': 'create', 'path': 'diagnostic.py',
             'arguments': {'file_text': 'print("all pass")', 'command': 'create'}},
            {'index': 7, 'kind': 'shell', 'command': 'python diagnostic.py'},
            {'index': 9, 'kind': 'finish'},
        ]
        derived = copy.deepcopy(actions)
        derived[0]['arguments']['file_text'] = 'print("observed", 1 == 1)'
        plan = {'schema_version': 1, 'author': 'assistant', 'reason': 'Scope diagnostic',
                'source_actions': identity(actions), 'derived_actions': identity(derived),
                'amendments': [{'action_index': 0, 'field': 'file_text',
                                'before': actions[0]['arguments']['file_text'],
                                'after': derived[0]['arguments']['file_text'],
                                'reason': 'Compute the reported comparison'}]}
        return actions, plan

    def test_derivative_preserves_order_paths_and_source_without_aliasing(self):
        actions, plan = self.fixture()
        before = copy.deepcopy(actions)
        result = amend_actions(actions, plan)
        self.assertEqual(actions, before)
        self.assertEqual([a['index'] for a in result['actions']], [3, 7, 9])
        self.assertEqual(result['actions'][0]['path'], 'diagnostic.py')
        self.assertEqual(result['attribution'][0]['source_index'], 3)
        self.assertTrue(result['fresh_replay_required'])
        self.assertFalse(result['training_approved'])
        result['actions'][0]['arguments']['command'] = 'changed'
        self.assertEqual(actions, before)

    def test_changed_source_destination_or_preimage_rejected(self):
        for which in ('source', 'destination', 'preimage'):
            actions, plan = self.fixture()
            if which == 'source':
                actions[1]['command'] = 'different command'
            elif which == 'destination':
                plan['derived_actions']['sha256'] = '0' * 64
            else:
                plan['amendments'][0]['before'] = 'wrong text'
            with self.subTest(which=which), self.assertRaises(ValueError):
                amend_actions(actions, plan)

    def test_duplicate_boolean_out_of_range_and_unapproved_fields_rejected(self):
        for index in (True, -1, 3):
            actions, plan = self.fixture()
            plan['amendments'][0]['action_index'] = index
            with self.subTest(index=index), self.assertRaises(ValueError):
                amend_actions(actions, plan)
        for field in ('path', 'index', 'kind'):
            actions, plan = self.fixture()
            plan['amendments'][0]['field'] = field
            with self.subTest(field=field), self.assertRaises(ValueError):
                amend_actions(actions, plan)
        actions, plan = self.fixture()
        plan['amendments'].append(copy.deepcopy(plan['amendments'][0]))
        with self.assertRaises(ValueError):
            amend_actions(actions, plan)

    def test_noop_unknown_plan_keys_and_invalid_identity_rejected(self):
        for variant in ('noop', 'extra', 'bool_size', 'teacher'):
            actions, plan = self.fixture()
            if variant == 'noop':
                plan['amendments'][0]['after'] = plan['amendments'][0]['before']
            elif variant == 'extra':
                plan['reuse_observations'] = True
            elif variant == 'bool_size':
                plan['source_actions']['size_bytes'] = True
            else:
                plan['author'] = 'teacher'
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                amend_actions(actions, plan)

    def test_shell_change_bound_to_whole_action_list(self):
        actions, plan = self.fixture()
        after = 'python -B diagnostic.py'
        derived = copy.deepcopy(actions)
        derived[1]['command'] = after
        plan['derived_actions'] = identity(derived)
        plan['amendments'] = [{'action_index': 1, 'field': 'command',
                               'before': actions[1]['command'], 'after': after,
                               'reason': 'Disable bytecode writes'}]
        self.assertEqual(amend_actions(actions, plan)['actions'], derived)
