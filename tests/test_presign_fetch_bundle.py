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
        self.assertEqual(script.count('test "$(wc -c < '), 2)
        self.assertTrue(script.startswith('#!/bin/sh\nset -e\n'))
        self.assertTrue(script.rstrip().endswith('echo FETCH_DONE'))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fetch.sh'
            path.write_text(script)
            self.assertEqual(subprocess.run(['sh', '-n', str(path)]).returncode, 0)


    def test_parallel_fetch_runs_every_file_and_fails_on_any_bad_one(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            bin_dir = d / 'bin'
            bin_dir.mkdir()
            # Fake curl: writes the byte count named in the URL; 'bad' URLs exit 22.
            (bin_dir / 'curl').write_text('#!/bin/sh\nout=""; url=""\nwhile [ $# -gt 0 ]; do case "$1" in -o) out="$2"; shift 2;; -*) shift;; *) url="$1"; shift;; esac; done\n'
                                          'case "$url" in *bad*) exit 22;; esac\nn="${url##*/}"; head -c "$n" /dev/zero > "$out"\n')
            (bin_dir / 'curl').chmod(0o755)
            files = [{'path': f'f{i}.bin', 'sha256': str(i + 1), 'size_bytes': i + 1} for i in range(5)]
            env = {**os.environ, 'PATH': f'{bin_dir}:{os.environ["PATH"]}', 'TMPDIR': directory}
            good = build_script([('data', {'files': files}, str(d / 'out'))], lambda s: f'https://e/{s}', parallel=2)
            (d / 'good.sh').write_text(good)
            run = subprocess.run(['sh', str(d / 'good.sh')], env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('FETCH_DONE', run.stdout)
            self.assertEqual(sorted(p.stat().st_size for p in (d / 'out').iterdir()), [1, 2, 3, 4, 5])
            bad = build_script([('data', {'files': files}, str(d / 'out2'))],
                               lambda s: f'https://e/bad/{s}' if s == '3' else f'https://e/{s}', parallel=2)
            (d / 'bad.sh').write_text(bad)
            run = subprocess.run(['sh', str(d / 'bad.sh')], env=env, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertNotIn('FETCH_DONE', run.stdout)
            wrong = build_script([('data', {'files': [{'path': 'w', 'sha256': '4', 'size_bytes': 9}]}, str(d / 'o3'))],
                                 lambda s: f'https://e/{s}')
            (d / 'wrong.sh').write_text(wrong)
            self.assertNotEqual(subprocess.run(['sh', str(d / 'wrong.sh')], env=env, capture_output=True).returncode, 0)


if __name__ == '__main__':
    unittest.main()
