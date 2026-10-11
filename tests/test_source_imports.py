"""Check import-root boundary validation and execution-profile agreement."""
import unittest
from zenithsync.source_imports import source_pythonpath
from scripts.run_rebench_controls import validate_profile as control_profile
from scripts.replay_source_teacher import validate_profile as replay_profile


class SourceImportTests(unittest.TestCase):
    def test_both_runtimes_map_the_same_relative_directory(self):
        for root in ('src', 'python/packages', 'package_2/src-lib'):
            self.assertEqual(source_pythonpath(root, '/workspace'), '/workspace/' + root)
            self.assertEqual(source_pythonpath(root, '/testbed'), '/testbed/' + root)

    def test_rejects_paths_outside_one_explicit_directory(self):
        for root in ('', '.', '..', '../src', 'src/../lib', 'src//lib', '/src',
                     'src/', 'src:.', 'src:/tmp', 'src\x00', 'src\n', '.git',
                     'src/.git', 'src\\lib', 'src;pwd', None, [], 1):
            with self.subTest(root=root), self.assertRaises(ValueError):
                source_pythonpath(root, '/workspace')
        with self.assertRaises(ValueError):
            source_pythonpath('src', '/tmp')

    def test_replay_and_grader_validate_the_optional_field(self):
        replay = {'instance_id': 'example__repo-1', 'trajectory_id': '1'*8+'-'+'1'*4+'-'+'1'*4+'-'+'1'*4+'-'+'1'*12,
                  'image': 'sha256:'+'a'*64, 'base_commit': 'b'*40,
                  'source_root': '/workspace/example__repo__1', 'repo': 'example/repo', 'max_tool_calls': 40}
        control = {'instance_id': 'example__repo-1', 'python': '/opt/conda/bin/python',
                   'module': 'example', 'expected_origin': '/testbed/src/example/__init__.py',
                   'test_targets': ['tests/test_example.py']}
        for validate, profile in ((replay_profile, replay), (control_profile, control)):
            self.assertEqual(validate(profile), profile)
            self.assertEqual(validate({**profile, 'import_root': 'src'})['import_root'], 'src')
            for invalid in ('../src', '', None, '/workspace/src', 'src:/tmp'):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    validate({**profile, 'import_root': invalid})
            with self.assertRaises(ValueError):
                validate({**profile, 'import_root': 'src', 'extra': True})


if __name__ == '__main__':
    unittest.main()
