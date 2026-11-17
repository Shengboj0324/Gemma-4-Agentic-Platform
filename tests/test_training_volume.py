"""Storage admission parsing; no claim of a real mounted volume from mocks."""

import json
from pathlib import Path
from subprocess import CompletedProcess
import tempfile
import unittest
from unittest.mock import patch

from scripts.run_p1_training_worker import EPHEMERAL_ACK, require_volume


class TrainingVolumeTests(unittest.TestCase):
    def test_exact_mount_and_child_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            row = {'target': str(root), 'fstype': 'nfs4', 'source': 'test-volume'}
            result = CompletedProcess([], 0, json.dumps({'filesystems': [row]}), '')
            with patch('scripts.run_p1_training_worker.subprocess.run', return_value=result):
                self.assertEqual(require_volume(root / 'future/output', root), row)

    def test_wrong_mount_and_ephemeral_filesystems(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for target, kind in [(str(root), 'overlay'), (str(root), 'tmpfs'), ('/', 'ext4')]:
                result = CompletedProcess([], 0, json.dumps({'filesystems': [
                    {'target': target, 'fstype': kind, 'source': 'test'}]}), '')
                with patch('scripts.run_p1_training_worker.subprocess.run', return_value=result):
                    with self.assertRaises(ValueError):
                        require_volume(root / 'output', root)

    def test_ephemeral_only_with_explicit_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            row = {'target': str(root), 'fstype': 'overlay', 'source': 'overlay'}
            result = CompletedProcess([], 0, json.dumps({'filesystems': [row]}), '')
            with patch('scripts.run_p1_training_worker.subprocess.run', return_value=result):
                with self.assertRaisesRegex(ValueError, 'Ephemeral'):
                    require_volume(root / 'output', root)
                self.assertEqual(require_volume(root / 'output', root, allow_ephemeral=True),
                                 {**row, 'ephemeral_acknowledged': EPHEMERAL_ACK})
            wrong = CompletedProcess([], 0, json.dumps({'filesystems': [{**row, 'target': '/elsewhere'}]}), '')
            with patch('scripts.run_p1_training_worker.subprocess.run', return_value=wrong):
                with self.assertRaisesRegex(ValueError, 'mounted filesystem'):
                    require_volume(root / 'output', root, allow_ephemeral=True)

    def test_flag_accepts_only_the_acknowledgement_and_passes_through(self):
        from scripts.run_corpus_training_worker import parser
        base = ['--model', 'm', '--manifest', 'm', '--corpus', 'c', '--schedule', 's', '--config', 'c', '--output', 'o',
                '--manifest-sha256', 'a', '--corpus-sha256', 'a', '--schedule-sha256', 'a', '--config-sha256', 'a']
        self.assertIsNone(parser().parse_args(base).ephemeral_volume_ack)
        self.assertEqual(parser().parse_args(base + ['--ephemeral-volume-ack', EPHEMERAL_ACK]).ephemeral_volume_ack,
                         EPHEMERAL_ACK)
        with self.assertRaises(SystemExit):
            parser().parse_args(base + ['--ephemeral-volume-ack', 'yes'])

    def test_symlink_escape_rejected_before_probe(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            (root / 'escape').symlink_to(outside, target_is_directory=True)
            with patch('scripts.run_p1_training_worker.subprocess.run') as probe:
                with self.assertRaisesRegex(ValueError, 'escapes'):
                    require_volume(root / 'escape/output', root)
                probe.assert_not_called()
