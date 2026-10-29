"""Preflight checks must reproduce the worker's pins exactly and fail loudly."""

import re
import unittest
import unittest.mock
from pathlib import Path

from zenithsync.runtime_preflight import (REQUIRED_FREE_DEVICE_BYTES,
                                          REQUIRED_PACKAGES, REQUIRED_PLATFORM,
                                          REQUIRED_PYTHON, check_device_memory,
                                          check_packages, check_platform,
                                          check_sequence_capacity, device_report,
                                          summarise)

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / 'scripts/run_corpus_training_worker.py'


class PinAgreementTests(unittest.TestCase):
    """The whole point of preflight is to predict the worker; drift breaks that."""

    def setUp(self):
        self.source = WORKER.read_text(encoding='utf-8')

    def test_package_pins_match_the_worker_source(self):
        block = re.search(r"required = \{(.*?)\}", self.source, re.S)
        self.assertIsNotNone(block, 'worker pin block not found')
        pairs = dict(re.findall(r"'([a-z-]+)':\s*'([^']+)'", block.group(1)))
        self.assertEqual(pairs, REQUIRED_PACKAGES)

    def test_platform_and_python_pins_match_the_worker_source(self):
        # Derive the worker's values and compare, rather than restating ours:
        # restating them passes even with check_platform deleted.
        self.assertIn(f"platform.system() != '{REQUIRED_PLATFORM}'", self.source)
        major, minor = REQUIRED_PYTHON
        self.assertIn(f'sys.version_info[:2] != ({major}, {minor})', self.source)

    def test_free_memory_floor_matches_the_worker_source(self):
        # Parse the worker's arithmetic rather than grepping one spelling of it,
        # so reformatting the worker does not fail a test about behaviour.
        match = re.search(r'free\s*<\s*(\d+)\s*\*\s*1024\s*\*\*\s*3', self.source)
        self.assertIsNotNone(match, 'worker free-memory floor not found')
        self.assertEqual(int(match.group(1)) * 1024**3, REQUIRED_FREE_DEVICE_BYTES)

    def test_the_worker_excludes_its_own_pid_from_the_exclusivity_query(self):
        # The preflight must match this, or it fails a healthy exclusive host.
        self.assertIn('--query-compute-apps=pid', self.source)
        self.assertIn('str(os.getpid())', self.source)


class PlatformTests(unittest.TestCase):
    def test_matching_platform_passes(self):
        result = check_platform('Linux', (3, 12, 7))
        self.assertTrue(result['satisfied'])
        self.assertEqual(result['problems'], [])
        self.assertEqual(result['python_version'], [3, 12])

    def test_wrong_platform_and_python_are_both_reported(self):
        result = check_platform('Darwin', (3, 13))
        self.assertFalse(result['satisfied'])
        self.assertEqual(len(result['problems']), 2)
        self.assertIn('Darwin', result['problems'][0])
        self.assertIn('3.13', result['problems'][1])

    def test_malformed_inputs_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'Platform system name'):
            check_platform('', (3, 12))
        with self.assertRaisesRegex(ValueError, 'pair of integers'):
            check_platform('Linux', ('3', '12'))


class PackageTests(unittest.TestCase):
    def exact(self):
        return dict(REQUIRED_PACKAGES)

    def test_exact_pins_pass(self):
        result = check_packages(self.exact())
        self.assertTrue(result['satisfied'])
        self.assertEqual(result['problems'], [])
        self.assertEqual(len(result['packages']), 4)

    def test_local_build_tags_are_stripped_before_comparison(self):
        installed = self.exact()
        installed['torch'] = '2.10.0+cu128'
        result = check_packages(installed)
        self.assertTrue(result['satisfied'])
        row = next(r for r in result['packages'] if r['name'] == 'torch')
        self.assertEqual(row['found'], '2.10.0+cu128')
        self.assertEqual(row['compared'], '2.10.0')

    def test_a_different_version_is_reported_not_accepted(self):
        installed = self.exact()
        installed['torch'] = '2.9.0'
        result = check_packages(installed)
        self.assertFalse(result['satisfied'])
        self.assertEqual(result['problems'], ['torch is 2.9.0, worker requires 2.10.0'])

    def test_an_absent_package_is_reported(self):
        installed = self.exact()
        installed['peft'] = None
        result = check_packages(installed)
        self.assertFalse(result['satisfied'])
        self.assertIn('peft is not installed', result['problems'][0])
        row = next(r for r in result['packages'] if r['name'] == 'peft')
        self.assertIsNone(row['found'])

    def test_extra_reported_packages_are_listed_but_not_failures(self):
        result = check_packages({**self.exact(), 'numpy': '2.2.6'})
        self.assertTrue(result['satisfied'])
        self.assertEqual(result['unpinned_packages_reported'], ['numpy'])

    def test_metadata_disagreeing_with_the_imported_module_is_a_problem(self):
        # importlib.metadata reads dist-info from sys.path; a stale one wins over
        # the package that actually imports, so the pin claim would be about
        # metadata rather than about the running code.
        result = check_packages(self.exact(), imported={'torch': '2.14.1'})
        self.assertFalse(result['satisfied'])
        self.assertIn('metadata says 2.10.0 but the imported module reports 2.14.1',
                      result['problems'][0])
        row = next(r for r in result['packages'] if r['name'] == 'torch')
        self.assertEqual(row['imported'], '2.14.1')
        self.assertFalse(row['satisfied'])

    def test_an_agreeing_imported_version_passes_and_is_recorded(self):
        result = check_packages(self.exact(), imported={'torch': '2.10.0+cu128'})
        self.assertTrue(result['satisfied'])
        row = next(r for r in result['packages'] if r['name'] == 'torch')
        self.assertEqual(row['imported'], '2.10.0+cu128')

    def test_an_unimportable_module_does_not_fabricate_a_disagreement(self):
        result = check_packages(self.exact(), imported={'torch': None})
        self.assertTrue(result['satisfied'])

    def test_a_malformed_imported_mapping_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'Imported version mapping'):
            check_packages(self.exact(), imported=['torch'])

    def test_malformed_inputs_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'Installed package mapping'):
            check_packages(['torch'])
        with self.assertRaisesRegex(ValueError, 'nonempty string'):
            check_packages({**self.exact(), 'torch': ''})


