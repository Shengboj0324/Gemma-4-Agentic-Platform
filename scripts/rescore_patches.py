"""Re-grade a finished run's patches under a different verification environment.

The agents' work is fixed: each task's saved patch (`patches/<id>.patch`, empty
when the agent produced none) and its recorded agent error are replayed
through swegemma's own per-task path, with the agent phase replaced by that
record. Only Phase 2 — snapshot, test patch, hidden tests — runs again, so a
change of test environment can be measured on exactly the same patches.
Writes a results tree in swegemma's format, which compare_paired_eval reads.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync import netns
from scripts.run_official_eval import use_test_site
from scripts.qualify_verifier import config_for


def recorded_attempts(results_dir):
    """{instance_id: (patch text, agent error)} from a finished candidate's results."""
    attempts = {}
    for line in (results_dir / 'task_results.jsonl').read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        tid = row['instance_id']
        patch_file = results_dir / 'patches' / f'{tid}.patch'
        patch = patch_file.read_text() if patch_file.exists() else ''
        if bool(patch.strip()) != bool(row.get('agent_patch_size')):
            raise ValueError(f'{tid}: saved patch and recorded patch size disagree')
        attempts[tid] = (patch, row.get('error'))
    return attempts


def replay_evaluator(attempts):
    from adk_eval_core.tracing import SessionTrace
    from swegemma.evaluate import Evaluator

    class ReplayEvaluator(Evaluator):
        """The official Evaluator, with the agent replaced by a recorded attempt."""

        async def _run_agent_sandbox(self, task, snapshot_path, task_index, total_tasks, **kwargs):
            patch, error = attempts[task.instance_id]
            return patch, error, SessionTrace()
    return ReplayEvaluator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, action='append', required=True, help='NAME=DIR')
    parser.add_argument('--tasks', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--concurrency', type=int, default=8)
    parser.add_argument('--test-site', type=Path)
    parser.add_argument('--test-site-order', choices=('append', 'prepend'), default='append')
    parser.add_argument('--isolation', choices=netns.MODES, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    os.environ.update(KAGGLE_SANDBOX_DIR=str(args.data_root / 'sandbox'), LITELLM_LOCAL_MODEL_COST_MAP='True')
    isolation = netns.isolate(args.isolation)
    use_test_site(args.test_site, args.test_site_order)
    args.output.mkdir(parents=True)
    receipt = {'schema_version': 1, 'started_utc': datetime.now(timezone.utc).isoformat(),
               'network_isolation': isolation, 'test_site': str(args.test_site) if args.test_site else None,
               'test_site_order': args.test_site_order, 'script': file_record(Path(__file__)), 'candidates': {}}
    for spec in args.results:
        name, directory = spec.split('=', 1)
        directory = Path(directory)
        attempts = recorded_attempts(directory)
        out = args.output / name
        config = config_for(args, out, sorted(attempts), skip_agent_patch=False)
        asyncio.run(replay_evaluator(attempts)(config).run())
        rows = [json.loads(l) for l in (out / 'task_results.jsonl').read_text().splitlines() if l.strip()]
        receipt['candidates'][name] = {'source': str(directory),
                                       'source_results': file_record(directory / 'task_results.jsonl'),
                                       'tasks': len(rows), 'resolved': sum(r['resolved'] for r in rows)}
    receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print(json.dumps(receipt['candidates']))


if __name__ == '__main__':
    main()
