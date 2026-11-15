import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from scripts.build_submission_notebook import build_zip, collect, notebook


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


if __name__ == '__main__':
    unittest.main()
