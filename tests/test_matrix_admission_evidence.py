"""Synthetic end-to-end admission evidence; no claimed external executions."""
from copy import deepcopy
import base64
import hashlib
from pathlib import Path
import unittest

from scripts.qualify_swe_rebench_evaluator import PLUGIN, PROBE
from tests import test_matrix_grade_evidence as evidence_fixtures
from tests import test_replay_admission as replay_fixtures
from zenithsync.artifacts import file_record, load_json
from zenithsync.matrix_admission_evidence import predicate_probe, verify_matrix_grade


class MatrixAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = evidence_fixtures.EvidenceTests('test_recomputes_without_mutating_or_granting_admission')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.write = self.fixture.write
        self.bundle = deepcopy(self.fixture.bundle)
        self.profile = dict(instance_id='fixture', python='/usr/local/bin/python', module='package',
                            expected_origin='/testbed/src/package/__init__.py', import_root='src',
                            platform='linux/arm64', test_targets=['tests'])
        self.patch = self.fixture.root / 'candidate.patch'
        self.patch.write_bytes(b'synthetic candidate')
        self.patches = dict(candidate=self.patch.read_bytes(), reference=b'synthetic reference', tests=b'synthetic tests')
        self.replay = dict(instance_id='fixture', profile=dict(repo='owner/repo', base_commit='d'*40),
                           patch=file_record(self.patch), image='sha256:'+'b'*64)
        patchrefs = {key:self.write(value.decode()) for key,value in self.patches.items() if key != 'candidate'}
        publisher = dict(task=dict(instance_id='fixture',repo='owner/repo',base_commit='d'*40),
                         files={key+'.patch':ref['identity'] for key,ref in patchrefs.items()})
        publisher['files']['metadata.json'] = self.bundle['metadata']['identity']
        allowed = ['src/package/__init__.py']
        proof = dict(publisher=self.write(publisher), profile=self.write(self.profile), patches=patchrefs,
                     primary='new', allowed_source_paths=allowed, environments={})
        for name, environment in self.bundle['environments'].items():
            image = 'sha256:' + ('a' if name=='old' else 'b')*64
            snapshot = dict(snapshot_commit='e'*40, source_tree='f'*40, base_commit='d'*40,exact_tree_preserved=True)
            verification = dict(tracked_manifest_matches=True,reachable_commits=1,old_commits_inaccessible=['d'*40])
            upstream=self.write('synthetic upstream input')
            env=dict(snapshot=self.write(snapshot),verification=self.write(verification),
                     receipt=self.write(self.receipt('',image)),
                     input_bindings=self.write({upstream['path']:upstream['identity']}),roles={},version_assertion=False)
            export=predicate_probe(self.patches['tests'],self.bundle['module_path'])
            environment['receipt']=self.write(self.receipt(export,image,grading=False))
            for role, role_refs in environment['roles'].items():
                settings=dict(BASE='e'*40,TREE='f'*40,ROLE=role,PYTHON=self.profile['python'],MODULE='package',
                              EXPECTED_ORIGIN=self.profile['expected_origin'],SOURCE_PYTHONPATH='/testbed/src',
                              ALLOWED_PATHS=allowed,TEST_TARGETS=['tests'],PLUGIN=PLUGIN,RESOURCE_PAYLOAD='',RESOURCE_ADAPTER='',
                              PATCHES={k:base64.b64encode(v).decode() for k,v in self.patches.items()})
                probe=''.join(f'{k}={v!r}\n' for k,v in settings.items())+PROBE
                role_refs['receipt']=self.write(self.receipt(probe,image))
                runtime=dict(role=role,tests_started=True,tracked_diff_unchanged_by_tests=True,
                             pytest_exit=load_json(Path(role_refs['outcomes']['path']))['exitstatus'])
                runtime['import']=dict(returncode=0,stdout=self.profile['expected_origin'])
                env['roles'][role]=dict(probe=self.write(probe),runtime=self.write(runtime),allowed_paths=allowed)
            proof['environments'][name]=env
        self.grade=dict(matrix=self.bundle,provenance=proof,task='fixture',
                        grading=dict(all_cases_match_reference=True,case_count=3,disagreements=[]))

    @staticmethod
    def receipt(probe,image,grading=True):
        return dict(image=image,image_id=image,platform='linux/arm64',entrypoint='/usr/local/bin/python',
                    probe_source=dict(sha256=hashlib.sha256(probe.encode()).hexdigest(),size_bytes=len(probe.encode())),
                    generated_grading_tests_executed=grading,agent_executed=False,
                    returncode=0,copy_returncode=0,cleanup_returncode=0,
                    state=dict(Status='exited',ExitCode=0,OOMKilled=False,Error=''))

    def check(self, grade=None):
        return verify_matrix_grade(self.grade if grade is None else grade,self.replay,self.patch)

    def test_composed_evidence_and_full_admission_keep_training_closed(self):
        self.assertGreater(len(self.check()),20)
        fixture=replay_fixtures.ReplayAdmissionTests('test_exact_boundary_never_approves_training')
        fixture.setUp();self.addCleanup(fixture.doCleanups)
        replay=load_json(fixture.root/'attempt/receipt.json')
        replay.update(self.replay)
        fixture.write('attempt/submitted.patch',self.patch.read_text())
        fixture.write('attempt/receipt.json',replay)
        history=load_json(fixture.root/'history/receipt.json')
        history['attempt']=fixture.record('attempt/receipt.json')
        fixture.write('history/receipt.json',history)
        grade=deepcopy(self.grade)
        grade.update(backend='swe_rebench_version_matrix',attempt=fixture.record('attempt/receipt.json'),
                     inputs=dict(patch=fixture.record('attempt/submitted.patch')))
        fixture.write('grade/report.json',grade)
        result=fixture.assess()
        self.assertTrue(result['mechanical_checks_passed'])
        self.assertFalse(result['training_approved'])
        self.assertEqual(fixture.assess(output_reserve=11)['mechanical_blockers'],['input_plus_output_reserve_exceeds_context'])

    def test_task_primary_image_and_normalized_grade_mismatches_reject(self):
        for change in ('task','primary','summary'):
            grade=deepcopy(self.grade)
            if change=='task':grade['task']='other'
            elif change=='primary':grade['provenance']['primary']='old'
            else:grade['grading']['case_count']=4
            with self.subTest(change=change),self.assertRaises(ValueError):self.check(grade)

    def test_rehashed_snapshot_runtime_and_export_failures_reject(self):
        for change in ('snapshot','runtime','export','empty_bindings'):
            grade=deepcopy(self.grade)
            env=grade['provenance']['environments']['new']
            if change=='snapshot':
                value=load_json(Path(env['verification']['path']));value['tracked_manifest_matches']=False
                env['verification']=self.write(value)
            elif change=='runtime':
                value=load_json(Path(env['roles']['candidate']['runtime']['path']));value['tests_started']=False
                env['roles']['candidate']['runtime']=self.write(value)
            elif change=='empty_bindings':env['input_bindings']=self.write({})
            else:
                ref=grade['matrix']['environments']['new']['receipt']
                value=load_json(Path(ref['path']));value['probe_source']['sha256']='0'*64
                grade['matrix']['environments']['new']['receipt']=self.write(value)
            with self.subTest(change=change),self.assertRaises(ValueError):self.check(grade)

    def test_rehashed_publisher_patch_substitution_rejects(self):
        grade=deepcopy(self.grade)
        grade['provenance']['patches']['tests']=self.write('substituted tests')
        with self.assertRaisesRegex(ValueError,'Publisher patch'):self.check(grade)
