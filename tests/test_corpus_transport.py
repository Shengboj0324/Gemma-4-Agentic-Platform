"""Corpus transport must publish only the corpus and prove restored identity."""

from pathlib import Path
import shutil
import tempfile
import unittest

from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.corpus_admission import promote_corpus
from zenithsync.corpus_transport import (corpus_file_paths, publish_corpus,
                                         restore_corpus)
from zenithsync.object_store import ArtifactStore
from zenithsync.training_corpus import GATES, corpus_content_identity


class CorpusTransportTests(unittest.TestCase):
    def setUp(self):
        from tests.test_object_store import MemoryClient
        from tests.test_training_corpus import CorpusTests
        self.fixture = CorpusTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.write('corpus.json', self.fixture.manifest)
        self.quarantine = self.fixture.root
        self.quarantine_identity = file_record(self.quarantine / 'corpus.json')
        self.content = corpus_content_identity(self.fixture.manifest)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.client = MemoryClient()
        self.store = ArtifactStore(self.client, 'test-bucket', prefix='quarantine/v1')

    def admitted(self):
        documents = {}
        for gate in GATES:
            path = self.work / (gate + '.json')
            body = {'schema_version': 1, 'synthetic_test_only': True}
            if gate == 'task_alignment':
                body.update(self.fixture.alignment_evidence())
            path.write_bytes(canonical_json(body))
            documents[gate] = [path]
        destination = self.work / 'admitted'
        receipt = promote_corpus(source_root=self.quarantine,
                                 source_manifest_sha256=self.quarantine_identity['sha256'],
                                 destination=destination, gate_evidence=documents,
                                 reviewer='unit-test')
        return destination, receipt['destination']['manifest']['sha256']

    # --- publish --------------------------------------------------------------

    def test_quarantine_roundtrip_preserves_identity_and_status(self):
        published = publish_corpus(self.store, self.quarantine,
                                   corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                   source='unit-test', revision='001',
                                   expected_status='quarantine')
        self.assertEqual(published['corpus_content_sha256'], self.content)
        self.assertEqual(published['corpus_status'], 'quarantine')
        self.assertEqual(published['file_count'], 3)
        destination = self.work / 'restored-quarantine'
        result = restore_corpus(self.store, published['artifact_manifest'], destination,
                                expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                expected_content_sha256=self.content,
                                expected_status='quarantine', purpose='inspection',
                                max_restore_bytes=10**6)
        self.assertEqual(result['summary']['content_sha256'], self.content)
        self.assertFalse(result['summary']['training_admitted'])
        self.assertEqual(result['corpus'].fetch('trace1')['input_ids'], [1, 2, 3])
        self.assertEqual(file_record(destination / 'corpus.json'), self.quarantine_identity)

    def test_admitted_roundtrip_carries_receipts_and_evidence(self):
        root, manifest_sha256 = self.admitted()
        published = publish_corpus(self.store, root,
                                   corpus_manifest_sha256=manifest_sha256,
                                   source='unit-test', revision='002',
                                   expected_status='admitted')
        # corpus.json + two example files + four receipts + four evidence copies
        self.assertEqual(published['file_count'], 11)
        self.assertEqual(published['corpus_status'], 'admitted')
        destination = self.work / 'restored-admitted'
        result = restore_corpus(self.store, published['artifact_manifest'], destination,
                                expected_corpus_manifest_sha256=manifest_sha256,
                                expected_content_sha256=self.content,
                                expected_status='admitted', purpose='training',
                                max_restore_bytes=10**6)
        self.assertTrue(result['summary']['training_admitted'])
        self.assertEqual(result['summary']['returned_examples'], 1)
        for gate, reference in load_json(destination / 'corpus.json')['admission'].items():
            body = load_json(destination / reference['path'])
            self.assertEqual(body['gate'], gate)
            for evidence in body['evidence']:
                self.assertTrue((destination / evidence['path']).is_file())

    def test_extra_file_in_the_tree_blocks_publication(self):
        (self.quarantine / '.env').write_text('R2_SECRET_ACCESS_KEY=planted\n')
        with self.assertRaisesRegex(ValueError, r"extra=\['\.env'\]"):
            publish_corpus(self.store, self.quarantine,
                           corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           source='unit-test', revision='001')
        self.assertFalse(self.client.objects)

    def test_declared_status_mismatch_blocks_publication(self):
        with self.assertRaisesRegex(ValueError, 'status differs'):
            publish_corpus(self.store, self.quarantine,
                           corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           source='unit-test', revision='001',
                           expected_status='admitted')
        self.assertFalse(self.client.objects)

    def test_wrong_corpus_digest_blocks_publication(self):
        with self.assertRaises(ValueError):
            publish_corpus(self.store, self.quarantine,
                           corpus_manifest_sha256='c' * 64,
                           source='unit-test', revision='001')
        self.assertFalse(self.client.objects)

    # --- restore refusals -----------------------------------------------------

    def test_restore_refuses_wrong_content_identity(self):
        published = publish_corpus(self.store, self.quarantine,
                                   corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                   source='unit-test', revision='001')
        with self.assertRaisesRegex(ValueError, 'content identity differs'):
            restore_corpus(self.store, published['artifact_manifest'],
                           self.work / 'bad-content',
                           expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           expected_content_sha256='e' * 64,
                           expected_status='quarantine', purpose='inspection',
                           max_restore_bytes=10**6)

    def test_restore_refuses_wrong_declared_status(self):
        published = publish_corpus(self.store, self.quarantine,
                                   corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                   source='unit-test', revision='001')
        with self.assertRaisesRegex(ValueError, 'Training restoration requires'):
            restore_corpus(self.store, published['artifact_manifest'],
                           self.work / 'bad-purpose',
                           expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           expected_content_sha256=self.content,
                           expected_status='quarantine', purpose='training',
                           max_restore_bytes=10**6)
        with self.assertRaisesRegex(ValueError, 'status must be'):
            restore_corpus(self.store, published['artifact_manifest'],
                           self.work / 'bad-status',
                           expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           expected_content_sha256=self.content,
                           expected_status='approved', purpose='inspection',
                           max_restore_bytes=10**6)

    def test_quarantine_corpus_cannot_be_restored_as_admitted(self):
        published = publish_corpus(self.store, self.quarantine,
                                   corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                   source='unit-test', revision='001')
        with self.assertRaises(ValueError):
            restore_corpus(self.store, published['artifact_manifest'],
                           self.work / 'claims-admitted',
                           expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           expected_content_sha256=self.content,
                           expected_status='admitted', purpose='training',
                           max_restore_bytes=10**6)

    def test_restore_refuses_a_bundle_missing_the_corpus_manifest(self):
        published = publish_corpus(self.store, self.quarantine,
                                   corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                   source='unit-test', revision='001')
        manifest = published['artifact_manifest']
        trimmed = {**manifest, 'files': [row for row in manifest['files']
                                         if row['path'] != 'corpus.json']}
        with self.assertRaisesRegex(ValueError, 'does not contain a corpus manifest'):
            restore_corpus(self.store, trimmed, self.work / 'no-manifest',
                           expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           expected_content_sha256=self.content,
                           expected_status='quarantine', purpose='inspection',
                           max_restore_bytes=10**6)

    def test_restore_refuses_a_bundle_carrying_an_undeclared_extra_file(self):
        published = publish_corpus(self.store, self.quarantine,
                                   corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                   source='unit-test', revision='001')
        planted = self.quarantine / 'planted.json'
        planted.write_bytes(canonical_json({'planted': True}))
        record = file_record(planted)
        record['path'] = 'planted.json'
        self.client.upload_file(str(planted), 'test-bucket',
                                self.store.blob_key(record['sha256']))
        manifest = published['artifact_manifest']
        widened = {**manifest, 'files': sorted([*manifest['files'], record],
                                               key=lambda row: row['path'])}
        with self.assertRaisesRegex(ValueError, 'differs from the paths'):
            restore_corpus(self.store, widened, self.work / 'extra-file',
                           expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           expected_content_sha256=self.content,
                           expected_status='quarantine', purpose='inspection',
                           max_restore_bytes=10**6)

    def test_restore_byte_budget_is_enforced(self):
        published = publish_corpus(self.store, self.quarantine,
                                   corpus_manifest_sha256=self.quarantine_identity['sha256'],
                                   source='unit-test', revision='001')
        with self.assertRaisesRegex(ValueError, 'restore byte budget'):
            restore_corpus(self.store, published['artifact_manifest'],
                           self.work / 'too-big',
                           expected_corpus_manifest_sha256=self.quarantine_identity['sha256'],
                           expected_content_sha256=self.content,
                           expected_status='quarantine', purpose='inspection',
                           max_restore_bytes=1)

    # --- path enumeration -----------------------------------------------------

    def test_path_enumeration_rejects_a_tampered_receipt(self):
        root, manifest_sha256 = self.admitted()
        manifest = load_json(root / 'corpus.json')
        self.assertIn('admission/task_alignment/receipt.json', corpus_file_paths(root, manifest))
        reference = manifest['admission']['split_isolation']
        (root / reference['path']).write_bytes(canonical_json({'gate': 'split_isolation'}))
        with self.assertRaisesRegex(ValueError, 'receipt identity differs'):
            corpus_file_paths(root, manifest)

    def test_path_enumeration_rejects_an_unknown_gate(self):
        manifest = load_json(self.quarantine / 'corpus.json')
        manifest['admission']['invented_gate'] = None
        with self.assertRaisesRegex(ValueError, 'Unknown admission gate'):
            corpus_file_paths(self.quarantine, manifest)

    def test_restored_admitted_corpus_survives_losing_its_origin(self):
        root, manifest_sha256 = self.admitted()
        published = publish_corpus(self.store, root,
                                   corpus_manifest_sha256=manifest_sha256,
                                   source='unit-test', revision='002')
        shutil.rmtree(root)
        shutil.rmtree(self.quarantine)
        destination = self.work / 'origin-free'
        result = restore_corpus(self.store, published['artifact_manifest'], destination,
                                expected_corpus_manifest_sha256=manifest_sha256,
                                expected_content_sha256=self.content,
                                expected_status='admitted', purpose='training',
                                max_restore_bytes=10**6)
        self.assertTrue(result['summary']['training_admitted'])
        self.assertEqual(result['corpus'].fetch('trace1')['labels'], [-100, -100, 3])


if __name__ == '__main__':
    unittest.main()
