"""The independent audit must re-derive the same numbers and catch tampering."""

import hashlib
from pathlib import Path
import tempfile
import unittest

from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.corpus_admission import promote_corpus
from zenithsync.corpus_audit import (CorpusAuditError, audit_corpus,
                                     compare_with_loader, verify_schedule_coverage)
from zenithsync.training_corpus import GATES, IndexedCorpus
from zenithsync.training_schedule import make_schedule


class CorpusAuditTests(unittest.TestCase):
    def setUp(self):
        from tests.test_training_corpus import CorpusTests
        self.fixture = CorpusTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.write('corpus.json', self.fixture.manifest)
        self.quarantine = self.fixture.root
        self.quarantine_sha256 = file_record(self.quarantine / 'corpus.json')['sha256']
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.root, self.manifest_sha256 = self.admit()

    def admit(self):
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
                                 source_manifest_sha256=self.quarantine_sha256,
                                 destination=destination, gate_evidence=documents,
                                 reviewer='unit-test')
        return destination, receipt['destination']['manifest']['sha256']

    def audit(self, **overrides):
        arguments = {'expected_manifest_sha256': self.manifest_sha256}
        arguments.update(overrides)
        return audit_corpus(self.root, **arguments)

    def rewrite(self, relative, value):
        """Write a corpus file and refresh the manifest digest the audit expects."""
        (self.root / relative).write_bytes(canonical_json(value))

    # --- agreement ------------------------------------------------------------

    def test_audit_matches_the_loader_on_every_shared_quantity(self):
        report = self.audit(expected_status='admitted', context_limit=10, output_reserve=4)
        self.assertEqual(report['examples'], 1)
        self.assertEqual(report['input_tokens'], 3)
        self.assertEqual(report['supervised_tokens'], 1)
        self.assertEqual(report['unique_tasks'], 1)
        self.assertEqual(report['repository_groups'], 1)
        self.assertEqual(report['split_counts'], {'train': 1, 'development': 0,
                                                  'confirmation': 0})
        self.assertEqual(report['max_input_tokens'], 3)
        self.assertEqual(report['min_context_margin'], 3)
        self.assertTrue(report['training_admitted'])
        self.assertEqual(report['vocab_size'], 8)
        self.assertEqual(report['pad_token_id'], 0)
        for gate in GATES:
            self.assertTrue(report['gates'][gate]['resolved'])
            self.assertEqual(report['gates'][gate]['evidence_documents'], 1)
        corpus = IndexedCorpus(self.root, self.root / 'corpus.json',
                               expected_manifest_sha256=self.manifest_sha256,
                               purpose='training')
        agreement = compare_with_loader(report, corpus.summary)
        self.assertTrue(agreement['agreed'])
        self.assertEqual(agreement['disagreements'], {})

    def test_audit_recomputes_content_identity_and_rejects_a_wrong_one(self):
        report = self.audit()
        self.assertEqual(report['corpus_content_sha256'],
                         hashlib.sha256(canonical_json({
                             key: load_json(self.root / 'corpus.json')[key]
                             for key in ('schema_version', 'tokenizer_assets',
                                         'max_length', 'examples')})).hexdigest())
        with self.assertRaisesRegex(CorpusAuditError, 'content identity differs'):
            self.audit(expected_content_sha256='d' * 64)

    def test_quarantine_corpus_audits_as_unresolved_and_not_admitted(self):
        report = audit_corpus(self.quarantine,
                              expected_manifest_sha256=self.quarantine_sha256)
        self.assertEqual(report['corpus_status'], 'quarantine')
        self.assertFalse(report['training_admitted'])
        for gate in GATES:
            self.assertFalse(report['gates'][gate]['resolved'])

    def test_declared_status_and_manifest_digest_are_enforced(self):
        with self.assertRaisesRegex(CorpusAuditError, 'manifest digest differs'):
            self.audit(expected_manifest_sha256='a' * 64)
        with self.assertRaisesRegex(CorpusAuditError, 'status differs'):
            self.audit(expected_status='quarantine')

    # --- tampering the audit must catch ---------------------------------------

    def test_tampered_token_array_is_caught(self):
        record = load_json(self.root / 'corpus.json')['examples'][0]
        candidate = load_json(self.root / record['tokens']['path'])
        candidate['input_ids'] = [1, 2, 4]
        self.rewrite(record['tokens']['path'], candidate)
        with self.assertRaisesRegex(CorpusAuditError, 'Identity differs'):
            self.audit()

    def test_audit_catches_counts_that_disagree_with_the_stored_audit(self):
        # Rebuild a self-consistent corpus whose audit file understates targets.
        self.fixture.audit['supervised_tokens'] = 2
        self.fixture.write('audit.json', self.fixture.audit)
        self.fixture.record['audit'] = self.fixture.ref('audit.json')
        self.fixture.manifest['examples'] = [self.fixture.record]
        self.fixture.write('corpus.json', self.fixture.manifest)
        with self.assertRaisesRegex(CorpusAuditError,
                                   'Recomputed supervised_tokens differs'):
            audit_corpus(self.quarantine, expected_manifest_sha256=file_record(
                self.quarantine / 'corpus.json')['sha256'])

    def test_audit_catches_a_label_that_is_not_its_own_input_token(self):
        # A fully self-consistent corpus: the audit file binds and agrees with a
        # token candidate whose final label is a foreign token.
        ident = {'sha256': 'a' * 64, 'size_bytes': 1}
        candidate = {'schema_version': 1, 'input_ids': [1, 2, 3],
                     'labels': [-100, -100, 9], 'vocab_size': 8, 'pad_token_id': 0,
                     'training_approved': False, 'history': ident, 'tools': ident}
        self.fixture.write('tokens.json', candidate)
        self.fixture.audit.update(
            token_candidate=file_record(self.quarantine / 'tokens.json'),
            input_sha256=self.fixture.hash(candidate['input_ids']),
            labels_sha256=self.fixture.hash(candidate['labels']))
        self.fixture.write('audit.json', self.fixture.audit)
        self.fixture.record['tokens'] = self.fixture.ref('tokens.json')
        self.fixture.record['audit'] = self.fixture.ref('audit.json')
        self.fixture.manifest['examples'] = [self.fixture.record]
        self.fixture.write('corpus.json', self.fixture.manifest)
        with self.assertRaisesRegex(CorpusAuditError, 'neither the ignore index'):
            audit_corpus(self.quarantine, expected_manifest_sha256=file_record(
                self.quarantine / 'corpus.json')['sha256'])

    def second_example(self, **overrides):
        """A distinct example with its own non-aliasing files and token sequence."""
        candidate = load_json(self.quarantine / 'tokens.json')
        candidate['input_ids'] = [1, 2, 4]
        candidate['labels'] = [-100, -100, 4]
        self.fixture.write('tokens2.json', candidate)
        self.fixture.write('audit2.json', dict(
            self.fixture.audit,
            token_candidate=file_record(self.quarantine / 'tokens2.json'),
            input_sha256=self.fixture.hash(candidate['input_ids']),
            labels_sha256=self.fixture.hash(candidate['labels'])))
        row = dict(self.fixture.record, example_id='trace2',
                   tokens=self.fixture.ref('tokens2.json'),
                   audit=self.fixture.ref('audit2.json'))
        row.update(overrides)
        return row

    def test_audit_catches_cross_split_leakage(self):
        self.fixture.manifest['examples'] = [self.fixture.record,
                                             self.second_example(split='confirmation')]
        self.fixture.write('corpus.json', self.fixture.manifest)
        with self.assertRaisesRegex(CorpusAuditError, 'Cross-split leakage'):
            audit_corpus(self.quarantine, expected_manifest_sha256=file_record(
                self.quarantine / 'corpus.json')['sha256'])

    def test_audit_accepts_two_distinct_examples_in_one_split(self):
        self.fixture.manifest['examples'] = [self.fixture.record,
                                             self.second_example(task_id='repo-2',
                                                                 leakage_group='repo-2')]
        self.fixture.write('corpus.json', self.fixture.manifest)
        report = audit_corpus(self.quarantine, expected_manifest_sha256=file_record(
            self.quarantine / 'corpus.json')['sha256'])
        self.assertEqual(report['examples'], 2)
        self.assertEqual(report['unique_tasks'], 2)
        self.assertEqual(report['input_tokens'], 6)
        self.assertEqual(report['supervised_tokens'], 2)

    def test_audit_catches_a_duplicate_token_sequence(self):
        self.fixture.write('tokens2.json', load_json(self.quarantine / 'tokens.json'))
        self.fixture.write('audit2.json', dict(
            self.fixture.audit, token_candidate=file_record(self.quarantine / 'tokens2.json')))
        second = dict(self.fixture.record, example_id='trace2', task_id='repo-2',
                      leakage_group='repo-2', tokens=self.fixture.ref('tokens2.json'),
                      audit=self.fixture.ref('audit2.json'))
        self.fixture.manifest['examples'] = [self.fixture.record, second]
        self.fixture.write('corpus.json', self.fixture.manifest)
        with self.assertRaisesRegex(CorpusAuditError, 'Duplicate token sequence'):
            audit_corpus(self.quarantine, expected_manifest_sha256=file_record(
                self.quarantine / 'corpus.json')['sha256'])

    def test_audit_catches_a_token_candidate_claiming_training_approval(self):
        candidate = load_json(self.quarantine / 'tokens.json')
        candidate['training_approved'] = True
        self.fixture.write('tokens.json', candidate)
        self.fixture.record['tokens'] = self.fixture.ref('tokens.json')
        self.fixture.manifest['examples'] = [self.fixture.record]
        self.fixture.write('corpus.json', self.fixture.manifest)
        with self.assertRaisesRegex(CorpusAuditError, 'claims training approval'):
            audit_corpus(self.quarantine, expected_manifest_sha256=file_record(
                self.quarantine / 'corpus.json')['sha256'])

    def test_context_limit_rejects_an_example_that_cannot_leave_output_room(self):
        with self.assertRaisesRegex(CorpusAuditError, 'output reserve exceeds'):
            self.audit(context_limit=4, output_reserve=2)

    def test_audit_catches_a_receipt_bound_to_another_corpus(self):
        manifest = load_json(self.root / 'corpus.json')
        reference = manifest['admission']['split_isolation']
        receipt = load_json(self.root / reference['path'])
        receipt['corpus_content_sha256'] = 'f' * 64
        self.rewrite(reference['path'], receipt)
        with self.assertRaisesRegex(CorpusAuditError, 'Identity differs'):
            self.audit()

    # --- comparison and schedule coverage -------------------------------------

    def test_comparison_reports_a_disagreeing_loader_summary(self):
        report = self.audit()
        corpus = IndexedCorpus(self.root, self.root / 'corpus.json',
                               expected_manifest_sha256=self.manifest_sha256,
                               purpose='training')
        summary = dict(corpus.summary, supervised_tokens=99)
        with self.assertRaisesRegex(CorpusAuditError, 'supervised_tokens'):
            compare_with_loader(report, summary)
        summary = dict(corpus.summary, manifest={'sha256': 'b' * 64, 'size_bytes': 1})
        with self.assertRaisesRegex(CorpusAuditError, 'manifest'):
            compare_with_loader(report, summary)

    def test_schedule_coverage_requires_exact_one_to_one_cover(self):
        report = self.audit()
        rows = [{key: row[key] for key in ('example_id', 'input_tokens',
                                           'supervised_tokens')}
                for row in report['examples_detail']]
        schedule = make_schedule(rows,
                                 corpus_content_sha256=report['corpus_content_sha256'],
                                 seed=1, target_supervised_tokens=3, max_epochs=4,
                                 max_update_supervised_tokens=8)
        coverage = verify_schedule_coverage(report, schedule)
        self.assertTrue(coverage['coverage_exact'])
        self.assertEqual(coverage['scheduled_examples'], 1)
        self.assertEqual(coverage['supervised_tokens_per_epoch'], 1)
        self.assertEqual(coverage['declared_epoch_allowance'], 4)
        self.assertEqual(coverage['repetition_factor_at_target'], 3.0)
        with self.assertRaisesRegex(CorpusAuditError, 'another corpus'):
            verify_schedule_coverage(report, {**schedule,
                                              'corpus_content_sha256': 'a' * 64})
        with self.assertRaisesRegex(CorpusAuditError, 'does not cover exactly'):
            verify_schedule_coverage(report, {**schedule, 'examples': [
                {'example_id': 'ghost', 'input_tokens': 3, 'supervised_tokens': 1}]})
        with self.assertRaisesRegex(CorpusAuditError, 'count differs'):
            verify_schedule_coverage(report, {**schedule, 'examples': [
                {'example_id': 'trace1', 'input_tokens': 3, 'supervised_tokens': 2}]})
        with self.assertRaisesRegex(CorpusAuditError, 'epoch allowance'):
            verify_schedule_coverage(report, {**schedule, 'max_epochs': 1,
                                              'target_supervised_tokens': 3})

    def test_schedule_coverage_rejects_a_repeated_example_identity(self):
        report = self.audit()
        rows = [{key: row[key] for key in ('example_id', 'input_tokens',
                                           'supervised_tokens')}
                for row in report['examples_detail']]
        schedule = make_schedule(rows,
                                 corpus_content_sha256=report['corpus_content_sha256'],
                                 seed=1, target_supervised_tokens=1, max_epochs=1,
                                 max_update_supervised_tokens=8)
        with self.assertRaisesRegex(CorpusAuditError, 'repeats an example identity'):
            verify_schedule_coverage(report, {**schedule,
                                              'examples': rows + rows})


if __name__ == '__main__':
    unittest.main()
