"""Check which fused SDPA kernels accept Gemma 4's real attention shapes.

Run on the training GPU before loading the model. For each layer kind the 31B
config declares (sliding: head_dim 256 with a window mask; full: global_head_dim
512, causal) this runs one forward and backward at the requested sequence length
under the workers' settings — deterministic algorithms on, math and cuDNN SDPA
disabled — and records, per backend, whether it ran, how long it took and the
peak allocation. Key/value heads are pre-expanded, as transformers does whenever
a mask is present or head_dim exceeds 256, so ``enable_gqa`` is never used.

The sliding mask is ``0 <= q - kv < sliding_window``; it reproduces the shape and
density of transformers' mask for kernel selection and memory, and makes no
claim about Gemma's exact window semantics.

Exit status 0 only if the workers' policy (flash or memory-efficient) ran for
every layer kind, and the windowed sliding path ran too. Writes ``receipt.json``
under a new ``--output``.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record


def layer_shapes(config):
    text = config['text_config']
    heads = text['num_attention_heads']
    full_kv = text['num_global_key_value_heads'] if text['attention_k_eq_v'] else text['num_key_value_heads']
    kinds = {}
    for kind in sorted(set(text['layer_types'])):
        if kind == 'sliding_attention':
            kinds[kind] = {'heads': heads, 'kv_heads': text['num_key_value_heads'],
                           'head_dim': text['head_dim'], 'window': text['sliding_window']}
        elif kind == 'full_attention':
            kinds[kind] = {'heads': heads, 'kv_heads': full_kv,
                           'head_dim': text['global_head_dim'], 'window': None}
        else:
            raise ValueError('Unsupported layer type: ' + kind)
    return kinds


def run_case(torch, shape, length, backends, windowed=False):
    from torch.nn.attention import sdpa_kernel
    from zenithsync.windowed_attention import windowed_attention
    generator = torch.Generator(device='cuda').manual_seed(7401)
    size = (1, shape['heads'], length, shape['head_dim'])
    q, k, v = (torch.randn(size, device='cuda', dtype=torch.bfloat16, generator=generator)
               .requires_grad_(True) for _ in range(3))
    mask = None
    if shape['window'] is not None and not windowed:
        positions = torch.arange(length, device='cuda')
        delta = positions[:, None] - positions[None, :]
        mask = ((delta >= 0) & (delta < shape['window']))[None, None]
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    baseline = torch.cuda.memory_allocated()
    started = time.monotonic()
    try:
        with sdpa_kernel(backends):
            if windowed:
                out = windowed_attention(q, k, v, window=shape['window'], scale=1.0)
            else:
                out = torch.nn.functional.scaled_dot_product_attention(
                    q, k, v, attn_mask=mask, is_causal=mask is None, scale=1.0)
            out.backward(torch.ones_like(out))
        torch.cuda.synchronize()
        result = {'status': 'ran', 'seconds': time.monotonic() - started,
                  'peak_extra_bytes': torch.cuda.max_memory_allocated() - baseline,
                  'finite': bool(torch.isfinite(q.grad).all().item())}
    except RuntimeError as error:
        torch.cuda.synchronize()
        result = {'status': 'refused', 'error': str(error).splitlines()[0][:400]}
    del q, k, v, mask
    torch.cuda.empty_cache()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--sequence-tokens', type=int, default=24366)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.sequence_tokens < 2:
        raise ValueError('Sequence length of at least two required')
    config = json.loads(args.config.read_text())
    shapes = layer_shapes(config)
    args.output.mkdir(parents=True, exist_ok=False)
    import torch
    from torch.nn.attention import SDPBackend
    from zenithsync.packed_base import restrict_attention_kernels
    if not torch.cuda.is_available():
        raise ValueError('CUDA device required')
    torch.use_deterministic_algorithms(True)
    flags = restrict_attention_kernels()
    candidates = {'flash': [SDPBackend.FLASH_ATTENTION],
                  'mem_efficient': [SDPBackend.EFFICIENT_ATTENTION],
                  'policy': [SDPBackend.FLASH_ATTENTION, SDPBackend.EFFICIENT_ATTENTION]}
    results = {kind: {'shape': shape, **{name: run_case(torch, shape, args.sequence_tokens, backends)
                                         for name, backends in candidates.items()}}
               for kind, shape in shapes.items()}
    if 'sliding_attention' in results:
        # The workers' path for sliding layers: window-sized blocks, same kernels.
        results['sliding_attention']['windowed'] = run_case(
            torch, shapes['sliding_attention'], args.sequence_tokens, candidates['policy'], windowed=True)
    passed = all(row['policy']['status'] == 'ran' and row['policy']['finite'] for row in results.values())
    if 'sliding_attention' in results:
        windowed = results['sliding_attention']['windowed']
        passed = passed and windowed['status'] == 'ran' and windowed['finite']
    receipt = {'schema_version': 1, 'status': 'passed' if passed else 'failed',
               'device': torch.cuda.get_device_name(0), 'capability': list(torch.cuda.get_device_capability(0)),
               'torch': torch.__version__, 'sequence_tokens': args.sequence_tokens,
               'deterministic': torch.are_deterministic_algorithms_enabled(), 'flags': flags,
               'config': file_record(args.config), 'results': results,
               'scope': 'Isolated SDPA forward and backward at real head shapes; not a model run'}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print(json.dumps({kind: {name: [value['status'], round(value.get('seconds') or 0, 3)]
                             for name, value in row.items() if name != 'shape'}
                      for kind, row in results.items()}))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
