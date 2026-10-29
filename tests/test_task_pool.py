"""Task-pool screening must refuse with reasons and select reproducibly."""

from fractions import Fraction
import unittest

from zenithsync.task_pool import (PERMISSIVE_LICENSES, TaskRecordError,
                                  disjoint_cohorts, screen_task_pool,
                                  select_task_pool, validate_task_record)

REVISION = '10483de0f50fe5da545942705a76c6150171af7f'


def row(instance, repo, *, commit=None, language='python', license='MIT',
        image='docker.io/example/img:1', created='2024-01-01 00:00:00'):
    return {'instance_id': instance, 'repo': repo,
            'base_commit': commit or ('a' * 39 + str(abs(hash(instance)) % 10)),
            'language': language, 'license': license, 'image_name': image,
            'created_at': created}


class ValidateTests(unittest.TestCase):
    def test_a_well_formed_row_normalises(self):
        record = validate_task_record(row('Owner__Repo-12', 'Owner/Repo',
                                          commit='b' * 40))
        self.assertEqual(record['instance_id'], 'Owner__Repo-12')
        self.assertEqual(record['repo'], 'Owner/Repo')
        self.assertEqual(record['owner'], 'owner')
        self.assertEqual(record['repository_group'], 'owner/repo')
        self.assertEqual(record['base_commit'], 'b' * 40)
        self.assertEqual(record['license_key'], 'mit')
        # Commit digests are normalised to lower case rather than refused.
        self.assertEqual(validate_task_record(
            row('o__r-1', 'o/r', commit='B' * 40))['base_commit'], 'b' * 40)
        # A missing environment image parses; screening decides whether it matters.
        self.assertEqual(validate_task_record(
            {k: v for k, v in row('o__r-1', 'o/r').items()
             if k != 'image_name'})['image_name'], '')

    def test_malformed_rows_carry_stable_reason_codes(self):
        cases = [
            ([], 'record_not_an_object'),
            (row('no-separator', 'o/r'), 'malformed_instance_id'),
            (row('o__r-1', 'notapath'), 'malformed_repo'),
            (row('o__r-1', 'o/r', commit='short'), 'base_commit_is_not_a_full_sha1'),
            ({**row('o__r-1', 'o/r'), 'license': '  '}, 'missing_license'),
            ({**row('o__r-1', 'o/r'), 'image_name': 7}, 'malformed_image_name'),
            ({k: v for k, v in row('o__r-1', 'o/r').items() if k != 'created_at'},
             'missing_created_at'),
        ]
        for value, reason in cases:
            with self.assertRaises(TaskRecordError) as caught:
                validate_task_record(value)
            self.assertEqual(caught.exception.reason, reason)


