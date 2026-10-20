import hashlib
from pathlib import Path
import tempfile
import unittest

from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.pytest_controls import compare_candidate, compare_controls
from zenithsync.replay_history import native_replay_history
from zenithsync.v2_synthetic_admission import assess_v2_synthetic_bundle, assess_legacy_synthetic_bundle


class V2SyntheticBundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.attempt, self.grade, self.tokens, self.snapshot = [self.root/p for p in ('attempt','grade','tokens','snapshot')]
        for p in (self.attempt,self.grade,self.tokens,self.snapshot):
            p.mkdir()
        self.task = self.root/'task.json'
        self.review = self.root/'review.json'
        self.sources = {key:self.root/(key+'.py') for key in ('runner','fixture')}
        for path in self.sources.values():
            path.write_text('# synthetic test fixture\n')
        self.write(self.snapshot/'snapshot.json',{'base_commit':'base','snapshot_commit':'snapshot'})
        task = {'instance_id':'test-1','base_commit':'base','problem_statement':'issue',
                'FAIL_TO_PASS':['tests/test_a.py::a'],'PASS_TO_PASS':['tests/test_a.py::b']}
        self.write(self.task,task)
        tools = [{'function':{'name':name}} for name in ('run_command','submit_patch')]
        events = [{'source_index':i,'kind':'synthetic','result':{'status':'ok'},
            'native_calls':[{'name':name,'arguments':{},'result':{'status':'ok'}}]}
            for i,name in enumerate(('run_command','submit_patch'))]
        messages = native_replay_history(events,system='system',problem='issue',
            allowed_tools={'run_command','submit_patch'})['messages'] + [{'role':'assistant','content':'Bounded result.'}]
        for name,value in [('events',events),('history',messages),('tools',tools)]:
            self.write(self.attempt/(name+'.json'),value)
        (self.attempt/'submitted.patch').write_text('fixture patch\n')
        receipt = dict(kind='synthetic_native_trajectory',author='assistant',reference_informed=True,
            source_observations_reused=False,new_model_evaluated=False,training_approved=False,
            status='captured_not_graded',cleanup={'removed':True},image='sha256:'+'a'*64,tool_calls=1,
            snapshot=load_json(self.snapshot/'snapshot.json'),
            patch=file_record(self.attempt/'submitted.patch'),history=file_record(self.attempt/'history.json'),
            tools=file_record(self.attempt/'tools.json'))
        receipt.update({key:file_record(path) for key,path in self.sources.items()})
        self.write(self.attempt/'receipt.json',receipt)
        outcomes, controls = {}, {}
        for role in ('base','reference','candidate'):
            directory = self.grade/role
            directory.mkdir()
            nodes = ['tests/test_a.py::a','tests/test_a.py::b']
            outcomes[role] = {'collected':nodes,'collection_errors':[], 'exitstatus':int(role=='base'),
                'reports':[{'nodeid':node,'when':phase,'outcome':
                    'failed' if role=='base' and node==nodes[0] and phase=='call' else 'passed'}
                    for node in nodes for phase in ('setup','call','teardown')]}
            controls[role] = {'image_id':'sha256:'+'a'*64,'state':{'OOMKilled':False,'Status':'exited','ExitCode':0},
                'returncode':0,'copy_returncode':0,'cleanup_returncode':0}
            self.write(directory/'receipt.json',controls[role])
            self.write(directory/'runtime.json',{'role':role,'tests_started':True,
                'tracked_diff_unchanged_by_tests':True,'pytest_exit':outcomes[role]['exitstatus']})
            self.write(directory/'outcomes.json',outcomes[role])
        expectations = {k:task[k] for k in ('FAIL_TO_PASS','PASS_TO_PASS')}
        expectations.update(FAIL_TO_FAIL=[],PASS_TO_FAIL=[])
        bound = [self.attempt/n for n in ('receipt.json','events.json','history.json','tools.json','submitted.patch')]
        bound += [self.task,self.snapshot/'snapshot.json']
        self.write(self.grade/'report.json',{'trajectory_kind':'synthetic_native_trajectory',
            'training_approved':False,'sanitized_snapshot':True,'inputs':{str(p):file_record(p) for p in bound},
            'controls':controls,'comparison':compare_controls(outcomes['base'],outcomes['reference'],expectations),
            'candidate_comparison':compare_candidate(outcomes['reference'],outcomes['candidate'])})
        candidate = {'history':receipt['history'],'tools':receipt['tools'],'training_approved':False,
                     'input_ids':[1,2,3,4],'labels':[-100,-100,3,4]}
        self.write(self.tokens/'tokens.json',candidate)
        self.write(self.tokens/'report.json',dict(history=receipt['history'],tools=receipt['tools'],
            training_approved=False,truncated=False,token_candidate=file_record(self.tokens/'tokens.json'),
            input_tokens=4,supervised_tokens=2,
            input_sha256=hashlib.sha256(canonical_json(candidate['input_ids'])).hexdigest(),
            labels_sha256=hashlib.sha256(canonical_json(candidate['labels'])).hexdigest()))
        self.write(self.review,dict(task='test-1',history=receipt['history'],grade=file_record(self.grade/'report.json'),
            synthetic=True,reference_informed=True,content_quality_accepted=True,training_approved=False))
        self.arguments = dict(attempt=self.attempt,grade=self.grade,tokens=self.tokens,task=self.task,
            snapshot=self.snapshot,review=self.review,capture_sources=self.sources)

    @staticmethod
    def write(path,value):
        path.write_bytes(canonical_json(value))

    def test_valid_bundle_remains_unapproved_and_does_not_mutate(self):
        before = {str(p):file_record(p) for p in self.root.rglob('*') if p.is_file()}
        report = assess_v2_synthetic_bundle(**self.arguments)
        self.assertTrue(report['mechanical_checks_passed'])
        self.assertIs(report['training_approved'],False)
        self.assertEqual(report['supervised_tokens'],2)
        self.assertEqual(before,{str(p):file_record(p) for p in self.root.rglob('*') if p.is_file()})

    def test_context_and_call_limits_remain_blockers(self):
        result = assess_v2_synthetic_bundle(**self.arguments,max_input_tokens=5,output_reserve=2)
        self.assertEqual(result['mechanical_blockers'],['input_plus_output_reserve_exceeds_context'])
        with self.assertRaisesRegex(ValueError,'policy'):
            assess_v2_synthetic_bundle(**self.arguments,max_tool_calls=True)

    def test_mutated_source_is_rejected(self):
        self.sources['fixture'].write_text('changed fixture')
        with self.assertRaisesRegex(ValueError,'source identity'):
            assess_v2_synthetic_bundle(**self.arguments)

    def test_mutated_capture_is_rejected(self):
        self.write(self.attempt/'events.json',[])
        with self.assertRaisesRegex(ValueError,'bind selected events'):
            assess_v2_synthetic_bundle(**self.arguments)

    def test_false_grade_is_recomputed(self):
        p=self.grade/'candidate/outcomes.json'
        value=load_json(p)
        value['reports'][1]['outcome']='failed'
        value['exitstatus']=1
        self.write(p,value)
        p=self.grade/'candidate/runtime.json';value=load_json(p);value['pytest_exit']=1;self.write(p,value)
        with self.assertRaisesRegex(ValueError,'recomputed outcomes'):
            assess_v2_synthetic_bundle(**self.arguments)

    def test_labels_and_boolean_counts_are_rejected(self):
        path=self.tokens/'report.json';value=load_json(path);value['supervised_tokens']=True;self.write(path,value)
        with self.assertRaisesRegex(ValueError,'token audit'):
            assess_v2_synthetic_bundle(**self.arguments)
        value['supervised_tokens']=2;self.write(path,value)
        path=self.tokens/'tokens.json';value=load_json(path);value['labels'][2]=999;self.write(path,value)
        with self.assertRaisesRegex(ValueError,'token arrays'):
            assess_v2_synthetic_bundle(**self.arguments)

    def test_review_must_bind_exact_grade(self):
        value=load_json(self.review);value['grade']={'sha256':'different'};self.write(self.review,value)
        with self.assertRaisesRegex(ValueError,'content acceptance'):
            assess_v2_synthetic_bundle(**self.arguments)

    def legacy_bundle(self, *, stable_failure=False):
        task = load_json(self.task)
        task.update(FAIL_TO_FAIL=[], PASS_TO_FAIL=[])
        if stable_failure:
            node = task['PASS_TO_PASS'].pop()
            task['FAIL_TO_FAIL'] = [node]
            for role in ('base','reference','candidate'):
                path = self.grade/role/'outcomes.json'
                outcomes = load_json(path)
                for row in outcomes['reports']:
                    if row['nodeid'] == node and row['when'] == 'call':
                        row['outcome'] = 'failed'
                outcomes['exitstatus'] = 1
                self.write(path,outcomes)
                path = self.grade/role/'runtime.json'
                runtime = load_json(path); runtime['pytest_exit'] = 1; self.write(path,runtime)
        self.write(self.task, task)
        path = self.grade/'report.json'
        grade = load_json(path)
        grade['publisher_format'] = 'legacy_four_transitions'
        grade['inputs'][str(self.task)] = file_record(self.task)
        expected = {k:task[k] for k in ('FAIL_TO_PASS','PASS_TO_PASS','FAIL_TO_FAIL','PASS_TO_FAIL')}
        grade['comparison'] = compare_controls(load_json(self.grade/'base/outcomes.json'),
            load_json(self.grade/'reference/outcomes.json'), expected)
        grade['candidate_comparison'] = compare_candidate(load_json(self.grade/'reference/outcomes.json'),
            load_json(self.grade/'candidate/outcomes.json'))
        self.write(path,grade)
        review = load_json(self.review); review['grade'] = file_record(path); self.write(self.review,review)

    def test_legacy_retains_declared_stable_failure_without_training_approval(self):
        self.legacy_bundle(stable_failure=True)
        before = {str(p):file_record(p) for p in self.root.rglob('*') if p.is_file()}
        result = assess_legacy_synthetic_bundle(**self.arguments)
        self.assertTrue(result['mechanical_checks_passed'])
        self.assertIs(result['training_approved'],False)
        self.assertEqual(result['publisher_format'],'legacy_four_transitions')
        self.assertEqual(before,{str(p):file_record(p) for p in self.root.rglob('*') if p.is_file()})

    def test_publisher_formats_cannot_be_interchanged(self):
        with self.assertRaisesRegex(ValueError,'format mismatch'):
            assess_legacy_synthetic_bundle(**self.arguments)
        self.legacy_bundle()
        with self.assertRaisesRegex(ValueError,'format mismatch'):
            assess_v2_synthetic_bundle(**self.arguments)

    def test_legacy_missing_category_and_false_summary_rejected(self):
        self.legacy_bundle()
        task = load_json(self.task); del task['FAIL_TO_FAIL']; self.write(self.task,task)
        path = self.grade/'report.json'; grade = load_json(path)
        grade['inputs'][str(self.task)] = file_record(self.task); self.write(path,grade)
        with self.assertRaisesRegex(ValueError,'four legacy transition'):
            assess_legacy_synthetic_bundle(**self.arguments)
        self.legacy_bundle()
        grade = load_json(path); grade['comparison'] = {}; self.write(path,grade)
        with self.assertRaisesRegex(ValueError,'recomputed outcomes'):
            assess_legacy_synthetic_bundle(**self.arguments)


if __name__ == '__main__':
    unittest.main()
