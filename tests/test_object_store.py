"""Fault-injected object transport tests, separate from live R2 evidence."""

import errno
import io
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from zenithsync.artifacts import inventory, verify
from zenithsync.object_store import ArtifactStore, IntegrityError


class Missing(Exception):
    response = {"Error": {"Code": "NoSuchKey"}}


class MemoryClient:
    def __init__(self):
        self.objects = {}
        self.corrupt_upload = False
        self.uploads = 0
        self.reads = []

    def get_object(self, *, Bucket, Key):
        self.reads.append(Key)
        if Key not in self.objects:
            raise Missing()
        data = self.objects[Key]
        return {"ContentLength": len(data), "Body": io.BytesIO(data)}

    def upload_file(self, filename, bucket, key):
        self.uploads += 1
        data = Path(filename).read_bytes()
        self.objects[key] = b"X" * len(data) if self.corrupt_upload else data

    def put_object(self, *, Bucket, Key, Body, ContentType):
        self.objects[Key] = Body


class ObjectStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "a").write_bytes(b"synthetic fixture")
        (self.source / "empty").write_bytes(b"")
        self.manifest = inventory(self.source, kind="fixture", source="test", revision="1")
        self.client = MemoryClient()
        self.store = ArtifactStore(self.client, "test-bucket")

    def test_roundtrip_and_idempotent_retry(self):
        first = self.store.publish(self.source, self.manifest)
        second = self.store.publish(self.source, self.manifest)
        self.assertEqual(first["uploaded_files"], 2)
        self.assertEqual(second["reused_files"], 2)
        self.assertEqual(self.client.uploads, 2)
        dest = self.root / "restored"
        result = self.store.restore(self.manifest, dest, max_bytes=100)
        self.assertEqual(result["destination"], str(dest.resolve()))
        self.assertTrue(result["destination_verified"])
        verify(dest, self.manifest)

    def test_removed_promoted_destination_is_not_reported_as_verified(self):
        self.store.publish(self.source, self.manifest)
        dest = self.root / 'removed-after-promotion'
        original = Path.rename

        def remove_after_rename(source, target):
            result = original(source, target)
            shutil.rmtree(target)
            return result

        with patch.object(Path, 'rename', remove_after_rename):
            with self.assertRaises(ValueError):
                self.store.restore(self.manifest, dest, max_bytes=100)
        self.assertFalse(dest.exists())

    def test_relative_destination_does_not_follow_callback_cwd_change(self):
        self.store.publish(self.source, self.manifest)
        original = self.client.get_object
        alternate = self.root / 'other'
        alternate.mkdir()
        previous = Path.cwd()

        def change_cwd(**kwargs):
            os.chdir(alternate)
            return original(**kwargs)

        try:
            os.chdir(self.root)
            self.client.get_object = change_cwd
            result = self.store.restore(self.manifest, Path('restored'), max_bytes=100)
        finally:
            os.chdir(previous)
        verify(self.root / 'restored', self.manifest)
        self.assertFalse((alternate / 'restored').exists())
        self.assertEqual(result['destination'], str(self.root.resolve() / 'restored'))

    def test_corrupt_upload_cannot_commit_manifest(self):
        self.client.corrupt_upload = True
        with self.assertRaises(IntegrityError):
            self.store.publish(self.source, self.manifest)
        self.assertFalse(any("/manifests/" in k for k in self.client.objects))

    def test_corrupt_restore_cannot_expose_partial_bundle(self):
        self.store.publish(self.source, self.manifest)
        row = self.manifest["files"][0]
        self.client.objects[self.store.blob_key(row["sha256"])] = b"X" * row["size_bytes"]
        dest = self.root / "restored"
        with self.assertRaises(IntegrityError):
            self.store.restore(self.manifest, dest, max_bytes=100)
        self.assertFalse(dest.exists())
        self.assertEqual(list(self.root.glob(".restore-*")), [])

    def test_existing_output_and_budget_protected(self):
        with self.assertRaises(FileExistsError):
            self.store.restore(self.manifest, self.source, max_bytes=100)
        with self.assertRaises(ValueError):
            self.store.restore(self.manifest, self.root / "too-large", max_bytes=1)
        self.assertEqual(self.client.uploads, 0)

    def test_insufficient_disk_rejected_before_download(self):
        destination = self.root / 'no-space'
        usage = shutil.disk_usage(self.root)._replace(free=0)
        with patch('zenithsync.object_store.shutil.disk_usage', return_value=usage), \
                patch.object(self.client, 'get_object') as get:
            with self.assertRaises(OSError) as raised:
                self.store.restore(self.manifest, destination, max_bytes=100)
            self.assertEqual(raised.exception.errno, errno.ENOSPC)
            get.assert_not_called()
        self.assertFalse(destination.exists())
        self.assertEqual(list(self.root.glob('.restore-*')), [])

    def test_midstream_disconnect_closes_body_and_allows_clean_retry(self):
        self.store.publish(self.source, self.manifest)
        original = self.client.get_object
        bodies = []

        class InterruptedBody(io.BytesIO):
            def read(self, size=-1):
                if self.tell():
                    raise ConnectionError('synthetic midstream disconnect')
                return super().read(1)

        def interrupted(**kwargs):
            response = original(**kwargs)
            if response['ContentLength']:
                data = response['Body'].read()
                response['Body'].close()
                response['Body'] = InterruptedBody(data)
                bodies.append(response['Body'])
            return response

        destination = self.root / 'interrupted'
        with patch.object(self.client, 'get_object', side_effect=interrupted):
            with self.assertRaises(ConnectionError):
                self.store.restore(self.manifest, destination, max_bytes=100)
        self.assertTrue(bodies)
        self.assertTrue(all(body.closed for body in bodies))
        self.assertFalse(destination.exists())
        self.assertEqual(list(self.root.glob('.restore-*')), [])
        self.store.restore(self.manifest, destination, max_bytes=100)
        verify(destination, self.manifest)

    def test_disk_exhaustion_during_fsync_never_promotes_bundle(self):
        self.store.publish(self.source, self.manifest)
        destination = self.root / 'disk-exhausted'
        with patch('zenithsync.object_store.os.fsync',
                   side_effect=OSError(errno.ENOSPC, 'synthetic disk exhaustion')):
            with self.assertRaises(OSError) as raised:
                self.store.restore(self.manifest, destination, max_bytes=100)
            self.assertEqual(raised.exception.errno, errno.ENOSPC)
        self.assertFalse(destination.exists())
        self.assertEqual(list(self.root.glob('.restore-*')), [])
        self.store.restore(self.manifest, destination, max_bytes=100)
        verify(destination, self.manifest)

    def test_source_drift_is_rejected_before_upload(self):
        (self.source / "a").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.store.publish(self.source, self.manifest)
        self.assertEqual(self.client.objects, {})

    def test_credential_paths_rejected(self):
        (self.source / ".env").write_bytes(b"synthetic excluded file")
        manifest = inventory(self.source, kind="fixture", source="test", revision="1")
        with self.assertRaises(ValueError):
            self.store.publish(self.source, manifest)
        self.assertEqual(self.client.objects, {})

    def test_access_error_does_not_trigger_overwrite(self):
        def denied(**kwargs):
            raise PermissionError("synthetic denial")
        self.client.get_object = denied
        with self.assertRaises(PermissionError):
            self.store.publish(self.source, self.manifest)
        self.assertEqual(self.client.uploads, 0)

    def test_interrupted_publication_reuses_only_verified_completed_objects(self):
        original = self.client.upload_file

        def interrupted(filename, bucket, key):
            original(filename, bucket, key)
            raise ConnectionError('synthetic failure after remote object completion')

        self.client.upload_file = interrupted
        with self.assertRaises(ConnectionError):
            self.store.publish(self.source, self.manifest)
        self.assertEqual(len(self.client.objects), 1)
        self.assertFalse(any('/manifests/' in key for key in self.client.objects))
        self.client.upload_file = original
        # A fresh transport instance has no in-process knowledge of prior progress.
        retry = ArtifactStore(self.client, 'test-bucket')
        result = retry.publish(self.source, self.manifest)
        self.assertEqual(result['reused_files'], 1)
        self.assertEqual(result['uploaded_files'], 1)
        self.assertEqual(self.client.uploads, 2)
        retry.restore(self.manifest, self.root / 'recovered', max_bytes=100)
        verify(self.root / 'recovered', self.manifest)

    def test_lost_manifest_acknowledgement_is_idempotent(self):
        original = self.client.put_object
        calls = []

        def lost_ack(**kwargs):
            calls.append(kwargs['Key'])
            original(**kwargs)
            raise ConnectionError('synthetic lost acknowledgement after commit')

        self.client.put_object = lost_ack
        with self.assertRaises(ConnectionError):
            self.store.publish(self.source, self.manifest)
        self.assertEqual(len(calls), 1)
        retry = ArtifactStore(self.client, 'test-bucket')
        result = retry.publish(self.source, self.manifest)
        self.assertEqual(result['uploaded_files'], 0)
        self.assertEqual(result['reused_files'], 2)
        self.assertEqual(len(calls), 1)
        self.assertIn(result['manifest_key'], self.client.objects)


