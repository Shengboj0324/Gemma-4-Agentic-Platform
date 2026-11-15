import hashlib
import io
import unittest

from scripts.r2_handoff import check_key, stream_digest


class R2HandoffTests(unittest.TestCase):
    def test_keys_are_confined(self):
        check_key('artifacts/v1/tmp/x/results.tar')
        check_key('artifacts/v1/runs/screen-1.tar')
        for bad in ('artifacts/v1/blobs/sha256/x', 'artifacts/v1/tmp/../blobs/x', 'other/x'):
            with self.assertRaises(ValueError):
                check_key(bad)

    def test_digest_streams_without_holding_the_object(self):
        data = b'x' * (3 * 1024 * 1024 + 7)
        digest, size = stream_digest(io.BytesIO(data), chunk=1024 * 1024)
        self.assertEqual((digest, size), (hashlib.sha256(data).hexdigest(), len(data)))


if __name__ == '__main__':
    unittest.main()
