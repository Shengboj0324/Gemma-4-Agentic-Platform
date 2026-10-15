"""A qualified snapshot supplies the image; task-only resolutions remain usable."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_rebench_controls as runner
from zenithsync.artifacts import canonical_json, file_record


class SnapshotControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = {'instance_id': 'fixture-1', 'base_commit': 'original'}
        self.write('resolution.json', {'task': self.task})
        for name in ('scripts/run_rebench_controls.py', 'scripts/qualify_swe_rebench_evaluator.py',
                     'scripts/compare_source_snapshot.py', 'zenithsync/source_imports.py'):
            self.write(name, {'fixture': name})
        self.write('inputs/reference.patch', '')
        self.write('inputs/tests.patch', '')
        self.write('inputs/receipt.json', {
            'task': self.task, 'resolution': file_record(self.root / 'resolution.json'),
            'files': {n: file_record(self.root / 'inputs' / n)
                      for n in ('reference.patch', 'tests.patch')}})
        self.write('profile.json', {'instance_id': 'fixture-1',
            'python': '/opt/python', 'module': 'package',
            'expected_origin': '/testbed/package.py', 'test_targets': ['test_file.py']})
        self.write('snapshot/snapshot.json', {'base_commit': 'original',
            'exact_tree_preserved': True, 'snapshot_commit': 'snapshot', 'source_tree': 'tree'})
        self.write('snapshot/verification.json', {'tracked_manifest_matches': True,
            'reachable_commits': 1, 'old_commits_inaccessible': ['original']})
        self.write('snapshot/receipt.json', {'returncode': 0, 'cleanup_returncode': 0,
            'image_id': 'sha256:verified-snapshot'})
        self.write('snapshot/input-bindings.json', {})

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json(value))

    def run_controls(self, *, snapshot=True):
        args = ['controls', '--resolution', str(self.root / 'resolution.json'),
                '--inputs', str(self.root / 'inputs'), '--profile', str(self.root / 'profile.json'),
                '--output', str(self.root / 'out')]
        if snapshot:
            args += ['--snapshot', str(self.root / 'snapshot')]
        def fake_run(image, directory, **kwargs):
            directory.mkdir(parents=True)
            (directory / 'runtime.json').write_text('{}')
            return {'image_id': image}
        with patch.object(runner, 'ROOT', self.root), patch.object(
                runner, '__file__', str(self.root / 'scripts/run_rebench_controls.py')), patch(
                'sys.argv', args), patch.object(runner, 'run_image', side_effect=fake_run) as execute:
            runner.main()
            return execute

    def test_task_only_resolution_uses_verified_snapshot(self):
        execute = self.run_controls()
        self.assertEqual(execute.call_count, 2)
        for call in execute.call_args_list:
            self.assertEqual(call.args[0], 'sha256:verified-snapshot')
            self.assertIn("BASE='snapshot'", call.kwargs['probe'])
            self.assertTrue(call.kwargs['generated_grading_tests'])
            self.assertEqual(call.kwargs['entrypoint'], '/opt/python')
        self.assertFalse(json.loads((self.root / 'out/report.json').read_text())['training_approved'])

    def test_unverified_snapshot_cannot_replace_registry(self):
        self.write('snapshot/verification.json', {'tracked_manifest_matches': False,
            'reachable_commits': 1, 'old_commits_inaccessible': ['original']})
        with self.assertRaisesRegex(ValueError, 'Snapshot provenance'):
            self.run_controls()
        self.assertFalse((self.root / 'out').exists())

    def test_without_snapshot_registry_is_still_required(self):
        with self.assertRaises(KeyError):
            self.run_controls(snapshot=False)
        self.assertFalse((self.root / 'out').exists())
