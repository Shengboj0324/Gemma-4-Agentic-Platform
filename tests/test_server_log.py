from pathlib import Path
import tempfile
import unittest

from zenithsync.server_log import stop_keeping_log


class Server:
    """Mimics VllmServer.stop(): writes a last line, then unlinks its log."""

    def __init__(self, log_path, fail=False):
        self.log_path, self.fail, self.stopped = str(log_path), fail, False

    def stop(self):
        with open(self.log_path, 'a') as handle:
            handle.write('shutdown\n')
        Path(self.log_path).unlink()
        self.stopped = True
        if self.fail:
            raise RuntimeError('stop failed')


class StopKeepingLogTests(unittest.TestCase):
    def test_the_whole_log_survives_stop_including_shutdown_lines(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / 'inference_server.log'
            log.write_text('ready\n')
            server = Server(log)
            text = stop_keeping_log(server, Path(d) / 'vllm-server.log')
            self.assertTrue(server.stopped)
            self.assertEqual(text, 'ready\nshutdown\n')
            self.assertEqual((Path(d) / 'vllm-server.log').read_text(), 'ready\nshutdown\n')
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ['vllm-server.log'])

    def test_log_is_kept_even_when_stop_raises(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / 'a.log'
            log.write_text('x\n')
            with self.assertRaises(RuntimeError):
                stop_keeping_log(Server(log, fail=True), Path(d) / 'out.log')
            self.assertEqual((Path(d) / 'out.log').read_text(), 'x\nshutdown\n')

    def test_a_missing_log_gives_empty_text(self):
        class Gone:
            log_path = '/nonexistent/x.log'

            def stop(self):
                pass
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(stop_keeping_log(Gone(), Path(d) / 'o.log'), '')


if __name__ == '__main__':
    unittest.main()
