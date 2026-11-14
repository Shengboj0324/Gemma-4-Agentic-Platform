import io
from pathlib import Path
import tempfile
import threading
import unittest
import zipfile

from tests.test_object_store import MemoryClient
from zenithsync.artifacts import validate_manifest
from zenithsync.kaggle_ingest import fetch_with_retries, ingest, materialise, normalise_listing, retryable
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



class Response:
    def __init__(self, status):
        self.status_code = status


class HTTPError(Exception):
    def __init__(self, status):
        super().__init__(f'{status} error')
        self.response = Response(status)


class RetryTests(unittest.TestCase):
    def test_rate_limits_are_retried_with_backoff_and_partial_files_cleared(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            calls, sleeps = [], []
            def fetch(path, target):
                calls.append(sorted(p.name for p in target.iterdir()))
                (target / 'partial').write_bytes(b'x')
                if len(calls) < 3:
                    raise HTTPError(429)
            fetch_with_retries(fetch, 'f', directory, sleep=sleeps.append)
            self.assertEqual(calls, [[], [], []])  # each attempt starts clean
            self.assertEqual(sleeps, [2.0, 4.0])

    def test_permanent_errors_and_exhaustion_propagate(self):
        with tempfile.TemporaryDirectory() as directory:
            def forbidden(path, target):
                raise HTTPError(403)
            with self.assertRaises(HTTPError):
                fetch_with_retries(forbidden, 'f', Path(directory), sleep=lambda s: None)
            attempts = []
            def always_busy(path, target):
                attempts.append(1)
                raise HTTPError(503)
            with self.assertRaises(HTTPError):
                fetch_with_retries(always_busy, 'f', Path(directory), attempts=4, sleep=lambda s: None)
            self.assertEqual(len(attempts), 4)
        self.assertTrue(retryable(ConnectionError()))
        self.assertFalse(retryable(ValueError()))



class ZipIngestTests(unittest.TestCase):
    def test_archive_ingest_resumes_from_the_journal_without_refetching(self):
        import io as _io
        from zenithsync.kaggle_ingest import Journal, ingest_zip
        buffer = _io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in FILES.items():
                archive.writestr(name, data)
        listing = [{'path': p, 'size_bytes': len(b)} for p, b in FILES.items()]
        opened = []
        def open_archive():
            opened.append(1)
            return zipfile.ZipFile(_io.BytesIO(buffer.getvalue()))
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            client = MemoryClient()
            store = ArtifactStore(client, 'b')
            journal = Journal(directory / 'journal.jsonl')
            records, uploaded = ingest_zip(listing[:2], open_archive, store, directory, journal=journal,
                                           workers=2, log=lambda _: None)
            self.assertEqual(uploaded, 2)
            resumed = Journal(directory / 'journal.jsonl')
            self.assertEqual(len(resumed.records), 2)
            uploads_before = client.uploads
            records, uploaded = ingest_zip(listing, open_archive, store, directory, journal=resumed,
                                           workers=2, log=lambda _: None)
            self.assertEqual((uploaded, client.uploads - uploads_before), (1, 1))  # only the new file
            self.assertEqual([r['path'] for r in records], sorted(FILES))
            self.assertEqual(sorted(p.name for p in directory.iterdir()), ['journal.jsonl'])
            manifest = validate_manifest({'schema_version': 1, 'kind': 'harness', 'source': 's',
                                          'revision': 'r', 'files': records})
            store.commit_manifest(manifest)
            bad = [dict(listing[0], size_bytes=listing[0]['size_bytes'] + 1)]
            with self.assertRaisesRegex(ValueError, 'differs'):
                ingest_zip(bad, open_archive, store, directory, journal=Journal(directory / 'j2.jsonl'),
                           workers=1, log=lambda _: None)


if __name__ == '__main__':
    unittest.main()
