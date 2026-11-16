"""Convert SWE-rebench-V2 cohort tasks into swegemma tasks, one repository at a time.

For each selected repository this writes, under OUTPUT/<repo_slug>/:

  tasks.jsonl          swegemma rows: instance_id, repo, base_commit, patch,
                       test_patch, problem_statement, hints_text, created_at
  snapshots/<id>.tgz   the official snapshot format: a fresh repository built by
                       `git fast-export` up to base_commit (no future history),
                       branch `main` checked out, archived from its root
  wheels/              empty (the dependencies live in the test site instead)
  site/site-packages   the repository's runtime and test dependencies, installed
                       by the task's own `install_config.install` commands into a
                       throwaway venv, with the repository's own distribution
                       removed afterwards (swegemma installs /workspace itself),
                       plus the official image's build backends and pytest pins
  build.json           what was done per task and per command, with exit codes

The site is built once per repository, at the newest selected base commit; tasks
whose tests then fail with the reference patch are removed later by gold/empty
qualification (`qualify_verifier.py`), not here. Network is used only while
building, before any guard. The cohort gate refuses a confirmation-cohort task.

Commands that need a system package manager or a toolchain download (apt-get,
curl | sh, rustup, conda) are skipped and recorded; a task that needed them will
fail qualification and be dropped, which is the honest outcome.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
SKIP = re.compile(r'^\s*(apt-get|apt |sudo |curl |wget |conda |mamba |rustup|export DEBIAN|source |\. )')
IMAGE_PACKAGES = ['pytest', 'pytest-timeout==2.1.0', 'typer', 'pdm-backend', 'setuptools', 'wheel',
                  'poetry-core', 'hatchling', 'flit-core', 'editables']
# Run with the build venv's interpreter: argv = tree, distribution names. Prints the site-relative files
# that are code copies or import hooks (to delete; .dist-info kept) and each top-level package's
# directory relative to the tree (where /workspace must be searched).
OWN_LAYOUT = r'''
import importlib.metadata as m, importlib.util, json, os, sys
tree = os.path.realpath(sys.argv[1]); code, dirs = [], set()
for name in sys.argv[2:]:
    dist = m.distribution(name)
    for f in dist.files or []:
        if '.dist-info' not in str(f) and '.egg-info' not in str(f):
            code.append(str(f))
    tops = (dist.read_text('top_level.txt') or '').split()
    if not tops:
        tops = sorted({str(f).split('/')[0].removesuffix('.py') for f in dist.files or []
                       if '/' in str(f) or str(f).endswith('.py')} - {'..'})
    for top in tops:
        try:
            spec = importlib.util.find_spec(top)
        except (ImportError, ValueError):
            continue
        where = (list(spec.submodule_search_locations or []) or [spec.origin]) if spec else []
        found = False
        for loc in where:
            loc = os.path.realpath(loc or '')
            if loc.startswith(tree + os.sep):
                dirs.add(os.path.relpath(os.path.dirname(loc), tree)); found = True
        if not found and (os.path.isdir(os.path.join(tree, 'src', top))
                          or os.path.isfile(os.path.join(tree, 'src', top + '.py'))):
            dirs.add('src')
# Installers that record no top-level names (hatch editable: only a .pth): a src/ layout is still src/.
src = os.path.join(tree, 'src')
if not dirs and os.path.isdir(src) and any(
        os.path.isfile(os.path.join(src, e, '__init__.py')) or e.endswith('.py') for e in os.listdir(src)):
    dirs.add('src')
print(json.dumps({'code_files': [c for c in code if not c.startswith('..')], 'package_dirs': sorted(dirs)}))
'''
WORKSPACE_PTH = ("import os, sys; [sys.path.insert(0, os.path.join(p, d)) for p in "
                 "os.environ.get('PYTHONPATH', '').split(os.pathsep) if p for d in {dirs} "
                 "if os.path.isdir(os.path.join(p, d))]")
# Ubuntu's stdlib sitecustomize imports `apport_python_hook` from sys.path and calls install(). In the
# local subprocess sandbox the test site is on sys.path by then (as a plain path from swegemma's
# _host_env.pth, so its own .pth files are never processed). This shim processes them, as a real
# site-packages directory would be: that is what makes the workspace mapping above take effect.
# Local data-generation plumbing only; nothing of it reaches a submission.
APPORT_SHIM = '''\"\"\"Test-site shim written by scripts/build_rebench_tasks.py (local harness only).\"\"\"
import os
import site
import sys


def install():
    here = os.path.dirname(os.path.abspath(__file__))
    site.addsitedir(here)
    # Sandbox-only precedence: the task's dependencies before every other site-packages directory
    # (after the stdlib and /workspace), while the evaluating host process keeps its own order.
    if here in sys.path:
        sys.path.remove(here)
    first = next((i for i, p in enumerate(sys.path) if 'site-packages' in p), len(sys.path))
    sys.path.insert(first, here)
'''
SLOW_SNAPSHOT_SECONDS = 120
SLOW_REPO_TASKS = 4
ROW_KEYS = ('instance_id', 'repo', 'base_commit', 'patch', 'test_patch', 'problem_statement', 'created_at')


def run(cmd, *, cwd=None, env=None, timeout=1800, shell=False):
    started = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, shell=shell, capture_output=True, text=True, timeout=timeout)
        code, tail = p.returncode, (p.stdout[-1500:] + p.stderr[-1500:])
    except subprocess.TimeoutExpired:
        code, tail = 'timeout', ''
    return {'cmd': cmd if isinstance(cmd, str) else ' '.join(cmd), 'exit': code,
            'seconds': round(time.monotonic() - started, 1), 'tail': tail}


def slug(repo):
    return repo.replace('/', '__')


def select(rows, cohort_ids, *, repos, per_repo, only_repos):
    by_repo = {}
    for r in rows:
        if r['instance_id'] in cohort_ids:
            by_repo.setdefault(r['repo'], []).append(r)
    names = sorted(by_repo)
    if only_repos:
        names = [n for n in names if n in set(only_repos)]
    names = names[:repos] if repos else names
    return {n: sorted(by_repo[n], key=lambda r: r['created_at'])[-per_repo:] if per_repo else
            sorted(by_repo[n], key=lambda r: r['created_at']) for n in names}


def snapshot(source, commit, dest_tgz, work):
    """Official format: fast-export up to `commit` into a fresh repository on `main`."""
    new = work / 'snap'
    shutil.rmtree(new, ignore_errors=True)
    new.mkdir(parents=True)
    steps = [run(['git', '-C', str(source), 'branch', '-f', 'export_ref', commit])]
    steps.append(run(['git', 'init', '-q', '-b', 'main', str(new)]))
    export = subprocess.Popen(['git', '-C', str(source), 'fast-export', '--reencode=yes', '--signed-tags=strip',
                               '--tag-of-filtered-object=drop', 'export_ref'], stdout=subprocess.PIPE)
    imp = subprocess.run(['git', '-C', str(new), 'fast-import', '--quiet'], stdin=export.stdout,
                         capture_output=True, text=True)
    export.wait()
    steps.append({'cmd': 'fast-export | fast-import', 'exit': export.returncode or imp.returncode,
                  'tail': imp.stderr[-800:]})
    steps.append(run(['git', '-C', str(new), 'branch', '-f', 'main', 'export_ref']))
    steps.append(run(['git', '-C', str(new), 'checkout', '-q', '-f', 'main']))
    head = run(['git', '-C', str(new), 'rev-parse', 'HEAD'])
    tree_src = run(['git', '-C', str(source), 'rev-parse', f'{commit}^{{tree}}'])
    tree_new = run(['git', '-C', str(new), 'rev-parse', 'HEAD^{tree}'])
    same_tree = tree_src['exit'] == 0 and tree_src['tail'].strip() == tree_new['tail'].strip()
    future = run(['git', '-C', str(new), 'log', '--all', '--format=%H'])
    if not same_tree or any(s['exit'] != 0 for s in steps):
        return {'ok': False, 'steps': steps, 'same_tree': same_tree}
    with tarfile.open(dest_tgz, 'w:gz') as tar:
        tar.add(new, arcname='.')
    digest = hashlib.sha256(dest_tgz.read_bytes()).hexdigest()
    return {'ok': True, 'same_tree': True, 'commits': len(future['tail'].split()), 'sha256': digest,
            'size_bytes': dest_tgz.stat().st_size, 'head': head['tail'].strip()}


def build_requires(tree):
    """PEP 518 `[build-system].requires` of the checked-out tree, or [] when absent or unreadable."""
    import tomllib
    path = Path(tree) / 'pyproject.toml'
    try:
        requires = tomllib.loads(path.read_text())['build-system']['requires']
    except (OSError, KeyError, ValueError, TypeError):
        return []
    return [r for r in requires if isinstance(r, str) and r.strip()] if isinstance(requires, list) else []


def build_site(source, commit, install, out_dir, work, python):
    """Install the task's dependencies into a venv, drop the repository itself, keep site-packages."""
    tree = work / 'tree'
    shutil.rmtree(tree, ignore_errors=True)
    log = [run(['git', '-C', str(source), 'worktree', 'add', '-f', '--detach', str(tree), commit])]
    venv = out_dir / 'venv'
    shutil.rmtree(venv, ignore_errors=True)
    log.append(run([python, '-m', 'venv', str(venv)]))
    pip = str(venv / 'bin' / 'pip')
    log.append(run([pip, 'install', '-q', '--upgrade', 'pip'], timeout=600))
    env = {'PATH': f"{venv / 'bin'}:/usr/local/bin:/usr/bin:/bin", 'HOME': str(work), 'VIRTUAL_ENV': str(venv),
           'PIP_DISABLE_PIP_VERSION_CHECK': '1', 'GIT_TERMINAL_PROMPT': '0'}
    for command in install:
        if SKIP.search(command):
            log.append({'cmd': command, 'exit': 'skipped'})
            continue
        log.append(run(command, cwd=tree, env=env, shell=True, timeout=2400))
    log.append(run([pip, 'install', '-q', *IMAGE_PACKAGES], timeout=900))
    # swegemma installs /workspace with --no-build-isolation, so the build backend's own requirements
    # (hatch-vcs, setuptools-scm, ...) must already be in the site, or the package is not importable.
    requires = build_requires(tree)
    if requires:
        log.append(run([pip, 'install', '-q', *requires], timeout=900))
    # The repository's own distribution, editable or copied, would shadow /workspace: find it by its
    # PEP 610 direct_url pointing at the build tree, and remove it.
    own = []
    try:
        report = json.loads(subprocess.run([pip, 'inspect'], capture_output=True, text=True, timeout=300).stdout)
        own = sorted({d['metadata']['name'] for d in report.get('installed', [])
                      if str((d.get('direct_url') or {}).get('url', '')).startswith(f'file://{tree}')})
    except (ValueError, KeyError, subprocess.TimeoutExpired):
        log.append({'cmd': 'pip inspect', 'exit': 'unparsed'})
    # swegemma's subprocess sandbox skips the editable install the Docker scorer performs and only puts
    # /workspace on PYTHONPATH. Reproduce what the editable install provides instead: keep the
    # distribution's metadata (importlib.metadata lookups), delete its code copies and import hooks, and
    # map each top-level package's directory (e.g. src/) onto whatever /workspace is at run time.
    layout = {'own': own, 'package_dirs': [], 'deleted_files': 0}
    if own:
        probe = subprocess.run([str(venv / 'bin' / 'python'), '-c', OWN_LAYOUT, str(tree), *own],
                               capture_output=True, text=True, timeout=300)
        try:
            layout.update(json.loads(probe.stdout))
        except ValueError:
            log.append({'cmd': 'own-layout probe', 'exit': probe.returncode, 'tail': probe.stderr[-1500:]})
    site = next((venv / 'lib').glob('python3*/site-packages'))
    target = out_dir / 'site' / 'site-packages'
    shutil.rmtree(target.parent, ignore_errors=True)
    shutil.copytree(site, target, symlinks=True)
    for rel in layout.get('code_files', []):
        path = target / rel
        if path.is_file() or path.is_symlink():
            path.unlink()
            layout['deleted_files'] += 1
    for pth in list(target.glob('__editable__*')) + list(target.glob('*.egg-link')):
        pth.unlink()
    dirs = sorted(d for d in layout.get('package_dirs', []) if d not in ('', '.'))
    if dirs:
        (target / 'zz_rebench_workspace.pth').write_text(WORKSPACE_PTH.format(dirs=repr(dirs)) + '\n')
    (target / 'apport_python_hook.py').write_text(APPORT_SHIM)
    layout.pop('code_files', None)
    log.append(run(['git', '-C', str(source), 'worktree', 'remove', '--force', str(tree)]))
    shutil.rmtree(venv, ignore_errors=True)
    failed = [s for s in log if s['exit'] not in (0, 'skipped')]
    return {'own_layout': layout, 'failed_commands': len(failed), 'log': log}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--parquet', type=Path, required=True)
    parser.add_argument('--cohorts', type=Path, default=ROOT / 'evidence/data/task-pool-v2-python-001/cohorts.json')
    parser.add_argument('--cohort', choices=('train', 'development'), default='train')
    parser.add_argument('--freeze', type=Path, default=ROOT / 'evidence/data/confirmation-cohort-freeze-001/freeze.json')
    parser.add_argument('--repos', type=int, default=0, help='first N repositories by name (0 = all)')
    parser.add_argument('--only-repo', action='append', default=[])
    parser.add_argument('--per-repo', type=int, default=0, help='newest N tasks per repository (0 = all)')
    parser.add_argument('--shard', default='0/1', help='K/N: build only repositories with index %% N == K')
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import pyarrow.parquet as pq
    cohorts = json.loads(args.cohorts.read_text())
    ids = set(next(c for c in cohorts['cohorts'] if c['name'] == args.cohort)['instance_ids'])
    frozen = json.loads(args.freeze.read_text())
    reserved = set()
    for key in ('reserved_tasks', 'instance_ids', 'tasks'):
        value = frozen.get(key) or frozen.get('body', {}).get(key)
        if isinstance(value, list):
            reserved |= {v if isinstance(v, str) else v.get('instance_id') for v in value}
    confirmation = set(next(c for c in cohorts['cohorts'] if c['name'] == 'confirmation')['instance_ids'])
    if ids & (reserved | confirmation):
        raise SystemExit('refused: selection overlaps the frozen confirmation cohort')
    columns = list(ROW_KEYS) + ['install_config']
    rows = pq.read_table(args.parquet, columns=columns).to_pylist()
    chosen = select(rows, ids, repos=args.repos, per_repo=args.per_repo, only_repos=args.only_repo)
    k, n = (int(x) for x in args.shard.split('/'))
    args.output.mkdir(parents=True, exist_ok=True)
    for index, (repo, tasks) in enumerate(sorted(chosen.items())):
        if index % n != k:
            continue
        out = args.output / slug(repo)
        if (out / 'build.json').exists():
            continue
        work = Path('/tmp/rebench-work') / slug(repo)
        shutil.rmtree(work, ignore_errors=True)
        (out / 'snapshots').mkdir(parents=True, exist_ok=True)
        (out / 'wheels').mkdir(exist_ok=True)
        work.mkdir(parents=True)
        source = work / 'src.git'
        record = {'repo': repo, 'tasks': {}, 'started': time.time()}
        clone = run(['git', 'clone', '-q', '--bare', f'https://github.com/{repo}.git', str(source)], timeout=3600)
        record['clone'] = clone
        if clone['exit'] != 0:
            (out / 'build.json').write_text(json.dumps(record, indent=1))
            print(json.dumps({'repo': repo, 'clone': 'failed'}), flush=True)
            continue
        good = []
        # Newest first: a repository whose history makes one snapshot slow (each is a full fast-export)
        # keeps only its SLOW_REPO_TASKS newest tasks, so one repository cannot stall a whole batch.
        queue = list(reversed(tasks))
        for index, task in enumerate(queue):
            started = time.monotonic()
            snap = snapshot(source, task['base_commit'], out / 'snapshots' / f"{task['instance_id']}.tgz", work)
            snap['seconds'] = round(time.monotonic() - started, 1)
            record['tasks'][task['instance_id']] = {'snapshot': snap}
            if snap['ok']:
                good.append(task)
            if index == 0 and snap['seconds'] > SLOW_SNAPSHOT_SECONDS and len(queue) > SLOW_REPO_TASKS:
                record['capped_slow_history'] = {'first_snapshot_seconds': snap['seconds'], 'kept': SLOW_REPO_TASKS,
                                                 'dropped': [t['instance_id'] for t in queue[SLOW_REPO_TASKS:]]}
                queue[SLOW_REPO_TASKS:] = []
        good.sort(key=lambda t: t['created_at'])
        if good:
            newest = good[-1]
            record['site'] = build_site(source, newest['base_commit'], newest['install_config'].get('install') or [],
                                        out, work, args.python)
            record['site']['built_at_commit'] = newest['base_commit']
            with open(out / 'tasks.jsonl', 'w') as handle:
                for task in good:
                    row = {key: task[key] for key in ROW_KEYS}
                    row['created_at'] = str(row['created_at'])
                    row['hints_text'] = ''
                    handle.write(json.dumps(row) + '\n')
        record['finished'] = time.time()
        (out / 'build.json').write_text(json.dumps(record, indent=1))
        shutil.rmtree(work, ignore_errors=True)
        print(json.dumps({'repo': repo, 'tasks': len(tasks), 'snapshots': len(good),
                          'site_failed_commands': record.get('site', {}).get('failed_commands'),
                          'seconds': round(record['finished'] - record['started'])}), flush=True)


if __name__ == '__main__':
    main()