class DeviceMemoryTests(unittest.TestCase):
    def test_sufficient_memory_passes_with_headroom_reported(self):
        result = check_device_memory(80 * 1024**3, 96 * 1024**3)
        self.assertTrue(result['satisfied'])
        self.assertEqual(result['headroom_bytes'], 10 * 1024**3)
        self.assertAlmostEqual(result['total_gib'], 96.0)

    def test_insufficient_memory_is_reported_in_bytes_and_gib(self):
        result = check_device_memory(40 * 1024**3, 48 * 1024**3)
        self.assertFalse(result['satisfied'])
        self.assertIn('40.00 GiB', result['problems'][0])
        self.assertIn('70.00 GiB', result['problems'][0])
        self.assertLess(result['headroom_bytes'], 0)

    def test_an_explicit_floor_overrides_the_default(self):
        result = check_device_memory(40 * 1024**3, 48 * 1024**3,
                                     required_free_bytes=32 * 1024**3)
        self.assertTrue(result['satisfied'])

    def test_impossible_and_malformed_readings_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'exceeds total'):
            check_device_memory(100, 10)
        with self.assertRaisesRegex(ValueError, 'free_bytes'):
            check_device_memory(-1, 10)


class SequenceCapacityTests(unittest.TestCase):
    def test_a_fitting_corpus_passes_with_slack_reported(self):
        result = check_sequence_capacity(24366, 32768)
        self.assertTrue(result['satisfied'])
        self.assertEqual(result['slack_tokens'], 8402)

    def test_an_example_over_capacity_is_refused_not_truncated(self):
        result = check_sequence_capacity(40000, 32768)
        self.assertFalse(result['satisfied'])
        self.assertIn('truncation is forbidden', result['problems'][0])

    def test_malformed_inputs_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'longest_input_tokens'):
            check_sequence_capacity(0, 32768)