class ScreenTests(unittest.TestCase):
    def screen(self, rows, **kwargs):
        arguments = {'dataset': 'nebius/SWE-rebench-V2', 'revision': REVISION}
        arguments.update(kwargs)
        return screen_task_pool(rows, **arguments)

    def test_eligible_rows_are_accepted_and_counted_by_repository(self):
        rows = [row('a__one-1', 'a/one'), row('b__two-2', 'b/two'),
                row('a__one-3', 'a/one')]
        report = self.screen(rows)
        self.assertEqual(report['accepted'], 3)
        self.assertEqual(report['refused'], 0)
        self.assertEqual(report['distinct_repositories'], 2)
        self.assertEqual(report['distinct_owners'], 2)
        self.assertEqual(report['accepted_license_distribution'], {'MIT': 3})
        self.assertEqual(report['dataset'], 'nebius/SWE-rebench-V2')
        self.assertEqual(report['revision'], REVISION)
        self.assertFalse(report['rights_cleared'])
        self.assertFalse(report['training_approved'])

    def test_placeholder_licence_is_refused_separately_from_a_real_refusal(self):
        rows = [row('a__one-1', 'a/one', license='custom-check-github'),
                row('b__two-1', 'b/two', license='GPL-3.0'),
                row('c__three-1', 'c/three', license='NOASSERTION'),
                row('d__four-1', 'd/four', license='Apache-2.0')]
        report = self.screen(rows)
        self.assertEqual(report['accepted'], 1)
        self.assertEqual(report['refusal_reasons'],
                         {'license_label_is_a_placeholder': 2,
                          'license_not_in_screening_allowlist': 1})

    def test_a_placeholder_cannot_be_allowlisted(self):
        with self.assertRaisesRegex(ValueError, 'placeholder licence'):
            self.screen([row('a__one-1', 'a/one')],
                        allowed_licenses={'mit', 'custom-check-github'})

    def test_language_environment_and_exclusions_each_have_their_own_reason(self):
        rows = [row('a__one-1', 'a/one', language='ts'),
                row('b__two-1', 'b/two', image=''),
                row('c__three-1', 'c/three'),
                row('d__four-1', 'd/four'),
                row('e__five-1', 'e/five'),
                row('f__six-1', 'f/six', created='2019-01-01 00:00:00')]
        report = self.screen(rows, excluded_repositories=['C/Three'],
                             excluded_owners=['D'], excluded_instances=['E__FIVE-1'],
                             minimum_created_at='2020-01-01')
        self.assertEqual(report['accepted'], 0)
        self.assertEqual(report['refusal_reasons'], {
            'language_not_selected': 1,
            'no_executable_environment_image': 1,
            'repository_excluded_as_exposed_or_reserved': 1,
            'owner_excluded_as_exposed_or_reserved': 1,
            'instance_excluded_as_exposed_or_reserved': 1,
            'created_before_minimum_date': 1})
        self.assertEqual(report['language_distribution'], {'python': 5, 'ts': 1})

    def test_duplicate_instances_and_repeated_base_commits_are_refused(self):
        rows = [row('a__one-1', 'a/one', commit='c' * 40),
                row('a__one-1', 'a/one', commit='c' * 40),
                row('a__one-2', 'a/one', commit='c' * 40),
                row('a__one-3', 'a/one', commit='d' * 40)]
        report = self.screen(rows)
        self.assertEqual(report['accepted'], 2)
        self.assertEqual(report['refusal_reasons'],
                         {'duplicate_instance_id': 1,
                          'duplicate_repository_base_commit': 1})

    def test_pinning_and_bounds_are_mandatory(self):
        rows = [row('a__one-1', 'a/one')]
        with self.assertRaisesRegex(ValueError, 'dataset identifier'):
            screen_task_pool(rows, dataset='  ', revision=REVISION)
        with self.assertRaisesRegex(ValueError, 'dataset revision'):
            screen_task_pool(rows, dataset='x/y', revision='main')
        with self.assertRaisesRegex(ValueError, 'Nonempty metadata row list'):
            self.screen([])
        with self.assertRaisesRegex(ValueError, 'exceeds the explicit ceiling'):
            self.screen(rows * 2, max_rows=1)
        with self.assertRaisesRegex(ValueError, 'Positive row ceiling'):
            self.screen(rows, max_rows=0)

    def test_the_real_permissive_allowlist_excludes_copyleft(self):
        for name in ('gpl-3.0', 'agpl-3.0', 'lgpl-2.1', 'mpl-2.0'):
            self.assertNotIn(name, PERMISSIVE_LICENSES)
        for name in ('mit', 'apache-2.0', 'bsd-3-clause', 'isc'):
            self.assertIn(name, PERMISSIVE_LICENSES)


