import tempfile
import unittest
from pathlib import Path

from zenithsync.artifacts import canonical_json, file_record, inventory
from zenithsync.transfer_evidence import record_transfer_verification


class TransferEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.original = self.root / 'original'
        self.restored = self.root / 'restored'
        for directory in (self.original, self.restored):
            directory.mkdir()
            (directory / 'restore-receipt.json').write_bytes(b'original corpus receipt\n')
        self.manifest = self.root / 'manifest.json'
        self.manifest.write_bytes(canonical_json(inventory(
            self.original, kind='candidate', source='synthetic-test', revision='1')))
        for operation in ('publish', 'restore'):
            (self.root / (operation + '.json')).write_bytes(canonical_json({
                'operation': operation, 'status': 'verified',
                'manifest_file': file_record(self.manifest)}))

    def record(self, output=None):
        return record_transfer_verification(
            original=self.original, restored=self.restored, manifest=self.manifest,
            publish_receipt=self.root / 'publish.json',
            restore_receipt=self.root / 'restore.json',
            output=output if output is not None else self.root / 'evidence')

    def test_receipt_named_artifact_member_is_preserved(self):
        before = file_record(self.original / 'restore-receipt.json')
        report = self.record()
        self.assertEqual(report['verified_files_per_tree'], 1)
        self.assertEqual(file_record(self.original / 'restore-receipt.json'), before)
        self.assertEqual(file_record(self.restored / 'restore-receipt.json'), before)
        self.assertEqual(file_record(self.root / 'evidence/restore-receipt.json'),
                         file_record(self.root / 'restore.json'))

    def test_nested_equal_and_ancestor_outputs_rejected(self):
        for directory in (self.original, self.restored):
            for target in (directory, directory / 'metadata', directory.parent):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    self.record(target)
            self.assertFalse((directory / 'metadata').exists())

    def test_symlink_alias_into_artifact_rejected(self):
        alias = self.root / 'alias'
        alias.symlink_to(self.original, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.record(alias / 'metadata')
        self.assertFalse((self.original / 'metadata').exists())

    def test_corrupt_restored_member_cannot_emit_verification(self):
        (self.restored / 'restore-receipt.json').write_bytes(b'overwritten')
        with self.assertRaises(ValueError):
            self.record()
        self.assertFalse((self.root / 'evidence').exists())

    def test_wrong_receipt_manifest_or_operation_rejected(self):
        path = self.root / 'restore.json'
        for receipt in ({'operation': 'publish', 'status': 'verified',
                         'manifest_file': file_record(self.manifest)},
                        {'operation': 'restore', 'status': 'verified',
                         'manifest_file': {'sha256': '0' * 64, 'size_bytes': 1}},
                        {'operation': 'restore', 'status': 'failed',
                         'manifest_file': file_record(self.manifest)}):
            path.write_bytes(canonical_json(receipt))
            with self.assertRaises(ValueError):
                self.record()
            self.assertFalse((self.root / 'evidence').exists())

    def test_existing_output_is_never_overwritten(self):
        self.record()
        before = file_record(self.root / 'evidence/verification.json')
        with self.assertRaises(FileExistsError):
            self.record()
        self.assertEqual(file_record(self.root / 'evidence/verification.json'), before)

    def test_original_cannot_masquerade_as_restored_tree(self):
        alias = self.root / 'restore-alias'
        alias.symlink_to(self.original, target_is_directory=True)
        self.restored = alias
        with self.assertRaises(ValueError):
            self.record()
        self.assertFalse((self.root / 'evidence').exists())
