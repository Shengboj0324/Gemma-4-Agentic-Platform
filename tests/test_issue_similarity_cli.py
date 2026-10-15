import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1]/'scripts/audit_issue_similarity.py'


class IssueSimilarityCliTests(unittest.TestCase):
    def invoke(self, root, payload, extra=()):
        source, output = root/'issues.json', root/'output'
        source.write_bytes(payload)
        result = subprocess.run([sys.executable, str(SCRIPT), '--issues', str(source),
            '--sha256', hashlib.sha256(payload).hexdigest(), '--size-bytes', str(len(payload)),
            '--output', str(output), *extra], capture_output=True, text=True, timeout=30)
        return result, output

    def test_real_cli_preserves_identity_and_exact_threshold(self):
        payload = b'[{"task_id":"a","issue":"x y"},{"task_id":"b","issue":"x z"}]'
        with tempfile.TemporaryDirectory() as temporary:
            result, output = self.invoke(Path(temporary), payload,
                ['--shingle-width', '1', '--jaccard', '1/3', '--containment', '1'])
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((output/'report.json').read_text())
            self.assertEqual(report['input']['sha256'], hashlib.sha256(payload).hexdigest())
            self.assertEqual(report['flagged_pairs'][0]['jaccard'], [1, 3])
            self.assertFalse(report['training_approved'])

    def test_invalid_inputs_never_create_success_output(self):
        cases = [
            (b'[{"task_id":"a","issue":"x","issue":"y"}]', []),
            (b'[{"task_id":"a","issue":NaN}]', []),
            (b'[{"task_id":"a","issue":"x"}]', ['--sha256', '0'*64]),
            (b'[{"task_id":"a","issue":"x"}]', ['--max-bytes', '1']),
            (b'[{"task_id":"a","issue":"x"}]', ['--jaccard', '0']),
        ]
        for payload, extra in cases:
            with self.subTest(extra=extra, payload=payload), tempfile.TemporaryDirectory() as temporary:
                result, output = self.invoke(Path(temporary), payload, extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
