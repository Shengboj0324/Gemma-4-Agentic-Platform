"""Execution parity and boundary checks for repository subdirectory scripts."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.replay_source_teacher import adapt_source_subdirectory_script, preflight


class SourceSubdirectoryCommandsTests(unittest.TestCase):
    def test_execution_parity_preserves_working_directory_and_failure(self):
        prefix = '/workspace/example__repo__1'
        original = 'cd ' + prefix + '/tests && ./run_all.sh'
        mapped = adapt_source_subdirectory_script(original, prefix)
        self.assertEqual(mapped, 'cd /workspace/tests && ./run_all.sh')
        with tempfile.TemporaryDirectory() as directory:
            tests = Path(directory)/'tests'
            tests.mkdir()
            (tests/'marker').write_text('correct-directory\n')
            script = tests/'run_all.sh'
            script.write_text('#!/bin/sh\ncat marker\nexit 7\n')
            script.chmod(0o700)
            before = subprocess.run(['/bin/sh', '-c', original.replace(prefix, directory, 1)],
                                    capture_output=True, timeout=5)
            after = subprocess.run(['/bin/sh', '-c', mapped.replace('/workspace', directory, 1)],
                                   capture_output=True, timeout=5)
            self.assertEqual((before.returncode, before.stdout, before.stderr),
                             (after.returncode, after.stdout, after.stderr))
            self.assertEqual(after.returncode, 7)
            self.assertEqual(after.stdout, b'correct-directory\n')

    def test_preflight_retains_source_timeout(self):
        args = {'command': 'cd /workspace/example__repo__1/tests && ./run_all.sh', 'timeout': 30}
        result = preflight([{'tool_calls': [{'function': {'name': 'execute_bash', 'arguments': args}}]}],
                           '/workspace/example__repo__1')
        self.assertEqual(result, [{'index': 0, 'kind': 'shell',
                                  'command': 'cd /workspace/tests && ./run_all.sh',
                                  'source_timeout_seconds': 30}])

    def test_rejects_nonliteral_or_nonlocal_commands(self):
        prefix = '/workspace/example__repo__1'
        for command in [
            'cd /tmp/tests && ./run_all.sh',
            'cd ' + prefix + 'extra/tests && ./run_all.sh',
            'cd ' + prefix + '/tests && ../run_all.sh',
            'cd ' + prefix + '/tests && ./run_all.sh --flag',
            'cd ' + prefix + '/tests && ./run_all.sh; pwd',
            'cd ' + prefix + '/tests && ./run_all.sh\n',
            'cd ' + prefix + '/tests && ./$(pwd).sh',
        ]:
            with self.subTest(command=command):
                self.assertIsNone(adapt_source_subdirectory_script(command, prefix))
        for path in ('tests/../other', 'tests//other', '.git/hooks'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                adapt_source_subdirectory_script('cd ' + prefix + '/' + path + ' && ./run_all.sh', prefix)


if __name__ == '__main__':
    unittest.main()
