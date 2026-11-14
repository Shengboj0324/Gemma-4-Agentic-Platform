import io
from pathlib import Path
import tempfile
import threading
import unittest
import zipfile

from tests.test_object_store import MemoryClient
from zenithsync.artifacts import validate_manifest
from zenithsync.kaggle_ingest import ingest, materialise, normalise_listing
from zenithsync.object_store import ArtifactStore


FILES = {'tasks.jsonl': b'{"id": 1}\n', 'snapshots/a.tgz': b'A' * 3000, 'wheels/x.whl': b'PK\x03\x04wheel'}


class FakeKaggle:
    """Serves FILES; zips some, as Kaggle does for compressible files."""

    def __init__(self, zipped=(), corrupt=()):
        self.zipped, self.corrupt = set(zipped), set(corrupt)
        self.live = 0
        self.peak = 0
        self.lock = threading.Lock()

    def fetch(self, path, directory):
        name = Path(path).name
        data = FILES[path] + (b'!' if path in self.corrupt else b'')
        if path in self.zipped:
            with zipfile.ZipFile(directory / (name + '.zip'), 'w') as archive:
                archive.writestr(name, data)
        else:
            (directory / name).write_bytes(data)
        with self.lock:
            self.live += 1
            self.peak = max(self.peak, self.live)


class KaggleIngestTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.scratch = Path(temp.name)
        self.listing = [{'path': p, 'size_bytes': len(b)} for p, b in FILES.items()]

    def test_streams_every_file_with_readback_and_leaves_nothing_behind(self):
        client = MemoryClient()
        store = ArtifactStore(client, 'b', verify_once_per_run=True)
        records, uploaded = ingest(self.listing, FakeKaggle(zipped={'tasks.jsonl'}).fetch, store,
                                   self.scratch, workers=2, log=lambda _: None)
        self.assertEqual(uploaded, 3)
        self.assertEqual([r['path'] for r in records], sorted(FILES))
        manifest = validate_manifest({'schema_version': 1, 'kind': 'harness', 'source': 's',
                                      'revision': 'r', 'files': records})
        shipment = store.commit_manifest(manifest)
        self.assertEqual(shipment['verified_bytes'], sum(len(b) for b in FILES.values()))
        self.assertEqual(list(self.scratch.iterdir()), [])  # nothing kept locally
        restored = self.scratch / 'restored'
        store.restore(manifest, restored, max_bytes=10**6)
        for path, data in FILES.items():
            self.assertEqual((restored / path).read_bytes(), data)

    def test_size_mismatch_fails_and_commits_nothing(self):
        client = MemoryClient()
        store = ArtifactStore(client, 'b')
        with self.assertRaisesRegex(ValueError, 'Size differs'):
            ingest(self.listing, FakeKaggle(corrupt={'wheels/x.whl'}).fetch, store,
                   self.scratch, workers=1, log=lambda _: None)
        self.assertFalse(any('/manifests/' in key for key in client.objects))

    def test_listing_and_zip_wrappers_are_strict(self):
        for rows in ([], [('a', 1), ('a', 1)], [('../x', 1)], [('a', -1)], [('a', 1.0)]):
            with self.assertRaises(ValueError):
                normalise_listing(rows)
        directory = self.scratch / 'z'
        directory.mkdir()
        with zipfile.ZipFile(directory / 'f.txt.zip', 'w') as archive:
            archive.writestr('f.txt', b'one')
            archive.writestr('g.txt', b'two')
        with self.assertRaisesRegex(ValueError, 'zip wrapper'):
            materialise(directory, 'f.txt')
        with self.assertRaisesRegex(ValueError, 'neither'):
            materialise(directory, 'missing.txt')
        # A wheel is a zip: delivered under its own name it is kept byte for byte.
        with zipfile.ZipFile(directory / 'pkg-1.0-py3-none-any.whl', 'w') as archive:
            archive.writestr('pkg/__init__.py', b'x')
        wheel = (directory / 'pkg-1.0-py3-none-any.whl').read_bytes()
        self.assertEqual(materialise(directory, 'wheels/pkg-1.0-py3-none-any.whl').read_bytes(), wheel)
        # A real .zip in the listing is likewise kept as delivered.
        with zipfile.ZipFile(directory / 'real.zip', 'w') as archive:
            archive.writestr('inner', b'x')
        self.assertEqual(materialise(directory, 'real.zip'), directory / 'real.zip')


if __name__ == '__main__':
    unittest.main()
