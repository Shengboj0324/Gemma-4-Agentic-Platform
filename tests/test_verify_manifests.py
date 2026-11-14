from pathlib import Path
import tempfile
import unittest

from scripts.verify_manifests import check
from zenithsync.artifacts import inventory


class VerifyManifestsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name) / 'devset'
        (root / 'snapshots').mkdir(parents=True)
        (root / 'tasks.jsonl').write_text('{"instance_id": "a"}\n')
        (root / 'snapshots' / 'a.tgz').write_bytes(b'tgz')
        full = inventory(root, kind='harness', source='s', revision='r')
        core = {**full, 'files': [f for f in full['files'] if not f['path'].startswith('snapshots/')]}
        snaps = {**full, 'files': [f for f in full['files'] if f['path'].startswith('snapshots/')]}
        self.root = root
        self.bundle = {'core': {'dest': '/mnt/data/devset', 'manifest': core},
                       'snapshots': {'dest': '/mnt/data/devset', 'manifest': snaps}}
        self.remap = {'/mnt/data/devset': str(root)}

    def tearDown(self):
        self.directory.cleanup()

    def test_manifests_sharing_a_destination_are_verified_as_their_union(self):
        report = check(self.bundle, self.remap)
        self.assertEqual(report[str(self.root)], {'manifests': ['core', 'snapshots'], 'files': 2})

    def test_a_tampered_or_extra_file_fails(self):
        (self.root / 'tasks.jsonl').write_text('{"instance_id": "b"}\n')
        with self.assertRaises(ValueError):
            check(self.bundle, self.remap)

    def test_an_extra_file_fails(self):
        (self.root / 'snapshots' / 'planted.tgz').write_bytes(b'x')
        with self.assertRaises(ValueError):
            check(self.bundle, self.remap)


if __name__ == '__main__':
    unittest.main()
