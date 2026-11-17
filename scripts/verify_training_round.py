"""Gate a fine-tuning round before any evaluation GPU time is spent on it.

Reads the worker's worker.json, the schedule, and the PEFT export, and FAILS (exit 1) unless:

  session      worker status `corpus_session_returned`, session status `schedule_complete`,
               and exactly one checkpoint per scheduled update
  identity     the final checkpoint's file matches its recorded sha256 and size; the export
               receipt names that checkpoint; every exported file matches the receipt
  loss         every update's loss is finite; the mean loss of the last third of updates is
               below the mean of the first third (a round that did not reduce training loss
               is not evaluated)
  memory       the recorded peak device memory is below the device total
  adapter      adapter_config.json declares the expected rank and alpha; the safetensors hold
               an A and a B matrix for every adapted projection, all finite; at least 95% of
               the B matrices are non-zero (LoRA initialises B to zero, so an all-zero B means
               the adapter does nothing)

Writes a JSON verdict with every measured value, pass or fail, to --output.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 22), b''):
            digest.update(block)
    return digest.hexdigest()


def loss_of(metrics):
    for key in ('loss', 'mean_loss', 'token_weighted_loss', 'train_loss'):
        if isinstance(metrics.get(key), (int, float)):
            return float(metrics[key])
    found = [v for k, v in metrics.items() if 'loss' in k and isinstance(v, (int, float))]
    return float(found[0]) if found else None


def thirds(values):
    third = max(1, len(values) // 3)
    return sum(values[:third]) / third, sum(values[-third:]) / third


def check_adapter(export_dir, expected_rank, expected_alpha):
    from safetensors.torch import load_file
    import torch
    config = json.loads((export_dir / 'adapter' / 'adapter_config.json').read_text())
    tensors = load_file(str(export_dir / 'adapter' / 'adapter_model.safetensors'))
    a = {k: v for k, v in tensors.items() if 'lora_A' in k}
    b = {k: v for k, v in tensors.items() if 'lora_B' in k}
    nonfinite = [k for k, v in tensors.items() if not torch.isfinite(v.float()).all()]
    zero_b = [k for k, v in b.items() if float(v.float().abs().max()) == 0.0]
    b_norms = sorted(float(v.float().norm()) for v in b.values())
    return {'rank': config.get('r'), 'alpha': config.get('lora_alpha'),
            'target_modules': config.get('target_modules'), 'tensors': len(tensors),
            'lora_A': len(a), 'lora_B': len(b), 'nonfinite': nonfinite[:10],
            'zero_B': len(zero_b), 'b_norm_median': b_norms[len(b_norms) // 2] if b_norms else None,
            'ok': (config.get('r') == expected_rank and config.get('lora_alpha') == expected_alpha
                   and len(a) == len(b) > 0 and not nonfinite and len(zero_b) <= 0.05 * len(b))}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--worker-json', type=Path, required=True)
    parser.add_argument('--schedule', type=Path, required=True)
    parser.add_argument('--export-dir', type=Path, required=True)
    parser.add_argument('--expected-rank', type=int, default=4)
    parser.add_argument('--expected-alpha', type=int, default=8)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    worker = json.loads(args.worker_json.read_text())
    schedule = json.loads(args.schedule.read_text())
    session = worker.get('session', {})
    checkpoints = session.get('checkpoints', [])
    scheduled = schedule.get('updates')
    if not isinstance(scheduled, int):
        scheduled = len(scheduled) if isinstance(scheduled, list) else schedule.get('completed_updates')
    verdict = {'checks': {}}
    checks = verdict['checks']
    checks['session'] = {'worker_status': worker.get('status'), 'session_status': session.get('status'),
                         'checkpoints': len(checkpoints), 'scheduled_updates': scheduled,
                         'ok': (worker.get('status') == 'corpus_session_returned'
                                and session.get('status') == 'schedule_complete'
                                and scheduled is not None and len(checkpoints) == scheduled)}
    final = checkpoints[-1] if checkpoints else None
    receipt = json.loads((args.export_dir / 'receipt.json').read_text())
    identity_ok = bool(final) and Path(final['path']).exists() and \
        sha256(final['path']) == final['identity']['sha256'] and \
        Path(final['path']).stat().st_size == final['identity']['size_bytes']
    files_ok = all(sha256(args.export_dir / 'adapter' / name) == record['sha256']
                   for name, record in receipt.get('files', {}).items())
    checks['identity'] = {'final_checkpoint': final['path'] if final else None,
                          'receipt_names_final': bool(final) and receipt.get('checkpoint') == final['identity'],
                          'final_hash_ok': identity_ok, 'export_files_ok': files_ok,
                          'ok': identity_ok and files_ok and bool(final)
                          and receipt.get('checkpoint') == final['identity']}
    losses = [loss_of(c.get('metrics') or {}) for c in checkpoints]
    finite = [x for x in losses if x is not None and math.isfinite(x)]
    first, last = thirds(finite) if finite else (None, None)
    checks['loss'] = {'per_update': [round(x, 4) if x is not None else None for x in losses],
                      'first_third_mean': first, 'last_third_mean': last,
                      'ok': len(finite) == len(losses) > 0 and last < first}
    peak = worker.get('peak_allocated_bytes')
    total = worker.get('device_total_bytes')
    checks['memory'] = {'peak_allocated_bytes': peak, 'device_total_bytes': total,
                        'ok': isinstance(peak, int) and isinstance(total, int) and peak < total}
    checks['adapter'] = check_adapter(args.export_dir, args.expected_rank, args.expected_alpha)
    verdict['pass'] = all(c['ok'] for c in checks.values())
    args.output.write_text(json.dumps(verdict, indent=1))
    print(json.dumps({'pass': verdict['pass'], **{k: v['ok'] for k, v in checks.items()},
                      'loss_first_last': [first, last], 'zero_B': checks['adapter']['zero_B'],
                      'lora_B': checks['adapter']['lora_B']}))
    if not verdict['pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
