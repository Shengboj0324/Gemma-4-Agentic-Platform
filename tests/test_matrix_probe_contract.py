"""Synthetic programs and receipts exercise probe substitution rejection."""
import base64
import hashlib
import unittest

from scripts.qualify_swe_rebench_evaluator import PLUGIN, PROBE
from zenithsync.matrix_probe_contract import verify_matrix_probe


class MatrixProbeTests(unittest.TestCase):
    def setUp(self):
        self.image = 'sha256:' + 'a' * 64
        self.snapshot = dict(snapshot_commit='b' * 40, source_tree='c' * 40)
        self.profile = dict(python='/usr/local/bin/python', module='package',
                            expected_origin='/testbed/src/package/__init__.py',
                            import_root='src', test_targets=['tests'], platform='linux/arm64')
        self.patches = {name: (name + ' synthetic patch').encode()
                        for name in ('candidate', 'reference', 'tests')}
        self.allowed = ['src/package/__init__.py']
        self.settings = dict(BASE=self.snapshot['snapshot_commit'], TREE=self.snapshot['source_tree'],
                             ROLE='candidate', PYTHON=self.profile['python'], MODULE='package',
                             EXPECTED_ORIGIN=self.profile['expected_origin'], SOURCE_PYTHONPATH='/testbed/src',
                             ALLOWED_PATHS=self.allowed, TEST_TARGETS=['tests'], PLUGIN=PLUGIN,
                             RESOURCE_PAYLOAD='', RESOURCE_ADAPTER='',
                             PATCHES={k: base64.b64encode(v).decode() for k, v in self.patches.items()})

    def program(self):
        return ''.join(f'{k}={v!r}\n' for k, v in self.settings.items()) + PROBE

    def check(self, source, version=None):
        # Rehash even malicious programs: the test must reject their semantics,
        # rather than merely detecting a stale receipt hash.
        receipt = dict(image=self.image, image_id=self.image, platform='linux/arm64',
                       entrypoint=self.profile['python'], generated_grading_tests_executed=True,
                       agent_executed=False, returncode=0, copy_returncode=0, cleanup_returncode=0,
                       state=dict(Status='exited', ExitCode=0, OOMKilled=False, Error=''),
                       probe_source=dict(sha256=hashlib.sha256(source.encode()).hexdigest(),
                                         size_bytes=len(source.encode())))
        return verify_matrix_probe(source, receipt, image=self.image, snapshot=self.snapshot,
                                   role='candidate', patches=self.patches, profile=self.profile,
                                   allowed_paths=self.allowed, version_assertion=version)

    def test_known_program_and_version_assertion(self):
        self.check(self.program())
        self.check("import django; assert django.get_version() == '3.1.14'\n" + self.program(), '3.1.14')
        with self.assertRaises(ValueError):
            self.check(self.program(), '3.1.14')

    def test_executable_duplicate_settings_and_altered_body_reject(self):
        for source in ('import os\n' + self.program(), 'ROLE="candidate"\n' + self.program(),
                       'INJECT=print("executed")\n' + self.program(), self.program() + '\npass\n'):
            with self.subTest(source=source[:40]), self.assertRaises(ValueError):
                self.check(source)

    def test_rehashed_weakened_targets_role_plugin_and_snapshot_reject(self):
        for key, value in [('TEST_TARGETS', ['tests/one.py']), ('ROLE', 'base'),
                           ('PLUGIN', ''), ('BASE', 'd' * 40), ('RESOURCE_ADAPTER', 'pass')]:
            original = self.settings[key]
            self.settings[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check(self.program())
            self.settings[key] = original

    def test_missing_or_substituted_patch_rejects(self):
        del self.settings['PATCHES']['candidate']
        with self.assertRaises(ValueError):
            self.check(self.program())
        self.settings['PATCHES']['candidate'] = base64.b64encode(b'other patch').decode()
        with self.assertRaises(ValueError):
            self.check(self.program())
