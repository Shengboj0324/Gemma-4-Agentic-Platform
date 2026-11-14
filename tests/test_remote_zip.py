import io
from pathlib import Path
import tempfile
import unittest
import zipfile
import zlib

from zenithsync.remote_zip import HTTPRangeReader, extract_member


class Response:
    def __init__(self, status, content=b'', headers=None):
        self.status_code, self.content, self.headers = status, content, headers or {}

    def raise_for_status(self):
        raise RuntimeError(f'HTTP {self.status_code}')


class RangeSession:
    """Serves `data` honouring Range; counts requests and bytes sent."""

    def __init__(self, data, honour=True):
        self.data, self.honour = data, honour
        self.requests = 0
        self.sent = 0

    def get(self, url, headers, timeout):
        self.requests += 1
        start, end = (int(x) for x in headers['Range'].split('=')[1].split('-'))
        if not self.honour:
            return Response(200, self.data)
        body = self.data[start:end + 1]
        self.sent += len(body)
        return Response(206, body, {'Content-Range': f'bytes {start}-{end}/{len(self.data)}'})


class RemoteZipTests(unittest.TestCase):
    def setUp(self):
        buffer = io.BytesIO()
        self.members = {'tasks.jsonl': b'{"a":1}\n' * 1000,
                        'snapshots/x.tgz': bytes(range(256)) * 4000,
                        'wheels/p-1.0-py3-none-any.whl': b'PK\x03\x04' + b'w' * 50}
        with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in self.members.items():
                archive.writestr(name, data)
        self.data = buffer.getvalue()

    def test_members_stream_through_ranges_without_fetching_everything_at_once(self):
        session = RangeSession(self.data)
        reader = HTTPRangeReader('https://x', session=session, block=4096)
        self.assertEqual(reader.size, len(self.data))
        with tempfile.TemporaryDirectory() as directory, zipfile.ZipFile(reader) as archive:
            self.assertEqual(sorted(archive.namelist()), sorted(self.members))
            for info in archive.infolist():
                out = extract_member(archive, info, Path(directory) / info.filename.replace('/', '_'))
                self.assertEqual(out.read_bytes(), self.members[info.filename])
        self.assertGreater(session.requests, 3)

    def test_a_server_ignoring_ranges_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'range'):
            HTTPRangeReader('https://x', session=RangeSession(self.data, honour=False))

    def test_corruption_is_caught_by_the_member_crc(self):
        corrupt = bytearray(self.data)
        corrupt[200] ^= 0xFF
        reader = HTTPRangeReader('https://x', session=RangeSession(bytes(corrupt)), block=4096)
        with tempfile.TemporaryDirectory() as directory, zipfile.ZipFile(reader) as archive:
            with self.assertRaises((zipfile.BadZipFile, zlib.error)):
                for info in archive.infolist():
                    extract_member(archive, info, Path(directory) / info.filename.replace('/', '_'))

    def test_seek_semantics(self):
        reader = HTTPRangeReader('https://x', session=RangeSession(b'0123456789'), block=4)
        reader.seek(-3, io.SEEK_END)
        self.assertEqual(reader.read(), b'789')
        reader.seek(2)
        self.assertEqual(reader.read(3), b'234')
        reader.seek(1, io.SEEK_CUR)
        self.assertEqual(reader.read(100), b'6789')
        self.assertEqual(reader.read(1), b'')
        with self.assertRaises(ValueError):
            reader.seek(-1)


if __name__ == '__main__':
    unittest.main()