if __name__ == "__main__":
    unittest.main()


class VerifyOncePerRunTests(unittest.TestCase):
    """A hot content-addressed key is what R2 refuses; dedup must be opt-in."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Two bundles sharing identical bytes, so they share one blob key.
        for name in ("one", "two"):
            tree = self.root / name
            tree.mkdir()
            (tree / "shared").write_bytes(b"identical bytes")
        self.manifests = {
            name: inventory(self.root / name, kind="fixture",
                            source="test", revision="1")
            for name in ("one", "two")}
        self.client = MemoryClient()

    def shared_key(self):
        store = ArtifactStore(self.client, "test-bucket")
        return store.blob_key(self.manifests["one"]["files"][0]["sha256"])

    def test_default_reads_the_shared_key_for_every_bundle(self):
        store = ArtifactStore(self.client, "test-bucket")
        for name in ("one", "two"):
            store.publish(self.root / name, self.manifests[name])
        key = self.shared_key()
        # Bundle one: a miss, then a post-upload verify. Bundle two: another
        # read, because without dedup every bundle rests on its own.
        self.assertEqual(self.client.reads.count(key), 3)

    def test_opt_in_reads_the_shared_key_once_after_upload(self):
        store = ArtifactStore(self.client, "test-bucket",
                              verify_once_per_run=True)
        for name in ("one", "two"):
            store.publish(self.root / name, self.manifests[name])
        key = self.shared_key()
        self.assertEqual(self.client.reads.count(key), 2)
        self.assertTrue(store.verify_once_per_run)

    def test_a_separate_store_does_not_inherit_the_verified_set(self):
        first = ArtifactStore(self.client, "test-bucket",
                              verify_once_per_run=True)
        first.publish(self.root / "one", self.manifests["one"])
        self.client.reads.clear()
        second = ArtifactStore(self.client, "test-bucket",
                               verify_once_per_run=True)
        second.publish(self.root / "two", self.manifests["two"])
        self.assertIn(self.shared_key(), self.client.reads)

    def test_a_failed_digest_is_never_recorded_as_verified(self):
        store = ArtifactStore(self.client, "test-bucket",
                              verify_once_per_run=True)
        self.client.corrupt_upload = True
        with self.assertRaises(IntegrityError):
            store.publish(self.root / "one", self.manifests["one"])
        # The corrupt object must not be remembered as clean: a second attempt
        # has to read it again and fail again.
        self.client.reads.clear()
        with self.assertRaises(IntegrityError):
            store.publish(self.root / "one", self.manifests["one"])
        self.assertIn(self.shared_key(), self.client.reads)

    def test_a_restore_still_transfers_bytes_after_a_verified_publish(self):
        store = ArtifactStore(self.client, "test-bucket",
                              verify_once_per_run=True)
        store.publish(self.root / "one", self.manifests["one"])
        self.client.reads.clear()
        destination = self.root / "restored"
        store.restore(self.manifests["one"], destination, max_bytes=1000)
        # A read with a target must never be skipped, or the destination would
        # be missing the file the manifest promises.
        self.assertIn(self.shared_key(), self.client.reads)
        verify(destination, self.manifests["one"])

    def test_the_verified_set_is_shared_safely_across_threads(self):
        store = ArtifactStore(self.client, "test-bucket",
                              verify_once_per_run=True)
        store.publish(self.root / "one", self.manifests["one"])
        errors = []

        def publish():
            try:
                store.publish(self.root / "two", self.manifests["two"])
            except Exception as error:  # pragma: no cover - failure path
                errors.append(error)

        threads = [threading.Thread(target=publish) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])


class OneWriterPerKeyTests(unittest.TestCase):
    """Duplicate bytes share a key; two workers must not write it at once."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("one", "two", "three", "four"):
            tree = self.root / name
            tree.mkdir()
            (tree / "shared").write_bytes(b"identical bytes across bundles")
        self.manifests = {
            name: inventory(self.root / name, kind="fixture",
                            source="test", revision="1")
            for name in ("one", "two", "three", "four")}

    def test_concurrent_bundles_never_write_one_key_simultaneously(self):
        overlaps = []

        class CountingClient(MemoryClient):
            def __init__(self):
                super().__init__()
                self.active = {}
                self.guard = threading.Lock()

            def _enter(self, key):
                with self.guard:
                    self.active[key] = self.active.get(key, 0) + 1
                    if self.active[key] > 1:
                        overlaps.append(key)

            def _leave(self, key):
                with self.guard:
                    self.active[key] -= 1

            def upload_file(self, filename, bucket, key):
                self._enter(key)
                try:
                    time.sleep(0.02)
                    super().upload_file(filename, bucket, key)
                finally:
                    self._leave(key)

            def put_object(self, *, Bucket, Key, Body, ContentType):
                self._enter(Key)
                try:
                    time.sleep(0.02)
                    super().put_object(Bucket=Bucket, Key=Key, Body=Body,
                                       ContentType=ContentType)
                finally:
                    self._leave(Key)

        client = CountingClient()
        store = ArtifactStore(client, "test-bucket")
        errors = []

        def publish(name):
            try:
                store.publish(self.root / name, self.manifests[name])
            except Exception as error:  # pragma: no cover - failure path
                errors.append(error)

        threads = [threading.Thread(target=publish, args=(name,))
                   for name in self.manifests]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(overlaps, [])
        # Exactly one worker uploaded the shared blob; the rest reused it.
        self.assertEqual(client.uploads, 1)

    def test_distinct_keys_are_not_serialised_behind_one_another(self):
        store = ArtifactStore(MemoryClient(), "test-bucket")
        first = store._one_writer_per_key("a")
        with first:
            # A different key must be available while 'a' is held, or the whole
            # run would be effectively single-threaded.
            with store._one_writer_per_key("b"):
                pass

    def test_an_upload_failure_releases_the_key(self):
        class FailingClient(MemoryClient):
            def upload_file(self, filename, bucket, key):
                raise RuntimeError("upload refused")

        store = ArtifactStore(FailingClient(), "test-bucket")
        with self.assertRaises(RuntimeError):
            store.publish(self.root / "one", self.manifests["one"])
        # The lock must not be held after the failure, or every later bundle
        # touching this key would block forever instead of reporting an error.
        key = store.blob_key(self.manifests["one"]["files"][0]["sha256"])
        with store._one_writer_per_key(key):
            pass
