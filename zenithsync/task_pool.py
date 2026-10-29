"""Screen and select executable repository tasks from pinned public metadata.

This is the intake stage that decides which public tasks are *eligible* before
any replay compute is spent. It operates on metadata only: identifiers, commits,
language labels, licence labels and environment image names. It never reads a
gold patch, an issue body or repository source, so it cannot and does not expose
reference solutions to anything downstream.

Three honesty boundaries hold throughout:

* A publisher's licence label is a label. It is evidence for a rights review,
  never a rights clearance, and a placeholder value is rejected as unknown
  rather than optimistically treated as permissive.
* Excluding a repository that development has already seen reduces known
  contamination. It does not establish that the remainder is unseen, because
  forks, backports, vendored copies and pretraining exposure are not visible
  here.
* Deterministic hash ranking is a reproducible selection rule. It is not a
  claim of statistical independence between the tasks it selects.
"""

import hashlib
import re

from .artifacts import canonical_json

REQUIRED_FIELDS = ('instance_id', 'repo', 'base_commit', 'language', 'license',
                   'created_at')
# `image_name` is optional at validation so that screening, not parsing, decides
# whether a task without a published environment is usable. A source that has no
# images at all must still be screenable with `require_image=False`.
OPTIONAL_FIELDS = ('image_name',)

# Licences whose standard texts permit redistribution and commercial use. This
# is a screening allowlist for a reviewer, not legal advice, and it deliberately
# excludes copyleft families that need a case-by-case decision.
PERMISSIVE_LICENSES = frozenset({
    '0bsd', 'apache-2.0', 'bsd-2-clause', 'bsd-3-clause', 'bsl-1.0', 'isc',
    'mit', 'mit-0', 'psf-2.0', 'python-2.0', 'unlicense', 'zlib',
})
# Values that look like a licence but carry no decision. Treating one of these
# as permissive would manufacture a rights conclusion out of a to-do marker.
PLACEHOLDER_LICENSES = frozenset({
    '', 'custom-check-github', 'none', 'noassertion', 'other', 'unknown',
    'proprietary', 'see-license', 'todo',
})

INSTANCE_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*__[A-Za-z0-9][A-Za-z0-9._-]*$')
REPO_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$')
COMMIT_PATTERN = re.compile(r'^[0-9a-f]{40}$')


