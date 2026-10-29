"""Preflight checks must reproduce the worker's pins exactly and fail loudly."""

import re
import unittest
from pathlib import Path

from zenithsync.runtime_preflight import (REQUIRED_FREE_DEVICE_BYTES,
                                          REQUIRED_PACKAGES, REQUIRED_PLATFORM,
                                          REQUIRED_PYTHON, check_device_memory,
                                          check_packages, check_platform,
                                          check_sequence_capacity, summarise)

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
        self.assertIn("platform.system() != 'Linux'", self.source)
        self.assertEqual(REQUIRED_PLATFORM, 'Linux')
        self.assertIn('sys.version_info[:2] != (3, 12)', self.source)
        self.assertEqual(REQUIRED_PYTHON, (3, 12))

    def test_free_memory_floor_matches_the_worker_source(self):
        self.assertIn('free < 70*1024**3', self.source)
        self.assertEqual(REQUIRED_FREE_DEVICE_BYTES, 70 * 1024**3)


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


if __name__ == '__main__':
    unittest.main()
