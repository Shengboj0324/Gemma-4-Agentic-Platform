"""Qualify that the official vLLM launcher serves the base model with our adapter.

Starts `adk_submission.VllmServer` exactly as the scoring harness configures it
(Gemma 4 tool and reasoning parsers, 32,768 context, adapters discovered from
the submission and rank rounded by the official rule), inside the loopback-only
namespace. Then: the adapter must be listed by /v1/models; the same greedy
requests — one plain, one requiring a tool call — go to the base model and to
the adapter; the adapter's outputs must differ (a LoRA that changes nothing was
not applied) and both must parse. Writes receipt.json and the server log.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync import netns

TOOL = {'type': 'function', 'function': {
    'name': 'read_file', 'description': 'Read a file from the repository.',
    'parameters': {'type': 'object', 'properties': {'filepath': {'type': 'string'}},
                   'required': ['filepath']}}}
PROMPTS = [
    {'name': 'plain', 'messages': [{'role': 'user', 'content':
        'In one sentence: what does a failing pytest assertion tell a developer?'}], 'tools': None},
    {'name': 'tool', 'messages': [{'role': 'user', 'content':
        'The bug is in src/app/router.py. Read that file before doing anything else.'}], 'tools': [TOOL]},
]


def chat(base_url, model, prompt, max_tokens):
    import requests
    body = {'model': model, 'messages': prompt['messages'], 'temperature': 0.0, 'max_tokens': max_tokens}
    if prompt['tools']:
        body['tools'] = prompt['tools']
    started = time.monotonic()
    response = requests.post(base_url.rstrip('/') + '/chat/completions', json=body, timeout=600)
    response.raise_for_status()
    message = response.json()['choices'][0]['message']
    return {'seconds': time.monotonic() - started, 'content': message.get('content'),
            'reasoning': message.get('reasoning_content') or message.get('reasoning'),
            'tool_calls': [{'name': c['function']['name'], 'arguments': c['function']['arguments']}
                           for c in message.get('tool_calls') or []]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-tokens', type=int, default=512)
    parser.add_argument('--gpu-memory-utilization', type=float, default=0.90)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', VLLM_NO_USAGE_STATS='1', DO_NOT_TRACK='1')
    netns.reexec_isolated()
    netns.bring_loopback_up()
    isolation = netns.require_isolation()
    import requests
    from adk_submission.discovery import discover_adapters
    from adk_submission.server import VllmConfig, VllmServer
    manifest = discover_adapters(args.submission)
    if not manifest.adapters:
        raise ValueError('Submission declares no adapters')
    server = VllmServer(VllmConfig(model=str(args.model), tool_call_parser='gemma4', reasoning_parser='gemma4',
                                   max_model_len=32768, gpu_memory_utilization=args.gpu_memory_utilization,
                                   enable_lora=True, max_loras=len(manifest.adapters), startup_timeout=1200),
                        adapter_manifest=manifest)
    args.output.mkdir(parents=True)
    receipt = {'schema_version': 1, 'started_utc': datetime.now(timezone.utc).isoformat(),
               'network_isolation': isolation, 'server_cmd': server.build_cmd(),
               'adapters': {name: str(info.path) for name, info in manifest.adapters.items()},
               'script': file_record(Path(__file__))}
    try:
        started = time.monotonic()
        server.start()
        receipt['server_ready_seconds'] = time.monotonic() - started
        models = requests.get(server.base_url.rstrip('/') + '/models', timeout=30).json()
        served = [m['id'] for m in models['data']]
        receipt['served_models'] = served
        adapter = next(iter(manifest.adapters))
        if adapter not in served:
            raise ValueError(f'Adapter {adapter} not served: {served}')
        results = {}
        for prompt in PROMPTS:
            results[prompt['name']] = {'base': chat(server.base_url, str(args.model), prompt, args.max_tokens),
                                       'adapter': chat(server.base_url, adapter, prompt, args.max_tokens)}
        receipt['results'] = results
        differs = {name: r['base'] != {**r['adapter'], 'seconds': r['base']['seconds']}
                   for name, r in results.items()}
        receipt['adapter_changes_output'] = differs
        tool = results['tool']
        receipt['tool_calls_parsed'] = {side: [c['name'] for c in tool[side]['tool_calls']] for side in ('base', 'adapter')}
        ok = any(differs.values()) and all(tool[s]['tool_calls'] for s in ('base', 'adapter'))
        receipt['status'] = 'lora_serving_qualified' if ok else 'lora_serving_not_qualified'
    except Exception as error:
        receipt['status'] = 'failed'
        receipt['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        server.stop()
        log = Path(server.log_path).read_text(errors='replace')
        (args.output / 'vllm-server.log').write_text(log)
        receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print(json.dumps({'status': receipt['status'], 'adapter_changes_output': receipt.get('adapter_changes_output'),
                      'tool_calls_parsed': receipt.get('tool_calls_parsed')}))
    if receipt['status'] != 'lora_serving_qualified':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
