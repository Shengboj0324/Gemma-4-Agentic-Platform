"""Evaluate submissions on frozen official tasks with the official harness.

Mirrors the competition's own path rather than reimplementing it: the official
`adk_submission.VllmServer` serves the base model with every candidate's LoRA
adapters (rank rounded by the official rule), `swegemma`'s
`setup_gemma_model_registry` routes each agent to its adapter, and `swegemma`'s
`Evaluator` runs Phase 1 (agent) and Phase 2 (hidden-test verification) in the
subprocess sandbox the Kaggle runtime uses where Docker is absent.

Candidates run *concurrently* against one server at equal concurrency, so a
paired comparison sees the same load. The whole process tree — server included
— runs in a fresh network namespace with only loopback (see
`zenithsync/netns.py`), matching the official air gap; isolation is probed and
recorded before anything starts. Only tasks in the frozen split's pilot and
development roles may be used; the holdout is refused.

Differences from the scoring machine, recorded in the receipt: one A100 with
tensor parallelism 1 instead of four L4s with 4; subprocess sandboxes without
the official 4 GiB / 2 vCPU container limits.
"""
import argparse
import asyncio
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync import netns
from zenithsync.official_split import require_cohort

MODEL_ALIAS = 'gemma-4-31b-it-qat-w4a16-ct'
PACKAGES = ('swegemma', 'adk-submission', 'adk-eval-core', 'google-adk', 'vllm', 'torch',
            'transformers', 'compressed-tensors', 'litellm')


def versions():
    found = {}
    for name in PACKAGES:
        try:
            found[name] = version(name)
        except Exception:
            found[name] = None
    return found


def candidate_budget(candidate: Path):
    import yaml
    path = candidate / 'eval_config.yaml'
    evaluation = yaml.safe_load(path.read_text())['evaluation'] if path.exists() else {}
    keys = {'timeout_seconds', 'max_tool_calls', 'max_time_minutes', 'max_turns'}
    if set(evaluation) - keys:
        raise ValueError('Unexpected eval_config.yaml keys: ' + str(set(evaluation) - keys))
    return evaluation


def worker(args):
    """One candidate's Evaluator run against the already-running server."""
    from adk_submission.discovery import discover_adapters
    from adk_submission.resolvers.generation import install_litellm_reasoning_patch
    from swegemma.config import EvalConfig
    from swegemma.evaluate import Evaluator
    from swegemma.models.registry import setup_gemma_model_registry
    from zenithsync.harness_context import competition_context_configs
    netns.require_isolation()
    install_litellm_reasoning_patch()
    manifest = discover_adapters(args.candidate_dir)
    registry = setup_gemma_model_registry(api_base=args.api_base, api_key='EMPTY',
                                          served_model=args.served_model,
                                          adapter_manifest=manifest, backend='vllm')
    task_ids = json.loads(Path(args.task_ids_file).read_text())
    config = EvalConfig(tasks_path=args.tasks, snapshots_dir=args.data_root / 'snapshots',
                        results_dir=args.results_dir, submission_dir=args.candidate_dir,
                        models=registry, sandbox='subprocess', wheels_dir=args.data_root / 'wheels',
                        graph_dir=str(args.data_root / 'graphs'),
                        embeddings_dir=str(args.data_root / 'embeddings'),
                        task_ids=task_ids, concurrency=args.concurrency, display_mode='quiet',
                        adapter_manifest=manifest, **competition_context_configs(),
                        **candidate_budget(args.candidate_dir))
    started = time.monotonic()
    result = asyncio.run(Evaluator(config).run())
    record = {'candidate': args.name, 'resolved': result.resolved, 'total': result.total,
              'resolution_rate': result.resolution_rate, 'seconds': time.monotonic() - started,
              'adapters': sorted(manifest.adapters)}
    (Path(args.results_dir) / 'worker.json').write_bytes(canonical_json(record))
    print(json.dumps(record), flush=True)


def kv_capacity(log_text):
    tokens = re.findall(r'GPU KV cache size: ([\d,]+) tokens', log_text)
    concurrency = re.findall(r'Maximum concurrency for ([\d,]+) tokens per request: ([\d.]+)x', log_text)
    return {'kv_cache_tokens': int(tokens[-1].replace(',', '')) if tokens else None,
            'max_concurrency_at_context': ({'context': int(concurrency[-1][0].replace(',', '')),
                                            'factor': float(concurrency[-1][1])} if concurrency else None)}


