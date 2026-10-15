from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from zenithsync.source_capture import capture_tracked_sources


class SourceCaptureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.root / 'LICENSE').write_bytes(b'fixture notice\n')
        (self.root / 'source.py').write_bytes(b'print("fixture")\n')
        (self.root / 'link').symlink_to('source.py')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        self.commit = self.git('rev-parse', 'HEAD').decode().strip()
        self.tree = self.git('rev-parse', 'HEAD^{tree}').decode().strip()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], timeout=30)

    def capture(self, paths=None, **kwargs):
        options = {'expected_commit': self.commit, 'expected_tree': self.tree}
        options.update(kwargs)
        return capture_tracked_sources(self.root, self.base / 'export',
            ['LICENSE', 'source.py'] if paths is None else paths, **options)

    def test_exact_blobs_and_untracked_files_excluded(self):
        (self.root / 'untracked.txt').write_text('not captured')
        result = self.capture()
        self.assertEqual(result['total_bytes'], 32)
        self.assertFalse(result['training_approved'])
        self.assertEqual([r['path'] for r in result['files']], ['LICENSE', 'source.py'])
        for row in result['files']:
            self.assertEqual((self.base / 'export/source' / row['path']).read_bytes(),
                             self.git('cat-file', 'blob', row['git_blob']))
        with self.assertRaises(FileExistsError):
            self.capture()

    def test_paths_symlinks_and_missing_files_rejected(self):
        for paths in ([], ['../LICENSE'], ['/LICENSE'], ['./LICENSE'], ['a//b'],
                      ['LICENSE', 'LICENSE'], ['.git/config'], ['link'], ['absent']):
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                self.capture(paths)
            self.assertFalse((self.base / 'export').exists())

    def test_wrong_identity_and_dirty_checkout_rejected(self):
        with self.assertRaises(ValueError):
            self.capture(expected_commit='0' * 40)
        with self.assertRaises(ValueError):
            self.capture(expected_tree='0' * 40)
        (self.root / 'source.py').write_text('changed')
        with self.assertRaises(ValueError):
            self.capture()
        self.assertFalse((self.base / 'export').exists())

    def test_budget_preflight_does_not_read_blobs(self):
        real = subprocess.check_output
        calls = []
        def tracked(args, **kwargs):
            calls.append(args)
            return real(args, **kwargs)
        for limits in ({'max_file_bytes': 13}, {'max_total_bytes': 30},
                       {'max_files': 1}, {'max_files': True}):
            with self.subTest(limits=limits), patch('zenithsync.source_capture.subprocess.check_output', side_effect=tracked):
                with self.assertRaises(ValueError):
                    self.capture(**limits)
            self.assertFalse((self.base / 'export').exists())
        self.assertFalse(any('blob' in call for call in calls))

    def test_changed_snapshot_after_export_has_no_success_report(self):
        real = subprocess.check_output
        def mutate(args, **kwargs):
            result = real(args, **kwargs)
            if args[-3:-1] == ['cat-file', 'blob']:
                (self.root / 'source.py').write_text('changed during capture')
            return result
        with patch('zenithsync.source_capture.subprocess.check_output', side_effect=mutate):
            with self.assertRaises(ValueError):
                self.capture()
        self.assertFalse((self.base / 'export/report.json').exists())

    def test_corrupt_blob_rejected(self):
        real = subprocess.check_output
        def corrupt(args, **kwargs):
            result = real(args, **kwargs)
            return b'x' * len(result) if args[-3:-1] == ['cat-file', 'blob'] else result
        with patch('zenithsync.source_capture.subprocess.check_output', side_effect=corrupt):
            with self.assertRaises(ValueError):
                self.capture()
        self.assertFalse((self.base / 'export/report.json').exists())

    def test_literal_pathspec_and_exact_byte_limits(self):
        (self.root / '[special].py').write_bytes(b'abcd')
        self.git('add', '--', '[special].py')
        self.git('commit', '-qm', 'literal path fixture')
        self.commit = self.git('rev-parse', 'HEAD').decode().strip()
        self.tree = self.git('rev-parse', 'HEAD^{tree}').decode().strip()
        result = self.capture(['[special].py'], max_file_bytes=4, max_total_bytes=4)
        self.assertEqual(result['total_bytes'], 4)
        self.assertEqual((self.base / 'export/source/[special].py').read_bytes(), b'abcd')


if __name__ == '__main__':
    unittest.main()