class SelectTests(unittest.TestCase):
    def setUp(self):
        rows = []
        for owner in 'abcdef':
            for index in range(4):
                rows.append(row(f'{owner}__repo{index}-1', f'{owner}/repo{index}',
                                commit=f'{owner}{index}'.ljust(40, '0')))
        self.eligible = screen_task_pool(rows, dataset='x/y',
                                         revision=REVISION)['eligible_tasks']

    def test_selection_prefers_breadth_across_repositories(self):
        result = select_task_pool(self.eligible, seed=7401, target_tasks=6,
                                  max_per_repository=1)
        self.assertEqual(result['selected_tasks'], 6)
        self.assertEqual(result['selected_repositories'], 6)
        self.assertTrue(result['target_met'])
        self.assertEqual(result['shortfall'], 0)
        self.assertEqual({r['selection_round'] for r in result['selection']}, {0})

    def test_selection_is_deterministic_for_a_seed_and_changes_with_it(self):
        first = select_task_pool(self.eligible, seed=1, target_tasks=5)
        again = select_task_pool(self.eligible, seed=1, target_tasks=5)
        other = select_task_pool(self.eligible, seed=2, target_tasks=5)
        self.assertEqual([r['instance_id'] for r in first['selection']],
                         [r['instance_id'] for r in again['selection']])
        self.assertNotEqual([r['instance_id'] for r in first['selection']],
                            [r['instance_id'] for r in other['selection']])

    def test_owner_cap_limits_concentration_and_is_reported(self):
        result = select_task_pool(self.eligible, seed=3, target_tasks=24,
                                  max_per_repository=2, max_per_owner=2)
        per_owner = {}
        for record in result['selection']:
            per_owner[record['owner']] = per_owner.get(record['owner'], 0) + 1
        self.assertTrue(all(count <= 2 for count in per_owner.values()))
        self.assertEqual(result['selected_tasks'], 12)
        self.assertEqual(result['shortfall'], 12)
        self.assertFalse(result['target_met'])
        self.assertEqual(result['owners_at_cap'], list('abcdef'))

    def test_shortfall_is_reported_rather_than_breaking_a_cap(self):
        result = select_task_pool(self.eligible, seed=5, target_tasks=100,
                                  max_per_repository=1)
        self.assertEqual(result['selected_tasks'], 24)
        self.assertEqual(result['shortfall'], 76)
        self.assertFalse(result['target_met'])

    def test_malformed_selection_inputs_are_refused(self):
        cases = [({'seed': -1}, 'Nonnegative integer seed'),
                 ({'target_tasks': 0}, 'Positive task target'),
                 ({'max_per_repository': 0}, 'Positive per-repository cap'),
                 ({'max_per_repository': 3, 'max_per_owner': 1}, 'at least the'),
                 ({'records': []}, 'Nonempty eligible task list')]
        for override, message in cases:
            arguments = {'records': self.eligible, 'seed': 1, 'target_tasks': 2}
            arguments.update(override)
            records = arguments.pop('records')
            with self.assertRaisesRegex(ValueError, message):
                select_task_pool(records, **arguments)

    def test_duplicate_eligible_identity_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate eligible task identity'):
            select_task_pool(self.eligible + self.eligible[:1], seed=1,
                             target_tasks=2)


