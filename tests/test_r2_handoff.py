import hashlib
import io
import unittest

from scripts.r2_handoff import blob_key, check_key, part_ranges, stream_digest


class R2HandoffTests(unittest.TestCase):
    def test_keys_are_confined(self):
        check_key('artifacts/v1/tmp/x/results.tar')
        check_key('artifacts/v1/runs/screen-1.tar')
        for bad in ('artifacts/v1/blobs/sha256/x', 'artifacts/v1/tmp/../blobs/x', 'other/x'):
            with self.assertRaises(ValueError):
                check_key(bad)

    def test_blob_keys_come_only_from_digests(self):
        digest = 'a' * 64
        self.assertEqual(blob_key(digest), 'artifacts/v1/blobs/sha256/' + digest)
        for bad in ('A' * 64, 'a' * 63, '../' + 'a' * 61, 'g' * 64):
            with self.assertRaises(ValueError):
                blob_key(bad)

    def test_parts_cover_the_object_exactly(self):
        for size in (1, 10, 11, 100):
            parts = part_ranges(size, part_size=10)
            self.assertEqual([p[0] for p in parts], list(range(1, len(parts) + 1)))
            self.assertEqual(parts[0][1], 0)
            self.assertEqual(parts[-1][2], size - 1)
            for (_, _, end), (_, start, _) in zip(parts, parts[1:]):
                self.assertEqual(start, end + 1)
            self.assertTrue(all(b - a + 1 == 10 for _, a, b in parts[:-1]))
        self.assertEqual(len(part_ranges(11513861828)), 22)
        with self.assertRaises(ValueError):
            part_ranges(0)

    def test_digest_streams_without_holding_the_object(self):
        data = b'x' * (3 * 1024 * 1024 + 7)
        digest, size = stream_digest(io.BytesIO(data), chunk=1024 * 1024)
        self.assertEqual((digest, size), (hashlib.sha256(data).hexdigest(), len(data)))


if __name__ == '__main__':
    unittest.main()
