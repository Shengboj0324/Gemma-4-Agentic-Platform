"""Rooted pytest mapping preserves argv and normal exit without shell expansion."""
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from scripts.replay_source_teacher import adapt_source_local_command


class SourcePytestPathTests(unittest.TestCase):
    def test_nested_file_and_directory(self):
        for command in ('python -m pytest hardware/tests/test_benchmark_mem.py -v',
                        'python -m pytest tests/ -v', 'python -m pytest tests/unit/'):
            self.assertEqual(adapt_source_local_command(command), 'cd /workspace && ' + command)

    def test_ambiguous_or_expanding_paths_not_adapted(self):
        for path in ('../tests/', '/tests/', 'tests//unit/', 'tests/../unit/',
                     'tests/*', 'tests/$(id).py', 'tests/`id`.py', 'tests/a.py;true',
                     'tests/a.py && true', '-x', 'tests/a.py::case', 'tests/./a.py'):
            with self.subTest(path=path):
                self.assertIsNone(adapt_source_local_command('python -m pytest ' + path))

    def test_real_shell_argv_cwd_and_nonzero_status_preserved(self):
        # A harmless executable records arguments; no source dataset command runs.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fake = root / 'python'
            fake.write_text('#!/bin/sh\n' + 'printf "%s\\n" "$PWD" "$@"\nexit 7\n')
            fake.chmod(0o755)
            command = 'python -m pytest tests/unit/test_case.py -v'
            mapped = adapt_source_local_command(command)
            env = {**os.environ, 'PATH': str(root) + os.pathsep + os.environ.get('PATH', '')}
            original = subprocess.run(['/bin/sh', '-c', command], cwd=root, env=env, capture_output=True)
            adapted = subprocess.run(['/bin/sh', '-c', mapped.replace('/workspace', shlex.quote(str(root)), 1)],
                                     cwd='/', env=env, capture_output=True)
            self.assertEqual(original.returncode, 7)
            self.assertEqual((adapted.returncode, adapted.stdout, adapted.stderr),
                             (original.returncode, original.stdout, original.stderr))


if __name__ == '__main__':
    unittest.main()
