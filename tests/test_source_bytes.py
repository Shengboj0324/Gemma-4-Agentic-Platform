import hashlib
from pathlib import Path
import tempfile
import unittest

from zenithsync.source_bytes import verified_source_bytes


class SourceBytesTests(unittest.TestCase):
    def test_changed_truncated_and_extended_inputs_are_rejected(self):
        original = b'pinned source'
        identity = {'size_bytes': len(original), 'sha256': hashlib.sha256(original).hexdigest()}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source'
            for changed in (b'changed bytes', original[:-1], original + b'x'):
                path.write_bytes(changed)
                with self.assertRaisesRegex(ValueError, 'differ from pinned identity'):
                    verified_source_bytes(path, identity, max_bytes=100)

    def test_budget_rejected_before_open(self):
        identity = {'size_bytes': 20, 'sha256': '0' * 64}
        with self.assertRaisesRegex(ValueError, 'exceeds byte budget'):
            verified_source_bytes(Path('/nonexistent/source'), identity, max_bytes=19)

    def test_parser_snapshot_survives_path_replacement(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest('PyArrow is required for the actual Parquet parser check')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.parquet'
            pq.write_table(pa.table({'task': ['one', 'two'], 'value': [3, 7]}), path)
            original = path.read_bytes()
            identity = {'size_bytes': len(original), 'sha256': hashlib.sha256(original).hexdigest()}
            payload = verified_source_bytes(path, identity, max_bytes=100_000)
            path.write_bytes(b'not a parquet file')
            result = pq.read_table(pa.BufferReader(payload), columns=['value'],
                                   filters=[('task', '=', 'two')]).to_pylist()
            self.assertEqual(result, [{'value': 7}])
            with self.assertRaisesRegex(ValueError, 'differ from pinned identity'):
                verified_source_bytes(path, identity, max_bytes=100_000)


if __name__ == '__main__':
    unittest.main()
