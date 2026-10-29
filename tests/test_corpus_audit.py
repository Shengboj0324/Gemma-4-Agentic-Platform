"""The independent audit must re-derive the same numbers and catch tampering."""

import hashlib
import shutil
from pathlib import Path
import tempfile
import unittest
import unittest.mock

from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.corpus_admission import promote_corpus
from zenithsync.corpus_audit import (CorpusAuditError, audit_corpus,
                                     compare_with_loader, verify_loader_offers,
                                     verify_schedule_coverage)
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
        # `training_admitted` is derived, not a literal: it must follow the
        # status and the resolved gates, so check those too.
        self.assertTrue(report['training_admitted'])
        self.assertEqual(report['corpus_status'], 'admitted')
        self.assertTrue(all(report['gates'][gate]['resolved'] for gate in GATES))
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

    def test_audit_catches_an_edited_receipt_by_its_identity(self):
        # Editing a receipt without re-signing the manifest trips the identity
        # check, not the binding check. The binding check has its own test.
        manifest = load_json(self.root / 'corpus.json')
        reference = manifest['admission']['split_isolation']
        receipt = load_json(self.root / reference['path'])
        receipt['corpus_content_sha256'] = 'f' * 64
        self.rewrite(reference['path'], receipt)
        with self.assertRaisesRegex(CorpusAuditError, 'Identity differs'):
            self.audit()

    def test_a_file_swapped_between_hashing_and_parsing_is_caught(self):
        import zenithsync.corpus_audit as audit_module
        record = load_json(self.root / 'corpus.json')['examples'][0]
        target = (self.root / record['tokens']['path']).resolve()
        original = audit_module.load_json
        swapped = {'swapped': True}

        def swap_then_load(path):
            value = original(path)
            if Path(path).resolve() == target:
                Path(path).write_bytes(canonical_json(swapped))
            return value

        with unittest.mock.patch.object(audit_module, 'load_json', swap_then_load):
            with self.assertRaisesRegex(CorpusAuditError, 'changed while being read'):
                self.audit()

    def test_a_reference_declaring_an_enormous_size_is_refused(self):
        manifest = load_json(self.root / 'corpus.json')
        record = manifest['examples'][0]
        record['tokens']['identity']['size_bytes'] = 1024**4
        self.rewrite('corpus.json', manifest)
        sha256 = file_record(self.root / 'corpus.json')['sha256']
        # The aggregate ceiling fires first, as it does in the loader.
        with self.assertRaisesRegex(CorpusAuditError, 'aggregate byte ceiling'):
            audit_corpus(self.root, expected_manifest_sha256=sha256)
        # Raise the aggregate ceiling and the per-example one still refuses it.
        with self.assertRaisesRegex(CorpusAuditError, 'Declared size out of bounds'):
            audit_corpus(self.root, expected_manifest_sha256=sha256,
                         max_total_bytes=1024**5)

    def test_the_aggregate_byte_ceiling_must_be_positive(self):
        with self.assertRaisesRegex(CorpusAuditError, 'aggregate byte ceiling'):
            self.audit(max_total_bytes=0)

    # --- path containment: the audit must not bless bytes outside the tree ----

    def resign(self):
        """Re-sign receipt identities into the manifest so the chain is valid."""
        manifest = load_json(self.root / 'corpus.json')
        for reference in manifest['admission'].values():
            reference['identity'] = file_record(self.root / reference['path'])
        self.rewrite('corpus.json', manifest)
        self.manifest_sha256 = file_record(self.root / 'corpus.json')['sha256']
        return self.manifest_sha256

    def test_evidence_reached_by_traversal_outside_the_root_is_refused(self):
        planted = self.work / 'planted'
        planted.mkdir()
        gate = 'rights_and_attribution'
        receipt_path = load_json(self.root / 'corpus.json')['admission'][gate]['path']
        receipt = load_json(self.root / receipt_path)
        evidence = receipt['evidence'][0]['path']
        shutil.move(str(self.root / evidence), str(planted / 'ev.json'))
        receipt['evidence'][0]['path'] = '../planted/ev.json'
        receipt['evidence'][0]['identity'] = file_record(planted / 'ev.json')
        self.rewrite(receipt_path, receipt)
        self.resign()
        with self.assertRaisesRegex(CorpusAuditError, 'Non-canonical relative path'):
            self.audit()

    def test_a_gate_directory_replaced_by_a_symlink_is_refused(self):
        # Every declared path stays byte-identical and canonical here, so only a
        # symlink check on the whole chain can catch it.
        inside = self.root / 'admission' / 'split_isolation'
        outside = self.work / 'moved-gate'
        shutil.move(str(inside), str(outside))
        inside.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(CorpusAuditError, 'Symlinked corpus path'):
            self.audit()
        # The loader refuses the same tree, so the two layers agree.
        with self.assertRaisesRegex(ValueError, 'Symlinked corpus paths rejected'):
            IndexedCorpus(self.root, self.root / 'corpus.json',
                          expected_manifest_sha256=self.manifest_sha256,
                          purpose='training')

    def test_an_example_file_replaced_by_a_symlink_is_refused(self):
        record = load_json(self.root / 'corpus.json')['examples'][0]
        inside = self.root / record['tokens']['path']
        outside = self.work / 'moved-tokens.json'
        shutil.move(str(inside), str(outside))
        inside.symlink_to(outside)
        with self.assertRaisesRegex(CorpusAuditError, 'Symlinked corpus path'):
            self.audit()

    def test_a_symlinked_corpus_root_is_refused(self):
        link = self.work / 'root-link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(CorpusAuditError, 'must not be a symlink'):
            audit_corpus(link, expected_manifest_sha256=self.manifest_sha256)

    def test_receipt_and_evidence_ceilings_match_the_loader(self):
        from zenithsync.corpus_audit import (EVIDENCE_MAX_BYTES, MANIFEST_MAX_BYTES,
                                             RECEIPT_MAX_BYTES)
        # The loader reads receipts under 1 MiB and evidence under 16 MiB; a
        # looser ceiling here would let the audit accept what the loader refuses.
        self.assertEqual(RECEIPT_MAX_BYTES, 1024**2)
        self.assertEqual(EVIDENCE_MAX_BYTES, 16 * 1024**2)
        self.assertEqual(MANIFEST_MAX_BYTES, 16 * 1024**2)
        source = (Path(__file__).resolve().parents[1]
                  / 'zenithsync/training_corpus.py').read_text(encoding='utf-8')
        self.assertIn("_bound_file(root, reference, 1024**2)", source)
        self.assertIn("_bound_file(root, evidence, 16*1024**2)", source)

    def test_evidence_naming_a_corpus_other_than_the_reviewed_one_is_refused(self):
        # Promotion checks this binding against the quarantine manifest, which
        # the admitted tree does not otherwise carry. The receipt records it so
        # the second layer can re-derive the same check.
        manifest = load_json(self.root / 'corpus.json')
        reference = manifest['admission']['split_isolation']
        receipt = load_json(self.root / reference['path'])
        self.assertEqual(receipt['reviewed_against_manifest'],
                         file_record(self.quarantine / 'corpus.json'))
        evidence = receipt['evidence'][0]['path']
        document = load_json(self.root / evidence)
        document['corpus'] = {'sha256': 'c' * 64, 'size_bytes': 7}
        self.rewrite(evidence, document)
        receipt['evidence'][0]['identity'] = file_record(self.root / evidence)
        self.rewrite(reference['path'], receipt)
        self.resign()
        with self.assertRaisesRegex(CorpusAuditError,
                                   'names a corpus other than the one'):
            self.audit()

    def test_each_gate_report_carries_the_reviewed_manifest(self):
        report = self.audit()
        reviewed = file_record(self.quarantine / 'corpus.json')
        for gate in GATES:
            self.assertEqual(report['gates'][gate]['reviewed_against_manifest'],
                             reviewed)

    def test_a_receipt_bound_to_another_corpus_is_refused_by_the_binding_check(self):
        # Re-sign the chain so the identity check passes and the binding check
        # is the one that fires; otherwise this test proves nothing about it.
        manifest = load_json(self.root / 'corpus.json')
        reference = manifest['admission']['split_isolation']
        receipt = load_json(self.root / reference['path'])
        receipt['corpus_content_sha256'] = 'f' * 64
        self.rewrite(reference['path'], receipt)
        self.resign()
        with self.assertRaisesRegex(CorpusAuditError,
                                   'binds a different corpus content identity'):
            self.audit()

    # --- loader-offer agreement: the invariant layer two exists for -----------

    def multi_split_corpus(self):
        """Admit a 2-train / 1-development corpus with distinct token arrays."""
        rows = []
        for index, split in enumerate(('train', 'train', 'development')):
            candidate = {'schema_version': 1, 'input_ids': [1, 2, 3 + index],
                         'labels': [-100, -100, 3 + index], 'vocab_size': 8,
                         'pad_token_id': 0, 'training_approved': False,
                         'history': {'sha256': 'a' * 64, 'size_bytes': 1},
                         'tools': {'sha256': 'a' * 64, 'size_bytes': 1}}
            self.fixture.write(f'tokens{index}.json', candidate)
            self.fixture.write(f'audit{index}.json', dict(
                self.fixture.audit,
                token_candidate=file_record(self.quarantine / f'tokens{index}.json'),
                input_sha256=self.fixture.hash(candidate['input_ids']),
                labels_sha256=self.fixture.hash(candidate['labels'])))
            rows.append({'example_id': f'trace{index}', 'task_id': f'repo-{index}',
                         'repository_group': f'owner/repo{index}',
                         'leakage_group': f'repo-{index}', 'split': split,
                         'tokens': self.fixture.ref(f'tokens{index}.json'),
                         'audit': self.fixture.ref(f'audit{index}.json')})
        self.fixture.manifest['examples'] = rows
        self.fixture.write('corpus.json', self.fixture.manifest)
        documents = {}
        for gate in GATES:
            path = self.work / ('multi-' + gate + '.json')
            body = {'schema_version': 1, 'synthetic_test_only': True}
            if gate == 'task_alignment':
                body['task_reviews'] = [
                    {'task_id': row['task_id'],
                     'repository_group': row['repository_group'],
                     'decision': 'accepted', 'rationale': 'synthetic'}
                    for row in rows]
            path.write_bytes(canonical_json(body))
            documents[gate] = [path]
        destination = self.work / 'multi-admitted'
        receipt = promote_corpus(
            source_root=self.quarantine,
            source_manifest_sha256=file_record(self.quarantine / 'corpus.json')['sha256'],
            destination=destination, gate_evidence=documents, reviewer='unit-test')
        return destination, receipt['destination']['manifest']['sha256']

    def test_a_held_out_example_substituted_into_training_is_refused(self):
        import zenithsync.training_corpus as loader_module
        root, sha256 = self.multi_split_corpus()
        audit = audit_corpus(root, expected_manifest_sha256=sha256)
        self.assertEqual(audit['split_counts'],
                         {'train': 2, 'development': 1, 'confirmation': 0})
        original = loader_module._load_corpus

        def leaking(root_, manifest_path, **kwargs):
            if kwargs.get('purpose') != 'training':
                return original(root_, manifest_path, **kwargs)
            everything = original(root_, manifest_path,
                                  **{**kwargs, 'purpose': 'inspection'})
            train = [row for row in everything['examples'] if row['split'] == 'train']
            held = [row for row in everything['examples']
                    if row['split'] == 'development']
            # One-for-one substitution: the count stays right, and each example
            # still matches its own audit row on every field.
            everything['examples'] = train[:-1] + held[:1]
            everything['summary'].update(returned_examples=len(everything['examples']),
                                         purpose='training', training_admitted=True)
            return everything

        with unittest.mock.patch.object(loader_module, '_load_corpus', leaking):
            corpus = IndexedCorpus(root, root / 'corpus.json',
                                   expected_manifest_sha256=sha256, purpose='training')
            self.assertEqual(sorted(m['example_id'] for m in corpus.metadata()),
                             ['trace0', 'trace2'])
            with self.assertRaisesRegex(CorpusAuditError,
                                       'differs from the audited training set'):
                verify_loader_offers(audit, corpus, purpose='training')

    def test_a_clean_training_split_is_accepted_and_counted(self):
        root, sha256 = self.multi_split_corpus()
        audit = audit_corpus(root, expected_manifest_sha256=sha256)
        corpus = IndexedCorpus(root, root / 'corpus.json',
                               expected_manifest_sha256=sha256, purpose='training')
        self.assertEqual(verify_loader_offers(audit, corpus, purpose='training'), 2)
        inspector = IndexedCorpus(root, root / 'corpus.json',
                                  expected_manifest_sha256=sha256,
                                  purpose='inspection')
        self.assertEqual(verify_loader_offers(audit, inspector, purpose='inspection'), 3)

    def test_a_tampered_token_array_is_caught_on_refetch(self):
        root, sha256 = self.multi_split_corpus()
        audit = audit_corpus(root, expected_manifest_sha256=sha256)
        corpus = IndexedCorpus(root, root / 'corpus.json',
                               expected_manifest_sha256=sha256, purpose='training')
        # Make the audit's recorded digest disagree with the stored bytes, which
        # is what the per-example re-hash on refetch exists to notice.
        for row in audit['examples_detail']:
            if row['split'] == 'train':
                row['input_sha256'] = 'd' * 64
                break
        with self.assertRaisesRegex(CorpusAuditError, 'differs from the independent'):
            verify_loader_offers(audit, corpus, purpose='training')

    def test_an_unknown_purpose_is_refused(self):
        root, sha256 = self.multi_split_corpus()
        audit = audit_corpus(root, expected_manifest_sha256=sha256)
        corpus = IndexedCorpus(root, root / 'corpus.json',
                               expected_manifest_sha256=sha256, purpose='training')
        with self.assertRaisesRegex(CorpusAuditError, 'Unknown corpus purpose'):
            verify_loader_offers(audit, corpus, purpose='confirmation')

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
        # Each negative case is re-signed, so the intended check fires rather
        # than the identity check that now guards the whole function.
        foreign = make_schedule(rows, corpus_content_sha256='a' * 64, seed=1,
                                target_supervised_tokens=1, max_epochs=1,
                                max_update_supervised_tokens=8)
        with self.assertRaisesRegex(CorpusAuditError, 'another corpus'):
            verify_schedule_coverage(report, foreign)
        ghost = make_schedule(
            [{'example_id': 'ghost', 'input_tokens': 3, 'supervised_tokens': 1}],
            corpus_content_sha256=report['corpus_content_sha256'], seed=1,
            target_supervised_tokens=1, max_epochs=1,
            max_update_supervised_tokens=8)
        with self.assertRaisesRegex(CorpusAuditError, 'does not cover exactly'):
            verify_schedule_coverage(report, ghost)
        miscounted = make_schedule(
            [{'example_id': 'trace1', 'input_tokens': 3, 'supervised_tokens': 2}],
            corpus_content_sha256=report['corpus_content_sha256'], seed=1,
            target_supervised_tokens=1, max_epochs=1,
            max_update_supervised_tokens=8)
        with self.assertRaisesRegex(CorpusAuditError, 'count differs'):
            verify_schedule_coverage(report, miscounted)

    def test_schedule_coverage_requires_a_reproducible_schedule_identity(self):
        report = self.audit()
        rows = [{key: row[key] for key in ('example_id', 'input_tokens',
                                           'supervised_tokens')}
                for row in report['examples_detail']]
        schedule = make_schedule(rows,
                                 corpus_content_sha256=report['corpus_content_sha256'],
                                 seed=1, target_supervised_tokens=1, max_epochs=1,
                                 max_update_supervised_tokens=8)
        # A stale digest means the iterator will refuse to run this schedule, so
        # attesting its coverage would attest coverage for something unrunnable.
        with self.assertRaisesRegex(CorpusAuditError, 'identity does not match'):
            verify_schedule_coverage(report, {**schedule, 'seed': 99})
        with self.assertRaisesRegex(CorpusAuditError, 'field set differs'):
            verify_schedule_coverage(report, {key: schedule[key] for key in
                                              ('corpus_content_sha256', 'examples',
                                               'max_epochs',
                                               'target_supervised_tokens')})
        with self.assertRaisesRegex(CorpusAuditError, 'Unsupported schedule schema'):
            verify_schedule_coverage(report, {**schedule, 'schema_version': 2})
        # The iterator agrees: it refuses the same stale-digest object.
        from zenithsync.training_schedule import iter_updates
        with self.assertRaisesRegex(ValueError, 'Schedule identity changed'):
            next(iter_updates({**schedule, 'seed': 99}), None)

    def test_schedule_coverage_rejects_a_repeated_example_identity(self):
        report = self.audit()
        rows = [{key: row[key] for key in ('example_id', 'input_tokens',
                                           'supervised_tokens')}
                for row in report['examples_detail']]
        schedule = make_schedule(rows,
                                 corpus_content_sha256=report['corpus_content_sha256'],
                                 seed=1, target_supervised_tokens=1, max_epochs=1,
                                 max_update_supervised_tokens=8)
        # A duplicated identity is unreproducible, so the identity guard reports
        # it first; `make_schedule` refuses to build such a schedule at all.
        with self.assertRaisesRegex(CorpusAuditError, 'not reproducible'):
            verify_schedule_coverage(report, {**schedule,
                                              'examples': rows + rows})


if __name__ == '__main__':
    unittest.main()