class DeviceReportTests(unittest.TestCase):
    """device_report must return findings, never raise, and never over-report."""

    def report_with(self, torch_module, run):
        import builtins
        import subprocess
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == 'torch':
                if torch_module is None:
                    raise ImportError('no module named torch')
                return torch_module
            return real_import(name, *args, **kwargs)

        with unittest.mock.patch.object(builtins, '__import__', fake_import):
            with unittest.mock.patch.object(subprocess, 'run', run):
                return device_report()

    def torch_stub(self, *, available=True, count=1, free=80 * 1024**3,
                   total=96 * 1024**3, raises=None):
        import types
        module = types.SimpleNamespace()
        module.__version__ = '2.10.0'
        module.__file__ = '/usr/lib/python3.12/site-packages/torch/__init__.py'

        def fail(*args, **kwargs):
            raise raises

        cuda = types.SimpleNamespace(
            is_available=lambda: available,
            device_count=lambda: count,
            mem_get_info=(fail if raises else (lambda: (free, total))),
            get_device_name=lambda index: 'NVIDIA H100 80GB HBM3',
            get_device_capability=lambda index: (9, 0))
        module.cuda = cuda
        return module

    def smi(self, pids, *, error=None):
        import subprocess

        def run(command, **kwargs):
            if error is not None:
                raise error
            return subprocess.CompletedProcess(
                command, 0, stdout='\n'.join(pids) + ('\n' if pids else ''), stderr='')
        return run

    def test_a_missing_nvidia_smi_is_a_failure_not_an_unknown(self):
        # The worker runs the same query with check=True, so a query that cannot
        # run here means the worker would abort after the pod is billing.
        report = self.report_with(self.torch_stub(),
                                  self.smi([], error=FileNotFoundError('nvidia-smi')))
        self.assertTrue(report['available'])
        self.assertIs(report['device_exclusive'], False)
        self.assertEqual(report['exclusivity_query_failed'], 'FileNotFoundError')
        verdict = summarise({'device_memory': {
            'problems': ['the exclusivity query failed'], 'satisfied': False}})
        self.assertEqual(verdict['status'], 'runtime_preflight_failed')

    def test_the_processes_own_pid_is_not_a_foreign_compute_process(self):
        import os
        report = self.report_with(self.torch_stub(), self.smi([str(os.getpid())]))
        self.assertIs(report['device_exclusive'], True)
        self.assertEqual(report['other_compute_processes'], [])
        self.assertEqual(report['own_pid'], str(os.getpid()))

    def test_a_foreign_compute_process_is_reported(self):
        import os
        report = self.report_with(self.torch_stub(),
                                  self.smi([str(os.getpid()), '4242']))
        self.assertIs(report['device_exclusive'], False)
        self.assertEqual(report['other_compute_processes'], ['4242'])

    def test_a_cuda_runtime_error_returns_a_finding_rather_than_raising(self):
        report = self.report_with(
            self.torch_stub(raises=RuntimeError('CUDA error: unknown error')),
            self.smi([]))
        self.assertFalse(report['available'])
        self.assertEqual(report['reason'], 'cuda_query_failed')
        self.assertIn('CUDA error: unknown error', report['detail'])

    def test_an_absent_torch_or_cuda_returns_a_finding(self):
        report = self.report_with(None, self.smi([]))
        self.assertEqual(report['reason'], 'torch_import_failed')
        report = self.report_with(self.torch_stub(available=False), self.smi([]))
        self.assertEqual(report['reason'], 'cuda_unavailable')
        report = self.report_with(self.torch_stub(count=2), self.smi([]))
        self.assertEqual(report['reason'], 'device_count_is_not_one')
        self.assertEqual(report['device_count'], 2)

    def test_a_healthy_exclusive_device_reports_its_torch_identity(self):
        import os
        report = self.report_with(self.torch_stub(), self.smi([str(os.getpid())]))
        self.assertEqual(report['torch_version'], '2.10.0')
        self.assertIn('torch/__init__.py', report['torch_file'])
        self.assertEqual(report['free_bytes'], 80 * 1024**3)


class SummariseTests(unittest.TestCase):
    def test_all_passing_checks_give_a_passing_verdict(self):
        verdict = summarise({'platform': check_platform('Linux', (3, 12)),
                             'packages': check_packages(dict(REQUIRED_PACKAGES))})
        self.assertEqual(verdict['status'], 'runtime_preflight_passed')
        self.assertTrue(verdict['satisfied'])
        self.assertEqual(verdict['failed_checks'], [])
        self.assertEqual(verdict['problems'], {})

    def test_every_problem_is_kept_and_the_failing_checks_named(self):
        verdict = summarise({'platform': check_platform('Darwin', (3, 13)),
                             'packages': check_packages({'torch': '2.9.0'}),
                             'capacity': check_sequence_capacity(1, 2)})
        self.assertEqual(verdict['status'], 'runtime_preflight_failed')
        self.assertFalse(verdict['satisfied'])
        self.assertEqual(verdict['failed_checks'], ['packages', 'platform'])
        self.assertEqual(len(verdict['problems']['platform']), 2)
        self.assertEqual(len(verdict['problems']['packages']), 4)

    def test_a_result_without_a_problems_list_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'problems list'):
            summarise({'platform': {'satisfied': True}})
        with self.assertRaisesRegex(ValueError, 'Nonempty named check results'):
            summarise({})

    def test_an_unsatisfied_check_with_no_stated_problem_still_fails(self):
        verdict = summarise({'device_memory': {'satisfied': False, 'problems': []}})
        self.assertEqual(verdict['status'], 'runtime_preflight_failed')
        self.assertFalse(verdict['satisfied'])
        self.assertEqual(verdict['failed_checks'], ['device_memory'])

    def test_a_skipped_device_cannot_be_read_as_a_full_pass(self):
        checks = {'platform': check_platform('Linux', (3, 12)),
                  'packages': check_packages(dict(REQUIRED_PACKAGES))}
        full = summarise(checks, device_checked=True)
        skipped = summarise(checks, device_checked=False)
        self.assertEqual(full['status'], 'runtime_preflight_passed')
        self.assertEqual(skipped['status'],
                         'runtime_preflight_passed_without_device_checks')
        self.assertNotEqual(full['status'], skipped['status'])
        self.assertFalse(skipped['device_checked'])
        self.assertIn('device was not examined', skipped['scope'])
        self.assertEqual(skipped['required_free_device_bytes'],
                         REQUIRED_FREE_DEVICE_BYTES)
        with self.assertRaisesRegex(ValueError, 'device_checked must be boolean'):
            summarise(checks, device_checked='no')


if __name__ == '__main__':
    unittest.main()
