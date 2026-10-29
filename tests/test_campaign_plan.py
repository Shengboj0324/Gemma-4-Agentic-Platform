"""Campaign arithmetic must be exact and must refuse unmeasured forecasts."""

from fractions import Fraction
import unittest

from zenithsync.campaign_plan import (account_tokens, diversity_limits,
                                      forecast_campaign, mixture_plan,
                                      padding_overhead)


def rows(*triples):
    return [{'example_id': name, 'input_tokens': inputs, 'supervised_tokens': targets,
             'repository_group': group}
            for name, inputs, targets, group in triples]


class AccountTokensTests(unittest.TestCase):
    def setUp(self):
        self.examples = rows(('a', 100, 25, 'owner/one'), ('b', 300, 75, 'owner/two'))

    def test_counts_are_separated_and_repetition_is_explicit(self):
        report = account_tokens(self.examples, target_tokens=1000,
                                basis='supervised_tokens', max_epochs=20)
        self.assertEqual(report['unique_input_tokens'], 400)
        self.assertEqual(report['unique_supervised_tokens'], 100)
        self.assertEqual(report['tokens_per_epoch_on_basis'], 100)
        self.assertEqual(report['declared_epoch_allowance'], 2000)
        self.assertTrue(report['feasible_within_max_epochs'])
        self.assertEqual(report['epochs_required'], 10)
        self.assertEqual(report['repetition_factor'], [10, 1])
        self.assertEqual(report['approximate_processed_supervised_tokens'], 1000)
        self.assertEqual(report['approximate_processed_input_tokens'], 4000)
        self.assertEqual(report['longest_example_input_tokens'], 300)

    def test_partial_epoch_targets_round_up_without_losing_exactness(self):
        report = account_tokens(self.examples, target_tokens=250,
                                basis='supervised_tokens', max_epochs=3)
        self.assertEqual(report['epochs_required'], 3)
        self.assertEqual(report['repetition_factor'], [5, 2])
        self.assertEqual(report['repetition_factor_float'], 2.5)
        self.assertEqual(report['approximate_processed_input_tokens'], 1000)

    def test_infeasible_target_is_reported_not_silently_accepted(self):
        report = account_tokens(self.examples, target_tokens=1000,
                                basis='supervised_tokens', max_epochs=5)
        self.assertFalse(report['feasible_within_max_epochs'])
        self.assertEqual(report['declared_epoch_allowance'], 500)
        self.assertEqual(report['epochs_required'], 10)

    def test_input_basis_targets_the_input_stream(self):
        report = account_tokens(self.examples, target_tokens=4000,
                                basis='input_tokens', max_epochs=10)
        self.assertEqual(report['tokens_per_epoch_on_basis'], 400)
        self.assertEqual(report['approximate_processed_input_tokens'], 4000)
        self.assertEqual(report['approximate_processed_supervised_tokens'], 1000)

    def test_malformed_inputs_are_refused(self):
        cases = [
            ({'basis': 'tokens'}, 'Basis must be one of'),
            ({'target_tokens': 0}, 'target_tokens'),
            ({'max_epochs': -1}, 'max_epochs'),
            ({'examples': []}, 'Nonempty example metadata'),
            ({'examples': rows(('a', 100, 25, 'x'), ('a', 100, 25, 'x'))},
             'Unique nonempty example identity'),
            ({'examples': rows(('a', 10, 10, 'x'))},
             'Supervised targets must be fewer'),
            ({'examples': [{'example_id': 'a', 'input_tokens': 10}]},
             'identity and both token counts'),
        ]
        for override, message in cases:
            arguments = {'examples': self.examples, 'target_tokens': 100,
                         'basis': 'supervised_tokens', 'max_epochs': 2}
            arguments.update(override)
            with self.assertRaisesRegex(ValueError, message):
                account_tokens(**arguments)


class PaddingTests(unittest.TestCase):
    def test_padding_is_reported_as_processed_cost(self):
        report = padding_overhead(rows(('a', 100, 25, 'x'), ('b', 300, 75, 'y')),
                                  batch_width_tokens=400)
        self.assertEqual(report['real_input_tokens'], 400)
        self.assertEqual(report['padded_positions'], 400)
        self.assertEqual(report['processed_positions'], 800)
        self.assertEqual(report['padding_fraction'], [400, 800])
        self.assertEqual(report['padding_fraction_float'], 0.5)
        self.assertEqual(report['max_padding_for_one_example'], 300)

    def test_an_example_longer_than_the_width_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'truncation is forbidden'):
            padding_overhead(rows(('a', 500, 25, 'x')), batch_width_tokens=400)


