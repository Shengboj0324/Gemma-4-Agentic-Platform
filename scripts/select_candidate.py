"""Rank screened agent candidates by fixed rules, with the evidence behind each rank.

Inputs: a finished multi-candidate run (`results/<name>/task_results.jsonl`)
and the reference candidate's name. Every candidate is compared with the
reference on the same tasks under the same load (paired). Ranking, in order:
resolved count; then fewer budget-exhausted runs without a patch; then lower
median task duration. Reported alongside, not used to rank, because they are
checks rather than goals:

- the exact McNemar p and discordant pairs against the reference;
- paired task durations against the reference: median difference, tasks
  faster/slower by more than 5 s, and a two-sided sign test. An unpaired
  median gap can come from capped runs alone, so speed claims need this;
- resolved count per repository, and whether the candidate is worse than the
  reference in any repository;
- patches touching test files, which the harness strips and which are a
  warning sign;
- a 12-hour projection for ~120 tasks at a given per-task cap, under the
  worst case of sequential execution. It uses each run's own duration,
  clipped at the cap, plus a per-task setup allowance.

A winner is named only if it resolves at least as many tasks as the
reference. Otherwise the reference stays. With tens of tasks, a lead of one
or two tasks is within noise, and the report says so, not hides it.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json
from zenithsync.paired_eval import _outcome, exact_mcnemar, load_task_results

TEST_PATH_MARKERS = ('/tests/', '/test/', 'tests/', 'test_', '_test.py', 'conftest.py', 'pytest.ini')


def touches_tests(patch):
    files = [line[6:] for line in patch.splitlines() if line.startswith('+++ b/')]
    return [f for f in files if any(m in f for m in TEST_PATH_MARKERS)]


def candidate_summary(results_dir, cap_minutes, setup_seconds, hidden_tasks):
    rows = load_task_results(results_dir / 'task_results.jsonl')
    classes = Counter(_outcome(rows, t)['class'] for t in rows)
    durations = [r.get('duration_seconds') or 0.0 for r in rows.values()]
    clipped = [min(d, cap_minutes * 60) + setup_seconds for d in durations]
    projected_hours = statistics.mean(clipped) * hidden_tasks / 3600 if clipped else None
    test_edits = {}
    for tid in rows:
        patch_file = results_dir / 'patches' / f'{tid}.patch'
        if patch_file.exists():
            hits = touches_tests(patch_file.read_text(errors='replace'))
            if hits:
                test_edits[tid] = hits
    by_repo = Counter(r['repo'] for r in rows.values() if r['resolved'])
    return rows, {'tasks': len(rows), 'resolved': sum(r['resolved'] for r in rows.values()),
                  'outcomes': dict(classes), 'budget_exhausted_no_patch': classes.get('budget_exhausted_no_patch', 0),
                  'median_duration_s': statistics.median(durations) if durations else None,
                  'projected_sequential_hours': projected_hours, 'resolved_by_repo': dict(by_repo),
                  'patches_touching_tests': test_edits}


def sign_test(wins, losses):
    """Two-sided exact sign test p-value."""
    import math
    n, k = wins + losses, min(wins, losses)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def paired_durations(rows, ref, tolerance=5.0):
    diffs = [(rows[t].get('duration_seconds') or 0.0) - (ref[t].get('duration_seconds') or 0.0) for t in ref]
    faster = sum(1 for d in diffs if d < -tolerance)
    slower = sum(1 for d in diffs if d > tolerance)
    return {'median_difference_s': statistics.median(diffs) if diffs else None, 'faster': faster,
            'slower': slower, 'sign_test_p': sign_test(faster, slower)}


def rank(summaries):
    return sorted(summaries, key=lambda n: (-summaries[n]['resolved'], summaries[n]['budget_exhausted_no_patch'],
                                            summaries[n]['median_duration_s'] or 0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-root', type=Path, required=True)
    parser.add_argument('--reference', required=True)
    parser.add_argument('--cap-minutes', type=float, required=True, help='per-task cap of the submission')
    parser.add_argument('--setup-seconds', type=float, default=45.0)
    parser.add_argument('--hidden-tasks', type=int, default=120)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    names = sorted(p.name for p in args.results_root.iterdir() if (p / 'task_results.jsonl').is_file())
    if args.reference not in names:
        raise ValueError(f'Reference {args.reference} not among {names}')
    rows, summaries = {}, {}
    for name in names:
        rows[name], summaries[name] = candidate_summary(args.results_root / name, args.cap_minutes,
                                                        args.setup_seconds, args.hidden_tasks)
    tasks = set(rows[args.reference])
    for name in names:
        if set(rows[name]) != tasks:
            raise ValueError(f'{name} covers different tasks from the reference')
    ref = rows[args.reference]
    for name in names:
        b = sum(1 for t in tasks if rows[name][t]['resolved'] and not ref[t]['resolved'])
        c = sum(1 for t in tasks if ref[t]['resolved'] and not rows[name][t]['resolved'])
        worse_repos = sorted(repo for repo in set(summaries[args.reference]['resolved_by_repo']) |
                             set(summaries[name]['resolved_by_repo'])
                             if summaries[name]['resolved_by_repo'].get(repo, 0)
                             < summaries[args.reference]['resolved_by_repo'].get(repo, 0))
        summaries[name]['vs_reference'] = {'candidate_only': b, 'reference_only': c,
                                           'exact_mcnemar_p': exact_mcnemar(b, c) if b + c else 1.0,
                                           'worse_in_repositories': worse_repos,
                                           'paired_durations': paired_durations(rows[name], ref)}
    order = rank(summaries)
    best = order[0]
    winner = best if summaries[best]['resolved'] >= summaries[args.reference]['resolved'] else args.reference
    report = {'schema_version': 1, 'reference': args.reference, 'cap_minutes': args.cap_minutes,
              'ranking': order, 'winner': winner, 'candidates': summaries,
              'noise_note': 'A lead of 1-2 tasks out of ~50 is within run-to-run noise; confirm before relying on it.'}
    args.output.write_bytes(canonical_json(report))
    for name in order:
        s = summaries[name]
        print(f"{name:22s} resolved {s['resolved']:2d}/{s['tasks']}  vs ref +{s['vs_reference']['candidate_only']}"
              f"/-{s['vs_reference']['reference_only']} p={s['vs_reference']['exact_mcnemar_p']:.3f}  "
              f"out-of-budget {s['budget_exhausted_no_patch']}  median {s['median_duration_s']:.0f}s  "
              f"12h-proj {s['projected_sequential_hours']:.1f}h  test-edits {len(s['patches_touching_tests'])}  "
              f"paired-time {s['vs_reference']['paired_durations']['median_difference_s']:+.0f}s "
              f"(p={s['vs_reference']['paired_durations']['sign_test_p']:.2f})")
    print('winner:', winner)


if __name__ == '__main__':
    main()