def orchestrate(args):
    netns.bring_loopback_up()
    isolation = netns.require_isolation()
    split = load_json(args.split)
    if file_record(args.split)['sha256'] != args.split_sha256:
        raise ValueError('Split file differs from its independently supplied identity')
    cohort = split['roles']['pilot'] + split['roles']['development']
    task_ids = require_cohort(split, args.task_id or cohort)
    tasks = {json.loads(l)['instance_id'] for l in args.tasks.read_text().splitlines() if l.strip()}
    if set(task_ids) - tasks:
        raise ValueError('Cohort tasks absent from tasks.jsonl')
    candidates = dict(item.split('=', 1) for item in args.candidate)
    if len(candidates) != len(args.candidate):
        raise ValueError('Duplicate candidate name')
    from adk_submission.discovery import discover_adapters
    from adk_submission.server import VllmConfig, VllmServer
    lora_modules = {}
    for name, directory in candidates.items():
        for adapter, info in discover_adapters(directory).adapters.items():
            if adapter in lora_modules:
                raise ValueError('Adapter name used by two candidates: ' + adapter)
            # VllmServer resolves a weight-file path to its checkpoint directory itself.
            lora_modules[adapter] = str(info.path)
    args.results_root.mkdir(parents=True, exist_ok=False)
    (args.results_root / 'task_ids.json').write_bytes(canonical_json(task_ids))
    config = VllmConfig(model=str(args.model), port=args.port, tool_call_parser='gemma4',
                        reasoning_parser='gemma4', max_model_len=32768,
                        gpu_memory_utilization=args.gpu_memory_utilization,
                        enable_lora=bool(lora_modules), max_loras=max(1, len(lora_modules)),
                        startup_timeout=args.startup_timeout, tensor_parallel_size=1)
    server = VllmServer(config, lora_modules=lora_modules)
    receipt = {'schema_version': 1, 'status': 'started', 'started_utc': datetime.now(timezone.utc).isoformat(),
               'network_isolation': isolation, 'versions': versions(), 'split': file_record(args.split),
               'split_freeze_sha256': split['freeze_sha256'], 'task_ids': len(task_ids),
               'candidates': {n: str(d) for n, d in candidates.items()}, 'lora_modules': lora_modules,
               'server_cmd': server.build_cmd(), 'concurrency_per_candidate': args.concurrency,
               'sandbox_setup': file_record(args.data_root / 'sandbox' / 'setup.py'),
               'script': file_record(Path(__file__)),
               'deviations_from_scoring_machine': [
                   'one A100-SXM4-80GB, tensor_parallel_size 1 (official: 4x L4, tp 4)',
                   'subprocess sandbox without per-container 4 GiB / 2 vCPU limits',
                   'candidates evaluated concurrently against one server']}
    workers = []
    server_started = time.monotonic()
    try:
        server.start()
        receipt['server_ready_seconds'] = time.monotonic() - server_started
        receipt['server'] = kv_capacity(Path(server.log_path).read_text(errors='replace'))
        for name, directory in candidates.items():
            out = args.results_root / name
            log = (args.results_root / f'{name}.worker.log').open('wb')
            command = [sys.executable, str(Path(__file__)), '--worker', '--name', name,
                       '--candidate-dir', str(directory), '--api-base', server.base_url,
                       '--served-model', str(args.model), '--tasks', str(args.tasks),
                       '--data-root', str(args.data_root), '--results-dir', str(out),
                       '--task-ids-file', str(args.results_root / 'task_ids.json'),
                       '--concurrency', str(args.concurrency)]
            workers.append((name, subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT), log))
        deadline = time.monotonic() + args.max_hours * 3600
        codes = {}
        for name, process, log in workers:
            try:
                codes[name] = process.wait(timeout=max(1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                process.kill()
                codes[name] = 'killed_at_deadline'
            log.close()
        receipt['worker_exit'] = codes
        receipt['status'] = 'completed' if all(c == 0 for c in codes.values()) else 'worker_failed'
    finally:
        for _, process, _ in workers:
            if process.poll() is None:
                process.kill()
        server.stop()
        log_text = Path(server.log_path).read_text(errors='replace')
        (args.results_root / 'vllm-server.log').write_text(log_text)
        receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
        (args.results_root / 'receipt.json').write_bytes(canonical_json(receipt))
    if receipt['status'] != 'completed':
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--name')
    parser.add_argument('--candidate-dir', type=Path)
    parser.add_argument('--api-base')
    parser.add_argument('--served-model')
    parser.add_argument('--task-ids-file')
    parser.add_argument('--results-dir', type=Path)
    parser.add_argument('--model', type=Path)
    parser.add_argument('--tasks', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--split', type=Path)
    parser.add_argument('--split-sha256')
    parser.add_argument('--candidate', action='append', default=[], help='name=directory')
    parser.add_argument('--task-id', action='append', default=[])
    parser.add_argument('--concurrency', type=int, default=2)
    parser.add_argument('--results-root', type=Path)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--gpu-memory-utilization', type=float, default=0.90)
    parser.add_argument('--startup-timeout', type=int, default=1200)
    parser.add_argument('--max-hours', type=float, default=4.0)
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return
    for name in ('model', 'split', 'split_sha256', 'results_root'):
        if getattr(args, name) is None:
            parser.error('--' + name.replace('_', '-') + ' is required')
    if not args.candidate or args.concurrency < 1:
        parser.error('At least one candidate and positive concurrency required')
    if args.results_root.exists():
        raise FileExistsError(args.results_root)
    # Offline everywhere: no hub lookups, telemetry or remote cost maps.
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', VLLM_NO_USAGE_STATS='1',
                      DO_NOT_TRACK='1', LITELLM_LOCAL_MODEL_COST_MAP='True', OTEL_SDK_DISABLED='true')
    # The harness finds the official sandbox bootstrap (sandbox/setup.py) through this.
    setup = args.data_root / 'sandbox' / 'setup.py'
    if not setup.is_file():
        raise FileNotFoundError(setup)
    os.environ['KAGGLE_SANDBOX_DIR'] = str(args.data_root / 'sandbox')
    netns.reexec_isolated()
    orchestrate(args)


if __name__ == '__main__':
    main()
