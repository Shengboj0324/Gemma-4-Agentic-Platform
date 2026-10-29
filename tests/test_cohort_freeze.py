"""A frozen cohort must be reproducible, tamper-evident, and actually enforced."""

import hashlib
import unittest

from zenithsync.artifacts import canonical_json
from zenithsync.cohort_freeze import (CohortFreezeError, check_against_frozen,
                                      freeze_cohorts, validate_freeze)

REVISION = '10483de0f50fe5da545942705a76c6150171af7f'


def inputs(**overrides):
    base = {'dataset': 'nebius/SWE-rebench-V2', 'revision': REVISION,
            'metadata': {'sha256': 'a' * 64, 'size_bytes': 47605612},
            'exposure_ledger': {'sha256': 'b' * 64, 'size_bytes': 84000},
            'seed': 7401}
    base.update(overrides)
    return base


def report(*cohorts):
    return {'cohorts': [{'name': name, 'instance_ids': sorted(identities)}
                        for name, identities in cohorts]}


BASE = report(('train', ['alpha__one-1', 'alpha__two-3', 'beta__one-2']),
              ('development', ['gamma__one-1']),
              ('confirmation', ['delta__one-5', 'delta__two-9', 'epsilon__one-1']))


class FreezeTests(unittest.TestCase):
    def freeze(self, **overrides):
        arguments = {'cohort_report': BASE, 'reserved': ['confirmation'],
                     'frozen_at': '2026-10-29T17:00:00+00:00',
                     'reviewer': 'unit-test', 'inputs': inputs()}
        arguments.update(overrides)
        return freeze_cohorts(**arguments)

    def test_a_freeze_records_the_reserved_tasks_and_their_owners(self):
        record = self.freeze()
        self.assertEqual(record['status'], 'frozen')
        self.assertEqual(record['reserved_cohorts'], ['confirmation'])
        self.assertEqual(record['training_cohorts'], ['development', 'train'])
        self.assertEqual(record['reserved_tasks'],
                         ['delta__one-5', 'delta__two-9', 'epsilon__one-1'])
        self.assertEqual(record['reserved_owners'], ['delta', 'epsilon'])
        self.assertEqual(record['reserved_task_count'], 3)
        self.assertEqual(record['reserved_owner_count'], 2)
        self.assertEqual(record['cohort_sizes'],
                         {'train': 3, 'development': 1, 'confirmation': 3})
        self.assertFalse(record['training_approved'])
        self.assertEqual(len(record['freeze_sha256']), 64)

    def test_the_identity_covers_the_whole_body_and_nothing_else(self):
        record = self.freeze()
        body = {key: value for key, value in record.items()
                if key not in ('freeze_sha256', 'training_approved', 'scope')}
        self.assertEqual(hashlib.sha256(canonical_json(body)).hexdigest(),
                         record['freeze_sha256'])
        self.assertEqual(validate_freeze(record), record)

    def test_the_identity_changes_with_every_input_that_matters(self):
        baseline = self.freeze()['freeze_sha256']
        variants = [
            self.freeze(reserved=['development'])['freeze_sha256'],
            self.freeze(inputs=inputs(seed=1))['freeze_sha256'],
            self.freeze(inputs=inputs(metadata={'sha256': 'c' * 64,
                                                'size_bytes': 1}))['freeze_sha256'],
            self.freeze(inputs=inputs(exposure_ledger={'sha256': 'd' * 64,
                                                       'size_bytes': 1}))['freeze_sha256'],
            self.freeze(reviewer='someone-else')['freeze_sha256'],
            self.freeze(frozen_at='2026-11-01T00:00:00+00:00')['freeze_sha256'],
        ]
        self.assertEqual(len(set(variants) | {baseline}), len(variants) + 1)

    def test_a_tampered_record_is_refused(self):
        record = self.freeze()
        altered = dict(record, reserved_tasks=record['reserved_tasks'][:-1])
        with self.assertRaisesRegex(CohortFreezeError, 'does not match its contents'):
            validate_freeze(altered)
        # A correctly signed record that is nonetheless not frozen: the status
        # check must fire on its own, not only via the identity check.
        draft = dict(record, status='draft')
        body = {key: value for key, value in draft.items()
                if key not in ('freeze_sha256', 'training_approved', 'scope')}
        draft['freeze_sha256'] = hashlib.sha256(canonical_json(body)).hexdigest()
        with self.assertRaisesRegex(CohortFreezeError, 'is not frozen'):
            validate_freeze(draft)
        with self.assertRaisesRegex(CohortFreezeError, 'freeze record is required'):
            validate_freeze({'status': 'frozen'})

    def test_reserving_everything_or_nothing_is_refused(self):
        with self.assertRaisesRegex(CohortFreezeError, 'leaves nothing to train on'):
            self.freeze(reserved=['train', 'development', 'confirmation'])
        with self.assertRaisesRegex(CohortFreezeError, 'At least one reserved cohort'):
            self.freeze(reserved=[])
        with self.assertRaisesRegex(CohortFreezeError, 'not in the report'):
            self.freeze(reserved=['holdout'])

    def test_an_owner_spanning_a_reserved_and_a_training_cohort_is_refused(self):
        # Reserving by task alone would let a sibling package of a reserved
        # repository be trained on, which is the leak this check exists for.
        leaking = report(('train', ['delta__sibling-7']),
                         ('confirmation', ['delta__one-5']))
        with self.assertRaisesRegex(CohortFreezeError, 'both a reserved and a training'):
            self.freeze(cohort_report=leaking)

    def test_an_instance_in_two_cohorts_is_refused(self):
        duplicated = report(('train', ['alpha__one-1']),
                            ('confirmation', ['alpha__one-1']))
        with self.assertRaisesRegex(CohortFreezeError, 'appears in two cohorts'):
            self.freeze(cohort_report=duplicated)

    def test_unpinned_or_malformed_inputs_are_refused(self):
        cases = [
            ({'seed': 7401}, 'must pin exactly'),
            (inputs(revision='main'), '40-character commit SHA'),
            (inputs(metadata={'sha256': 'a' * 64}), 'Exact file identity'),
            (inputs(exposure_ledger={'sha256': 'z' * 64, 'size_bytes': 1}), 'SHA-256'),
            (inputs(seed=-1), 'Nonnegative integer selection seed'),
            (inputs(dataset='  '), 'dataset'),
        ]
        for value, message in cases:
            with self.assertRaisesRegex(CohortFreezeError, message):
                self.freeze(inputs=value)

    def test_a_blank_reviewer_or_timestamp_is_refused(self):
        with self.assertRaisesRegex(CohortFreezeError, 'reviewer'):
            self.freeze(reviewer=' ')
        with self.assertRaisesRegex(CohortFreezeError, 'frozen_at'):
            self.freeze(frozen_at='')

    def test_a_single_cohort_report_cannot_be_frozen(self):
        with self.assertRaisesRegex(CohortFreezeError, 'At least two cohorts'):
            self.freeze(cohort_report=report(('train', ['alpha__one-1'])))

    def test_an_empty_cohort_is_refused(self):
        with self.assertRaisesRegex(CohortFreezeError, 'no instance identities'):
            self.freeze(cohort_report=report(('train', ['alpha__one-1']),
                                             ('confirmation', [])))


