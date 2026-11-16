"""Roll out one agent over qualified converted tasks, one official worker per repository, one server.

Each repository pack (from `build_rebench_tasks.py`) carries its own snapshots and its
own test site, so each needs its own swegemma worker; starting a vLLM server per
repository would cost 10+ minutes each. This starts the official `VllmServer` once and
runs `run_official_eval.py --worker` per pack against it, at most --parallel at a
time, each with that pack's test site **prepended** (the task's dependencies must win
over the evaluating interpreter's own packages; see docs/45, track D).

Only task ids listed in a pack's `qualified.json` (gold resolves, empty does not) are
run. The whole tree is air-gapped exactly as in `run_official_eval.py`, and the
isolation is re-probed after the last worker. Writes `receipt.json` with each worker's
exit code and resolved count.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync import netns
from zenithsync.server_log import stop_keeping_log


def packs_with_work(root):
    """[(pack_dir, [task ids])] for packs whose qualified.json lists at least one task."""
    out = []
    for pack in sorted(p for p in Path(root).iterdir() if p.is_dir()):
        q = pack / 'qualified.json'
        if not q.exists():
            continue
        ids = json.loads(q.read_text())
        tasks = {json.loads(l)['instance_id'] for l in (pack / 'tasks.jsonl').read_text().splitlines() if l.strip()}
        if set(ids) - tasks:
            raise ValueError(f'{pack.name}: qualified ids absent from tasks.jsonl')
        if ids:
            out.append((pack, sorted(ids)))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--packs', type=Path, required=True)
    parser.add_argument('--candidate', required=True, help='name=directory')
    parser.add_argument('--results-root', type=Path, required=True)
    parser.add_argument('--concurrency', type=int, default=3, help='agents per worker')
    parser.add_argument('--parallel', type=int, default=3, help='workers at a time')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--gpu-memory-utilization', type=float, default=0.90)
    parser.add_argument('--startup-timeout', type=int, default=1200)
    parser.add_argument('--max-hours', type=float, default=6.0)
    parser.add_argument('--isolation', choices=netns.MODES, required=True)
    args = parser.parse_args()
    name, candidate = args.candidate.split('=', 1)
    isolation = netns.isolate(args.isolation)
    work = packs_with_work(args.packs)
    args.results_root.mkdir(parents=True, exist_ok=False)
    from adk_submission.server import VllmConfig, VllmServer
    config = VllmConfig(model=str(args.model), port=args.port, tool_call_parser='gemma4', reasoning_parser='gemma4',
                        max_model_len=32768, gpu_memory_utilization=args.gpu_memory_utilization,
                        dtype='bfloat16', startup_timeout=args.startup_timeout)
    server = VllmServer(config)
    receipt = {'schema_version': 1, 'status': 'started', 'started_utc': datetime.now(timezone.utc).isoformat(),
               'network_isolation': isolation, 'candidate': {'name': name, 'directory': candidate},
               'packs': {p.name: ids for p, ids in work}, 'tasks': sum(len(i) for _, i in work),
               'concurrency_per_worker': args.concurrency, 'parallel_workers': args.parallel,
               'test_site_order': 'prepend', 'server_cmd': server.build_cmd(),
               'script': file_record(Path(__file__)), 'workers': {}}
    deadline = time.monotonic() + args.max_hours * 3600
    running = []
    try:
        started = time.monotonic()
        server.start()
        receipt['server_ready_seconds'] = round(time.monotonic() - started, 1)
        queue = list(work)
        while queue or running:
            while queue and len(running) < args.parallel and time.monotonic() < deadline:
                pack, ids = queue.pop(0)
                out = args.results_root / pack.name
                out.mkdir()
                (out / 'task_ids.json').write_bytes(canonical_json(ids))
                log = (args.results_root / f'{pack.name}.worker.log').open('wb')
                command = [sys.executable, str(ROOT / 'scripts' / 'run_official_eval.py'), '--worker',
                           '--name', name, '--candidate-dir', candidate, '--api-base', server.base_url,
                           '--served-model', str(args.model), '--tasks', str(pack / 'tasks.jsonl'),
                           '--data-root', str(pack), '--results-dir', str(out / 'results'),
                           '--task-ids-file', str(out / 'task_ids.json'), '--concurrency', str(args.concurrency),
                           '--isolation', args.isolation, '--test-site', str(pack / 'site' / 'site-packages'),
                           '--test-site-order', 'prepend']
                running.append((pack, subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT), log,
                                time.monotonic()))
            if time.monotonic() >= deadline:
                queue = []
            for item in list(running):
                pack, process, log, t0 = item
                code = process.poll()
                if code is None and time.monotonic() >= deadline:
                    process.kill()
                    code = 'killed_at_deadline'
                if code is not None:
                    log.close()
                    running.remove(item)
                    worker = args.results_root / pack.name / 'results' / 'worker.json'
                    summary = json.loads(worker.read_text()) if worker.exists() else {}
                    receipt['workers'][pack.name] = {'exit': code, 'seconds': round(time.monotonic() - t0, 1),
                                                     'resolved': summary.get('resolved'),
                                                     'total': summary.get('total')}
                    print(json.dumps({pack.name: receipt['workers'][pack.name]}), flush=True)
            time.sleep(5)
        try:
            receipt['network_isolation_after'] = netns.isolate(args.isolation)
        except Exception as error:
            receipt['network_isolation_after'] = {'error': f'{type(error).__name__}: {error}'}
            receipt['status'] = 'isolation_lost'
        if receipt['status'] == 'started':
            receipt['status'] = 'completed'
    finally:
        for _, process, _, _ in running:
            if process.poll() is None:
                process.kill()
        try:
            stop_keeping_log(server, args.results_root / 'vllm-server.log')
        finally:
            receipt['resolved'] = sum((w.get('resolved') or 0) for w in receipt['workers'].values())
            receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
            (args.results_root / 'receipt.json').write_bytes(canonical_json(receipt))
    print(json.dumps({'tasks': receipt['tasks'], 'resolved': receipt['resolved'], 'status': receipt['status']}))


if __name__ == '__main__':
    main()
