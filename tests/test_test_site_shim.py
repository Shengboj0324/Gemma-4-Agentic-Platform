import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from zenithsync import test_site_shim as shim

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {'*': {'pygments': [{'from': '2023-04-10', 'dir': 'pygments-2.15.1'},
                             {'from': '2025-01-05', 'dir': 'pygments-2.19.2'},
                             {'from': '2026-03-29', 'dir': 'pygments-2.20.0'}]},
          'fastapi': {'dirty-equals': [{'from': '2025-01-11', 'dir': 'dirty-equals-0.9.0'}]}}


def git(cwd, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t',
               GIT_COMMITTER_EMAIL='t@t', GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    subprocess.run(['git', *args], cwd=cwd, env=env, check=True, capture_output=True)


def make_workspace(root, *, src_layout, base='2024-08-26T12:00:00+00:00'):
    """A snapshot-like checkout whose base commit has `base` as committer date, plus the
    harness's baseline commit and tag (dated now)."""
    ws = Path(root) / 'workspace'
    package = ws / 'src' / 'mypkg' if src_layout else ws / 'mypkg'
    package.mkdir(parents=True)
    (package / '__init__.py').write_text("WHERE = 'workspace'\n")
    (ws / 'tests').mkdir()
    (ws / 'tests' / 'test_x.py').write_text('')
    (ws / '.hidden').mkdir()
    git(ws, 'init', '-q', '-b', 'main')
    git(ws, 'add', '-A')
    git(ws, 'commit', '-q', '-m', 'base', date=base)
    (ws / 'pytest.ini').write_text('[pytest]\n')
    git(ws, 'add', '-A')
    git(ws, 'commit', '-q', '-m', 'eval_baseline')
    git(ws, 'tag', '-f', shim.BASELINE_TAG)
    return ws


class SelectionTests(unittest.TestCase):
    def test_entry_current_at_the_base_date_is_chosen(self):
        self.assertEqual(shim.select_pins(GROUPS, '2024-08-26', set()), ['pygments-2.15.1'])
        self.assertEqual(shim.select_pins(GROUPS, '2025-01-05', set()), ['pygments-2.19.2'])
        self.assertEqual(shim.select_pins(GROUPS, '2026-04-12', set()), ['pygments-2.20.0'])

    def test_earlier_dates_take_the_first_entry_and_unknown_dates_the_last(self):
        self.assertEqual(shim.select_pins(GROUPS, '2019-01-01', set()), ['pygments-2.15.1'])
        self.assertEqual(shim.select_pins(GROUPS, None, set()), ['pygments-2.20.0'])

    def test_package_groups_apply_only_to_workspaces_that_provide_the_package(self):
        self.assertEqual(shim.select_pins(GROUPS, '2025-12-02', {'fastapi', 'docs_src'}),
                         ['pygments-2.19.2', 'dirty-equals-0.9.0'])
        self.assertEqual(shim.select_pins(GROUPS, '2025-12-02', {'rich'}), ['pygments-2.19.2'])


class RearrangeTests(unittest.TestCase):
    def test_editable_dirs_follow_the_workspace_and_pins_precede_every_site_packages(self):
        path = ['', '/ws', '/usr/lib/python312.zip', '/usr/lib/python3.12', '/sb/venv/site-packages',
                '/root/venv/site-packages', '/opt/t/site-packages']
        out = shim.rearrange(path, '/ws', ['/ws/src'], ['/opt/t/site-packages/_fidelity/pygments-2.15.1'],
                             ['/ws/src', '/ws/tests'])
        self.assertEqual(out, ['', '/ws', '/ws/src', '/usr/lib/python312.zip', '/usr/lib/python3.12',
                               '/opt/t/site-packages/_fidelity/pygments-2.15.1', '/sb/venv/site-packages',
                               '/root/venv/site-packages', '/opt/t/site-packages', '/ws/tests'])

    def test_is_idempotent_and_leaves_paths_alone_without_inputs(self):
        path = ['', '/ws', '/a/site-packages']
        once = shim.rearrange(path, '/ws', ['/ws/src'], ['/p'], ['/ws/t'])
        self.assertEqual(shim.rearrange(once, '/ws', ['/ws/src'], ['/p'], ['/ws/t']), once)
        self.assertEqual(shim.rearrange(path, '/ws', [], [], []), path)


class WorkspaceTests(unittest.TestCase):
    def test_src_layout_is_mapped_and_root_layout_is_not(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(d, src_layout=True)
            self.assertEqual(shim.editable_dirs(str(ws)), [str(ws / 'src')])
            self.assertEqual(shim.workspace_packages(str(ws)), {'mypkg'})
            self.assertEqual(shim.workspace_subdirs(str(ws)), [str(ws / 'src'), str(ws / 'tests')])
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(d, src_layout=False)
            self.assertEqual(shim.editable_dirs(str(ws)), [])
            self.assertEqual(shim.workspace_packages(str(ws)), {'mypkg'})

    def test_base_date_is_the_parent_of_the_baseline_tag(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(d, src_layout=False, base='2023-07-29T23:30:00-02:00')
            self.assertEqual(shim.base_date(str(ws)), '2023-07-30')  # UTC
            git(ws, 'tag', '-d', shim.BASELINE_TAG)
            self.assertNotEqual(shim.base_date(str(ws)), '2023-07-30')  # falls back to HEAD (now)

    def test_workspace_must_be_a_git_checkout_on_pythonpath(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(d, src_layout=True)
            self.assertEqual(shim.workspace_from({'PYTHONPATH': os.pathsep.join([d, str(ws)])}), str(ws))
            self.assertIsNone(shim.workspace_from({'PYTHONPATH': d}))
            self.assertIsNone(shim.plan({}, d))


class SandboxInterpreterTests(unittest.TestCase):
    """The shim in a real interpreter laid out like a subprocess sandbox: PYTHONPATH is the
    workspace and the host's site-packages (evaluator venv, then test site) follow."""

    def run_sandbox(self, d, ws):
        host = Path(d) / 'host' / 'site-packages'
        for package, value in (('mypkg', 'host-wheel'), ('pyg', 'host')):
            (host / package).mkdir(parents=True)
            (host / package / '__init__.py').write_text(f'WHERE = {value!r}\n')
        site = Path(d) / 'tools' / 'site-packages'
        (site / 'mypkg').mkdir(parents=True)
        (site / 'mypkg' / '__init__.py').write_text("WHERE = 'test-site-wheel'\n")
        for directory in ('pygments-2.15.1', 'pygments-2.19.2', 'pygments-2.20.0', 'dirty-equals-0.9.0'):
            (site / '_fidelity' / directory / 'pyg').mkdir(parents=True)
            (site / '_fidelity' / directory / 'pyg' / '__init__.py').write_text(f'WHERE = {directory!r}\n')
        import json
        (site / '_fidelity' / 'selection.json').write_text(json.dumps({'schema_version': 1, 'groups': GROUPS}))
        shutil.copyfile(ROOT / 'zenithsync' / 'test_site_shim.py', site / 'apport_python_hook.py')
        code = ('import sys; sys.path += sys.argv[1:]\n'
                'import apport_python_hook; apport_python_hook.install()\n'
                'import mypkg, pyg; print(mypkg.WHERE, pyg.WHERE, sys.path[-1])')
        result = subprocess.run([sys.executable, '-c', code, str(host), str(site)], cwd=d, check=True,
                                capture_output=True, text=True,
                                env={'PATH': os.environ['PATH'], 'PYTHONPATH': str(ws)})
        return result.stdout.split()

    def test_src_package_and_dated_pins_win_over_installed_copies(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(d, src_layout=True, base='2024-08-26T12:00:00+00:00')
            self.assertEqual(self.run_sandbox(d, ws), ['workspace', 'pygments-2.15.1', str(ws / 'tests')])

    def test_without_the_shim_the_installed_wheel_shadows_a_src_layout(self):
        with tempfile.TemporaryDirectory() as d:
            ws = make_workspace(d, src_layout=True)
            host = Path(d) / 'host' / 'site-packages'
            (host / 'mypkg').mkdir(parents=True)
            (host / 'mypkg' / '__init__.py').write_text("WHERE = 'host-wheel'\n")
            result = subprocess.run([sys.executable, '-c', 'import sys; sys.path += sys.argv[1:]; import mypkg; '
                                     'print(mypkg.WHERE)', str(host)], cwd=d, check=True, capture_output=True,
                                    text=True, env={'PATH': os.environ['PATH'], 'PYTHONPATH': str(ws)})
            self.assertEqual(result.stdout.strip(), 'host-wheel')


if __name__ == '__main__':
    unittest.main()
