"""No credential ever becomes a tracked file, and three layers must say so.

The project keeps live R2, Cloudflare, Runpod and DigitalOcean credentials in a
private `.env` at the repository root. Three independent mechanisms are supposed
to keep it out of both Git and the bucket:

1. `.gitignore` excludes it from the working tree's tracked set;
2. `object_store._snapshot` refuses any manifest naming it;
3. `evidence_shipment.forbidden` refuses any package containing it.

A test that only checked one of those would let the other two rot. These check
all three, and additionally scan what Git actually tracks, because an ignore rule
does nothing for a file already added with `-f`.
"""

from pathlib import Path
import re
import subprocess
import unittest

from zenithsync.artifacts import validate_manifest
from zenithsync.evidence_shipment import forbidden
from zenithsync.object_store import ArtifactStore

ROOT = Path(__file__).resolve().parents[1]

# Paths that must never be tracked or published, whatever a caller asks for.
CREDENTIAL_PATHS = ('.env', '.env.local', '.env.production', 'a/b/.env',
                    '.ssh/id_ed25519', 'x/.aws/credentials', '.kaggle/kaggle.json')

# Values that look like a live secret rather than a placeholder. Test fixtures
# deliberately use obvious fakes, so these patterns are written to miss them.
SECRET_PATTERNS = (
    re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
    re.compile(r'R2_SECRET_ACCESS_KEY\s*[=:]\s*["\']?[A-Za-z0-9+/]{32,}'),
    re.compile(r'RUNPOD_API_KEY\s*[=:]\s*["\']?rpa_[A-Za-z0-9]{20,}'),
    re.compile(r'CLOUDFLARE_API_TOKEN\s*[=:]\s*["\']?[A-Za-z0-9_-]{30,}'),
    re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
)


# Files that legitimately contain a credential *indicator* because their job is
# to prove a scanner detects one. Named explicitly, never by a glob, and still
# required below to carry no key material — an exemption that could hide a real
# key would be worse than no scan.
INDICATOR_FIXTURES = frozenset({
    'tests/test_source_credentials.py',
    'tests/test_repository_hygiene.py',
})
# A PEM header followed by base64 body lines is key material; a bare header on
# its own is an indicator.
KEY_BODY = re.compile(
    r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----[^\n]*\n\s*[A-Za-z0-9+/]{40,}')


def git(*arguments):
    return subprocess.run(['git', *arguments], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def in_a_git_checkout():
    try:
        git('rev-parse', '--git-dir')
    except (OSError, subprocess.SubprocessError):
        return False
    return True


class IgnoreRuleTests(unittest.TestCase):
    """Layer one: Git is told to ignore the credential file."""

    def setUp(self):
        if not in_a_git_checkout():
            self.skipTest('not a Git checkout')

    def test_every_credential_path_is_ignored(self):
        for name in ('.env', '.env.local', '.env.production'):
            result = subprocess.run(['git', 'check-ignore', '-q', name],
                                    cwd=ROOT, capture_output=True)
            self.assertEqual(result.returncode, 0,
                             f'{name} is not covered by .gitignore')

    def test_the_live_credential_file_is_not_tracked(self):
        tracked = set(git('ls-files').splitlines())
        for name in tracked:
            self.assertFalse(forbidden(name),
                             f'a credential path is tracked in Git: {name}')
        self.assertNotIn('.env', tracked)


class TrackedContentTests(unittest.TestCase):
    """An ignore rule does nothing for a file already added with -f."""

    def setUp(self):
        if not in_a_git_checkout():
            self.skipTest('not a Git checkout')

    def tracked_text_files(self):
        for name in git('ls-files').splitlines():
            path = ROOT / name
            if not path.is_file() or path.stat().st_size > 4 * 1024**2:
                continue
            if path.suffix.lower() in {'.zip', '.whl', '.safetensors', '.gguf',
                                       '.png', '.jpg', '.pt', '.so', '.gz'}:
                continue
            try:
                yield name, path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue

    def test_no_tracked_text_file_contains_a_live_secret(self):
        findings = []
        for name, text in self.tracked_text_files():
            if name in INDICATOR_FIXTURES:
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(f'{name}: {pattern.pattern}')
        self.assertEqual(findings, [], 'tracked files appear to contain secrets')

    def test_no_tracked_file_contains_private_key_material(self):
        # Applies to the indicator fixtures too: they may name a PEM header,
        # never carry a key body. This is what keeps the exemption honest.
        findings = [name for name, text in self.tracked_text_files()
                    if KEY_BODY.search(text)]
        self.assertEqual(findings, [], 'tracked files contain key material')

    def test_every_exempted_fixture_still_exists(self):
        # A stale exemption silently widens the scan's blind spot. Existence on
        # disk is the property that matters; a newly added fixture may not be
        # tracked yet.
        missing = sorted(name for name in INDICATOR_FIXTURES
                         if not (ROOT / name).is_file())
        self.assertEqual(missing, [], 'stale credential-scan exemptions')

    def test_each_exemption_is_needed(self):
        # An exemption for a file with no indicator is clutter that would hide a
        # future one, so require each to actually trip a pattern.
        unnecessary = []
        for name in sorted(INDICATOR_FIXTURES):
            if name == 'tests/test_repository_hygiene.py':
                continue  # this file holds the patterns themselves
            text = (ROOT / name).read_text(encoding='utf-8')
            if not any(pattern.search(text) for pattern in SECRET_PATTERNS):
                unnecessary.append(name)
        self.assertEqual(unnecessary, [], 'exemptions that nothing needs')


class PublicationRefusalTests(unittest.TestCase):
    """Layers two and three: neither transport path will carry a credential."""

    def test_the_object_store_refuses_a_manifest_naming_a_credential(self):
        from tests.test_object_store import MemoryClient
        store = ArtifactStore(MemoryClient(), 'test-bucket')
        for name in CREDENTIAL_PATHS:
            manifest = validate_manifest({
                'schema_version': 1, 'kind': 'fixture', 'source': 'hygiene',
                'revision': '1',
                'files': [{'path': name, 'sha256': 'a' * 64, 'size_bytes': 1}]})
            with self.assertRaises(ValueError, msg=name) as caught:
                store.publish(ROOT, manifest)
            self.assertIn('credential or workspace metadata path excluded',
                          str(caught.exception))

    def test_shipment_refuses_every_credential_path(self):
        for name in CREDENTIAL_PATHS:
            self.assertTrue(forbidden(name), name)

    def test_shipment_does_not_over_refuse_ordinary_names(self):
        for name in ('environment.json', 'a.env', 'env/settings.py',
                     'configs/p1-serving.json', 'docs/21-cloud-preparation.md',
                     'gitignore', 'a/.github/workflows/ci.yml'):
            self.assertFalse(forbidden(name), name)


class CredentialFileTests(unittest.TestCase):
    """If the live credential file exists, it must be private to its owner."""

    def test_the_credential_file_is_not_world_readable(self):
        path = ROOT / '.env'
        if not path.is_file():
            self.skipTest('no .env in this checkout')
        mode = path.stat().st_mode & 0o077
        self.assertEqual(mode, 0, f'.env is group/world accessible: {oct(mode)}')


if __name__ == '__main__':
    unittest.main()