class TaskRecordError(ValueError):
    """A stable reason code; never echoes issue text, source or patch content."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _string(row, field):
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise TaskRecordError('missing_' + field)
    return value.strip()


def validate_task_record(row):
    """Normalise one metadata row, rejecting anything structurally unusable."""
    if not isinstance(row, dict):
        raise TaskRecordError('record_not_an_object')
    for field in REQUIRED_FIELDS:
        _string(row, field)
    instance = _string(row, 'instance_id')
    repo = _string(row, 'repo')
    commit = _string(row, 'base_commit').lower()
    if not INSTANCE_PATTERN.fullmatch(instance):
        raise TaskRecordError('malformed_instance_id')
    if not REPO_PATTERN.fullmatch(repo):
        raise TaskRecordError('malformed_repo')
    if not COMMIT_PATTERN.fullmatch(commit):
        raise TaskRecordError('base_commit_is_not_a_full_sha1')
    owner, _, name = repo.partition('/')
    image = row.get('image_name')
    if image is not None and not isinstance(image, str):
        raise TaskRecordError('malformed_image_name')
    return {'instance_id': instance, 'repo': repo, 'owner': owner.casefold(),
            'repository_group': repo.casefold(), 'name': name.casefold(),
            'base_commit': commit, 'language': _string(row, 'language').casefold(),
            'license': _string(row, 'license'),
            'license_key': _string(row, 'license').casefold(),
            'image_name': (image or '').strip(),
            'created_at': _string(row, 'created_at')}


def _reason_for(record, *, language, allowed_licenses, excluded_repositories,
                excluded_owners, excluded_instances, require_image,
                minimum_created_at):
    if language is not None and record['language'] != language:
        return 'language_not_selected'
    if record['license_key'] in PLACEHOLDER_LICENSES:
        return 'license_label_is_a_placeholder'
    if record['license_key'] not in allowed_licenses:
        return 'license_not_in_screening_allowlist'
    if require_image and not record['image_name']:
        return 'no_executable_environment_image'
    if record['instance_id'].casefold() in excluded_instances:
        return 'instance_excluded_as_exposed_or_reserved'
    if record['repository_group'] in excluded_repositories:
        return 'repository_excluded_as_exposed_or_reserved'
    if record['owner'] in excluded_owners:
        return 'owner_excluded_as_exposed_or_reserved'
    if minimum_created_at is not None and record['created_at'] < minimum_created_at:
        return 'created_before_minimum_date'
    return None


def screen_task_pool(rows, *, dataset, revision, language='python',
                     allowed_licenses=PERMISSIVE_LICENSES,
                     excluded_repositories=(), excluded_owners=(),
                     excluded_instances=(), require_image=True,
                     minimum_created_at=None, max_rows=1000000):
    """Partition pinned metadata rows into eligible tasks and counted refusals.

    `dataset` and `revision` pin what was screened; a pool without them cannot
    be reproduced. Every refusal keeps its reason, because a refusal rate per
    reason is the useful signal about a source, not a number to be rounded off.
    """
    if not isinstance(dataset, str) or not dataset.strip():
        raise ValueError('Pinned dataset identifier required')
    if not isinstance(revision, str) or not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('Pinned 40-character dataset revision required')
    if type(max_rows) is not int or max_rows <= 0:
        raise ValueError('Positive row ceiling required')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Nonempty metadata row list required')
    if len(rows) > max_rows:
        raise ValueError('Metadata row count exceeds the explicit ceiling')
    allowed = frozenset(name.casefold() for name in allowed_licenses)
    if allowed & PLACEHOLDER_LICENSES:
        raise ValueError('A placeholder licence value cannot be allowlisted')
    excluded_repositories = frozenset(name.casefold() for name in excluded_repositories)
    excluded_owners = frozenset(name.casefold() for name in excluded_owners)
    excluded_instances = frozenset(name.casefold() for name in excluded_instances)
    if minimum_created_at is not None and not isinstance(minimum_created_at, str):
        raise ValueError('Minimum creation date must be a comparable string')
    accepted, refused = [], []
    reasons, licenses, languages = {}, {}, {}
    seen_instances, seen_commits = {}, {}
    for row in rows:
        try:
            record = validate_task_record(row)
        except TaskRecordError as error:
            reasons[error.reason] = reasons.get(error.reason, 0) + 1
            refused.append({'instance_id': row.get('instance_id')
                            if isinstance(row, dict) else None,
                            'reason': error.reason})
            continue
        languages[record['language']] = languages.get(record['language'], 0) + 1
        key = record['instance_id'].casefold()
        if key in seen_instances:
            reasons['duplicate_instance_id'] = reasons.get('duplicate_instance_id', 0) + 1
            refused.append({'instance_id': record['instance_id'],
                            'reason': 'duplicate_instance_id'})
            continue
        seen_instances[key] = record
        reason = _reason_for(record, language=language, allowed_licenses=allowed,
                             excluded_repositories=excluded_repositories,
                             excluded_owners=excluded_owners,
                             excluded_instances=excluded_instances,
                             require_image=require_image,
                             minimum_created_at=minimum_created_at)
        if reason is None:
            # Two tasks at the same repository commit are near-certain duplicates
            # of one another's state; keep the first and count the rest.
            commit_key = (record['repository_group'], record['base_commit'])
            if commit_key in seen_commits:
                reason = 'duplicate_repository_base_commit'
            else:
                seen_commits[commit_key] = record['instance_id']
        if reason is not None:
            reasons[reason] = reasons.get(reason, 0) + 1
            refused.append({'instance_id': record['instance_id'], 'reason': reason})
            continue
        licenses[record['license']] = licenses.get(record['license'], 0) + 1
        accepted.append(record)
    repositories = {record['repository_group'] for record in accepted}
    owners = {record['owner'] for record in accepted}
    return {
        'schema_version': 1, 'dataset': dataset, 'revision': revision,
        'language_selected': language, 'require_image': require_image,
        'allowed_licenses': sorted(allowed),
        'excluded_repositories': len(excluded_repositories),
        'excluded_owners': len(excluded_owners),
        'excluded_instances': len(excluded_instances),
        'minimum_created_at': minimum_created_at,
        'rows': len(rows), 'accepted': len(accepted), 'refused': len(refused),
        'acceptance_rate': len(accepted) / len(rows),
        'refusal_reasons': dict(sorted(reasons.items())),
        'language_distribution': dict(sorted(languages.items())),
        'accepted_license_distribution': dict(sorted(licenses.items())),
        'distinct_repositories': len(repositories),
        'distinct_owners': len(owners),
        'eligible_tasks': accepted, 'refused_tasks': refused,
        'rights_cleared': False, 'replay_verified': False, 'training_approved': False,
        'scope': 'Metadata eligibility only. A licence label is evidence for a rights '
                 'review, not a clearance. Exclusions reduce known contamination and '
                 'do not establish that the remainder is unseen. No issue text, '
                 'source or reference patch was read.',
    }


def _priority(seed, stratum, value):
    return hashlib.sha256(canonical_json([
        'task-pool-selection-v1', seed, stratum, value])).hexdigest()


def select_task_pool(records, *, seed, target_tasks, max_per_repository=1,
                     max_per_owner=None):
    """Select tasks deterministically with explicit repository and owner caps.

    Selection proceeds repository by repository in hash order, taking at most
    `max_per_repository` from each before revisiting any, so breadth across
    repositories is preferred over depth in whichever repository happens to be
    largest. Shortfall against the target is reported rather than met by
    breaking a cap.
    """
    if type(seed) is not int or seed < 0:
        raise ValueError('Nonnegative integer seed required')
    if type(target_tasks) is not int or target_tasks <= 0:
        raise ValueError('Positive task target required')
    if type(max_per_repository) is not int or max_per_repository <= 0:
        raise ValueError('Positive per-repository cap required')
    if max_per_owner is not None:
        if type(max_per_owner) is not int or max_per_owner < max_per_repository:
            raise ValueError('Per-owner cap must be an integer of at least the '
                             'per-repository cap')
    if not isinstance(records, list) or not records:
        raise ValueError('Nonempty eligible task list required')
    by_repository = {}
    seen = set()
    for record in records:
        for field in ('instance_id', 'repository_group', 'owner'):
            if not isinstance(record.get(field), str) or not record[field]:
                raise ValueError('Eligible task lacks ' + field)
        if record['instance_id'] in seen:
            raise ValueError('Duplicate eligible task identity')
        seen.add(record['instance_id'])
        by_repository.setdefault(record['repository_group'], []).append(record)
    for repository, group in by_repository.items():
        group.sort(key=lambda r: (_priority(seed, repository, r['instance_id']),
                                  r['instance_id']))
    order = sorted(by_repository, key=lambda r: (_priority(seed, 'repository', r), r))
    selected, per_owner, exhausted = [], {}, set()
    owner_capped = set()
    for round_index in range(max_per_repository):
        for repository in order:
            if len(selected) >= target_tasks:
                break
            group = by_repository[repository]
            if round_index >= len(group):
                exhausted.add(repository)
                continue
            record = group[round_index]
            owner = record['owner']
            if max_per_owner is not None and per_owner.get(owner, 0) >= max_per_owner:
                owner_capped.add(owner)
                continue
            per_owner[owner] = per_owner.get(owner, 0) + 1
            selected.append({**record, 'selection_round': round_index,
                             'selection_hash': _priority(seed, repository,
                                                         record['instance_id'])})
        if len(selected) >= target_tasks:
            break
    shortfall = max(0, target_tasks - len(selected))
    return {
        'schema_version': 1, 'seed': seed, 'target_tasks': target_tasks,
        'max_per_repository': max_per_repository, 'max_per_owner': max_per_owner,
        'eligible_tasks': len(records),
        'eligible_repositories': len(by_repository),
        'selected_tasks': len(selected),
        'selected_repositories': len({r['repository_group'] for r in selected}),
        'selected_owners': len({r['owner'] for r in selected}),
        'repositories_exhausted_before_cap': len(exhausted),
        'owners_at_cap': sorted(owner_capped),
        'shortfall': shortfall,
        'target_met': shortfall == 0,
        'selection': selected,
        'training_approved': False,
        'scope': 'Deterministic, reproducible breadth-first selection under declared '
                 'caps. Hash ordering is a selection rule, not statistical '
                 'independence, and a met target is not evidence of sufficiency.',
    }


def disjoint_cohorts(selection, *, cohorts):
    """Split a selection into repository- and owner-disjoint cohorts.

    No repository and no owner may appear in two cohorts: a fork, a backport or
    a sibling package inside one owner is exactly the contamination path that
    splitting by task misses. Owners are therefore the indivisible unit, which
    means a requested share can only be approached, never hit exactly. The
    achieved size and its deviation from the request are both reported; a cohort
    is never balanced by splitting an owner across two of them.

    Each cohort declares a `name` and either `share` (an exact Fraction, with
    the shares summing to one) or `tasks` (a target count).
    """
    from fractions import Fraction

    if not isinstance(cohorts, list) or len(cohorts) < 2:
        raise ValueError('At least two named cohorts required')
    records = selection['selection']
    if not records:
        raise ValueError('Selection is empty')
    names, targets = [], []
    modes = set()
    for cohort in cohorts:
        if not isinstance(cohort, dict) or set(cohort) not in ({'name', 'share'},
                                                               {'name', 'tasks'}):
            raise ValueError('Each cohort requires exactly a name and a share or '
                             'a task count')
        name = cohort['name']
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError('Unique nonempty cohort name required')
        names.append(name)
        if 'share' in cohort:
            modes.add('share')
            share = cohort['share']
            if not isinstance(share, Fraction) or not 0 < share <= 1:
                raise ValueError('Each share must be an exact Fraction in (0, 1]')
            targets.append(share)
        else:
            modes.add('tasks')
            count = cohort['tasks']
            if type(count) is not int or count <= 0:
                raise ValueError('Each cohort needs a positive task count')
            targets.append(count)
    if len(modes) != 1:
        raise ValueError('Declare every cohort by share or every cohort by count')
    if modes == {'share'}:
        if sum(targets) != 1:
            raise ValueError('Component shares must sum to exactly one')
        wanted = [share * len(records) for share in targets]
    else:
        if sum(targets) != len(records):
            raise ValueError('Cohort task counts must sum to the selection size')
        wanted = [Fraction(count) for count in targets]
    # Owners are indivisible, so pack them largest-first into whichever cohort
    # is furthest below its target. Ties break on the deterministic hash.
    owners = {}
    for record in records:
        owners.setdefault(record['owner'], []).append(record)
    if len(owners) < len(names):
        raise ValueError(f'{len(names)} cohorts cannot be filled from {len(owners)} '
                         'owners without splitting an owner')
    order = sorted(owners, key=lambda owner: (
        -len(owners[owner]), _priority(selection['seed'], 'cohort', owner), owner))
    assignments = {name: [] for name in names}
    # Seed every cohort with one whole owner, largest cohort first, so a declared
    # cohort is never left empty by greedy filling.
    seeding = sorted(range(len(names)), key=lambda i: (-wanted[i], names[i]))
    for position, index in enumerate(seeding):
        assignments[names[index]].extend(owners[order[position]])
    for owner in order[len(names):]:
        index = min(range(len(names)),
                    key=lambda i: (len(assignments[names[i]]) - wanted[i], names[i]))
        assignments[names[index]].extend(owners[owner])
    repositories = {name: {r['repository_group'] for r in rows}
                    for name, rows in assignments.items()}
    owner_sets = {name: {r['owner'] for r in rows} for name, rows in assignments.items()}
    for left in names:
        for right in names:
            if left < right:
                if repositories[left] & repositories[right]:
                    raise ValueError('Repository appears in two cohorts')
                if owner_sets[left] & owner_sets[right]:
                    raise ValueError('Owner appears in two cohorts')
    rows = []
    for index, name in enumerate(names):
        achieved = len(assignments[name])
        rows.append({'name': name, 'tasks': achieved,
                     'requested_tasks': float(wanted[index]),
                     'deviation_tasks': achieved - float(wanted[index]),
                     'achieved_share': [achieved, len(records)],
                     'achieved_share_float': achieved / len(records),
                     'repositories': len(repositories[name]),
                     'owners': len(owner_sets[name]),
                     'instance_ids': sorted(r['instance_id']
                                            for r in assignments[name])})
    if sum(row['tasks'] for row in rows) != len(records):
        raise ValueError('Cohort assignment lost or duplicated a task')
    return {'schema_version': 1, 'seed': selection['seed'],
            'selection_tasks': len(records), 'owners': len(owners),
            'cohorts': rows,
            'maximum_deviation_tasks': max(abs(row['deviation_tasks']) for row in rows),
            'repository_disjoint': True, 'owner_disjoint': True,
            'owner_indivisible': True,
            'split_frozen': False, 'training_approved': False,
            'scope': 'Declared repository- and owner-disjoint cohorts, packed by '
                     'whole owner so a requested share is approached rather than hit. '
                     'Forks, backports, vendored copies and pretraining exposure are '
                     'not detected here, so this is not an unseen-data guarantee.'}
