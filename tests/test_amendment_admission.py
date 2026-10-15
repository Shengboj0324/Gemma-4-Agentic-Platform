"""Admission reconstructs amended actions, even after outer receipts are rebound."""
import copy
from pathlib import Path
import unittest

from tests import test_completion_admission as fixtures
from zenithsync.artifacts import file_record
from zenithsync.replay_amendment import amended_replay_history


class AmendmentAdmissionTests(fixtures.CompletionAdmissionTests):
    def setUp(self):
        super().setUp()
        original = [{'index': 0, 'kind': 'shell', 'command': 'echo all-pass'},
                    {'index': 1, 'kind': 'finish'}]
        derived = copy.deepcopy(original)
        derived[0]['command'] = 'python check.py'
        self.write('attempt/original-actions.json', original)
        self.write('attempt/actions.json', derived)
        amendment = {
            'schema_version': 1, 'author': 'assistant', 'reason': 'Replace static claim',
            'source_actions': self.record('attempt/original-actions.json'),
            'derived_actions': self.record('attempt/actions.json'),
            'amendments': [{'action_index': 0, 'field': 'command',
                           'before': original[0]['command'], 'after': derived[0]['command'],
                           'reason': 'Execute a check'}],
        }
        self.plan['source_actions'] = amendment['derived_actions']
        event = self.events[0]
        event['kind'] = 'shell'
        event['native_calls'] = [{'name': 'run_command',
                                 'arguments': {'command': derived[0]['command']},
                                 'result': event['result']}]
        self.write('attempt/events.json', self.events)
        replay = self.read('attempt/receipt.json')
        replay.update(amendment_plan=amendment, original_actions=amendment['source_actions'],
                      derived_actions=amendment['derived_actions'], completion_plan=self.plan,
                      amendment_module=file_record(Path(__file__).resolve().parents[1]
                                                   / 'zenithsync/replay_amendment.py'))
        self.write('attempt/receipt.json', replay)
        projected = amended_replay_history(self.events, actions=original, plan=amendment,
            completion_plan=self.plan, system='system', problem='issue', allowed_tools=self.tools)
        self.write('history/history.json', projected['messages'])
        self.write('history/mapping.json', projected['mapping'])
        receipt = self.read('history/receipt.json')
        receipt.update(amendment_plan=amendment, completion_plan=self.plan)
        self.write('history/receipt.json', receipt)
        self.rebind()

    def test_amendment_without_completion_is_supported(self):
        replay = self.read('attempt/receipt.json')
        del replay['completion_plan']
        del replay['completion_module']
        replay['tool_calls'] = 1
        events = [event for event in self.events if event['kind'] != 'completion']
        self.write('attempt/events.json', events)
        self.write('attempt/receipt.json', replay)
        projected = amended_replay_history(events,
            actions=self.read('attempt/original-actions.json'), plan=replay['amendment_plan'],
            system='system', problem='issue', allowed_tools=self.tools)
        self.write('history/history.json', projected['messages'])
        self.write('history/mapping.json', projected['mapping'])
        receipt = self.read('history/receipt.json')
        del receipt['completion_plan']
        receipt['exchanges'] = 2
        self.write('history/receipt.json', receipt)
        self.rebind()
        result = self.assess()
        self.assertTrue(result['mechanical_checks_passed'])
        self.assertEqual(result['assistant_completion_calls'], 0)
        self.assertFalse(result['training_approved'])

    def test_amendment_bindings_reject_rebound_outer_receipts(self):
        original = self.read('attempt/receipt.json')
        for field in ('amendment_module', 'original_actions', 'derived_actions', 'amendment_plan'):
            changed = copy.deepcopy(original)
            changed[field] = None
            self.write('attempt/receipt.json', changed)
            self.rebind()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.assess()
        self.write('attempt/receipt.json', original)
        self.rebind()
        self.assertTrue(self.assess()['mechanical_checks_passed'])

    def test_original_action_tampering_rejected(self):
        self.write('attempt/original-actions.json', [])
        with self.assertRaisesRegex(ValueError, 'Amendment provenance'):
            self.assess()

    def test_history_amendment_plan_cannot_disagree(self):
        receipt = self.read('history/receipt.json')
        receipt['amendment_plan']['reason'] = 'Changed attribution'
        self.write('history/receipt.json', receipt)
        with self.assertRaisesRegex(ValueError, 'Amendment provenance'):
            self.assess()

    def test_missing_amendment_plan_rejected(self):
        replay = self.read('attempt/receipt.json')
        del replay['amendment_plan']
        self.write('attempt/receipt.json', replay)
        self.rebind()
        with self.assertRaisesRegex(ValueError, 'bound amendment plan'):
            self.assess()

    def test_original_command_cannot_replace_amended_exchange(self):
        self.events[0]['native_calls'][0]['arguments']['command'] = 'echo all-pass'
        self.write('attempt/events.json', self.events)
        self.rebind()
        with self.assertRaises(ValueError):
            self.assess()


if __name__ == '__main__':
    unittest.main()