class MixtureTests(unittest.TestCase):
    def test_shares_allocate_exactly_with_recorded_rounding(self):
        plan = mixture_plan([{'name': 'real', 'share': Fraction(3, 5)},
                             {'name': 'synthetic', 'share': Fraction(1, 5)},
                             {'name': 'protocol', 'share': Fraction(1, 5)}],
                            total_tokens=50_000_000)
        self.assertEqual(sum(row['allocated_tokens'] for row in plan['components']),
                         50_000_000)
        self.assertEqual([row['allocated_tokens'] for row in plan['components']],
                         [30_000_000, 10_000_000, 10_000_000])
        self.assertEqual(plan['largest_remainder_adjustments'], 0)

    def test_indivisible_totals_still_sum_exactly(self):
        plan = mixture_plan([{'name': 'a', 'share': Fraction(1, 3)},
                             {'name': 'b', 'share': Fraction(1, 3)},
                             {'name': 'c', 'share': Fraction(1, 3)}],
                            total_tokens=10)
        self.assertEqual(sum(row['allocated_tokens'] for row in plan['components']), 10)
        self.assertEqual(plan['largest_remainder_adjustments'], 1)
        self.assertEqual(sorted(row['allocated_tokens'] for row in plan['components']),
                         [3, 3, 4])

    def test_shares_must_be_exact_fractions_summing_to_one(self):
        cases = [
            ([{'name': 'a', 'share': Fraction(1, 2)}], 'sum to exactly one'),
            ([{'name': 'a', 'share': 0.5}, {'name': 'b', 'share': 0.5}],
             'exact Fraction'),
            ([{'name': 'a', 'share': Fraction(1, 1)}, {'name': 'a', 'share': Fraction(1, 1)}],
             'Unique nonempty component name'),
            ([{'name': 'a', 'share': Fraction(1, 1), 'extra': 1}],
             'exactly a name and a share'),
        ]
        for components, message in cases:
            with self.assertRaisesRegex(ValueError, message):
                mixture_plan(components, total_tokens=100)


class DiversityTests(unittest.TestCase):
    def test_concentration_is_measured_against_a_declared_cap(self):
        examples = rows(('a', 100, 90, 'owner/dominant'),
                        ('b', 100, 5, 'owner/small'),
                        ('c', 100, 5, 'owner/other'))
        report = diversity_limits(examples, maximum_share=Fraction(1, 2))
        self.assertEqual(report['groups'], 3)
        self.assertEqual(report['total_tokens'], 100)
        self.assertEqual(report['distribution'][0]['group'], 'owner/dominant')
        self.assertEqual(report['distribution'][0]['share'], [9, 10])
        self.assertTrue(report['distribution'][0]['exceeds_maximum'])
        self.assertEqual(report['groups_exceeding_maximum'], 1)
        self.assertFalse(report['policy_satisfied'])

    def test_group_labels_are_compared_case_insensitively(self):
        examples = rows(('a', 100, 10, 'Owner/Repo'), ('b', 100, 10, 'owner/repo'))
        report = diversity_limits(examples, maximum_share=Fraction(1, 1))
        self.assertEqual(report['groups'], 1)
        self.assertEqual(report['distribution'][0]['examples'], 2)
        self.assertTrue(report['policy_satisfied'])

    def test_missing_or_blank_group_field_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'lacks the grouping field'):
            diversity_limits([{'example_id': 'a', 'input_tokens': 2,
                               'supervised_tokens': 1}])
        with self.assertRaisesRegex(ValueError, 'nonempty string'):
            diversity_limits(rows(('a', 100, 10, '   ')))


class ForecastTests(unittest.TestCase):
    def test_forecast_uses_measured_throughput_and_shows_storage_separately(self):
        report = forecast_campaign(processed_input_tokens=3_600_000,
                                   measured_tokens_per_second=1000,
                                   measurement_evidence='worker.json peak run 2026-10-28',
                                   hourly_usd=4,
                                   storage_gib=200,
                                   storage_usd_per_gib_month=Fraction(7, 100),
                                   storage_hours=730)
        self.assertEqual(report['compute_seconds'], 3600.0)
        self.assertEqual(report['total_hours'], 1.0)
        self.assertEqual(report['compute_usd'], 4.0)
        self.assertAlmostEqual(report['storage_usd'], 14.0)
        self.assertAlmostEqual(report['total_usd'], 18.0)
        self.assertEqual(report['storage_hours_per_month_convention'], 730)

    def test_overhead_is_added_to_duration(self):
        report = forecast_campaign(processed_input_tokens=1000,
                                   measured_tokens_per_second=1000,
                                   measurement_evidence='measured fixture',
                                   hourly_usd=3600, overhead_seconds=3599)
        self.assertEqual(report['total_seconds'], 3600.0)
        self.assertEqual(report['total_usd'], 3600.0)

    def test_a_forecast_without_measurement_evidence_is_refused(self):
        for evidence in ('', '   ', None):
            with self.assertRaisesRegex(ValueError, 'measurement evidence is required'):
                forecast_campaign(processed_input_tokens=1000,
                                  measured_tokens_per_second=10,
                                  measurement_evidence=evidence, hourly_usd=1)

    def test_nonpositive_rates_and_prices_are_refused(self):
        base = {'processed_input_tokens': 1000, 'measured_tokens_per_second': 10,
                'measurement_evidence': 'measured', 'hourly_usd': 1}
        for override, message in [({'measured_tokens_per_second': 0}, 'must be positive'),
                                  ({'hourly_usd': -1}, 'must be positive'),
                                  ({'processed_input_tokens': 0}, 'processed_input_tokens'),
                                  ({'overhead_seconds': -5}, 'overhead_seconds'),
                                  ({'storage_gib': -1}, 'storage_gib')]:
            with self.assertRaisesRegex(ValueError, message):
                forecast_campaign(**{**base, **override})

    def test_zero_storage_needs_no_storage_price(self):
        report = forecast_campaign(processed_input_tokens=1000,
                                   measured_tokens_per_second=1000,
                                   measurement_evidence='measured', hourly_usd=36)
        self.assertEqual(report['storage_usd'], 0.0)
        self.assertEqual(report['total_usd'], report['compute_usd'])


if __name__ == '__main__':
    unittest.main()
