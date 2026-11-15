import errno
import importlib.util
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from scripts.run_official_eval import candidate_budget, declared_model, kv_capacity, lora_rank, use_test_site
from types import SimpleNamespace
import sys
from zenithsync import netns

ROOT = Path(__file__).resolve().parents[1]


class RunnerHelperTests(unittest.TestCase):
    def test_kv_capacity_is_read_from_the_vllm_log(self):
        log = ('INFO GPU KV cache size: 1,000 tokens\nINFO GPU KV cache size: 147,216 tokens\n'
               'INFO Maximum concurrency for 32,768 tokens per request: 4.49x\n')
        self.assertEqual(kv_capacity(log), {'kv_cache_tokens': 147216,
                                            'max_concurrency_at_context': {'context': 32768, 'factor': 4.49}})
        self.assertEqual(kv_capacity('nothing'), {'kv_cache_tokens': None, 'max_concurrency_at_context': None})

    @unittest.skipUnless(importlib.util.find_spec('yaml'), 'PyYAML required')
    def test_candidate_budget_comes_from_the_submission(self):
        self.assertEqual(candidate_budget(ROOT / 'candidates/p1-base'),
                         {'timeout_seconds': 120, 'max_tool_calls': 40, 'max_time_minutes': 10, 'max_turns': 40})
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(candidate_budget(Path(directory)), {})
            (Path(directory) / 'eval_config.yaml').write_text('evaluation:\n  max_turns: 3\n  extra: 1\n')
            with self.assertRaisesRegex(ValueError, 'Unexpected'):
                candidate_budget(Path(directory))


class NetnsTests(unittest.TestCase):
    def test_reachable_network_is_refused(self):
        evidence = {'loopback': True, 'external_reachable': True, 'external_error': None,
                    'dns_resolves': True, 'probe': 'x'}
        with patch.object(netns, 'probe_isolation', return_value=evidence):
            with self.assertRaisesRegex(RuntimeError, 'not isolated'):
                netns.require_isolation()
        isolated = dict(evidence, external_reachable=False, dns_resolves=False, external_error='ENETUNREACH')
        with patch.object(netns, 'probe_isolation', return_value=isolated):
            self.assertEqual(netns.require_isolation(), isolated)

    def test_probe_reports_an_unreachable_address_without_raising(self):
        def refuse(*args, **kwargs):
            raise OSError(errno.ENETUNREACH, 'Network is unreachable')
        real = socket.create_connection
        def fake(address, timeout=None):
            return real(address, timeout) if address[0] == '127.0.0.1' else refuse()
        real_lookup = socket.getaddrinfo
        def lookup(host, *args, **kwargs):
            if host == 'github.com':
                raise OSError('no dns')
            return real_lookup(host, *args, **kwargs)
        with patch('socket.create_connection', side_effect=fake), \
                patch('socket.getaddrinfo', side_effect=lookup):
            evidence = netns.probe_isolation()
        self.assertEqual((evidence['loopback'], evidence['external_reachable'], evidence['dns_resolves']),
                         (True, False, False))
        self.assertEqual(evidence['external_error'], 'ENETUNREACH')

    def test_reexec_is_a_no_op_once_inside(self):
        with patch.dict('os.environ', {netns.MARKER: '1'}), patch('os.execv') as execv:
            netns.reexec_isolated(['x'])
        execv.assert_not_called()



class DeclaredModelTests(unittest.TestCase):
    def test_one_allowed_model_with_or_without_provider_prefix(self):
        for declared in ({'gemma-4-31b-it-qat-w4a16-ct'}, {'openai/gemma-4-31b-it-qat-w4a16-ct'},
                         {'hosted_vllm/gemma-4-31b-it-qat-w4a16-ct', 'gemma-4-31b-it-qat-w4a16-ct'}):
            self.assertEqual(declared_model('x', lambda _: declared), 'gemma-4-31b-it-qat-w4a16-ct')

    def test_several_or_unlisted_models_are_refused(self):
        for declared in (set(), {'gemma-4-31b-it'},
                         {'gemma-4-31b-it-qat-w4a16-ct', 'gemma-4-12b-it-qat-w4a16-ct'}):
            with self.assertRaises(ValueError):
                declared_model('x', lambda _: declared)



class TestSiteTests(unittest.TestCase):
    def test_site_is_appended_or_prepended_once(self):
        with tempfile.TemporaryDirectory() as d:
            site = Path(d) / 'site-packages'
            site.mkdir()
            original = list(sys.path)
            try:
                use_test_site(site, 'append')
                use_test_site(site, 'append')
                self.assertEqual(sys.path[-1], str(site.resolve()))
                self.assertEqual(sys.path.count(str(site.resolve())), 1)
                use_test_site(site, 'prepend')
                self.assertEqual(sys.path[0], str(site.resolve()))
                self.assertEqual(sys.path.count(str(site.resolve())), 1)
            finally:
                sys.path[:] = original

    def test_only_an_existing_site_packages_directory_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                use_test_site(Path(d), 'append')
            with self.assertRaises(ValueError):
                use_test_site(Path(d) / 'site-packages', 'append')
        use_test_site(None)



class LoraRankTests(unittest.TestCase):
    def test_largest_detected_rank_else_the_official_default(self):
        manifest = lambda *ranks: SimpleNamespace(adapters={f'a{i}': SimpleNamespace(rank=r) for i, r in enumerate(ranks)})
        self.assertEqual(lora_rank([manifest(4), manifest(16, None)]), 16)
        self.assertEqual(lora_rank([manifest(), manifest(None, 0)]), 128)


if __name__ == '__main__':
    unittest.main()
