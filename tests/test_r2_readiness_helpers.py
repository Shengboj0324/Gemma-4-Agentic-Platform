"""The readiness check's two remote helpers must verify, not trust, what R2 says."""

import importlib.util
from pathlib import Path
import unittest

from zenithsync.object_store import ArtifactStore

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/verify_r2_training_readiness.py'


def load_script():
    """Import the CLI module without running it, so its helpers can be tested."""
    specification = importlib.util.spec_from_file_location(
        'verify_r2_training_readiness', SCRIPT)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def heading_client():
    """The shared memory client plus the `head_object` the readiness check needs.

    Subclassed rather than added to the shared fixture, so the object store's own
    tests keep exercising exactly the four operations it is allowed to use.
    """
    from tests.test_object_store import MemoryClient, Missing

    class HeadingMemoryClient(MemoryClient):
        def head_object(self, *, Bucket, Key):
            if Key not in self.objects:
                raise Missing()
            return {'ContentLength': len(self.objects[Key])}

    return HeadingMemoryClient()


class ReadinessHelperTests(unittest.TestCase):
    def setUp(self):
        self.module = load_script()
        self.client = heading_client()
        self.store = ArtifactStore(self.client, 'test-bucket', prefix='artifacts/v1')
        self.payload = b'synthetic tokenizer asset'
        import hashlib
        self.identity = {'sha256': hashlib.sha256(self.payload).hexdigest(),
                         'size_bytes': len(self.payload)}
        self.client.objects[self.store.blob_key(self.identity['sha256'])] = self.payload

    # --- fetch_blob -----------------------------------------------------------

    def test_a_matching_blob_is_returned_with_its_verified_identity(self):
        result = self.module.fetch_blob(self.client, 'test-bucket', self.store,
                                        self.identity, max_bytes=10**6)
        self.assertEqual(result, self.identity)

    def test_a_blob_whose_bytes_differ_is_refused(self):
        key = self.store.blob_key(self.identity['sha256'])
        self.client.objects[key] = b'X' * len(self.payload)
        with self.assertRaisesRegex(ValueError, 'digest or size differs'):
            self.module.fetch_blob(self.client, 'test-bucket', self.store,
                                   self.identity, max_bytes=10**6)

    def test_a_blob_longer_than_declared_is_refused_mid_stream(self):
        key = self.store.blob_key(self.identity['sha256'])
        self.client.objects[key] = self.payload + b'extra'
        with self.assertRaisesRegex(ValueError, 'exceeds its declared size'):
            self.module.fetch_blob(self.client, 'test-bucket', self.store,
                                   self.identity, max_bytes=10**6)

    def test_a_blob_shorter_than_declared_is_refused(self):
        key = self.store.blob_key(self.identity['sha256'])
        self.client.objects[key] = self.payload[:-1]
        with self.assertRaisesRegex(ValueError, 'digest or size differs'):
            self.module.fetch_blob(self.client, 'test-bucket', self.store,
                                   self.identity, max_bytes=10**6)

    def test_the_fetch_ceiling_is_checked_before_any_request(self):
        with self.assertRaisesRegex(ValueError, 'declared fetch ceiling'):
            self.module.fetch_blob(self.client, 'test-bucket', self.store,
                                   self.identity, max_bytes=1)

    # --- check_blob_present ---------------------------------------------------

    def test_presence_is_confirmed_from_metadata_without_downloading(self):
        reads = []
        original = self.client.get_object

        def record(**kwargs):
            reads.append(kwargs)
            return original(**kwargs)

        self.client.get_object = record
        result = self.module.check_blob_present(self.client, 'test-bucket',
                                                self.store, self.identity)
        self.assertEqual(result['sha256'], self.identity['sha256'])
        self.assertEqual(result['size_bytes'], self.identity['size_bytes'])
        self.assertEqual(result['verified_by'], 'remote_metadata_only')
        # A 21 GiB checkpoint must not be streamed by a readiness check.
        self.assertEqual(reads, [])

    def test_a_declared_length_mismatch_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'length differs from the manifest'):
            self.module.check_blob_present(
                self.client, 'test-bucket', self.store,
                {'sha256': self.identity['sha256'], 'size_bytes': 999})

    def test_an_absent_blob_raises_rather_than_passing(self):
        with self.assertRaises(Exception):
            self.module.check_blob_present(
                self.client, 'test-bucket', self.store,
                {'sha256': 'a' * 64, 'size_bytes': 1})


if __name__ == '__main__':
    unittest.main()
