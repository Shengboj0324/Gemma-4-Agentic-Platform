"""Qualify the verification environment before any agent result is trusted.

Runs swegemma's own per-task path (snapshot resolution, Phase 2 verification)
for every requested task twice: once with the task's gold patch in place of
the agent's, and once with an empty patch (`skip_agent_patch`). On a sound
environment gold patches resolve and empty ones do not. The first full run
scored 0/40 because the sandbox had no pytest; this is the check that would
have caught it. No model is involved. Writes receipt.json and both result trees.
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


def config_for(args, results_dir, task_ids, *, skip_agent_patch):
    from adk_submission import ModelRegistry
    from adk_submission.discovery import discover_adapters
    from swegemma.config import EvalConfig
    from zenithsync.harness_context import competition_context_configs
    from scripts.run_official_eval import candidate_budget
    return EvalConfig(tasks_path=args.tasks, snapshots_dir=args.data_root / 'snapshots',
                      results_dir=results_dir, submission_dir=args.submission, models=ModelRegistry(),
                      sandbox='subprocess', wheels_dir=args.data_root / 'wheels',
                      graph_dir=str(args.data_root / 'graphs'), embeddings_dir=str(args.data_root / 'embeddings'),
                      task_ids=task_ids, concurrency=args.concurrency, display_mode='quiet',
                      adapter_manifest=discover_adapters(args.submission), skip_agent_patch=skip_agent_patch,
                      **competition_context_configs(), **candidate_budget(args.submission))


def gold_evaluator():
    from adk_eval_core.tracing import SessionTrace
    from swegemma.evaluate import Evaluator

    class GoldEvaluator(Evaluator):
        """The official Evaluator, with the agent replaced by the task's gold patch."""

        async def _run_agent_sandbox(self, task, snapshot_path, task_index, total_tasks, **kwargs):
            return task.patch, None, SessionTrace()
    return GoldEvaluator


def summarise(results_dir):
    rows = [json.loads(line) for line in (results_dir / 'task_results.jsonl').read_text().splitlines() if line]
    return {'tasks': len(rows), 'resolved': sorted(r['instance_id'] for r in rows if r['resolved']),
            'unresolved': {r['instance_id']: (r.get('error') or f"exit {r.get('test_exit_code')}")
                           for r in rows if not r['resolved']}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--task-id', action='append', required=True)
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
    from swegemma.evaluate import Evaluator
    args.output.mkdir(parents=True)
    receipt = {'schema_version': 1, 'started_utc': datetime.now(timezone.utc).isoformat(),
               'network_isolation': isolation, 'tasks': args.task_id,
               'test_site': str(args.test_site) if args.test_site else None,
               'test_site_order': args.test_site_order, 'script': file_record(Path(__file__))}
    for name, evaluator, skip in (('gold', gold_evaluator(), False), ('empty', Evaluator, True)):
        directory = args.output / name
        asyncio.run(evaluator(config_for(args, directory, args.task_id, skip_agent_patch=skip)).run())
        receipt[name] = summarise(directory)
    gold, empty = receipt['gold'], receipt['empty']
    receipt['gold_resolved'] = f"{len(gold['resolved'])}/{gold['tasks']}"
    receipt['empty_resolved'] = f"{len(empty['resolved'])}/{empty['tasks']}"
    receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print(json.dumps({k: receipt[k] for k in ('gold_resolved', 'empty_resolved')}))


if __name__ == '__main__':
    main()
