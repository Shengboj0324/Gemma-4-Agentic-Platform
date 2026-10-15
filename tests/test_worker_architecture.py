import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.run_corpus_training_worker import require_architecture_layout
from zenithsync.artifacts import file_record


class WorkerArchitectureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = self.root/'manifest.json'
        self.manifest.write_text('{}\n')
        self.output = self.root/'architecture'
        self.report = {
            'status': 'complete_tensor_layout_passed', 'gpu_used': False,
            'model_manifest': file_record(self.manifest),
            'quantized_projections': 410, 'unquantized_tensors': 779,
            'checkpoint_tensors': 2009, 'logical_model_tensors': 1189,
        }

    def invoke(self):
        return require_architecture_layout(
            self.root/'model', self.manifest,
            file_record(self.manifest)['sha256'], self.output)

    def emit_report(self, command, **kwargs):
        self.assertTrue(kwargs['check'])
        self.assertEqual(kwargs['timeout'], 120)
        self.assertEqual(kwargs['env']['CUDA_VISIBLE_DEVICES'], '')
        self.assertIn('-I', command)
        self.output.mkdir(exist_ok=True)
        (self.output/'report.json').write_text(json.dumps(self.report))

    def test_bound_report_and_gpu_hidden_child(self):
        with patch('scripts.run_corpus_training_worker.subprocess.run', side_effect=self.emit_report):
            identity = self.invoke()
        self.assertEqual(identity, file_record(self.output/'report.json'))

    def test_failure_and_timeout_do_not_use_stale_success(self):
        self.output.mkdir()
        (self.output/'report.json').write_text(json.dumps(self.report))
        for error in (subprocess.CalledProcessError(1, ['check']),
                      subprocess.TimeoutExpired(['check'], 120)):
            with self.subTest(error=type(error).__name__):
                with patch('scripts.run_corpus_training_worker.subprocess.run', side_effect=error):
                    with self.assertRaises(type(error)):
                        self.invoke()

    def test_wrong_identity_counts_or_status_rejected(self):
        original = self.report.copy()
        for key, value in [('status', 'partial'), ('gpu_used', True),
                           ('model_manifest', {'sha256': '0'*64, 'size_bytes': 3}),
                           ('quantized_projections', True), ('unquantized_tensors', 778),
                           ('checkpoint_tensors', 2008), ('logical_model_tensors', 1188)]:
            with self.subTest(key=key):
                self.report = {**original, key: value}
                with patch('scripts.run_corpus_training_worker.subprocess.run', side_effect=self.emit_report):
                    with self.assertRaises(ValueError):
                        self.invoke()


if __name__ == '__main__':
    unittest.main()
