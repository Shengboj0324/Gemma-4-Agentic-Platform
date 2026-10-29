"""Promotion must bind real evidence and refuse every weakened variant."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
import unittest.mock

from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.corpus_admission import (EVIDENCE_MAX_BYTES, build_gate_receipt,
                                         promote_corpus)
from zenithsync.training_corpus import GATES, IndexedCorpus, corpus_content_identity


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        from tests.test_training_corpus import CorpusTests
        self.fixture = CorpusTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.write('corpus.json', self.fixture.manifest)
        self.source = self.fixture.root
        self.manifest_identity = file_record(self.source / 'corpus.json')
        self.content = corpus_content_identity(self.fixture.manifest)
        self.outside = tempfile.TemporaryDirectory()
        self.addCleanup(self.outside.cleanup)
        self.evidence_root = Path(self.outside.name)
        self.destination = self.evidence_root / 'admitted'
        self.documents = {}
        for gate in GATES:
            path = self.evidence_root / (gate + '-evidence.json')
            body = {'schema_version': 1, 'synthetic_test_only': True,
                    'corpus': self.manifest_identity, 'gate': gate}
            if gate == 'task_alignment':
                body.update(self.fixture.alignment_evidence())
                body['corpus'] = self.manifest_identity
            path.write_bytes(canonical_json(body))
            self.documents[gate] = [path]

    def promote(self, **overrides):
        arguments = {'source_root': self.source,
                     'source_manifest_sha256': self.manifest_identity['sha256'],
                     'destination': self.destination,
                     'gate_evidence': self.documents,
                     'reviewer': 'unit-test-reviewer'}
        arguments.update(overrides)
        return promote_corpus(**arguments)

    # --- the one success path -------------------------------------------------

    def test_promotion_preserves_content_and_reaches_training_admission(self):
        receipt = self.promote()
        self.assertEqual(receipt['status'], 'corpus_admitted')
        self.assertEqual(receipt['corpus_content_sha256'], self.content)
        self.assertTrue(receipt['summary']['training_admitted'])
        self.assertEqual(receipt['summary']['content_sha256'], self.content)
        # The source corpus is untouched and still unable to train.
        self.assertEqual(file_record(self.source / 'corpus.json'), self.manifest_identity)
        self.assertEqual(load_json(self.source / 'corpus.json')['status'], 'quarantine')
        promoted = load_json(self.destination / 'corpus.json')
        self.assertEqual(promoted['status'], 'admitted')
        self.assertEqual(promoted['examples'], self.fixture.manifest['examples'])
        self.assertEqual(corpus_content_identity(promoted), self.content)
        for gate in GATES:
            reference = promoted['admission'][gate]
            body = load_json(self.destination / reference['path'])
            self.assertEqual(body['gate'], gate)
            self.assertEqual(body['status'], 'passed')
            self.assertEqual(body['corpus_content_sha256'], self.content)
            self.assertFalse(body['training_approved_by_this_receipt_alone'])
            for evidence in body['evidence']:
                self.assertEqual(file_record(self.destination / evidence['path']),
                                 evidence['identity'])
        # An independent loader, not the promotion result, confirms admission.
        reader = IndexedCorpus(self.destination, self.destination / 'corpus.json',
                               expected_manifest_sha256=receipt['destination']['manifest']['sha256'],
                               purpose='training')
        self.assertEqual(reader.summary['supervised_tokens'],
                         self.fixture.audit['supervised_tokens'])
        self.assertEqual(reader.fetch('trace1')['input_ids'], [1, 2, 3])

    def test_promoted_tree_is_self_contained_without_the_source(self):
        receipt = self.promote()
        relocated = self.evidence_root / 'relocated'
        shutil.copytree(self.destination, relocated, symlinks=False)
        shutil.rmtree(self.source)
        reader = IndexedCorpus(relocated, relocated / 'corpus.json',
                               expected_manifest_sha256=receipt['destination']['manifest']['sha256'],
                               purpose='training')
        self.assertTrue(reader.summary['training_admitted'])

    # --- refusals -------------------------------------------------------------

    def test_missing_or_empty_gate_evidence_is_refused(self):
        partial = {gate: paths for gate, paths in self.documents.items()
                   if gate != 'split_isolation'}
        with self.assertRaisesRegex(ValueError, 'exactly the four admission gates'):
            self.promote(gate_evidence=partial)
        empty = dict(self.documents, split_isolation=[])
        with self.assertRaisesRegex(ValueError, 'at least one evidence document'):
            self.promote(gate_evidence=empty)
        self.assertFalse(self.destination.exists())

    def test_evidence_naming_another_corpus_is_refused(self):
        path = self.documents['rights_and_attribution'][0]
        body = load_json(path)
        body['corpus'] = {'sha256': 'f' * 64, 'size_bytes': 11}
        path.write_bytes(canonical_json(body))
        with self.assertRaisesRegex(ValueError, 'names a different corpus'):
            self.promote()
        self.assertFalse(self.destination.exists())

    def test_incomplete_task_alignment_review_is_refused(self):
        path = self.documents['task_alignment'][0]
        body = load_json(path)
        body['task_reviews'] = []
        path.write_bytes(canonical_json(body))
        with self.assertRaisesRegex(ValueError, 'versioned task reviews'):
            self.promote()
        body['task_reviews'] = [{'task_id': 'repo-1', 'repository_group': 'owner/repo',
                                 'decision': 'rejected', 'rationale': 'declined'}]
        path.write_bytes(canonical_json(body))
        with self.assertRaisesRegex(ValueError, 'not accepted'):
            self.promote()
        body['task_reviews'] = [{'task_id': 'other', 'repository_group': 'owner/repo',
                                 'decision': 'accepted', 'rationale': 'foreign'}]
        path.write_bytes(canonical_json(body))
        with self.assertRaisesRegex(ValueError, 'foreign task'):
            self.promote()
        self.assertFalse(self.destination.exists())

    def test_evidence_inside_the_corpus_tree_is_refused(self):
        inside = self.source / 'planted-evidence.json'
        inside.write_bytes(canonical_json({'schema_version': 1, 'planted': True}))
        with self.assertRaisesRegex(ValueError, 'outside the corpus tree'):
            self.promote(gate_evidence=dict(self.documents,
                                            rights_and_attribution=[inside]))

    def test_already_admitted_or_partly_admitted_source_is_refused(self):
        self.fixture.manifest['status'] = 'admitted'
        self.fixture.write('corpus.json', self.fixture.manifest)
        identity = file_record(self.source / 'corpus.json')
        with self.assertRaises(ValueError):
            self.promote(source_manifest_sha256=identity['sha256'])
        self.fixture.manifest['status'] = 'quarantine'
        self.fixture.write('placeholder.json', {'gate': 'rights_and_attribution'})
        self.fixture.manifest['admission']['rights_and_attribution'] = \
            self.fixture.ref('placeholder.json')
        self.fixture.write('corpus.json', self.fixture.manifest)
        identity = file_record(self.source / 'corpus.json')
        with self.assertRaises(ValueError):
            self.promote(source_manifest_sha256=identity['sha256'])
        self.assertFalse(self.destination.exists())

    def test_a_destination_inside_the_source_tree_is_refused(self):
        # Staging inside the source would write the admitted tree, and its
        # temporary directory, into the corpus promotion promises not to edit.
        before = sorted(path.name for path in self.source.iterdir())
        with self.assertRaisesRegex(ValueError, 'outside the source corpus tree'):
            self.promote(destination=self.source / 'admitted')
        (self.source / 'nested').mkdir()
        with self.assertRaisesRegex(ValueError, 'outside the source corpus tree'):
            self.promote(destination=self.source / 'nested' / 'admitted')
        (self.source / 'nested').rmdir()
        self.assertEqual(sorted(path.name for path in self.source.iterdir()), before)

    def test_a_missing_destination_parent_is_named_rather_than_crashing(self):
        with self.assertRaisesRegex(ValueError, 'parent directory does not exist'):
            self.promote(destination=self.evidence_root / 'absent' / 'admitted')

    def test_each_receipt_records_the_manifest_its_evidence_was_reviewed_against(self):
        self.promote()
        promoted = load_json(self.destination / 'corpus.json')
        for gate in GATES:
            body = load_json(self.destination / promoted['admission'][gate]['path'])
            self.assertEqual(body['reviewed_against_manifest'], self.manifest_identity)

    def test_wrong_manifest_digest_and_existing_destination_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'Untrusted or oversized'):
            self.promote(source_manifest_sha256='b' * 64)
        self.destination.mkdir()
        with self.assertRaises(FileExistsError):
            self.promote()

    def test_tampered_example_file_is_refused_before_publication(self):
        (self.source / 'tokens.json').write_bytes(canonical_json({'tampered': True}))
        with self.assertRaises(ValueError):
            self.promote()
        self.assertFalse(self.destination.exists())

    def test_evidence_changed_during_promotion_aborts_without_publishing(self):
        original = shutil.copyfile
        target = self.documents['runtime_qualification'][0].resolve()

        def mutate_then_copy(source, destination, *args, **kwargs):
            result = original(source, destination, *args, **kwargs)
            if Path(source).resolve() == target:
                target.write_bytes(canonical_json({'schema_version': 1, 'swapped': True}))
            return result

        with unittest.mock.patch.object(shutil, 'copyfile', mutate_then_copy):
            with self.assertRaises(ValueError):
                self.promote()
        self.assertFalse(self.destination.exists())

    def test_oversized_evidence_document_is_refused(self):
        path = self.evidence_root / 'huge.json'
        path.write_bytes(b'{"schema_version":1,"filler":"' +
                         b'x' * (EVIDENCE_MAX_BYTES + 1) + b'"}')
        with self.assertRaisesRegex(ValueError, 'size out of bounds'):
            self.promote(gate_evidence=dict(self.documents,
                                            rights_and_attribution=[path]))

    def test_non_object_evidence_document_is_refused(self):
        path = self.evidence_root / 'list.json'
        path.write_bytes(canonical_json([1, 2, 3]))
        with self.assertRaisesRegex(ValueError, 'must be a JSON object'):
            self.promote(gate_evidence=dict(self.documents, split_isolation=[path]))

    def test_duplicate_evidence_document_for_one_gate_is_refused(self):
        path = self.documents['split_isolation'][0]
        with self.assertRaisesRegex(ValueError, 'Duplicate evidence document'):
            self.promote(gate_evidence=dict(self.documents, split_isolation=[path, path]))

    def test_blank_reviewer_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'reviewer'):
            self.promote(reviewer='   ')

    # --- supporting evidence --------------------------------------------------

    def test_supporting_evidence_is_bound_without_schema_validation(self):
        # A coverage-control report has no task_reviews field, so it can never be
        # a primary task_alignment document; it must still travel with the bundle.
        control = self.evidence_root / 'alignment-coverage.json'
        control.write_bytes(canonical_json({
            'schema_version': 1, 'accepted': 1, 'unaccepted': 0,
            'missing_review_controls_rejected': 1, 'full_coverage_verified': True,
            'corpus': self.manifest_identity}))
        with self.assertRaisesRegex(ValueError, 'versioned task reviews'):
            self.promote(gate_evidence=dict(self.documents,
                                            task_alignment=[self.documents['task_alignment'][0],
                                                            control]))
        self.assertFalse(self.destination.exists())
        receipt = self.promote(supporting_evidence={'task_alignment': [control]})
        self.assertEqual(len(receipt['supporting_documents']['task_alignment']), 1)
        promoted = load_json(self.destination / 'corpus.json')
        body = load_json(self.destination / promoted['admission']['task_alignment']['path'])
        self.assertEqual(len(body['evidence']), 1)
        self.assertEqual(len(body['supporting_evidence']), 1)
        staged = self.destination / body['supporting_evidence'][0]['path']
        self.assertIn('/support/', staged.as_posix())
        self.assertEqual(file_record(staged), body['supporting_evidence'][0]['identity'])
        self.assertEqual(load_json(staged)['full_coverage_verified'], True)
        # The admitted corpus still loads for training with the extra files present.
        reader = IndexedCorpus(self.destination, self.destination / 'corpus.json',
                               expected_manifest_sha256=receipt['destination']['manifest']['sha256'],
                               purpose='training')
        self.assertTrue(reader.summary['training_admitted'])

    def test_supporting_evidence_must_be_keyed_by_gate_and_not_duplicate_primary(self):
        with self.assertRaisesRegex(ValueError, 'keyed by admission gate'):
            self.promote(supporting_evidence={'invented_gate': []})
        primary = self.documents['split_isolation'][0]
        with self.assertRaisesRegex(ValueError, 'both primary and supporting'):
            self.promote(supporting_evidence={'split_isolation': [primary]})
        self.assertFalse(self.destination.exists())

    def test_gates_without_supporting_evidence_record_an_empty_list(self):
        self.promote()
        promoted = load_json(self.destination / 'corpus.json')
        for gate in GATES:
            body = load_json(self.destination / promoted['admission'][gate]['path'])
            self.assertEqual(body['supporting_evidence'], [])

    # --- receipt builder ------------------------------------------------------

    def test_receipt_builder_rejects_malformed_inputs(self):
        reference = {'path': 'admission/x/000-a.json',
                     'identity': {'sha256': 'a' * 64, 'size_bytes': 5}}
        good = build_gate_receipt(gate='split_isolation', corpus_content_sha256='c' * 64,
                                  evidence=[reference], reviewer='r', scope='s')
        self.assertEqual(good['status'], 'passed')
        self.assertEqual(json.loads(canonical_json(good))['gate'], 'split_isolation')
        cases = [
            ({'gate': 'unknown_gate'}, 'Unknown admission gate'),
            ({'corpus_content_sha256': 'short'}, 'SHA-256'),
            ({'evidence': []}, 'at least one evidence reference'),
            ({'evidence': [reference, reference]}, 'Duplicate evidence reference'),
            ({'evidence': [{'path': '../escape.json', 'identity': reference['identity']}]},
             'relative POSIX path'),
            ({'evidence': [{'path': 'a.json',
                            'identity': {'sha256': 'a' * 64, 'size_bytes': 0}}]},
             'size out of bounds'),
            ({'reviewer': ''}, 'reviewer'),
            ({'scope': ' '}, 'scope'),
            ({'supporting_evidence': {}}, 'must be a list'),
            ({'supporting_evidence': [reference]}, 'Duplicate evidence reference'),
            ({'supporting_evidence': [{'path': 'support/a.json',
                                       'identity': {'sha256': 'a' * 64, 'size_bytes': 0}}]},
             'size out of bounds'),
        ]
        for override, message in cases:
            arguments = {'gate': 'split_isolation', 'corpus_content_sha256': 'c' * 64,
                         'evidence': [reference], 'reviewer': 'r', 'scope': 's'}
            arguments.update(override)
            with self.assertRaisesRegex(ValueError, message):
                build_gate_receipt(**arguments)


if __name__ == '__main__':
    unittest.main()
