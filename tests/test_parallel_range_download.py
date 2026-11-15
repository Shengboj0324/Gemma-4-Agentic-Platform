import hashlib
import http.server
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from scripts.parallel_range_download import parts

ROOT = Path(__file__).resolve().parents[1]
DATA = bytes(range(256)) * 4099  # 1,049,344 bytes, not a multiple of the part count


class RangeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        start, end = (int(x) for x in self.headers['Range'].split('=')[1].split('-'))
        body = DATA[start:end + 1]
        self.send_response(206)
        self.send_header('Content-Range', f'bytes {start}-{end}/{len(DATA)}')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class ParallelRangeDownloadTests(unittest.TestCase):
    def test_parts_cover_every_byte_once(self):
        ranges = parts(10, 3)
        self.assertEqual(ranges, [(0, 3), (4, 7), (8, 9)])
        self.assertEqual(sum(e - s + 1 for s, e in parts(1049344, 7)), 1049344)

    def test_downloads_and_hashes_exactly(self):
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), RangeHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as d:
                out = Path(d) / 'f.bin'
                run = subprocess.run([sys.executable, str(ROOT / 'scripts/parallel_range_download.py'),
                                      f'http://127.0.0.1:{server.server_port}/x', str(len(DATA)), str(out),
                                      '--parts', '7'], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(out.read_bytes(), DATA)
                self.assertEqual(json.loads(run.stdout)['sha256'], hashlib.sha256(DATA).hexdigest())
        finally:
            server.shutdown()


if __name__ == '__main__':
    unittest.main()
