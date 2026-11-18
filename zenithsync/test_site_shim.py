"""Sandbox-side import fidelity for the local test site (copied as `apport_python_hook.py`).

Local evaluation harness only; nothing of it reaches a submission. Standard library only,
because it runs inside every subprocess-sandbox interpreter at start-up.

Why: swegemma's subprocess sandbox skips the two steps that decide imports on the scorer
(`install_editable_package` and `/sandbox/setup.py --fast-path` both return early for
SubprocessManager). It only sets PYTHONPATH=<workspace> and lists the host's site-packages
(the evaluator venv, then the test site) in the sandbox venv's `_host_env.pth`. Three
consequences, all reproduced here inside the sandbox only:

1. Editable install. The scorer runs `pip install --no-deps -e /workspace`, which makes a
   `src/` layout package (psf/requests: `src/requests`) the one that is imported. Here the
   evaluator venv's or the test site's `requests` wheel shadowed it. Fix: put
   `<workspace>/src` right after `<workspace>` when it holds a package or module.
2. `workspace_paths.pth`. setup.py's fast path writes `/workspace` and every non-hidden
   top-level directory of it into site-packages (end of sys.path). Reproduced by appending.
3. Pinned test dependencies (scripts/build_test_site.py --fidelity-lock). Each pinned wheel
   is installed in its own directory under `_fidelity/`; `_fidelity/selection.json` says,
   per group (`*` = every workspace, otherwise a top-level package the workspace provides,
   e.g. `fastapi`) and per distribution, which version applies from which date. The date
   is the committer date of the task's base commit (the parent of the harness's
   `_swegemma_baseline` tag), so a task sees the release that was current when its tests
   were written (rich's expected ANSI strings depend on the Pygments release). Selected
   directories go ahead of every site-packages directory, so they also win over the
   evaluator venv's copies; nothing else changes precedence.

Trigger: Ubuntu's stdlib sitecustomize imports `apport_python_hook` from sys.path and calls
install(). The test site is on sys.path by then (via `_host_env.pth`, as a plain path, so
its own .pth files are never processed). build_test_site.py refuses an interpreter whose
sitecustomize does not do this. Every failure here is swallowed: a sandbox must still start.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

SELECTION = os.path.join('_fidelity', 'selection.json')
BASELINE_TAG = '_swegemma_baseline'


def workspace_from(environ):
    """The sandbox workspace: the first PYTHONPATH entry that is a git checkout."""
    for entry in environ.get('PYTHONPATH', '').split(os.pathsep):
        if entry and os.path.isdir(os.path.join(entry, '.git')):
            return os.path.abspath(entry)
    return None


def _is_package_root(directory):
    try:
        names = os.listdir(directory)
    except OSError:
        return False
    return any(n.endswith('.py') or os.path.isfile(os.path.join(directory, n, '__init__.py')) for n in names)


def workspace_packages(workspace):
    """Top-level import packages the workspace provides (at its root or under src/)."""
    found = set()
    for base in (workspace, os.path.join(workspace, 'src')):
        try:
            names = os.listdir(base)
        except OSError:
            continue
        found.update(n for n in names if not n.startswith('.')
                     and os.path.isfile(os.path.join(base, n, '__init__.py')))
    return found


def editable_dirs(workspace):
    """Directories an editable install would make importable ahead of any installed copy."""
    src = os.path.join(workspace, 'src')
    return [src] if os.path.isdir(src) and _is_package_root(src) else []


def workspace_subdirs(workspace):
    """What setup.py's fast path writes to workspace_paths.pth after /workspace itself."""
    try:
        names = sorted(os.listdir(workspace))
    except OSError:
        return []
    return [os.path.join(workspace, n) for n in names
            if not n.startswith('.') and os.path.isdir(os.path.join(workspace, n))]


def base_date(workspace, run=subprocess.run):
    """UTC date (YYYY-MM-DD) of the task's base commit, or None."""
    for rev in (BASELINE_TAG + '^', 'HEAD'):
        try:
            result = run(['git', '-C', workspace, 'log', '-1', '--format=%ct', rev, '--'],
                         capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return None
        stamp = (result.stdout or '').strip()
        if result.returncode == 0 and stamp.isdigit():
            return datetime.fromtimestamp(int(stamp), timezone.utc).date().isoformat()
    return None


def select_pins(groups, date, packages):
    """Directory names to activate: per active group and distribution, the last entry whose
    `from` date is <= date (the first entry if date precedes all; the last if date is None)."""
    chosen = []
    for group in sorted(groups):
        if group != '*' and group not in packages:
            continue
        for dist in sorted(groups[group]):
            entries = sorted(groups[group][dist], key=lambda e: e['from'])
            pick = entries[-1] if date is None else next(
                (e for e in reversed(entries) if e['from'] <= date), entries[0])
            chosen.append(pick['dir'])
    return chosen


def rearrange(path, workspace, front, pins, tail):
    """New sys.path: `front` right after the workspace, `pins` ahead of the first
    site-packages entry, `tail` appended; nothing else moves."""
    added = set(front) | set(pins) | set(tail)
    out = [p for p in path if p not in added]
    at = out.index(workspace) + 1 if workspace in out else 0
    out[at:at] = front
    site = next((i for i, p in enumerate(out) if 'site-packages' in p), len(out))
    out[site:site] = pins
    out.extend(t for t in tail if t not in out)
    return out


def plan(environ, here, run=subprocess.run):
    """What install() would do, as data (also used by the pod preflight)."""
    workspace = workspace_from(environ)
    if workspace is None:
        return None
    try:
        with open(os.path.join(here, SELECTION)) as handle:
            groups = json.load(handle)['groups']
    except (OSError, ValueError, KeyError):
        groups = {}
    packages = workspace_packages(workspace)
    date = base_date(workspace, run) if groups else None
    pins = [os.path.join(here, '_fidelity', d) for d in select_pins(groups, date, packages)]
    return {'workspace': workspace, 'packages': sorted(packages), 'base_date': date,
            'front': editable_dirs(workspace), 'pins': pins, 'tail': workspace_subdirs(workspace)}


def install():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        decided = plan(os.environ, here)
        if decided is None:
            return
        sys.path[:] = rearrange(sys.path, decided['workspace'], decided['front'], decided['pins'],
                                decided['tail'])
    except Exception:  # a sandbox interpreter must start whatever happens here
        pass
