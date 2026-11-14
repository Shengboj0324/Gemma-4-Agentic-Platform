"""A network filesystem that publishes ctime late must not fail a stable read.

Runpod's MooseFS volume moved a just-written checkpoint's ctime by one second
while it was being hashed, which failed update 3 of the first epoch run.
"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zenithsync import artifacts
from zenithsync.artifacts import CtimeOnlyChange, file_record


class Shifted:
    """A stat result with selected *_ns fields moved forward."""

    def __init__(self, real, **shift):
        self._real, self._shift = real, shift

    def __getattr__(self, name):
        return getattr(self._real, name) + self._shift.get(name, 0)


def fstat_shifting(field, times):
    """os.fstat whose post-read call (every second call) is shifted `times` times."""
    real = os.fstat
    state = {'calls': 0, 'shifted': 0}

    def fake(descriptor):
        state['calls'] += 1
        result = real(descriptor)
        if state['calls'] % 2 == 0 and state['shifted'] < times:
            state['shifted'] += 1
            return Shifted(result, **{field: 1_000_000_000})
        return result
    return fake, state


class CtimeSettleTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name).resolve() / 'blob.bin'
        self.path.write_bytes(b'checkpoint bytes' * 1000)
        self.expected = file_record(self.path)

    def test_ctime_moving_once_is_retried_and_succeeds(self):
        fake, state = fstat_shifting('st_ctime_ns', times=1)
        with patch('zenithsync.artifacts.os.fstat', side_effect=fake), \
                patch('time.sleep') as sleep:
            self.assertEqual(file_record(self.path), self.expected)
        self.assertEqual(state['shifted'], 1)
        sleep.assert_called_once_with(artifacts.CTIME_SETTLE_SECONDS)

    def test_ctime_that_never_settles_still_fails(self):
        fake, _ = fstat_shifting('st_ctime_ns', times=99)
        with patch('zenithsync.artifacts.os.fstat', side_effect=fake), patch('time.sleep') as sleep:
            with self.assertRaises(CtimeOnlyChange):
                file_record(self.path)
        self.assertEqual(sleep.call_count, artifacts.CTIME_SETTLE_ATTEMPTS - 1)

    def test_mtime_or_size_change_fails_without_retry(self):
        for field in ('st_mtime_ns', 'st_size'):
            fake, _ = fstat_shifting(field, times=1)
            with patch('zenithsync.artifacts.os.fstat', side_effect=fake), patch('time.sleep') as sleep:
                with self.assertRaises(ValueError) as caught:
                    file_record(self.path)
            self.assertNotIsInstance(caught.exception, CtimeOnlyChange, field)
            sleep.assert_not_called()


class CheckpointCtimeTests(unittest.TestCase):
    def setUp(self):
        try:
            import torch  # noqa: F401
        except ImportError:
            self.skipTest('torch required')
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()

    def test_load_checkpoint_retries_ctime_only_and_rejects_mtime(self):
        import torch
        from zenithsync.checkpoint_storage import load_checkpoint, save_checkpoint
        path = self.root / 'update-00000001.pt'
        identity = save_checkpoint(path, {'value': torch.arange(4)}, max_bytes=1024**2)
        fake, state = fstat_shifting('st_ctime_ns', times=1)
        with patch('zenithsync.checkpoint_storage.os.fstat', side_effect=fake), patch('time.sleep'):
            payload = load_checkpoint(path, expected_identity=identity, max_bytes=1024**2)
        self.assertTrue(torch.equal(payload['value'], torch.arange(4)))
        self.assertEqual(state['shifted'], 1)
        fake, _ = fstat_shifting('st_mtime_ns', times=1)
        with patch('zenithsync.checkpoint_storage.os.fstat', side_effect=fake), patch('time.sleep') as sleep:
            with self.assertRaisesRegex(ValueError, 'changed while reading'):
                load_checkpoint(path, expected_identity=identity, max_bytes=1024**2)
        sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
