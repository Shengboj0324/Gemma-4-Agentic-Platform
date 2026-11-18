from pathlib import Path
import unittest

from packaging.tags import Tag

import tempfile

from scripts.build_test_site import (build_fidelity, dockerfile_modules, fidelity_requirements,
                                     load_fidelity_lock, select_wheels, selection_table, shim_trigger)
from zenithsync.test_site_shim import select_pins

import hashlib
import json
from types import SimpleNamespace
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'requirements' / 'test-site-fidelity.json'


def fake_wheel(directory, dist, version, module):
    path = Path(directory) / f'{dist.replace("-", "_")}-{version}-py3-none-any.whl'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(f'{module}/__init__.py', f'VERSION = {version!r}\n')
    return path


def lock_for(wheels):
    """wheels: (group, dist, from, path, version)"""
    groups = {}
    for group, dist, start, path, version in wheels:
        groups.setdefault(group, {}).setdefault(dist, []).append(
            {'from': start, 'version': version, 'wheel': path.name,
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size_bytes': path.stat().st_size})
    return {'schema_version': 1, 'groups': groups}


def unzip(wheel, target):
    with zipfile.ZipFile(wheel) as z:
        z.extractall(target)


class SelectWheelsTests(unittest.TestCase):
    def test_highest_compatible_version_per_distribution(self):
        cp312 = {Tag('cp312', 'cp312', 'manylinux_2_17_x86_64'), Tag('py3', 'none', 'any')}
        wheels = [Path(n) for n in (
            'pytest-6.2.5-py3-none-any.whl', 'pytest-9.1.1-py3-none-any.whl', 'pytest-8.3.4-py3-none-any.whl',
            'pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_x86_64.whl',
            'pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_x86_64.whl',
            'SQLAlchemy-2.0.51-cp313-cp313-manylinux_2_17_x86_64.whl',
            'sqlalchemy-2.0.52-cp312-cp312-manylinux_2_17_x86_64.whl',
            'only313-1.0-cp313-cp313-manylinux_2_17_x86_64.whl')]
        chosen = [w.name for w in select_wheels(wheels, cp312)]
        self.assertEqual(chosen, ['pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_x86_64.whl',
                                  'pytest-9.1.1-py3-none-any.whl',
                                  'sqlalchemy-2.0.52-cp312-cp312-manylinux_2_17_x86_64.whl'])


    def test_only_modules_copied_into_site_packages_are_taken_from_the_dockerfile(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'Dockerfile.sandbox').write_text(
                'FROM python:3.13-slim\n'
                'COPY imp.py /usr/local/lib/python3.13/site-packages/imp.py\n'
                'COPY telnetlib.py /usr/local/lib/python3.13/site-packages/telnetlib.py\n'
                'COPY wheels/ /wheels/\n')
            self.assertEqual([p.name for p in dockerfile_modules(d)], ['imp.py', 'telnetlib.py'])


class FidelityLockTests(unittest.TestCase):
    def test_shipped_lock_is_valid_and_matches_the_audited_versions(self):
        lock = load_fidelity_lock(LOCK)
        self.assertEqual(len(fidelity_requirements(lock)), 19)
        table = selection_table(lock)
        rich = lambda date: select_pins(table, date, {'rich'})
        # rich_4079 (2026-04): monokai Name.Builtin is #f8f8f2 up to 2.20; 2.21 made it #a6e22e.
        self.assertEqual(rich('2026-04-12'), ['pygments-2.20.0'])
        # rich_3130 (2023-09) and rich_3469 (2024-08): Python whitespace was Token.Text before 2.19.
        self.assertEqual(rich('2023-09-17'), ['pygments-2.16.1'])
        self.assertEqual(rich('2024-08-26'), ['pygments-2.18.0'])
        self.assertEqual(rich('2026-11-18'), ['pygments-2.21.0'])
        fastapi = select_pins(table, '2025-12-02', {'fastapi', 'docs_src', 'tests'})
        self.assertEqual(fastapi, ['pygments-2.19.2', 'asttokens-3.0.1', 'dirty-equals-0.11', 'executing-2.2.1',
                                   'inline-snapshot-0.31.1', 'typing-inspection-0.4.4'])
        digests = {e['wheel']: e['sha256'] for d in lock['groups'].values() for es in d.values() for e in es}
        # Same bytes as the official devset wheels and the evaluator lock.
        self.assertEqual(digests['pygments-2.20.0-py3-none-any.whl'][:8], '81a9e26d')
        self.assertEqual(digests['pygments-2.21.0-py3-none-any.whl'][:8], '2363c69b')
        self.assertEqual(digests['typing_inspection-0.4.4-py3-none-any.whl'][:8], '65b8397b')

    def test_inconsistent_locks_are_refused(self):
        good = json.loads(LOCK.read_text())
        cases = []
        bad = json.loads(json.dumps(good)); bad['groups']['*']['pygments'][0]['version'] = '2.15.0'
        cases.append((bad, 'is not pygments'))
        bad = json.loads(json.dumps(good)); bad['groups']['*']['pygments'].reverse()
        cases.append((bad, 'ascending'))
        bad = json.loads(json.dumps(good)); bad['groups']['fast-api'] = bad['groups'].pop('fastapi')
        cases.append((bad, 'import name'))
        bad = json.loads(json.dumps(good)); bad['groups']['*']['pygments'][0]['sha256'] = ''
        cases.append((bad, 'sha256'))
        for lock, message in cases:
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / 'lock.json'
                path.write_text(json.dumps(lock))
                with self.assertRaisesRegex(ValueError, message):
                    load_fidelity_lock(path)

    def test_build_installs_each_pin_once_and_writes_the_selection_and_shim(self):
        with tempfile.TemporaryDirectory() as d:
            wheels = Path(d) / 'wheels'; wheels.mkdir()
            a = fake_wheel(wheels, 'pygments', '2.18.0', 'pygments')
            b = fake_wheel(wheels, 'pygments', '2.20.0', 'pygments')
            c = fake_wheel(wheels, 'dirty-equals', '0.9.0', 'dirty_equals')
            lock = lock_for([('*', 'pygments', '2024-05-04', a, '2.18.0'), ('*', 'pygments', '2026-03-29', b, '2.20.0'),
                             ('fastapi', 'dirty-equals', '2025-01-11', c, '0.9.0'),
                             ('httpx', 'dirty-equals', '2025-01-11', c, '0.9.0')])
            site = Path(d) / 'site-packages'; site.mkdir()
            calls = []
            record = build_fidelity(site, lock, wheels, install=lambda w, t: (calls.append(t.name), unzip(w, t)))
            self.assertEqual(sorted(calls), ['dirty-equals-0.9.0', 'pygments-2.18.0', 'pygments-2.20.0'])
            self.assertTrue((site / '_fidelity' / 'pygments-2.20.0' / 'pygments' / '__init__.py').is_file())
            selection = json.loads((site / '_fidelity' / 'selection.json').read_text())
            self.assertEqual(selection['groups'], record['selection'])
            self.assertEqual((site / 'apport_python_hook.py').read_bytes(),
                             (ROOT / 'zenithsync' / 'test_site_shim.py').read_bytes())
            with self.assertRaises(FileExistsError):
                build_fidelity(site, lock, wheels, install=unzip)

    def test_a_wheel_whose_digest_differs_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            a = fake_wheel(d, 'pygments', '2.18.0', 'pygments')
            lock = lock_for([('*', 'pygments', '2024-05-04', a, '2.18.0')])
            a.write_bytes(a.read_bytes() + b'x')
            site = Path(d) / 'site-packages'; site.mkdir()
            with self.assertRaisesRegex(ValueError, 'digest differs'):
                build_fidelity(site, lock, d, install=unzip)

    def test_shim_trigger_requires_a_sitecustomize_that_imports_apport_python_hook(self):
        with tempfile.TemporaryDirectory() as d:
            ubuntu = Path(d) / 'ubuntu.py'
            ubuntu.write_text('try:\n    import apport_python_hook\nexcept ImportError:\n    pass\n'
                              'else:\n    apport_python_hook.install()\n')
            other = Path(d) / 'other.py'
            other.write_text('pass\n')
            self.assertEqual(shim_trigger(lambda name: SimpleNamespace(origin=str(ubuntu))), str(ubuntu))
            self.assertIsNone(shim_trigger(lambda name: SimpleNamespace(origin=str(other))))
            self.assertIsNone(shim_trigger(lambda name: None))


if __name__ == '__main__':
    unittest.main()