class CohortTests(unittest.TestCase):
    def selection_of(self, owners, repos_per_owner=1, **kwargs):
        rows = [row(f'{owner}__repo{index}-1', f'{owner}/repo{index}',
                    commit=f'{owner}{index}'.ljust(40, '0'))
                for owner in owners for index in range(repos_per_owner)]
        eligible = screen_task_pool(rows, dataset='x/y',
                                    revision=REVISION)['eligible_tasks']
        return select_task_pool(eligible, seed=11, target_tasks=len(rows),
                                max_per_repository=repos_per_owner, **kwargs)

    def setUp(self):
        self.selection = self.selection_of('abcdef')

    def test_cohorts_are_repository_and_owner_disjoint(self):
        result = disjoint_cohorts(self.selection, cohorts=[
            {'name': 'train', 'tasks': 2},
            {'name': 'development', 'tasks': 2},
            {'name': 'confirmation', 'tasks': 2}])
        self.assertTrue(result['repository_disjoint'])
        self.assertTrue(result['owner_disjoint'])
        self.assertTrue(result['owner_indivisible'])
        self.assertFalse(result['split_frozen'])
        self.assertEqual([cohort['name'] for cohort in result['cohorts']],
                         ['train', 'development', 'confirmation'])
        identifiers = [identity for cohort in result['cohorts']
                       for identity in cohort['instance_ids']]
        self.assertEqual(sorted(identifiers), sorted(set(identifiers)))
        self.assertEqual(len(identifiers), 6)
        self.assertEqual(result['selection_tasks'], 6)
        self.assertEqual(result['owners'], 6)

    def test_shares_are_approached_and_deviation_is_reported(self):
        result = disjoint_cohorts(self.selection, cohorts=[
            {'name': 'train', 'share': Fraction(1, 2)},
            {'name': 'development', 'share': Fraction(1, 4)},
            {'name': 'confirmation', 'share': Fraction(1, 4)}])
        sizes = {cohort['name']: cohort['tasks'] for cohort in result['cohorts']}
        self.assertEqual(sum(sizes.values()), 6)
        self.assertEqual(sizes['train'], 3)
        self.assertEqual(result['maximum_deviation_tasks'], 0.5)
        train = next(c for c in result['cohorts'] if c['name'] == 'train')
        self.assertEqual(train['requested_tasks'], 3.0)
        self.assertEqual(train['achieved_share'], [3, 6])

    def test_whole_owners_stay_together_even_when_that_skews_a_share(self):
        # One owner holds four repositories; it cannot be divided to balance.
        selection = self.selection_of('ab', repos_per_owner=4)
        result = disjoint_cohorts(selection, cohorts=[
            {'name': 'train', 'share': Fraction(7, 8)},
            {'name': 'held_out', 'share': Fraction(1, 8)}])
        sizes = {cohort['name']: cohort['tasks'] for cohort in result['cohorts']}
        self.assertEqual(sizes, {'train': 4, 'held_out': 4})
        self.assertEqual(result['maximum_deviation_tasks'], 3.0)
        for cohort in result['cohorts']:
            self.assertEqual(cohort['owners'], 1)

    def test_cohort_sizes_must_sum_to_the_selection(self):
        with self.assertRaisesRegex(ValueError, 'sum to the selection size'):
            disjoint_cohorts(self.selection, cohorts=[{'name': 'a', 'tasks': 2},
                                                      {'name': 'b', 'tasks': 2}])

    def test_shares_must_sum_to_one_and_modes_cannot_be_mixed(self):
        with self.assertRaisesRegex(ValueError, 'sum to exactly one'):
            disjoint_cohorts(self.selection, cohorts=[
                {'name': 'a', 'share': Fraction(1, 2)},
                {'name': 'b', 'share': Fraction(1, 4)}])
        with self.assertRaisesRegex(ValueError, 'by share or every cohort by count'):
            disjoint_cohorts(self.selection, cohorts=[
                {'name': 'a', 'share': Fraction(1, 2)}, {'name': 'b', 'tasks': 3}])

    def test_malformed_cohort_declarations_are_refused(self):
        cases = [([{'name': 'a', 'tasks': 6}], 'At least two named cohorts'),
                 ([{'name': 'a', 'tasks': 3}, {'name': 'a', 'tasks': 3}],
                  'Unique nonempty cohort name'),
                 ([{'name': 'a', 'tasks': 0}, {'name': 'b', 'tasks': 6}],
                  'positive task count'),
                 ([{'name': 'a', 'tasks': 3}, {'name': 'b'}],
                  'a share or a task count'),
                 ([{'name': 'a', 'share': 0.5}, {'name': 'b', 'share': 0.5}],
                  'exact Fraction')]
        for cohorts, message in cases:
            with self.assertRaisesRegex(ValueError, message):
                disjoint_cohorts(self.selection, cohorts=cohorts)

    def test_more_cohorts_than_owners_is_refused(self):
        selection = self.selection_of('ab')
        with self.assertRaisesRegex(ValueError, 'cannot be filled from 2 owners'):
            disjoint_cohorts(selection, cohorts=[{'name': 'a', 'share': Fraction(1, 3)},
                                                 {'name': 'b', 'share': Fraction(1, 3)},
                                                 {'name': 'c', 'share': Fraction(1, 3)}])


if __name__ == '__main__':
    unittest.main()