class EnforcementTests(unittest.TestCase):
    def setUp(self):
        self.record = freeze_cohorts(
            cohort_report=BASE, reserved=['confirmation'],
            frozen_at='2026-10-29T17:00:00+00:00', reviewer='unit-test',
            inputs=inputs())

    def test_training_candidates_outside_the_reservation_are_accepted(self):
        result = check_against_frozen(self.record,
                                      ['alpha__one-1', 'beta__one-2', 'gamma__one-1'])
        self.assertTrue(result['no_reserved_task_used'])
        self.assertEqual(result['checked_tasks'], 3)
        self.assertEqual(result['reserved_tasks'], 3)
        self.assertEqual(result['freeze_sha256'], self.record['freeze_sha256'])

    def test_a_reserved_task_is_refused(self):
        with self.assertRaises(CohortFreezeError) as caught:
            check_against_frozen(self.record, ['alpha__one-1', 'delta__one-5'])
        self.assertIn("by_task=['delta__one-5']", str(caught.exception))

    def test_a_sibling_of_a_reserved_owner_is_refused(self):
        # Never reserved by identity, but its owner was.
        with self.assertRaises(CohortFreezeError) as caught:
            check_against_frozen(self.record, ['alpha__one-1', 'delta__brand-new-99'])
        self.assertIn("by_reserved_owner=['delta__brand-new-99']", str(caught.exception))

    def test_case_differences_cannot_evade_the_reservation(self):
        with self.assertRaises(CohortFreezeError):
            check_against_frozen(self.record, ['DELTA__ONE-5'])
        with self.assertRaises(CohortFreezeError):
            check_against_frozen(self.record, ['Delta__Something-1'])

    def test_a_wrong_or_tampered_freeze_cannot_authorise_a_check(self):
        with self.assertRaisesRegex(CohortFreezeError, 'not the expected one'):
            check_against_frozen(self.record, ['alpha__one-1'],
                                 expected_freeze_sha256='f' * 64)
        self.assertTrue(check_against_frozen(
            self.record, ['alpha__one-1'],
            expected_freeze_sha256=self.record['freeze_sha256'])['no_reserved_task_used'])
        altered = dict(self.record, reserved_tasks=[])
        with self.assertRaisesRegex(CohortFreezeError, 'does not match its contents'):
            check_against_frozen(altered, ['delta__one-5'])

    def test_malformed_candidate_lists_are_refused(self):
        with self.assertRaisesRegex(CohortFreezeError, 'nonempty candidate task list'):
            check_against_frozen(self.record, [])
        with self.assertRaisesRegex(CohortFreezeError, 'Duplicate candidate task'):
            check_against_frozen(self.record, ['alpha__one-1', 'alpha__one-1'])
        with self.assertRaisesRegex(CohortFreezeError, 'candidate task identity'):
            check_against_frozen(self.record, ['alpha__one-1', ''])


if __name__ == '__main__':
    unittest.main()
