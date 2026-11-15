"""Measure what serving a LoRA adapter costs in latency, per target-module set.

In the held-out evaluation the adapter's agents took ~18.6 s per model call
against the base's 12.2 s. Longer outputs explain only part of that, and under
a 10-minute wall-clock budget the rest is lost turns. This separates serving
cost from behaviour: the official `VllmServer` (Gemma 4 parsers, 32,768
context) serves the base and subsets of one real adapter — every projection,
attention only (q/k/v/o), MLP only (gate/up/down) — and the same unique
long prompts go to each with a fixed output length (`ignore_eos`), so output
length cannot differ. Reports time to first token and decode rate at several
concurrencies, and each adapter's ratio to the base. Weights in a subset are
the trained ones, unchanged; only which modules carry them differs.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync.server_log import stop_keeping_log

GROUPS = {'full': ('q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'),
          'attn': ('q_proj', 'k_proj', 'v_proj', 'o_proj'),
          'mlp': ('gate_proj', 'up_proj', 'down_proj')}


def module_of(tensor_name):
    """'...layers.3.self_attn.q_proj.lora_A.weight' -> (module path, projection)."""
    path = tensor_name.split('.lora_')[0]
    return path, path.rsplit('.', 1)[1]


def subset_adapter(source, destination, projections):
    """Write the adapter restricted to `projections`; returns (tensor count, module count)."""
    from safetensors.torch import load_file, save_file
    import re
    tensors = load_file(str(source / 'adapter_model.safetensors'))
    kept = {k: v for k, v in tensors.items() if module_of(k)[1] in projections}
    if not kept:
        raise ValueError(f'No tensors for {projections}')
    modules = sorted({module_of(k)[0].removeprefix('base_model.model.') for k in kept})
    config = json.loads((source / 'adapter_config.json').read_text())
    config['target_modules'] = '(?:' + '|'.join(re.escape(m) for m in modules) + ')'
    destination.mkdir(parents=True)
    save_file(kept, str(destination / 'adapter_model.safetensors'))
    (destination / 'adapter_config.json').write_text(json.dumps(config, indent=1))
    return len(kept), len(modules)


def prompt(seed, words):
    rng = random.Random(seed)
    vocab = ['def', 'class', 'return', 'import', 'self', 'value', 'error', 'test', 'request', 'response',
             'config', 'path', 'file', 'line', 'patch', 'assert', 'module', 'raise', 'yield', 'async']
    body = ' '.join(rng.choice(vocab) for _ in range(words))
    return [{'role': 'user', 'content': f'Request {seed}. Summarise this code-like text:\n{body}'}]


def one_request(base_url, model, messages, max_tokens):
    import requests
    body = {'model': model, 'messages': messages, 'max_tokens': max_tokens, 'temperature': 0.0,
            'ignore_eos': True, 'stream': True, 'stream_options': {'include_usage': True}}
    started = time.monotonic()
    first = None
    usage = None
    with requests.post(base_url.rstrip('/') + '/chat/completions', json=body, stream=True, timeout=900) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line.startswith(b'data: ') or line == b'data: [DONE]':
                continue
            chunk = json.loads(line[6:])
            if chunk.get('usage'):
                usage = chunk['usage']
            for choice in chunk.get('choices') or []:
                delta = choice.get('delta') or {}
                if first is None and any(delta.get(k) for k in ('content', 'reasoning_content', 'reasoning')):
                    first = time.monotonic()
    total = time.monotonic() - started
    tokens = (usage or {}).get('completion_tokens')
    ttft = (first - started) if first else None
    decode = (tokens - 1) / (total - ttft) if tokens and ttft and total > ttft else None
    return {'ttft_s': ttft, 'total_s': total, 'completion_tokens': tokens,
            'prompt_tokens': (usage or {}).get('prompt_tokens'), 'decode_tok_s': decode}


def summarise(rows):
    def med(key):
        values = [r[key] for r in rows if r[key] is not None]
        return statistics.median(values) if values else None
    return {'requests': len(rows), 'ttft_s': med('ttft_s'), 'total_s': med('total_s'),
            'decode_tok_s': med('decode_tok_s'), 'completion_tokens': med('completion_tokens'),
            'prompt_tokens': med('prompt_tokens')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--adapter-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--concurrency', type=int, action='append', default=[])
    parser.add_argument('--prompt-words', type=int, default=4500)
    parser.add_argument('--max-tokens', type=int, default=256)
    parser.add_argument('--rounds', type=int, default=2, help='per cell; the first is discarded as warm-up')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    concurrencies = args.concurrency or [1, 4, 8]
    os.environ.update(VLLM_HOST_IP='127.0.0.1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                      VLLM_NO_USAGE_STATS='1', DO_NOT_TRACK='1')
    from adk_submission.server import VllmConfig, VllmServer
    args.output.mkdir(parents=True)
    variants = {}
    for name, projections in GROUPS.items():
        tensors, modules = subset_adapter(args.adapter_dir, args.output / 'adapters' / name, projections)
        variants[name] = {'projections': projections, 'tensors': tensors, 'modules': modules}
    server = VllmServer(VllmConfig(model=str(args.model), tool_call_parser='gemma4', reasoning_parser='gemma4',
                                   max_model_len=32768, gpu_memory_utilization=0.90, enable_lora=True,
                                   max_loras=len(GROUPS), startup_timeout=1500),
                        lora_modules={n: str(args.output / 'adapters' / n) for n in GROUPS})
    receipt = {'schema_version': 1, 'started_utc': datetime.now(timezone.utc).isoformat(),
               'server_cmd': server.build_cmd(), 'variants': variants, 'concurrency': concurrencies,
               'prompt_words': args.prompt_words, 'max_tokens': args.max_tokens,
               'adapter': {p.name: file_record(p) for p in sorted(args.adapter_dir.iterdir()) if p.is_file()},
               'script': file_record(Path(__file__))}
    seed = 0
    try:
        server.start()
        results = {}
        for model in ['base', *GROUPS]:
            served = str(args.model) if model == 'base' else model
            results[model] = {}
            for c in concurrencies:
                rows = []
                for round_index in range(args.rounds):
                    batch = []
                    for _ in range(c):
                        seed += 1
                        batch.append(prompt(seed, args.prompt_words))
                    with ThreadPoolExecutor(c) as pool:
                        got = list(pool.map(lambda m: one_request(server.base_url, served, m, args.max_tokens), batch))
                    if round_index > 0 or args.rounds == 1:
                        rows.extend(got)
                results[model][str(c)] = summarise(rows)
                print(model, c, json.dumps(results[model][str(c)]), flush=True)
        receipt['results'] = results
        receipt['ratio_to_base'] = {
            m: {c: {k: (results[m][c][k] / results['base'][c][k]
                        if results[m][c][k] and results['base'][c][k] else None)
                    for k in ('ttft_s', 'total_s', 'decode_tok_s')} for c in results[m]}
            for m in GROUPS}
        receipt['status'] = 'measured'
    except Exception as error:
        receipt['status'] = 'failed'
        receipt['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        try:
            stop_keeping_log(server, args.output / 'vllm-server.log')
        finally:
            receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
            (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
            print(json.dumps({'status': receipt['status'], 'ratio_to_base': receipt.get('ratio_to_base')}))


if __name__ == '__main__':
    main()
