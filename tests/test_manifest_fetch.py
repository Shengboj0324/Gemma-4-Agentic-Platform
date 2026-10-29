"""A manifest fetched from the bucket must be the one that was asked for."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

fetch_module = None
if importlib.util.find_spec('boto3') is not None:
    import fetch_manifest_from_r2 as fetch_module


class StubClient:
    def __init__(self, objects, *, truncate=False, overstate=False):
        self.objects = objects
        self.truncate = truncate
        self.overstate = overstate

    def get_object(self, *, Bucket, Key):
        if Key not in self.objects:
            raise KeyError(Key)
        data = self.objects[Key]
        declared = len(data) + 16 if self.overstate else len(data)
        body = io.BytesIO(data[:-1] if self.truncate else data)
        return {'ContentLength': declared, 'Body': body}


@unittest.skipUnless(importlib.util.find_spec('boto3'), 'boto3 is required')
class FetchTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.dumps({'files': []}, sort_keys=True).encode()
        self.digest = hashlib.sha256(self.payload).hexdigest()
        self.key = f'artifacts/v1/manifests/sha256/{self.digest}.json'
        self.objects = {self.key: self.payload}

    def fetch(self, client, *, expected=None, max_bytes=1024):
        return fetch_module.fetch(client, 'bucket', self.key,
                                  expected_sha256=expected or self.digest,
                                  max_bytes=max_bytes)

    def test_the_expected_manifest_comes_back_byte_identical(self):
        got = self.fetch(StubClient(self.objects))
        self.assertEqual(got, self.payload)
        self.assertEqual(hashlib.sha256(got).hexdigest(), self.digest)

    def test_a_different_digest_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'digest differs'):
            self.fetch(StubClient(self.objects), expected='0' * 64)

    def test_a_manifest_over_the_ceiling_is_refused_before_reading(self):
        with self.assertRaisesRegex(ValueError, 'over the'):
            self.fetch(StubClient(self.objects), max_bytes=4)

    def test_a_short_stream_is_refused_rather_than_accepted(self):
        with self.assertRaisesRegex(ValueError, 'shorter than it declared'):
            self.fetch(StubClient(self.objects, truncate=True))

    def test_a_stream_longer_than_declared_is_refused(self):
        # ContentLength under the real size must not let extra bytes through.
        key = self.key
        objects = {key: self.payload}

        class Overlong(StubClient):
            def get_object(self, *, Bucket, Key):
                return {'ContentLength': 4, 'Body': io.BytesIO(objects[Key])}

        with self.assertRaisesRegex(ValueError, 'exceeds declared size'):
            self.fetch(Overlong(objects))

    def test_an_unusable_declared_length_is_refused(self):
        class NoLength(StubClient):
            def get_object(self, *, Bucket, Key):
                return {'Body': io.BytesIO(self.objects[Key])}

        with self.assertRaisesRegex(ValueError, 'no usable length'):
            self.fetch(NoLength(self.objects))

    def test_the_body_is_closed_even_when_the_digest_is_wrong(self):
        closed = []

        class TrackedBody(io.BytesIO):
            def close(self):
                closed.append(True)
                super().close()

        class Tracking(StubClient):
            def get_object(self, *, Bucket, Key):
                data = self.objects[Key]
                return {'ContentLength': len(data), 'Body': TrackedBody(data)}

        with self.assertRaises(ValueError):
            self.fetch(Tracking(self.objects), expected='1' * 64)
        self.assertEqual(closed, [True])


@unittest.skipUnless(importlib.util.find_spec('boto3'), 'boto3 is required')
class SurfaceTests(unittest.TestCase):
    def test_the_exit_codes_are_distinct_and_documented(self):
        codes = {fetch_module.EXIT_FETCHED, fetch_module.EXIT_DIGEST_MISMATCH,
                 fetch_module.EXIT_BAD_ARGUMENTS, fetch_module.EXIT_RUN_FAILED}
        self.assertEqual(len(codes), 4)
        self.assertEqual(fetch_module.EXIT_FETCHED, 0)
        for name in ('bootstrap', 'digest'):
            self.assertIn(name, fetch_module.__doc__)

    def test_the_ceiling_matches_the_loader_s_manifest_ceiling(self):
        from zenithsync.corpus_audit import MANIFEST_MAX_BYTES
        self.assertEqual(fetch_module.MAX_MANIFEST_BYTES, MANIFEST_MAX_BYTES)


if __name__ == '__main__':
    unittest.main()
