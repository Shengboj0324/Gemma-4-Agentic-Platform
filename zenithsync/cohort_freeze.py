"""Freeze a reserved task cohort, and refuse anything that would spend it.

A held-out cohort is only held out if something later refuses to train on it.
This records which tasks are reserved, under which selection and exclusion
inputs, with an identity of its own — and then provides the check that a corpus
assembly must pass before it may use a task.

The freeze is a commitment, not a measurement. It establishes that these task
identities were reserved *before* any optimisation ran against the training
cohort, which is the only thing that makes a later comparison meaningful. It
does **not** establish that the reserved tasks are unseen: forks, backports,
vendored copies and base-model pretraining exposure are invisible here, and the
exposure ledger the selection used says of itself that it is incomplete.

Repository and owner labels are frozen alongside the task identities, because a
sibling package inside one owner is the contamination path that reserving by
task alone misses.
"""

import hashlib

from .artifacts import canonical_json
from .contracts import digest


class CohortFreezeError(ValueError):
    """A frozen cohort was contradicted, or a reserved task would be spent."""


def _nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise CohortFreezeError(name + ' must be a nonempty string')
    return value


def freeze_cohorts(cohort_report, *, reserved, frozen_at, reviewer, inputs):
    """Produce an immutable freeze record reserving the named cohorts.

    `cohort_report` is the output of `task_pool.disjoint_cohorts`. `reserved` names
    which of its cohorts are held out. `inputs` must pin everything the selection
    depended on — the dataset and its revision, the metadata file identity, the
    exposure ledger identity and the selection seed — because a freeze that
    cannot be reproduced reserves nothing a reader can check.
    """
    if not isinstance(cohort_report, dict) or 'cohorts' not in cohort_report:
        raise CohortFreezeError('A cohort report is required')
    rows = cohort_report['cohorts']
    if not isinstance(rows, list) or len(rows) < 2:
        raise CohortFreezeError('At least two cohorts are required to reserve one')
    names = [_nonempty(row['name'], 'cohort name') for row in rows]
    if len(set(names)) != len(names):
        raise CohortFreezeError('Duplicate cohort name')
    if not isinstance(reserved, (list, tuple)) or not reserved:
        raise CohortFreezeError('At least one reserved cohort is required')
    reserved = [_nonempty(name, 'reserved cohort name') for name in reserved]
    if len(set(reserved)) != len(reserved):
        raise CohortFreezeError('Duplicate reserved cohort name')
    unknown = sorted(set(reserved) - set(names))
    if unknown:
        raise CohortFreezeError('Reserved cohort is not in the report: '
                                + ','.join(unknown))
    if set(reserved) == set(names):
        raise CohortFreezeError('Reserving every cohort leaves nothing to train on')
    _nonempty(reviewer, 'reviewer')
    _nonempty(frozen_at, 'frozen_at')

    required = {'dataset', 'revision', 'metadata', 'exposure_ledger', 'seed'}
    if not isinstance(inputs, dict) or set(inputs) != required:
        raise CohortFreezeError('Freeze inputs must pin exactly ' + ','.join(sorted(required)))
    _nonempty(inputs['dataset'], 'dataset')
    revision = _nonempty(inputs['revision'], 'revision')
    if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
        raise CohortFreezeError('Revision must be a 40-character commit SHA')
    for name in ('metadata', 'exposure_ledger'):
        value = inputs[name]
        if (not isinstance(value, dict) or set(value) != {'sha256', 'size_bytes'}
                or type(value['size_bytes']) is not int or value['size_bytes'] <= 0):
            raise CohortFreezeError('Exact file identity required for ' + name)
        # Raise this module's error type, so a caller catching CohortFreezeError
        # does not have to also catch a bare ValueError from the digest helper.
        try:
            digest(value['sha256'])
        except ValueError as error:
            raise CohortFreezeError(f'Invalid {name} SHA-256: {error}') from error
    if type(inputs['seed']) is not int or inputs['seed'] < 0:
        raise CohortFreezeError('Nonnegative integer selection seed required')

    held, training = [], []
    seen_tasks = set()
    for row in rows:
        identities = row.get('instance_ids')
        if not isinstance(identities, list) or not identities:
            raise CohortFreezeError('Cohort has no instance identities: ' + row['name'])
        if sorted(identities) != sorted(set(identities)):
            raise CohortFreezeError('Duplicate instance identity in ' + row['name'])
        for identity in identities:
            _nonempty(identity, 'instance identity')
            if identity.casefold() in seen_tasks:
                raise CohortFreezeError('Instance appears in two cohorts: ' + identity)
            seen_tasks.add(identity.casefold())
        (held if row['name'] in reserved else training).append(row)

    # The reserved tasks' owners and repositories are reserved with them.
    def owners(identities):
        return sorted({identity.split('__', 1)[0].casefold()
                       for identity in identities})

    reserved_tasks = sorted(identity for row in held for identity in row['instance_ids'])
    reserved_owners = owners(reserved_tasks)
    training_tasks = sorted(identity for row in training
                            for identity in row['instance_ids'])
    overlap = sorted(set(owners(training_tasks)) & set(reserved_owners))
    if overlap:
        raise CohortFreezeError('Owner appears in both a reserved and a training '
                                'cohort: ' + ','.join(overlap))

    body = {'schema_version': 1, 'status': 'frozen',
            'frozen_at': frozen_at, 'reviewer': reviewer, 'inputs': inputs,
            'reserved_cohorts': sorted(reserved),
            'training_cohorts': sorted(set(names) - set(reserved)),
            'reserved_tasks': reserved_tasks,
            'reserved_owners': reserved_owners,
            'reserved_task_count': len(reserved_tasks),
            'reserved_owner_count': len(reserved_owners),
            'cohort_sizes': {row['name']: len(row['instance_ids']) for row in rows}}
    return {**body,
            'freeze_sha256': hashlib.sha256(canonical_json(body)).hexdigest(),
            'training_approved': False,
            'scope': 'A prospective reservation made before any optimisation. Not '
                     'evidence that the reserved tasks are unseen: forks, '
                     'backports, vendored copies and pretraining exposure are not '
                     'detected, and the exposure ledger used is incomplete by its '
                     'own account.'}


