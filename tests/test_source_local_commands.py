"""Behavior and rejection boundaries for root-relative replay commands."""
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from scripts.replay_source_teacher import adapt_source_local_command, adapt_source_search, preflight

class SourceLocalCommandsTests(unittest.TestCase):
    def test_literal_commands_execute_in_mapped_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'check.py').write_text('from pathlib import Path\nassert Path("marker").read_text()=="expected"\n')
            (root/'marker').write_text('expected')
            (root/'scratch.py').write_text('temporary')
            for command in ('python check.py', 'rm scratch.py'):
                mapped = adapt_source_local_command(command)
                self.assertIsNotNone(mapped)
                # Execute identical argv under the mapped working directory,
                # without depending on a host /workspace path or python alias.
                argv = mapped.removeprefix('cd /workspace && ').split()
                if argv[0] == 'python':
                    argv[0] = sys.executable
                result = subprocess.run(argv, cwd=root, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((root/'scratch.py').exists())

    def test_supported_commands_keep_text_and_timeout(self):
        for command in ('python tests.py','python -m pytest tests.py -v',
                        'python -m unittest tests.py','rm first.py second.py',
                        'git status','git diff module.py'):
            args = {'command':command,'timeout':30}
            messages = [{'tool_calls':[{'function':{'name':'execute_bash','arguments':args}}]}]
            action = preflight(messages, '/workspace/example__repo__1')[0]
            self.assertEqual(action['command'], 'cd /workspace && '+command)
            self.assertEqual(action['source_timeout_seconds'],30)
            self.assertEqual(args,{'command':command,'timeout':30})
            for suffix in ('; pwd',' && pwd','\n',' > out',' | cat',' $(pwd)'):
                self.assertIsNone(adapt_source_local_command(command+suffix))
        for command in ('rm -rf .','rm ../file.py','rm /tmp/file.py','python -c "print(1)"',
                        'python $HOME/file.py','python `pwd`/file.py','git reset --hard',
                        'git diff ../file.py','python a-b.py','python .hidden.py'):
            self.assertIsNone(adapt_source_local_command(command))

    def test_escaped_bracket_search_execution_parity(self):
        prefix='/workspace/example__repo__1'
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'module.py'
            path.write_text('abs_path[-1]\npattern[0]\nabs_path[\n')
            for pattern in (r'abs_path\[-1\]',r'\[-1\]',r'pattern\[',r'abs_path\['):
                original=f'grep -n "{pattern}" {prefix}/module.py'
                mapped=adapt_source_search(original,prefix)
                self.assertEqual(mapped,original.replace(prefix,'/workspace',1))
                a=subprocess.run(['/bin/sh','-c',original.replace(prefix,directory,1)],capture_output=True,timeout=5)
                b=subprocess.run(['/bin/sh','-c',mapped.replace('/workspace',directory,1)],capture_output=True,timeout=5)
                self.assertEqual((a.returncode,a.stdout,a.stderr),(b.returncode,b.stdout,b.stderr))
                self.assertEqual(a.returncode,0)
                for suffix in ('; pwd','\n',' > out',' | cat'):
                    self.assertIsNone(adapt_source_search(original+suffix,prefix))

if __name__=='__main__':
    unittest.main()
