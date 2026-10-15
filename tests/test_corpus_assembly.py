"""Assembly must preserve validation while avoiding corpus-wide token retention."""
from contextlib import redirect_stdout
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import assemble_training_corpus as assembly
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.training_corpus import load_corpus


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / 'candidate'
        self.source.mkdir()
        identity = {'sha256': 'a' * 64, 'size_bytes': 1}
        assets = {name: identity for name in (
            'chat_template.jinja', 'tokenizer.json', 'tokenizer_config.json')}
        tokens = dict(schema_version=1, input_ids=[1, 2, 3],
                      labels=[-100, -100, 3], vocab_size=8, pad_token_id=0,
                      history=identity, tools=identity, training_approved=False)
        (self.source / 'tokens.json').write_bytes(canonical_json(tokens))
        self.audit = dict(token_candidate=file_record(self.source / 'tokens.json'),
                          assets=assets, truncated=False, history=identity,
                          tools=identity, input_tokens=3, supervised_tokens=1)
        for field, values in [('input', tokens['input_ids']), ('labels', tokens['labels'])]:
            self.audit[field + '_sha256'] = hashlib.sha256(canonical_json(values)).hexdigest()
        self.write_audit()
        selection = [dict(example_id='trace', task_id='repo-1',
                          repository_group='owner/repo', leakage_group='repo-1',
                          split='train', candidate_directory='candidate')]
        (self.root / 'selection.json').write_bytes(canonical_json(selection))

    def write_audit(self):
        (self.source / 'report.json').write_bytes(canonical_json(self.audit))

    def run_assembly(self, *extra):
        argv = ['assemble', '--selection', str(self.root / 'selection.json'),
                '--directory', str(self.root / 'corpus'), '--output', str(self.root / 'output'),
                '--max-bytes', '1000000', *extra]
        with patch.object(assembly, 'ROOT', self.root), patch('sys.argv', argv), redirect_stdout(io.StringIO()):
            assembly.main()

    def test_indexed_validation_matches_materialized_summary(self):
        with patch.object(assembly, 'IndexedCorpus', wraps=assembly.IndexedCorpus) as reader:
            self.run_assembly()
        self.assertEqual(reader.call_args.kwargs['purpose'], 'inspection')
        root = self.root / 'corpus'
        manifest = root / 'corpus.json'
        loaded = load_corpus(root, manifest, expected_manifest_sha256=file_record(manifest)['sha256'])
        self.assertEqual(load_json(self.root / 'output/receipt.json')['summary'], loaded['summary'])
        with self.assertRaisesRegex(ValueError, 'Quarantine'):
            load_corpus(root, manifest, expected_manifest_sha256=file_record(manifest)['sha256'], purpose='training')

    def test_invalid_audit_produces_no_success_receipt(self):
        self.audit['supervised_tokens'] = 2
        self.write_audit()
        with self.assertRaisesRegex(ValueError, 'accounting'):
            self.run_assembly()
        self.assertFalse((self.root / 'output/receipt.json').exists())

    def test_per_file_limit_rejects_before_copy(self):
        with self.assertRaisesRegex(ValueError, 'Example file'):
            self.run_assembly('--max-example-bytes', '1')
        self.assertEqual(list((self.root / 'corpus').rglob('tokens.json')), [])

    def test_aggregate_limit_rejects_before_copy(self):
        with self.assertRaisesRegex(ValueError, 'corpus byte budget'):
            self.run_assembly('--max-bytes', '1')
        self.assertEqual(list((self.root / 'corpus').rglob('tokens.json')), [])

    def test_nonpositive_budget_creates_no_output(self):
        with redirect_stdout(io.StringIO()), patch('sys.stderr', new_callable=io.StringIO):
            with self.assertRaises(SystemExit):
                self.run_assembly('--max-example-bytes', '0')
        self.assertFalse((self.root / 'corpus').exists())
        self.assertFalse((self.root / 'output').exists())
