import copy
import hashlib
import unittest

from zenithsync.artifacts import canonical_json
from zenithsync.mini_replay_amendment import (
    mini_command_actions, mini_commands, verify_mini_amendment_binding,
)
from zenithsync.replay_history import mini_replay_history


def identity(value):
    data = canonical_json(value)
    return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}


class MiniAmendmentTests(unittest.TestCase):
    def setUp(self):
        self.source = [{'role': 'user', 'content': 'issue'}]
        for ordinal, command in enumerate(('python probe.py',
                'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && cat patch.txt')):
            self.source.append({'role': 'assistant', 'content': '', 'tool_calls': [{
                'id': str(ordinal), 'type': 'function', 'function': {
                    'name': 'bash', 'arguments': {'command': command}}}]})
            if ordinal == 0:
                self.source.append({'role': 'tool', 'tool_call_id': '0',
                                    'content': 'obsolete source observation'})
        actions = mini_command_actions(self.source)
        derived = copy.deepcopy(actions)
        derived[0]['command'] = 'python corrected_probe.py'
        self.plan = {'schema_version': 1, 'author': 'assistant', 'reason': 'Propagate failure',
            'source_actions': identity(actions), 'derived_actions': identity(derived),
            'amendments': [{'action_index': 0, 'field': 'command',
                'before': actions[0]['command'], 'after': derived[0]['command'],
                'reason': 'Use the reviewed corrected diagnostic'}]}
        self.events = [
            {'source_index': 1, 'adapter_authored': True, 'name': 'run_command',
             'arguments': {'command': derived[0]['command']}, 'result': {
                 'status': 'error', 'error_type': 'CommandError',
                 'details': {'exit_code': 1, 'stdout': 'fresh failure'}}},
            {'source_index': None, 'adapter_authored': True, 'name': 'run_command',
             'arguments': {'command': 'cleanup'}, 'result': {'status': 'ok'}},
            {'source_index': None, 'adapter_authored': True, 'name': 'submit_patch',
             'arguments': {}, 'result': {'status': 'ok'}}]

    def project(self, events, plan):
        return mini_replay_history(events, source_messages=self.source,
            system='native', problem='issue', allowed_tools={'run_command', 'submit_patch'},
            amendment_plan=plan)

    def test_fresh_failure_preserved_and_amendment_attributed(self):
        original = copy.deepcopy(self.source)
        result = self.project(self.events, self.plan)
        self.assertEqual(self.source, original)
        self.assertIn('fresh failure', str(result['messages']))
        self.assertNotIn('obsolete source observation', str(result['messages']))
        self.assertEqual(result['mapping'][0]['amendment']['source_index'], 1)
        self.assertEqual(result['mapping'][0]['author'], 'assistant')
        self.assertFalse(result['training_approved'])

    def test_source_success_claim_cannot_replace_fresh_timeout(self):
        self.source[1]['content'] = 'All tests passed despite the timeout.'
        self.source[1]['reasoning_content'] = 'Unverified teacher rationale.'
        self.source[-1]['content'] = 'The complete suite is proven correct.'
        events = copy.deepcopy(self.events)
        events[0]['result'] = {
            'status': 'error', 'error_type': 'TimeoutExceeded',
            'error_message': 'Command timed out after 30 seconds',
        }
        result = self.project(events, self.plan)
        assistants = [message for message in result['messages']
                      if message['role'] == 'assistant']
        self.assertTrue(assistants)
        for message in assistants:
            self.assertEqual(message['content'], '')
            self.assertNotIn('reasoning', message)
            self.assertNotIn('reasoning_content', message)
        observed = result['messages'][3]
        self.assertEqual(observed['role'], 'tool')
        self.assertEqual(observed['content'],
                         canonical_json(events[0]['result']).decode().rstrip('\n'))
        serialized = canonical_json(result['messages']).decode()
        for claim in ('All tests passed', 'Unverified teacher rationale',
                      'complete suite is proven', 'obsolete source observation'):
            self.assertNotIn(claim, serialized)

    def test_wrong_command_authorship_index_and_missing_plan_reject(self):
        for mutation in ('command', 'authorship', 'index', 'plan'):
            events = copy.deepcopy(self.events)
            plan = copy.deepcopy(self.plan)
            if mutation == 'command':
                events[0]['arguments']['command'] = 'python probe.py'
            elif mutation == 'authorship':
                events[0]['adapter_authored'] = False
            elif mutation == 'index':
                events[0]['source_index'] = 2
            else:
                plan = None
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.project(events, plan)

    def test_tampered_plan_and_terminal_change_reject(self):
        for mutation in ('source_hash', 'derived_hash', 'before', 'terminal'):
            plan = copy.deepcopy(self.plan)
            if mutation in ('source_hash', 'derived_hash'):
                key = 'source_actions' if mutation == 'source_hash' else 'derived_actions'
                plan[key]['sha256'] = '0' * 64
            elif mutation == 'before':
                plan['amendments'][0]['before'] = 'unobserved command'
            else:
                actions = mini_command_actions(self.source)
                derived = copy.deepcopy(actions)
                derived[-1]['command'] = 'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && cat /testbed/patch.txt'
                plan['derived_actions'] = identity(derived)
                plan['amendments'] = [{'action_index': len(actions) - 1, 'field': 'command',
                    'before': actions[-1]['command'], 'after': derived[-1]['command'],
                    'reason': 'Attempt terminal change'}]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                mini_commands(self.source, plan)

    def test_receipt_provenance_required_in_every_layer(self):
        document = {'amendment': self.plan}
        self.assertEqual(verify_mini_amendment_binding(document, document, document), self.plan)
        for profile, replay, history in (({}, document, {}), (document, {}, document),
                                         (document, document, {}), ({}, {}, document),
                                         ({'amendment': None}, {'amendment': None}, {})):
            with self.subTest(profile=profile, replay=replay), self.assertRaises(ValueError):
                verify_mini_amendment_binding(profile, replay, history)
        self.assertIsNone(verify_mini_amendment_binding({}, {}, {}))


if __name__ == '__main__':
    unittest.main()
