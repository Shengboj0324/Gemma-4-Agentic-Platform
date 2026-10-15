"""Reject evaluator profile ambiguity and argument/path injection."""
import os
from unittest.mock import patch
import unittest
from scripts.run_rebench_controls import validate_profile, control_environment_prefix


class ControlProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = {'instance_id': 'stitchfix__nodebook-8',
                        'python': '/opt/conda/envs/testbed/bin/python',
                        'module': 'nodebook', 'expected_origin': '/testbed/nodebook/__init__.py',
                        'test_targets': ['tests/test_nodebookcore.py']}

    def test_architecture_must_be_explicit_and_supported(self):
        for platform in ('linux/amd64', 'linux/arm64'):
            profile = {**self.profile, 'platform': platform}
            self.assertEqual(validate_profile(profile), profile)
        for platform in (None, True, 'arm64', 'linux/amd64 --network host', [], {}):
            with self.subTest(platform=platform), self.assertRaises(ValueError):
                validate_profile({**self.profile, 'platform': platform})
        self.assertNotIn('platform', validate_profile(self.profile))

    def test_reviewed_profile_and_node_selector(self):
        self.assertEqual(validate_profile(self.profile), self.profile)
        self.profile['test_targets'] = ['tests/test_nodebookcore.py::TestExample::test_one']
        validate_profile(self.profile)

    def test_path_activation_is_explicit_and_preserves_existing_search_path(self):
        self.assertEqual(control_environment_prefix(self.profile), '')
        profile = {**self.profile, 'python_on_path': True}
        with patch.dict(os.environ, {'PATH': '/usr/bin:/bin'}):
            exec(control_environment_prefix(profile), {})
            self.assertEqual(os.environ['PATH'], '/opt/conda/envs/testbed/bin:/usr/bin:/bin')
        self.assertEqual(control_environment_prefix({**profile, 'python_on_path': False}), '')

    def test_path_activation_rejects_ambiguous_flags_and_separators(self):
        for value in (1, 'true', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_profile({**self.profile, 'python_on_path': value})
        for executable in ('/opt/bad:path/python', '/opt/bad\npath/python'):
            with self.subTest(executable=executable), self.assertRaises(ValueError):
                validate_profile({**self.profile, 'python': executable, 'python_on_path': True})

    def test_rejects_unsafe_or_ambiguous_profiles(self):
        mutations = [('module', 'nodebook; import os'), ('python', '/usr/bin/python'),
                     ('expected_origin', '/testbed/../external.py'),
                     ('test_targets', ['--override-ini=addopts=']),
                     ('test_targets', ['/tmp/tests.py']), ('test_targets', ['../tests.py']),
                     ('test_targets', ['tests.py', 'tests.py']), ('test_targets', []),
                     ('test_targets', [None]), ('test_targets', 'tests.py')]
        for key, value in mutations:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_profile({**self.profile, key: value})
        with self.assertRaises(ValueError):
            validate_profile({**self.profile, 'extra': True})

    def test_container_python_locations_and_path_activation(self):
        for executable in ('/usr/local/bin/python', '/usr/local/bin/python3',
                           '/usr/local/bin/python3.13'):
            profile = {**self.profile, 'python': executable, 'python_on_path': True}
            with self.subTest(executable=executable):
                self.assertEqual(validate_profile(profile), profile)
                with patch.dict(os.environ, {'PATH': '/usr/bin:/bin'}):
                    exec(control_environment_prefix(profile), {})
                    self.assertEqual(os.environ['PATH'], '/usr/local/bin:/usr/bin:/bin')

    def test_interpreter_paths_are_canonical_even_without_path_activation(self):
        for executable in ('/opt//python', '/opt/./python', '/opt/../python',
                           '/opt/python/', '/opt/bad:path/python', '/opt/a\npython',
                           '/usr/local/bin/python-helper', '/usr/local/bin/sh',
                           '/usr/local/bin/python3.13/extra', '/usr/local/bin/../python',
                           'python', None):
            with self.subTest(executable=executable), self.assertRaises(ValueError):
                validate_profile({**self.profile, 'python': executable})


if __name__ == '__main__':
    unittest.main()
