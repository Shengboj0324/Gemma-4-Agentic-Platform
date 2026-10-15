import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from zenithsync.replay_noop import identical_edit, snapshot_file, verify_rejected_noop


class NoopTests(unittest.TestCase):
    def setUp(self):
        self.arguments = {'old_str': 'target', 'new_str': 'target'}
        self.error = {'status': 'error', 'error_type': 'FileEditError',
                      'error_message': 'No changes to apply. old_string and new_string are identical.'}

    def test_identical_requires_nonempty_text(self):
        self.assertTrue(identical_edit(self.arguments))
        for value in [None, {}, {'old_str': '', 'new_str': ''},
                      {'old_str': 'x', 'new_str': 'y'}, {'old_str': 1, 'new_str': 1}]:
            self.assertFalse(identical_edit(value))

    def test_error_remains_error(self):
        state = {'occurrences': 1, 'sha256': 'a'*64}
        evidence = verify_rejected_noop(self.arguments, self.error, state, dict(state))
        self.assertTrue(evidence['native_error_preserved'])
        self.assertEqual(self.error['status'], 'error')

    def test_different_error_or_claimed_success_rejected(self):
        state = {'occurrences': 1}
        for result in [{'status': 'ok'}, {**self.error, 'error_type': 'Other'},
                       {**self.error, 'error_message': 'File missing'},
                       {**self.error, 'extra': True}]:
            with self.assertRaises(ValueError):
                verify_rejected_noop(self.arguments, result, state, state)

    def test_changes_and_nonunique_matches_rejected(self):
        for before, after in [({'occurrences': 1}, {'occurrences': 2}),
                              ({'occurrences': 0}, {'occurrences': 0}),
                              ({'occurrences': 2}, {'occurrences': 2}),
                              ({'occurrences': 1, 'stat': [1]}, {'occurrences': 1, 'stat': [2]})]:
            with self.assertRaises(ValueError):
                verify_rejected_noop(self.arguments, self.error, before, after)

    def manager(self, root):
        class Manager:
            def exec(self, container, command, timeout):
                argv = shlex.split(command)
                argv[0] = sys.executable
                argv[2] = argv[2].replace("pathlib.Path('/workspace')", 'pathlib.Path('+repr(str(root))+')')
                result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
                return SimpleNamespace(exit_code=result.returncode, stdout=result.stdout)
        return Manager()

    def test_real_snapshot_and_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); path = root/'source.py'
            path.write_text('prefix target suffix')
            manager = self.manager(root)
            before = snapshot_file(manager, 'test', 'source.py', 'target')
            after = snapshot_file(manager, 'test', 'source.py', 'target')
            verify_rejected_noop(self.arguments, self.error, before, after)
            path.write_text('different target suffix')
            with self.assertRaises(ValueError):
                verify_rejected_noop(self.arguments, self.error, before,
                                     snapshot_file(manager, 'test', 'source.py', 'target'))

    def test_missing_repeated_symlink_and_invalid_utf8_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); path = root/'source.py'; manager = self.manager(root)
            for body in [b'absent', b'target target', b'target\xff']:
                path.write_bytes(body)
                with self.assertRaises(ValueError):
                    snapshot_file(manager, 'test', 'source.py', 'target')
            path.write_text('target'); (root/'link.py').symlink_to(path)
            for name in ['link.py', 'missing.py', '../source.py', '/source.py', './source.py']:
                with self.assertRaises(ValueError):
                    snapshot_file(manager, 'test', name, 'target')

    def test_failed_execution_and_malformed_receipts_rejected(self):
        for code, output in [(1, ''), (0, json.dumps({'sha256': 'bad'}))]:
            manager = SimpleNamespace(exec=lambda *args, **kwargs: SimpleNamespace(exit_code=code, stdout=output))
            with self.assertRaises(ValueError):
                snapshot_file(manager, 'test', 'source.py', 'target')
