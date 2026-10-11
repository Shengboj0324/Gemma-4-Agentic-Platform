"""Completion-aware admission retains authorship and rejects evidence tampering."""
import json
from pathlib import Path
import unittest
from tests import test_replay_admission as fixtures
from zenithsync.artifacts import file_record
from zenithsync.replay_completion import completed_replay_history

class CompletionAdmissionTests(fixtures.ReplayAdmissionTests):
    def setUp(self):
        super().setUp()
        self.write('attempt/actions.json',[{'index':0,'kind':'view'},{'index':1,'kind':'finish'}])
        self.plan={'schema_version':1,'author':'assistant','reason':'Independent fixture assertion',
                   'source_actions':self.record('attempt/actions.json'),
                   'final_patch':self.record('attempt/submitted.patch'),
                   'commands':[{'command':'python check.py','expected_exit_code':0}]}
        self.events=self.read('attempt/events.json')
        result={'status':'ok','exit_code':0,'stdout':'checked','stderr':''}
        self.events.insert(-1,{'source_index':None,'adapter_authored':True,'kind':'completion',
            'result':result,'native_calls':[{'name':'run_command','arguments':{'command':'python check.py'},'result':result}]})
        self.tools={'read_file','run_command','submit_patch'}
        self.write('attempt/events.json',self.events)
        replay=self.read('attempt/receipt.json')
        replay.update(completion_plan=self.plan,completion_module=file_record(
            Path(__file__).resolve().parents[1]/'zenithsync/replay_completion.py'),
            available_tools=sorted(self.tools),tool_calls=2)
        self.write('attempt/receipt.json',replay)
        projected=completed_replay_history(self.events,plan=self.plan,system='system',problem='issue',allowed_tools=self.tools)
        self.write('history/history.json',projected['messages'])
        self.write('history/mapping.json',projected['mapping'])
        self.write('history/tools.json',[{'function':{'name':name}} for name in sorted(self.tools)])
        history=self.read('history/receipt.json');history.update(completion_plan=self.plan,exchanges=3)
        self.write('history/receipt.json',history)
        self.rebind()

    def read(self,name):
        return json.loads((self.root/name).read_text())

    def rebind(self):
        history=self.read('history/receipt.json')
        history.update(attempt=self.record('attempt/receipt.json'),events=self.record('attempt/events.json'),
                       history=self.record('history/history.json'),tools=self.record('history/tools.json'))
        self.write('history/receipt.json',history)
        grade=self.read('grade/report.json');grade['attempt']=self.record('attempt/receipt.json')
        self.write('grade/report.json',grade)
        tokens=self.read('tokens/report.json');tokens.update(history=self.record('history/history.json'),tools=self.record('history/tools.json'))
        self.write('tokens/report.json',tokens)

    def assess(self,**kwargs):
        return super().assess(**({'max_tool_calls':2}|kwargs))

    def test_exact_boundary_never_approves_training(self):
        result=self.assess()
        self.assertTrue(result['mechanical_checks_passed'])
        self.assertFalse(result['training_approved'])
        self.assertEqual(result['assistant_completion_calls'],1)
        self.assertEqual(result['native_tool_calls'],2)
        self.assertEqual(self.assess(max_tool_calls=1)['mechanical_blockers'],['native_call_budget_exceeded'])

    def test_completion_bindings_rejected_even_with_rebound_outer_receipts(self):
        for field,value in [('completion_module',None),('completion_plan',None)]:
            original=self.read('attempt/receipt.json');changed=dict(original);changed[field]=value
            self.write('attempt/receipt.json',changed);self.rebind()
            with self.subTest(field=field),self.assertRaises(ValueError):self.assess()
            self.write('attempt/receipt.json',original);self.rebind()
        self.write('attempt/actions.json',[])
        with self.assertRaisesRegex(ValueError,'Completion provenance'):self.assess()

    def test_added_commands_and_authorship_cannot_be_relabelled(self):
        for change in ('command','author','result'):
            events=json.loads(json.dumps(self.events))
            if change=='command':events[-2]['native_calls'][0]['arguments']['command']='python other.py'
            elif change=='author':events[-2]['adapter_authored']=False
            else:events[-2]['result']['exit_code']=1
            self.write('attempt/events.json',events);self.rebind()
            with self.subTest(change=change),self.assertRaises(ValueError):self.assess()

    def test_missing_plan_and_changed_history_plan_rejected(self):
        history=self.read('history/receipt.json');history['completion_plan']=None
        self.write('history/receipt.json',history)
        with self.assertRaisesRegex(ValueError,'Completion provenance'):self.assess()
        replay=self.read('attempt/receipt.json');del replay['completion_plan']
        self.write('attempt/receipt.json',replay);self.rebind()
        with self.assertRaisesRegex(ValueError,'bound plan'):self.assess()

if __name__=='__main__':unittest.main()