def validate_freeze(record):
    """Re-derive a freeze record's identity, refusing a tampered one."""
    if not isinstance(record, dict) or 'freeze_sha256' not in record:
        raise CohortFreezeError('A freeze record is required')
    body = {key: value for key, value in record.items()
            if key not in ('freeze_sha256', 'training_approved', 'scope')}
    if hashlib.sha256(canonical_json(body)).hexdigest() != record['freeze_sha256']:
        raise CohortFreezeError('Freeze record identity does not match its contents')
    if record.get('status') != 'frozen':
        raise CohortFreezeError('Freeze record is not frozen')
    return record


def check_against_frozen(record, tasks, *, expected_freeze_sha256=None):
    """Refuse any task, or any task whose owner, a frozen cohort reserved.

    `tasks` are the candidate task identities an assembly wants to use. Owner
    reservation is enforced as well as task reservation, because training on a
    sibling package of a reserved repository is the leak that reserving by task
    alone permits.
    """
    validate_freeze(record)
    if expected_freeze_sha256 is not None:
        try:
            digest(expected_freeze_sha256)
        except ValueError as error:
            raise CohortFreezeError(f'Invalid expected freeze digest: {error}') from error
        if record['freeze_sha256'] != expected_freeze_sha256:
            raise CohortFreezeError('Freeze record is not the expected one')
    if not isinstance(tasks, (list, tuple)) or not tasks:
        raise CohortFreezeError('A nonempty candidate task list is required')
    reserved = {identity.casefold() for identity in record['reserved_tasks']}
    reserved_owners = set(record['reserved_owners'])
    by_task, by_owner = [], []
    seen = set()
    for identity in tasks:
        _nonempty(identity, 'candidate task identity')
        key = identity.casefold()
        if key in seen:
            raise CohortFreezeError('Duplicate candidate task: ' + identity)
        seen.add(key)
        if key in reserved:
            by_task.append(identity)
            continue
        owner = identity.split('__', 1)[0].casefold()
        if owner in reserved_owners:
            by_owner.append(identity)
    if by_task or by_owner:
        raise CohortFreezeError(
            'Candidate tasks are reserved by the frozen cohort: '
            f'by_task={sorted(by_task)}, by_reserved_owner={sorted(by_owner)}')
    return {'schema_version': 1, 'checked_tasks': len(seen),
            'freeze_sha256': record['freeze_sha256'],
            'reserved_tasks': record['reserved_task_count'],
            'reserved_owners': record['reserved_owner_count'],
            'no_reserved_task_used': True,
            'scope': 'None of these candidates is a reserved task or belongs to a '
                     'reserved owner. Not a statement that they are otherwise '
                     'uncontaminated or fit to train on.'}
