import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from zenithsync import netns


class Completed:
    def __init__(self, stdout='', returncode=0, stderr=''):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


class InstallRemoveTests(unittest.TestCase):
    def test_install_then_remove_restores_both_files_exactly(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            preload, resolv, state = d / 'ld.so.preload', d / 'resolv.conf', d / 'state.json'
            resolv.write_text('nameserver 10.0.0.2\n')
            library = d / netns.GUARD_NAME
            library.write_bytes(b'')
            netns.install_guard(library, state, preload=preload, resolv=resolv)
            self.assertEqual(preload.read_text(), str(library.resolve()) + '\n')
            self.assertEqual(resolv.read_text(), netns.DEAD_RESOLVER)
            with self.assertRaises(FileExistsError):
                netns.install_guard(library, state, preload=preload, resolv=resolv)
            netns.remove_guard(state, preload=preload, resolv=resolv)
            self.assertFalse(preload.exists())
            self.assertEqual(resolv.read_text(), 'nameserver 10.0.0.2\n')
            self.assertFalse(state.exists())

    def test_an_existing_preload_is_kept_and_restored(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            preload, resolv, state = d / 'p', d / 'r', d / 's'
            preload.write_text('/lib/other.so\n')
            netns.install_guard(d / 'g.so', state, preload=preload, resolv=resolv)
            self.assertTrue(preload.read_text().startswith('/lib/other.so\n'))
            netns.remove_guard(state, preload=preload, resolv=resolv)
            self.assertEqual(preload.read_text(), '/lib/other.so\n')
            self.assertFalse(resolv.exists())


class RequireGuardTests(unittest.TestCase):
    isolated = {'loopback': True, 'external_reachable': False, 'external_error': 'ENETUNREACH',
                'dns_resolves': False, 'probe': '1.1.1.1:443'}

    def fresh(self, **python):
        return {'python': {**self.isolated, 'guard_loaded': True, **python},
                'curl': {'exit_code': 7, 'stderr': 'refused'}}

    def test_refused_when_not_loaded_in_this_process(self):
        with patch.object(netns, 'guard_loaded', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'not loaded'):
                netns.require_guard()

    def test_refused_when_a_fresh_process_escapes(self):
        cases = [self.fresh(guard_loaded=False), self.fresh(external_reachable=True),
                 self.fresh(dns_resolves=True), {**self.fresh(), 'curl': {'exit_code': 0, 'stderr': ''}}]
        for fresh in cases:
            with patch.object(netns, 'guard_loaded', return_value=True), \
                    patch.object(netns, 'probe_isolation', return_value=self.isolated), \
                    patch.object(netns, 'probe_fresh_process', return_value=fresh):
                with self.assertRaises(RuntimeError):
                    netns.require_guard()

    def test_isolate_reports_the_mode_and_fresh_evidence(self):
        with patch.object(netns, 'guard_loaded', return_value=True), \
                patch.object(netns, 'probe_isolation', return_value=self.isolated), \
                patch.object(netns, 'probe_fresh_process', return_value=self.fresh()):
            evidence = netns.isolate('egress-guard')
        self.assertEqual(evidence['mode'], 'egress-guard')
        self.assertTrue(evidence['fresh_process']['python']['guard_loaded'])
        with self.assertRaises(ValueError):
            netns.isolate('none')

    def test_fresh_probe_uses_an_empty_environment(self):
        calls = []

        def run(command, **kwargs):
            calls.append(command)
            if '-c' in command:
                return Completed(json.dumps({**self.isolated, 'guard_loaded': True}))
            return Completed(returncode=7, stderr='Failed to connect')
        with patch('shutil.which', return_value='/usr/bin/curl'):
            evidence = netns.probe_fresh_process(run=run)
        self.assertTrue(all(c[:2] == ['env', '-i'] for c in calls))
        self.assertEqual(evidence['curl']['exit_code'], 7)

    def test_guard_loaded_reads_the_memory_map(self):
        with tempfile.NamedTemporaryFile('w', suffix='maps') as maps:
            maps.write('7f00 r-xp /root/egress-guard/' + netns.GUARD_NAME + '\n')
            maps.flush()
            self.assertTrue(netns.guard_loaded(Path(maps.name)))
        self.assertFalse(netns.guard_loaded(Path('/nonexistent/maps')))


@unittest.skipUnless(sys.platform.startswith('linux') and shutil.which('cc'), 'Linux with a C compiler')
class GuardLibraryTests(unittest.TestCase):
    def test_preloaded_library_refuses_external_peers_and_allows_loopback(self):
        with tempfile.TemporaryDirectory() as d:
            library = netns.build_guard(d)
            code = ('import socket, errno\n'
                    's = socket.socket(); s.settimeout(3)\n'
                    'try:\n    s.connect(("1.1.1.1", 443)); print("REACHED")\n'
                    'except OSError as e:\n    print(errno.errorcode.get(e.errno))\n'
                    'srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(1)\n'
                    'socket.create_connection(srv.getsockname(), timeout=3); print("LOOPBACK")\n'
                    'u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n'
                    'try:\n    u.sendto(b"x", ("8.8.8.8", 53)); print("SENT")\n'
                    'except OSError as e:\n    print(errno.errorcode.get(e.errno))\n')
            out = subprocess.run([sys.executable, '-I', '-c', code], env={'LD_PRELOAD': str(library)},
                                 capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(out, ['ENETUNREACH', 'LOOPBACK', 'ENETUNREACH'])


if __name__ == '__main__':
    unittest.main()
