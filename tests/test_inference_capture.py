"""Synthetic transport checks, not model quality tests."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from zenithsync.inference_capture import capture_inference


class CaptureTests(unittest.TestCase):
    def test_upstream_response_framing(self):
        # Real sockets exercise HTTPResponse.read(n), which can silently return
        # a short body when Content-Length was declared but the peer closed.
        cases = [
            ('complete', [('Content-Length', '2')], b'{}', 200),
            ('close_delimited', [], b'{}', 200),
            ('short', [('Content-Length', '20')], b'{}', 502),
            ('invalid_length', [('Content-Length', 'no')], b'{}', 502),
            ('conflicting_lengths', [('Content-Length', '2'), ('Content-Length', '20')], b'{}', 502),
            ('ambiguous', [('Transfer-Encoding', 'chunked'), ('Content-Length', '2')], b'2\r\n{}\r\n0\r\n\r\n', 502),
            ('chunked', [('Transfer-Encoding', 'chunked')], b'2\r\n{}\r\n0\r\n\r\n', 200),
            ('short_chunk', [('Transfer-Encoding', 'chunked')], b'20\r\n{}', 502),
        ]
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for name, headers, body, expected in cases:
            with self.subTest(name=name):
                class Upstream(BaseHTTPRequestHandler):
                    def log_message(self, *_):
                        pass

                    def do_POST(self):
                        self.rfile.read(int(self.headers['Content-Length']))
                        self.send_response(200)
                        for key, value in headers:
                            self.send_header(key, value)
                        self.end_headers()
                        self.wfile.write(body)
                        self.close_connection = True

                server = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    with tempfile.TemporaryDirectory() as temporary:
                        output = Path(temporary) / 'capture'
                        with capture_inference(output, server.server_port) as endpoint:
                            request = urllib.request.Request(endpoint + '/chat/completions', data=b'{}')
                            try:
                                response = opener.open(request, timeout=5)
                            except urllib.error.HTTPError as error:
                                response = error
                            with response:
                                self.assertEqual(response.status, expected)
                                if expected == 200:
                                    self.assertEqual(response.read(), b'{}')
                        record = output / '0001'
                        if expected == 502:
                            self.assertTrue((record / 'transport-error.txt').is_file())
                            self.assertFalse((record / 'response.json').exists())
                            self.assertFalse((record / 'status.json').exists())
                        else:
                            self.assertEqual((record / 'response.json').read_bytes(), b'{}')
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=5)

    def test_request_change_and_response_preservation(self):
        received = []
        response_bytes = b'{"choices": [], "token_ids": [123]}'

        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_bytes)

        server = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        payload = {'model': 'synthetic', 'messages': [{'role': 'user', 'content': 'data 🌍'}]}
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)/'capture'
                with capture_inference(output, server.server_port) as endpoint:
                    request = urllib.request.Request(endpoint+'/chat/completions',
                        data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
                    with opener.open(request, timeout=5) as response:
                        self.assertEqual(response.read(), response_bytes)
                self.assertEqual(received, [{**payload, 'return_token_ids': True}])
                self.assertEqual(json.loads((output/'0001/original-request.json').read_bytes()), payload)
                self.assertEqual((output/'0001/response.json').read_bytes(), response_bytes)
                self.assertEqual(json.loads((output/'0001/status.json').read_bytes()), {'http_status':200})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_streaming_rejected_without_forwarding(self):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'capture'
            with capture_inference(output, 18000) as endpoint:
                request = urllib.request.Request(endpoint+'/chat/completions', data=b'{"stream":true}')
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    opener.open(request, timeout=5)
                self.assertEqual(raised.exception.code, 400)
            self.assertEqual(list(output.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
