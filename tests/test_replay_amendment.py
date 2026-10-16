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


class SourceEditAmendmentTests(unittest.TestCase):
    def fixture(self):
        actions = [
            {'index': 4, 'kind': 'str_replace', 'path': 'module.py',
             'arguments': {'old_str': 'if sql is None:',
                           'new_str': 'if not isinstance(sql, str):'}},
            {'index': 8, 'kind': 'finish'},
        ]
        derived = copy.deepcopy(actions)
        derived[0]['arguments']['new_str'] = 'if sql is None:  # preserve other inputs'
        plan = {'schema_version': 2, 'author': 'assistant',
                'reason': 'Preserve non-None behavior in an attributed source derivative',
                'source_actions': identity(actions), 'derived_actions': identity(derived),
                'amendments': [{'action_index': 0, 'field': 'new_str',
                    'before': actions[0]['arguments']['new_str'],
                    'after': derived[0]['arguments']['new_str'],
                    'reason': 'Replace only the existing edit replacement text'}]}
        result = {'status': 'ok', 'occurrences': 1}
        events = [
            {'source_index': 4, 'kind': 'str_replace', 'result': result,
             'native_calls': [{'name': 'edit_file', 'arguments': {
                 'filepath': 'module.py', 'old_string': 'if sql is None:',
                 'new_string': derived[0]['arguments']['new_str']}, 'result': result}]},
            {'source_index': 8, 'kind': 'finish', 'result': {'status': 'ok'},
             'native_calls': [{'name': 'submit_patch', 'arguments': {},
                              'result': {'status': 'ok'}}]},
        ]
        return actions, plan, events

    def project(self, actions, plan, events):
        return amended_replay_history(events, actions=actions, plan=plan,
            system='Repair the issue.', problem='Handle None.',
            allowed_tools={'edit_file', 'submit_patch'})

    def test_source_derivative_has_explicit_authorship_and_preserves_preimage(self):
        actions, plan, events = self.fixture()
        original = copy.deepcopy(actions)
        derivative = amend_actions(actions, plan)
        self.assertEqual(actions, original)
        self.assertEqual(derivative['actions'][0]['path'], 'module.py')
        self.assertEqual(derivative['actions'][0]['arguments']['old_str'], 'if sql is None:')
        self.assertEqual(derivative['attribution'][0]['field'], 'new_str')
        projected = self.project(actions, plan, events)
        self.assertEqual(projected['mapping'][0]['author'], 'assistant')
        self.assertEqual(projected['mapping'][0]['amendment']['kind'], 'str_replace')
        self.assertFalse(projected['training_approved'])
        self.assertTrue(derivative['fresh_replay_required'])

    def test_old_or_invalid_versions_cannot_enable_source_edits(self):
        for version in (1, True, 2.0, 3, '2'):
            actions, plan, _ = self.fixture()
            plan['schema_version'] = version
            with self.subTest(version=version), self.assertRaises(ValueError):
                amend_actions(actions, plan)

    def test_source_preimage_path_and_action_kind_cannot_be_amended(self):
        for field in ('old_str', 'path', 'kind', 'index'):
            actions, plan, _ = self.fixture()
            plan['amendments'][0]['field'] = field
            with self.subTest(field=field), self.assertRaises(ValueError):
                amend_actions(actions, plan)

    def test_rehashed_destination_cannot_sneak_in_unlisted_source_changes(self):
        for field in ('old_str', 'path'):
            actions, plan, _ = self.fixture()
            derived = amend_actions(actions, plan)['actions']
            if field == 'path':
                derived[0]['path'] = 'other.py'
            else:
                derived[0]['arguments']['old_str'] = 'different preimage'
            plan['derived_actions'] = identity(derived)
            with self.subTest(field=field), self.assertRaises(ValueError):
                amend_actions(actions, plan)

    def test_projection_rejects_old_replacement_changed_preimage_path_or_result(self):
        for field in ('new_string', 'old_string', 'filepath', 'result'):
            actions, plan, events = self.fixture()
            call = events[0]['native_calls'][0]
            if field == 'result':
                call['result'] = {'status': 'error'}
            else:
                call['arguments'][field] = 'different'
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.project(actions, plan, events)

    def test_invalid_preimage_rejected_even_when_source_hash_matches(self):
        for value in ('', None, 123, 'x\0y'):
            actions, plan, _ = self.fixture()
            actions[0]['arguments']['old_str'] = value
            plan['source_actions'] = identity(actions)
            with self.subTest(value=value), self.assertRaises(ValueError):
                amend_actions(actions, plan)
