import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.presign_fetch_bundle import build_script


class FetchScriptTests(unittest.TestCase):
    def test_script_checks_every_size_and_quotes_paths(self):
        manifest = {'files': [{'path': 'a b/c.txt', 'sha256': '1' * 64, 'size_bytes': 3},
                              {'path': 'd.txt', 'sha256': '2' * 64, 'size_bytes': 0}]}
        script = build_script([('data', manifest, '/mnt/data/x')], lambda d: f'https://e/{d}?sig=1&x=2')
        self.assertIn("'/mnt/data/x/a b/c.txt'", script)
        self.assertIn("'https://e/" + '1' * 64 + "?sig=1&x=2'", script)
        self.assertEqual(script.count('test "$(stat -c %s'), 2)
        self.assertTrue(script.startswith('#!/bin/sh\nset -e\n'))
        self.assertTrue(script.rstrip().endswith('echo FETCH_DONE'))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fetch.sh'
            path.write_text(script)
            self.assertEqual(subprocess.run(['sh', '-n', str(path)]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
