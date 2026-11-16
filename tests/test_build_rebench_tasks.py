import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.build_rebench_tasks import SKIP, build_requires, select, snapshot


def git(*args, cwd):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class SnapshotTests(unittest.TestCase):
    def test_snapshot_has_no_future_history_and_the_exact_tree(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            src = d / 'src'
            src.mkdir()
            git('init', '-q', '-b', 'main', cwd=src)
            git('config', 'user.email', 't@t', cwd=src)
            git('config', 'user.name', 't', cwd=src)
            (src / 'a.py').write_text('x = 1\n')
            git('add', '.', cwd=src)
            git('commit', '-q', '-m', 'one', cwd=src)
            base = git('rev-parse', 'HEAD', cwd=src)
            (src / 'a.py').write_text('x = 2\n')
            git('commit', '-q', '-am', 'future', cwd=src)
            bare = d / 'src.git'
            git('clone', '-q', '--bare', str(src), str(bare), cwd=d)
            out = d / 't.tgz'
            work = d / 'work'
            work.mkdir()
            info = snapshot(bare, base, out, work)
            self.assertTrue(info['ok'], info)
            self.assertEqual(info['commits'], 1)
            unpacked = d / 'u'
            with tarfile.open(out) as tar:
                tar.extractall(unpacked)
            self.assertEqual((unpacked / 'a.py').read_text(), 'x = 1\n')
            self.assertEqual(git('rev-parse', '--abbrev-ref', 'HEAD', cwd=unpacked), 'main')
            self.assertEqual(git('log', '--all', '--format=%s', cwd=unpacked), 'one')
            self.assertEqual(git('status', '--porcelain', cwd=unpacked), '')


class SelectionTests(unittest.TestCase):
    def test_newest_per_repository_inside_the_cohort_only(self):
        rows = [{'instance_id': f'r{i}', 'repo': 'o/a', 'created_at': f'2020-0{i}'} for i in range(1, 5)]
        rows.append({'instance_id': 'x', 'repo': 'o/b', 'created_at': '2021'})
        chosen = select(rows, {'r1', 'r2', 'r3', 'x'}, repos=0, per_repo=2, only_repos=[])
        self.assertEqual([r['instance_id'] for r in chosen['o/a']], ['r2', 'r3'])
        self.assertEqual(list(chosen), ['o/a', 'o/b'])

    def test_system_commands_are_skipped_and_pip_is_not(self):
        for command in ('apt-get update -qq', 'export DEBIAN_FRONTEND=noninteractive',
                        "curl --proto '=https' -sSf https://sh.rustup.rs | sh"):
            self.assertTrue(SKIP.search(command), command)
        for command in ('pip install -q -e .[test]', 'git submodule update --init --recursive',
                        "sed -i 's/a/b/' pyproject.toml"):
            self.assertFalse(SKIP.search(command), command)


class BuildRequiresTests(unittest.TestCase):
    def test_reads_pep518_requires_and_tolerates_absence(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(build_requires(d), [])
            Path(d, 'pyproject.toml').write_text('[build-system]\nrequires = ["hatchling", "hatch-vcs"]\n')
            self.assertEqual(build_requires(d), ['hatchling', 'hatch-vcs'])
            Path(d, 'pyproject.toml').write_text('[project]\nname = "x"\n')
            self.assertEqual(build_requires(d), [])
            Path(d, 'pyproject.toml').write_text('not toml [')
            self.assertEqual(build_requires(d), [])


if __name__ == '__main__':
    unittest.main()
