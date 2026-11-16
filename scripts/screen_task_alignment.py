"""Automated task-alignment screen for resolved rollout trajectories (not a human review).

For every tokenized history (TOKENS/<instance_id>/tokens.json present), decides accept or
reject from measured facts only, and writes:

  task-reviews.json  the `task_alignment` gate document ({schema_version, task_reviews:
                     [{task_id, repository_group, decision, rationale}]}) for ACCEPTED
                     tasks only, so the corpus selection can cover it exactly
  screen.json        every task with its facts, decision and reason (accepted and rejected)
  selection.json     assembly rows for the accepted tasks (split `train`)

Accept only if all hold:
  licence     the pool licence review outcome is `confirmed` (copyleft, mismatch, absent and
              indeterminate tasks are excluded)
  cohort      the task is in the train cohort and not in the frozen confirmation cohort
  resolved    swegemma's verifier resolved the agent's own patch (hidden reference tests)
  no tests    the agent's patch edits no test file or test configuration
  located     the patch edits at least one non-test file that the reference patch edits
  size        the patch changes at most max(10 x reference lines, 200) lines
  length      the tokenized example is within the 32,768-token cap (tokens.json exists)

The rationale records these facts. A passing screen is evidence of semantic alignment at the
level of location and verified behaviour; it is not a claim of universal correctness.
"""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record

TEST_PATH = re.compile(r'(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)conftest\.py$|'
                       r'(^|/)(pytest\.ini|tox\.ini|setup\.cfg|pyproject\.toml)$')


def patch_files(patch):
    """{path: changed_lines} from a unified diff (b/ side; new and deleted files included)."""
    files, current = {}, None
    for line in patch.splitlines():
        if line.startswith('diff --git '):
            parts = line.split(' b/', 1)
            current = parts[1].strip() if len(parts) == 2 else None
            if current:
                files.setdefault(current, 0)
        elif line.startswith('+++ ') or line.startswith('--- '):
            continue
        elif current and (line.startswith('+') or line.startswith('-')):
            files[current] += 1
    return files


def decide(facts):
    checks = [('licence', facts['licence'] == 'confirmed', f"licence review outcome {facts['licence']}"),
              ('cohort', facts['cohort'] == 'train', f"cohort {facts['cohort']}"),
              ('resolved', facts['resolved'] is True, 'verifier did not resolve the patch'),
              ('no tests', not facts['agent_test_files'], f"edits test files {facts['agent_test_files']}"),
              ('located', bool(facts['shared_source_files']), 'no source file in common with the reference'),
              ('size', facts['agent_lines'] <= max(10 * facts['reference_lines'], 200),
               f"{facts['agent_lines']} changed lines against {facts['reference_lines']} in the reference"),
              ('length', facts['tokenized'], 'over the 32,768-token cap')]
    failed = [reason for name, ok, reason in checks if not ok]
    return ('accepted', None) if not failed else ('rejected', '; '.join(failed))


def rationale(facts):
    return (f"Automated screen, no human review. The agent's patch was resolved by swegemma's verifier "
            f"against the hidden reference tests; it edits {len(facts['agent_files'])} file(s), "
            f"{facts['agent_lines']} changed lines, none of them tests, and shares "
            f"{', '.join(facts['shared_source_files'])} with the reference patch "
            f"({facts['reference_lines']} changed lines). Licence {facts['licence']} by the pool review; "
            f"train cohort. This accepts location and verified-behaviour alignment only, not universal "
            f"correctness or equivalence to the reference.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--tokens', type=Path, required=True, help='TOKENS/<instance_id>/{tokens,report}.json')
    parser.add_argument('--results-root', type=Path, action='append', required=True)
    parser.add_argument('--parquet', type=Path, required=True, help='SWE-rebench-V2 at the pinned revision')
    parser.add_argument('--observations', type=Path,
                        default=ROOT / 'evidence/data/pool-licence-review-001/observations.json')
    parser.add_argument('--cohorts', type=Path, default=ROOT / 'evidence/data/task-pool-v2-python-001/cohorts.json')
    parser.add_argument('--candidate-prefix', default='', help='prefix of candidate_directory in selection rows')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import pyarrow.parquet as pq
    observations = {o['instance_id']: o for o in json.loads(args.observations.read_text())}
    cohort_of = {}
    for cohort in json.loads(args.cohorts.read_text())['cohorts']:
        for iid in cohort['instance_ids']:
            cohort_of[iid] = cohort['name']
    gold = {r['instance_id']: r['patch'] for r in pq.read_table(args.parquet, columns=['instance_id', 'patch']).to_pylist()}
    results = {}
    for root in args.results_root:
        for path in sorted(root.glob('*/results/task_results.jsonl')):
            for line in path.read_text().splitlines():
                row = json.loads(line)
                if row.get('resolved') and row['instance_id'] not in results:
                    results[row['instance_id']] = (row, path.parent / 'patches' / f"{row['instance_id']}.patch")
    screen, reviews, selection = [], [], []
    for directory in sorted(p for p in args.tokens.iterdir() if p.is_dir()):
        iid = directory.name
        row, patch_path = results.get(iid, (None, None))
        agent = patch_files(patch_path.read_text()) if patch_path and patch_path.exists() else {}
        reference = patch_files(gold.get(iid, ''))
        observation = observations.get(iid, {})
        facts = {'licence': observation.get('outcome', 'missing'), 'cohort': cohort_of.get(iid, 'none'),
                 'resolved': bool(row and row.get('resolved')),
                 'agent_files': sorted(agent), 'agent_lines': sum(agent.values()),
                 'agent_test_files': sorted(f for f in agent if TEST_PATH.search(f)),
                 'reference_lines': sum(n for f, n in reference.items() if not TEST_PATH.search(f)),
                 'shared_source_files': sorted(f for f in agent if f in reference and not TEST_PATH.search(f)),
                 'tokenized': (directory / 'tokens.json').exists(),
                 'patch': file_record(patch_path) if patch_path and patch_path.exists() else None}
        decision, reason = decide(facts)
        group = observation.get('repository_group', iid.rsplit('-', 1)[0])
        screen.append({'task_id': iid, 'repository_group': group, 'decision': decision, 'reason': reason, **facts})
        if decision == 'accepted':
            reviews.append({'task_id': iid, 'repository_group': group, 'decision': 'accepted',
                            'rationale': rationale(facts)})
            selection.append({'example_id': iid, 'task_id': iid, 'repository_group': group,
                              'leakage_group': observation.get('owner', group.split('/')[0]), 'split': 'train',
                              'candidate_directory': args.candidate_prefix + iid})
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'screen.json').write_bytes(canonical_json(screen))
    (args.output / 'task-reviews.json').write_bytes(canonical_json({
        'schema_version': 1, 'method': 'automated alignment screen (scripts/screen_task_alignment.py); no human review',
        'script': file_record(Path(__file__)), 'task_reviews': reviews, 'training_approved': False}))
    (args.output / 'selection.json').write_bytes(canonical_json(selection))
    rejected = [s for s in screen if s['decision'] == 'rejected']
    print(json.dumps({'screened': len(screen), 'accepted': len(reviews), 'rejected': len(rejected),
                      'reasons': sorted({s['reason'] for s in rejected})[:12]}))


if __name__ == '__main__':
    main()
