"""Paired comparison of two official-harness runs over the frozen cohort.

Reads each candidate's swegemma task_results.jsonl, checks the cohort against
the frozen split (the holdout is refused), and writes comparison.json with the
protocol's primary metric, exact McNemar test, Wilson and bootstrap intervals,
outcome classes and per-repository counts to a new --output.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.official_split import require_cohort
from zenithsync.paired_eval import compare, load_task_results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', type=Path, required=True)
    parser.add_argument('--split-sha256', required=True)
    parser.add_argument('--task-ids', type=Path, required=True, help='task_ids.json from the run')
    parser.add_argument('--tasks', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if file_record(args.split)['sha256'] != args.split_sha256:
        raise ValueError('Split differs from its supplied identity')
    cohort = require_cohort(load_json(args.split), load_json(args.task_ids))
    repos = {}
    for line in args.tasks.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            repos[row['instance_id']] = row['repo']
    inputs = {'base': args.base / 'task_results.jsonl', 'candidate': args.candidate / 'task_results.jsonl'}
    result = compare(cohort, load_task_results(inputs['base']), load_task_results(inputs['candidate']),
                     repos=repos, seed=args.split_sha256)
    result['inputs'] = {name: file_record(path) for name, path in inputs.items()}
    result['split'] = file_record(args.split)
    result['sources'] = {name: file_record(ROOT / name) for name in
                         ('scripts/compare_paired_eval.py', 'zenithsync/paired_eval.py')}
    args.output.mkdir(parents=True)
    (args.output / 'comparison.json').write_bytes(canonical_json(result))
    summary = {'tasks': result['tasks'], 'base_resolved': result['base']['resolved'],
               'candidate_resolved': result['candidate']['resolved'],
               'candidate_only': result['paired']['candidate_only'],
               'base_only': result['paired']['base_only'],
               'exact_mcnemar_p': result['paired']['exact_mcnemar_p']}
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
