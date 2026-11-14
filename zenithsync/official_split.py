"""Freeze the official development tasks into pilot / development / holdout.

`docs/05-evaluation-protocol.md` allocates the 129 public tasks provisionally to
20 pilot, 29 development and 80 untouched holdout, grouped and stratified by
repository, decided without consulting any outcome. This implements exactly
that, deterministically, and returns a record whose identity can be checked
before anything runs.

Grouping: tasks sharing a base commit, or whose issue text is identical after
whitespace normalisation, are one group and always land in one role. Within a
repository, groups are ordered by SHA-256 of (seed, repository, group key) and
fill pilot, then development, then holdout, against per-repository quotas set by
largest remainder. Group sizes can push a role past its target by the size of
one group; the record says so rather than splitting a group.

The freeze is a commitment made before outcomes, not proof the tasks are unseen
by the base model's pretraining.
"""
import hashlib
import re

from .artifacts import canonical_json

ROLES = ('pilot', 'development', 'holdout')
TARGETS = {'pilot': 20, 'development': 29, 'holdout': 80}


def _normalise_issue(text):
    return re.sub(r'\s+', ' ', text or '').strip().lower()


def group_tasks(tasks):
    """Union tasks that share a base commit or an identical normalised issue."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    seen_commit, seen_issue = {}, {}
    for task in tasks:
        tid = task['instance_id']
        parent[tid] = tid
    for task in tasks:
        tid = task['instance_id']
        for index, key in ((seen_commit, (task['repo'], task['base_commit'])),
                           (seen_issue, (task['repo'], _normalise_issue(task['problem_statement'])))):
            if key in index:
                union(tid, index[key])
            else:
                index[key] = tid
    groups = {}
    for task in tasks:
        groups.setdefault(find(task['instance_id']), []).append(task['instance_id'])
    return {key: sorted(members) for key, members in groups.items()}


def _quotas(counts, targets):
    """Largest-remainder apportionment of each role's target across repositories."""
    total = sum(counts.values())
    if sum(targets.values()) != total:
        raise ValueError('Role targets must sum to the task count')
    quotas = {repo: {} for repo in counts}
    for role in ROLES:
        exact = {repo: targets[role] * n / total for repo, n in counts.items()}
        floors = {repo: int(value) for repo, value in exact.items()}
        spare = targets[role] - sum(floors.values())
        order = sorted(counts, key=lambda r: (-(exact[r] - floors[r]), r))
        for repo in order[:spare]:
            floors[repo] += 1
        for repo in counts:
            quotas[repo][role] = floors[repo]
    # Rounding per role can disagree with a repository's own size; holdout absorbs it.
    for repo, n in counts.items():
        quotas[repo]['holdout'] += n - sum(quotas[repo].values())
    return quotas


def freeze_split(tasks, *, seed, targets=None, inputs):
    targets = dict(TARGETS if targets is None else targets)
    if not isinstance(seed, str) or not seed.strip():
        raise ValueError('Nonempty seed required')
    ids = [t['instance_id'] for t in tasks]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate task identity')
    by_id = {t['instance_id']: t for t in tasks}
    groups = group_tasks(tasks)
    counts = {}
    for task in tasks:
        counts[task['repo']] = counts.get(task['repo'], 0) + 1
    quotas = _quotas(counts, targets)
    roles = {role: [] for role in ROLES}
    for repo in sorted(counts):
        repo_groups = [(key, members) for key, members in groups.items() if by_id[key]['repo'] == repo]
        repo_groups.sort(key=lambda item: hashlib.sha256(
            f'{seed}\0{repo}\0{item[0]}'.encode()).hexdigest())
        filled = {role: 0 for role in ROLES}
        for key, members in repo_groups:
            role = next((r for r in ROLES[:-1] if filled[r] < quotas[repo][r]), 'holdout')
            roles[role].extend(members)
            filled[role] += len(members)
    record = {'schema_version': 1, 'seed': seed, 'targets': targets, 'inputs': inputs,
              'roles': {role: sorted(members) for role, members in roles.items()},
              'groups': sorted(sorted(m) for m in groups.values() if len(m) > 1),
              'per_repository': {repo: {role: sum(by_id[t]['repo'] == repo for t in roles[role])
                                        for role in ROLES} for repo in sorted(counts)},
              'overshoot': {role: len(roles[role]) - targets[role] for role in ROLES},
              'scope': 'Outcome-blind commitment over task identities; not proof the tasks are '
                       'absent from base-model pretraining.'}
    record['freeze_sha256'] = hashlib.sha256(canonical_json(record)).hexdigest()
    return record


def validate_freeze(record):
    body = {k: v for k, v in record.items() if k != 'freeze_sha256'}
    if hashlib.sha256(canonical_json(body)).hexdigest() != record.get('freeze_sha256'):
        raise ValueError('Split record differs from its frozen identity')
    members = [t for role in ROLES for t in record['roles'][role]]
    if len(set(members)) != len(members):
        raise ValueError('A task appears in more than one role')
    return record


def require_cohort(record, task_ids, *, allowed=('pilot', 'development')):
    """Refuse any task outside the allowed roles — the holdout above all."""
    validate_freeze(record)
    role_of = {t: role for role in ROLES for t in record['roles'][role]}
    unknown = sorted(set(task_ids) - set(role_of))
    if unknown:
        raise ValueError(f'Tasks not in the frozen split: {unknown[:5]}')
    spent = sorted(t for t in task_ids if role_of[t] not in allowed)
    if spent:
        raise ValueError(f'Refusing to spend {len(spent)} task(s) outside {allowed}: {spent[:5]}')
    return sorted(task_ids)
