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

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        d = Path(self.directory.name)
        self.state = d / 'state.json'
        self.state.write_text(json.dumps({'library': str(d / 'lib' / netns.GUARD_NAME), 'preload': None,
                                          'resolv': 'nameserver 10.0.0.2\nsearch .\n'}))
        self.paths = {'preload': d / 'p', 'resolv': d / 'r'}

    def tearDown(self):
        self.directory.cleanup()

    def fresh(self, **python):
        return {'python': {**self.isolated, 'guard_loaded': True, **python},
                'curl': {'exit_code': 7, 'stderr': 'refused'}}

    def check(self, *, euid=1000, loaded=True, writable=(), answered=(), fresh=None):
        queried = []

        def answers(server):
            queried.append(server)
            return server in answered
        with patch('os.geteuid', return_value=euid), \
                patch.object(netns, 'guard_loaded', return_value=loaded), \
                patch('os.access', side_effect=lambda p, mode: str(p) in writable), \
                patch.object(netns, 'probe_isolation', return_value=self.isolated), \
                patch.object(netns, 'dns_answers', side_effect=answers), \
                patch.object(netns, 'probe_fresh_process', return_value=fresh or self.fresh()):
            evidence = netns.require_guard(self.state, **self.paths)
        return evidence, queried

    def test_passes_and_queries_the_original_and_runtime_resolvers(self):
        evidence, queried = self.check()
        self.assertEqual(queried, ['10.0.0.2', '127.0.0.11'])
        self.assertEqual(evidence['direct_dns_refused'], ['10.0.0.2', '127.0.0.11'])
        self.assertEqual(evidence['uid'], 1000)

    def test_root_is_refused(self):
        with self.assertRaisesRegex(RuntimeError, 'non-root'):
            self.check(euid=0)

    def test_refused_when_not_loaded_in_this_process(self):
        with self.assertRaisesRegex(RuntimeError, 'not loaded'):
            self.check(loaded=False)

    def test_refused_when_guard_files_are_writable(self):
        with self.assertRaisesRegex(RuntimeError, 'writable'):
            self.check(writable=(str(self.paths['preload']),))

    def test_refused_when_a_resolver_answers_directly(self):
        with self.assertRaisesRegex(RuntimeError, 'answered'):
            self.check(answered=('127.0.0.11',))

    def test_refused_when_a_fresh_process_escapes(self):
        cases = [self.fresh(guard_loaded=False), self.fresh(external_reachable=True),
                 self.fresh(dns_resolves=True), {**self.fresh(), 'curl': {'exit_code': 0, 'stderr': ''}}]
        for fresh in cases:
            with self.assertRaises(RuntimeError):
                self.check(fresh=fresh)

    def test_isolate_reports_the_mode(self):
        with patch.object(netns, 'require_guard', return_value={'uid': 1000}):
            self.assertEqual(netns.isolate('egress-guard'), {'mode': 'egress-guard', 'uid': 1000})
        with self.assertRaises(ValueError):
            netns.isolate('none')

    def test_nameservers_are_parsed_from_resolv_conf(self):
        text = '# c\nnameserver 127.0.0.11\nsearch .\nnameserver ::1\noptions edns0\n'
        self.assertEqual(netns.nameservers(text), ['127.0.0.11', '::1'])
        self.assertEqual(netns.nameservers(None), [])

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
            maps.write('7f00 r-xp /usr/local/lib/zenithsync/' + netns.GUARD_NAME + '\n')
            maps.flush()
            self.assertTrue(netns.guard_loaded(Path(maps.name)))
        self.assertFalse(netns.guard_loaded(Path('/nonexistent/maps')))


@unittest.skipUnless(sys.platform.startswith('linux') and shutil.which('cc'), 'Linux with a C compiler')
class GuardLibraryTests(unittest.TestCase):
    def test_preloaded_library_allows_only_127_0_0_1(self):
        with tempfile.TemporaryDirectory() as d:
            library = netns.build_guard(d)
            code = ('import socket, errno\n'
                    's = socket.socket(); s.settimeout(3)\n'
                    'try:\n    s.connect(("1.1.1.1", 443)); print("REACHED")\n'
                    'except OSError as e:\n    print(errno.errorcode.get(e.errno))\n'
                    'srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(1)\n'
                    'socket.create_connection(srv.getsockname(), timeout=3); print("LOOPBACK")\n'
                    'for host in ("8.8.8.8", "127.0.0.11", "127.0.0.2"):\n'
                    '    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n'
                    '    try:\n        u.sendto(b"x", (host, 53)); print("SENT")\n'
                    '    except OSError as e:\n        print(errno.errorcode.get(e.errno))\n')
            out = subprocess.run([sys.executable, '-I', '-c', code], env={'LD_PRELOAD': str(library)},
                                 capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(out, ['ENETUNREACH', 'LOOPBACK'] + ['ENETUNREACH'] * 3)


if __name__ == '__main__':
    unittest.main()
