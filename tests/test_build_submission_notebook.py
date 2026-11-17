import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from scripts.build_submission_notebook import binary_notebook, build_zip, collect, notebook, parse_binaries


class SubmissionNotebookTests(unittest.TestCase):
    def candidate(self, root):
        (root / 'prompts').mkdir(parents=True)
        (root / 'agent.yaml').write_text('name: a\nmodel: gemma-4-31b-it-qat-w4a16-ct\n')
        (root / 'prompts' / 'system.md').write_text('Prompt with "quotes" and \\ backslash.\n')
        return root

    def test_notebook_code_rebuilds_the_identical_archive(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            files = collect(self.candidate(d / 'c'))
            archive = build_zip(files)
            digest = hashlib.sha256(archive).hexdigest()
            self.assertEqual(build_zip(files), archive)
            with zipfile.ZipFile(d / 'x.zip', 'w') as _:
                pass
            (d / 'x.zip').write_bytes(archive)
            with zipfile.ZipFile(d / 'x.zip') as z:
                self.assertEqual(z.namelist(), ['agent.yaml', 'prompts/system.md'])
            code = notebook(files, digest, 'T', 'D')['cells'][1]['source'][0]
            code = code.replace("Path('/kaggle/working/submission.zip')", f"Path({str(d / 'out.zip')!r})")
            run = subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual((d / 'out.zip').read_bytes(), archive)

    def test_binaries_symlinks_and_a_missing_root_agent_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            c = self.candidate(d / 'c')
            (c / 'adapters').mkdir()
            (c / 'adapters' / 'w.safetensors').write_bytes(b'\x00')
            with self.assertRaisesRegex(ValueError, 'text'):
                collect(c)
            (c / 'adapters' / 'w.safetensors').unlink()
            os.symlink(c / 'agent.yaml', c / 'link.yaml')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                collect(c)
            (c / 'link.yaml').unlink()
            (c / 'agent.yaml').unlink()
            with self.assertRaisesRegex(ValueError, 'agent.yaml'):
                collect(c)

    def run_binary(self, d, weights, declared):
        files = collect(self.candidate(d / 'c'))
        files['adapters/main_lora/adapter_config.json'] = '{"r": 4}'
        src = d / 'input'; src.mkdir()
        (src / 'adapter_model.safetensors').write_bytes(weights)
        book, expected = binary_notebook(files, {'adapters/main_lora/adapter_model.safetensors': declared},
                                         '/kaggle/input/ds', 'T', 'D')
        code = book['cells'][1]['source'][0]
        code = code.replace("Path('/kaggle/input/ds')", f"Path({str(src)!r})")
        code = code.replace("Path('/kaggle/working/submission.zip')", f"Path({str(d / 'out.zip')!r})")
        return subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, text=True), expected

    def test_dataset_route_writes_and_verifies_every_member(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            weights = os.urandom(3 << 20)
            run, expected = self.run_binary(d, weights, hashlib.sha256(weights).hexdigest())
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('members verified 4', run.stdout)
            with zipfile.ZipFile(d / 'out.zip') as z:
                self.assertEqual(sorted(z.namelist()), sorted(expected))
                self.assertEqual(z.read('adapters/main_lora/adapter_model.safetensors'), weights)
                self.assertEqual(z.getinfo('adapters/main_lora/adapter_model.safetensors').compress_type, zipfile.ZIP_STORED)
                self.assertEqual(z.read('prompts/system.md').decode(), 'Prompt with "quotes" and \\ backslash.\n')

    def test_dataset_route_refuses_a_different_binary(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            run, _ = self.run_binary(d, b'tampered', hashlib.sha256(b'original').hexdigest())
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('differs from the trained artifact', run.stderr)
            self.assertFalse((d / 'out.zip').exists())

    def test_binary_arguments_are_validated(self):
        good = 'a' * 64
        self.assertEqual(parse_binaries([f'adapters/x/w.safetensors={good}']), {'adapters/x/w.safetensors': good})
        for bad in (['w.bin=xyz'], ['/abs/w.bin=' + good], ['../w.bin=' + good], ['w.bin=' + 'A' * 64],
                    ['a/w.bin=' + good, 'b/w.bin=' + good], ['w.bin=' + good, 'w.bin=' + good]):
            with self.assertRaises(ValueError):
                parse_binaries(bad)


if __name__ == '__main__':
    unittest.main()
