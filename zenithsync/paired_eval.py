"""Paired base-vs-candidate analysis over a frozen task cohort.

Implements the primary metric and tests of `docs/05-evaluation-protocol.md`:
resolved / all prespecified tasks, with every crash, timeout, missing result or
empty patch counted unresolved and reported separately — the denominator never
shrinks. The paired effect is Δ = (b − c) / n for b candidate-only and c
base-only resolutions, tested with the two-sided exact McNemar test, and given a
seeded percentile bootstrap interval over tasks. Marginal rates carry Wilson 95%
intervals.

These describe the sampled cohort. With tens of tasks from four repositories
they cannot support a population claim, and a non-significant difference is
not equivalence.
"""
import json
import math
import random
from statistics import median

Z95 = 1.959963984540054


def load_task_results(path):
    """Parse swegemma's task_results.jsonl; one row per instance, strictly."""
    rows = {}
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        tid = row.get('instance_id')
        if not isinstance(tid, str) or not tid:
            raise ValueError(f'Row {number} lacks an instance_id')
        if tid in rows:
            raise ValueError('Duplicate task result: ' + tid)
        if type(row.get('resolved')) is not bool:
            raise ValueError('Non-boolean resolved flag: ' + tid)
        rows[tid] = row
    return rows


def wilson(successes, n):
    if n == 0:
        return None
    p = successes / n
    denominator = 1 + Z95 ** 2 / n
    centre = (p + Z95 ** 2 / (2 * n)) / denominator
    half = Z95 * math.sqrt(p * (1 - p) / n + Z95 ** 2 / (4 * n * n)) / denominator
    return [max(0.0, centre - half), min(1.0, centre + half)]


def exact_mcnemar(b, c):
    """Two-sided exact McNemar p-value on discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, j) for j in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def bootstrap_difference(pairs, *, seed, resamples=10000):
    """Percentile 95% interval for mean(candidate − base) over resampled tasks."""
    if not pairs:
        return None
    rng = random.Random(seed)
    n = len(pairs)
    diffs = [int(c) - int(b) for b, c in pairs]
    stats = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    return [stats[int(0.025 * resamples)], stats[int(0.975 * resamples) - 1]]


def _outcome(rows, tid):
    """Classify one task. A patch is verified even when the agent ran out of
    budget, so the patch decides the class; the error is kept alongside it."""
    row = rows.get(tid)
    if row is None:
        return {'resolved': False, 'class': 'missing_result'}
    if row['resolved']:
        return {'resolved': True, 'class': 'resolved'}
    if row.get('agent_patch_size'):
        return {'resolved': False, 'class': 'patch_failed_verification'}
    error = str(row.get('error') or '')
    if 'budget' in error.lower():
        return {'resolved': False, 'class': 'budget_exhausted_no_patch'}
    if error:
        return {'resolved': False, 'class': 'error'}
    return {'resolved': False, 'class': 'no_patch'}


def _resources(rows, ids):
    present = [rows[t] for t in ids if t in rows]
    durations = [r.get('duration_seconds', 0) or 0 for r in present]
    return {'results_present': len(present),
            'median_duration_seconds': median(durations) if durations else None,
            'total_duration_seconds': sum(durations),
            'total_llm_calls': sum(r.get('total_llm_calls', 0) or 0 for r in present),
            'total_tool_calls': sum(r.get('tool_calls', 0) or 0 for r in present)}


def compare(cohort, base_rows, candidate_rows, *, repos, seed='paired-bootstrap'):
    """cohort: frozen task IDs. repos: {task_id: repository} for the breakdown."""
    ids = sorted(cohort)
    if len(set(ids)) != len(ids) or not ids:
        raise ValueError('Nonempty duplicate-free cohort required')
    extra = sorted((set(base_rows) | set(candidate_rows)) - set(ids))
    if extra:
        raise ValueError(f'Results outside the frozen cohort: {extra[:5]}')
    per_task, pairs = [], []
    classes = {'base': {}, 'candidate': {}}
    for tid in ids:
        base, cand = _outcome(base_rows, tid), _outcome(candidate_rows, tid)
        for name, outcome in (('base', base), ('candidate', cand)):
            classes[name][outcome['class']] = classes[name].get(outcome['class'], 0) + 1
        pairs.append((base['resolved'], cand['resolved']))
        per_task.append({'instance_id': tid, 'repo': repos[tid],
                         'base': base['class'], 'candidate': cand['class']})
    n = len(ids)
    base_solved = sum(b for b, _ in pairs)
    cand_solved = sum(c for _, c in pairs)
    b = sum(1 for x, y in pairs if y and not x)
    c = sum(1 for x, y in pairs if x and not y)
    by_repo = {}
    for row, (x, y) in zip(per_task, pairs):
        entry = by_repo.setdefault(row['repo'], {'tasks': 0, 'base_resolved': 0, 'candidate_resolved': 0})
        entry['tasks'] += 1
        entry['base_resolved'] += int(x)
        entry['candidate_resolved'] += int(y)
    return {'schema_version': 1, 'tasks': n,
            'base': {'resolved': base_solved, 'rate': base_solved / n,
                     'wilson95': wilson(base_solved, n), 'outcomes': classes['base'],
                     **_resources(base_rows, ids)},
            'candidate': {'resolved': cand_solved, 'rate': cand_solved / n,
                          'wilson95': wilson(cand_solved, n), 'outcomes': classes['candidate'],
                          **_resources(candidate_rows, ids)},
            'paired': {'candidate_only': b, 'base_only': c,
                       'both': sum(1 for x, y in pairs if x and y),
                       'neither': sum(1 for x, y in pairs if not x and not y),
                       'difference': (b - c) / n,
                       'bootstrap95': bootstrap_difference(pairs, seed=seed),
                       'exact_mcnemar_p': exact_mcnemar(b, c)},
            'by_repository': by_repo, 'per_task': per_task,
            'scope': 'Paired outcomes on this frozen cohort only. Missing results and errors '
                     'count as unresolved. Not a population or hidden-test claim.'}
