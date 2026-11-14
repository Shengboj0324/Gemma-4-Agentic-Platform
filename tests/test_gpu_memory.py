import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from zenithsync.gpu_memory import DeviceMemoryMonitor, parse_memory_csv


class GPUMemoryTests(unittest.TestCase):
    def test_parse_units_and_rejections(self):
        parsed = parse_memory_csv('GPU-abcd-1234, 7, 80\n')
        self.assertEqual(parsed['GPU-abcd-1234']['used_bytes'], 7 * 1024**2)
        for value in ['', 'GPU-ab, N/A, 80', 'GPU-ab, 81, 80', 'GPU-ab, 0, 0',
                      'GPU-ab, -1, 80', 'GPU-ab, 1.5, 80', 'GPU-ab, 1, 80\nGPU-ab, 1, 80']:
            with self.assertRaises(ValueError):
                parse_memory_csv(value)

    def test_initial_and_final_measurements_saved(self):
        first = parse_memory_csv('GPU-ab, 7, 80')
        last = parse_memory_csv('GPU-ab, 8, 80')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'memory.jsonl'
            with patch('zenithsync.gpu_memory.read_device_memory', side_effect=[first, last]):
                with DeviceMemoryMonitor(path) as monitor:
                    with self.assertRaises(RuntimeError):
                        monitor.summary()
            self.assertEqual(monitor.summary()['sampled_max_used_bytes']['GPU-ab'], 8 * 1024**2)
            records = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(records), 2)
            self.assertLessEqual(records[0]['elapsed_seconds'], records[1]['elapsed_seconds'])

    def test_final_read_failure_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'memory.jsonl'
            with patch('zenithsync.gpu_memory.read_device_memory', side_effect=[
                    parse_memory_csv('GPU-ab, 7, 80'), OSError('reader failed')]):
                with self.assertRaisesRegex(RuntimeError, 'incomplete'):
                    with DeviceMemoryMonitor(path):
                        pass
            self.assertEqual(len(path.read_text().splitlines()), 1)

    def test_worker_exception_preserved_on_reader_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('zenithsync.gpu_memory.read_device_memory', side_effect=[
                    parse_memory_csv('GPU-ab, 7, 80'), OSError('reader failed')]):
                with self.assertRaisesRegex(ValueError, 'worker failed'):
                    with DeviceMemoryMonitor(Path(directory) / 'memory.jsonl'):
                        raise ValueError('worker failed')

    def test_identity_change_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('zenithsync.gpu_memory.read_device_memory', side_effect=[
                    parse_memory_csv('GPU-ab, 7, 80'), parse_memory_csv('GPU-cd, 7, 80')]):
                with self.assertRaises(RuntimeError):
                    with DeviceMemoryMonitor(Path(directory) / 'memory.jsonl'):
                        pass

    def test_background_reader_failure_propagates(self):
        called = threading.Event()
        calls = 0
        def reader():
            nonlocal calls
            calls += 1
            if calls > 1:
                called.set()
                raise OSError('periodic failure')
            return parse_memory_csv('GPU-ab, 7, 80')
        with tempfile.TemporaryDirectory() as directory:
            with patch('zenithsync.gpu_memory.read_device_memory', side_effect=reader):
                with self.assertRaisesRegex(RuntimeError, 'incomplete'):
                    with DeviceMemoryMonitor(Path(directory) / 'memory.jsonl'):
                        self.assertTrue(called.wait(3), 'Periodic reader was never invoked')

    def test_transient_background_failures_are_counted_not_fatal(self):
        # One slow nvidia-smi once stopped all sampling for the rest of a run.
        import subprocess
        good = parse_memory_csv('GPU-ab, 7, 80')
        outcomes = [good, subprocess.TimeoutExpired('nvidia-smi', 5),
                    ValueError('Unavailable or malformed GPU memory measurement'),
                    parse_memory_csv('GPU-ab, 9, 80')]
        done = threading.Event()
        def reader():
            if outcomes:
                value = outcomes.pop(0)
                if not outcomes:
                    done.set()
                if isinstance(value, BaseException):
                    raise value
                return value
            return parse_memory_csv('GPU-ab, 8, 80')
        with tempfile.TemporaryDirectory() as directory:
            with patch('zenithsync.gpu_memory.read_device_memory', side_effect=reader):
                with DeviceMemoryMonitor(Path(directory) / 'memory.jsonl') as monitor:
                    self.assertTrue(done.wait(6), 'background reads did not reach the recovery')
            summary = monitor.summary()
        self.assertEqual(summary['failed_reads'], 2)
        self.assertEqual(summary['max_consecutive_failed_reads'], 2)
        self.assertEqual(summary['failed_read_types'], {'TimeoutExpired': 1, 'ValueError': 1})
        self.assertEqual(summary['sampled_max_used_bytes']['GPU-ab'], 9 * 1024**2)

    def test_persistent_background_failure_is_fatal_before_exit(self):
        failures = threading.Event()
        calls = 0
        def reader():
            nonlocal calls
            calls += 1
            if calls == 1:
                return parse_memory_csv('GPU-ab, 7, 80')
            if calls >= 4:
                failures.set()
            raise OSError('reader gone')
        with tempfile.TemporaryDirectory() as directory:
            with patch('zenithsync.gpu_memory.read_device_memory', side_effect=reader):
                monitor = DeviceMemoryMonitor(Path(directory) / 'memory.jsonl', max_consecutive_failures=3)
                with self.assertRaisesRegex(RuntimeError, 'incomplete') as caught:
                    with monitor:
                        self.assertTrue(failures.wait(8))
                        monitor._thread.join(5)
                self.assertIn('persistently', str(caught.exception.__cause__))

    def test_failure_tolerance_must_be_a_positive_integer(self):
        for value in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                DeviceMemoryMonitor(Path('unused.jsonl'), max_consecutive_failures=value)

