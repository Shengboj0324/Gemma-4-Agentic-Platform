"""Measure whether a served LoRA adapter changes the model at all: compare token logprobs.

Starts the official VllmServer with the submission's adapter (as qualify_lora_serving.py does),
then sends the same greedy requests to the base model and to the adapter and compares the
chosen-token logprobs position by position (while the generated tokens agree). Prompts are the
first turns of training histories (system + user from --histories), where a trained adapter
should move the distribution most, plus one plain prompt.

  identical logprobs (max |delta| == 0)   -> the adapter is not applied by the server
  small but non-zero deltas               -> applied; effect too weak to flip greedy tokens
  large deltas / different tokens         -> applied and effective

Writes report.json.
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
from zenithsync.artifacts import canonical_json
from zenithsync import netns
from zenithsync.server_log import stop_keeping_log


def request(base_url, model, messages, max_tokens):
    import requests
    body = {'model': model, 'messages': messages, 'temperature': 0.0, 'max_tokens': max_tokens,
            'logprobs': True, 'top_logprobs': 5}
    response = requests.post(base_url.rstrip('/') + '/chat/completions', json=body, timeout=600)
    response.raise_for_status()
    choice = response.json()['choices'][0]
    content = (choice.get('logprobs') or {}).get('content') or []
    return [(item['token'], item['logprob']) for item in content]


def compare(base, adapter):
    deltas, agree = [], 0
    for (tb, lb), (ta, la) in zip(base, adapter):
        if tb != ta:
            break
        agree += 1
        deltas.append(abs(lb - la))
    return {'tokens_base': len(base), 'tokens_adapter': len(adapter), 'agreeing_prefix': agree,
            'first_divergence': agree if agree < min(len(base), len(adapter)) else None,
            'max_abs_delta': max(deltas) if deltas else None,
            'mean_abs_delta': sum(deltas) / len(deltas) if deltas else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--histories', type=Path, required=True, help='dir of <id>/history.json')
    parser.add_argument('--count', type=int, default=4)
    parser.add_argument('--max-tokens', type=int, default=48)
    parser.add_argument('--isolation', choices=netns.MODES, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    os.environ.update(VLLM_HOST_IP='127.0.0.1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                      VLLM_NO_USAGE_STATS='1', DO_NOT_TRACK='1')
    netns.isolate(args.isolation)
    from adk_submission.discovery import discover_adapters
    from adk_submission.server import VllmConfig, VllmServer
    manifest = discover_adapters(args.submission)
    adapter = next(iter(manifest.adapters))
    prompts = [('plain', [{'role': 'user', 'content': 'Explain in two sentences what a Python context manager is.'}])]
    for path in sorted(args.histories.glob('*/history.json'))[:args.count]:
        messages = json.loads(path.read_text())
        prompts.append((path.parent.name, [m for m in messages[:2] if m['role'] in ('system', 'user')]))
    server = VllmServer(VllmConfig(model=str(args.model), tool_call_parser='gemma4', reasoning_parser='gemma4',
                                   max_model_len=32768, enable_lora=True, max_loras=1, startup_timeout=1200),
                        adapter_manifest=manifest)
    args.output.mkdir(parents=True)
    report = {'started_utc': datetime.now(timezone.utc).isoformat(), 'adapter': adapter, 'results': {}}
    try:
        server.start()
        for name, messages in prompts:
            base = request(server.base_url, str(args.model), messages, args.max_tokens)
            tuned = request(server.base_url, adapter, messages, args.max_tokens)
            report['results'][name] = compare(base, tuned)
            print(json.dumps({name: report['results'][name]}), flush=True)
        values = [r['max_abs_delta'] for r in report['results'].values() if r['max_abs_delta'] is not None]
        diverged = [n for n, r in report['results'].items() if r['first_divergence'] is not None]
        report['verdict'] = ('not_applied' if values and max(values) == 0.0 and not diverged
                             else 'applied_effective' if diverged else 'applied_weak')
    finally:
        try:
            stop_keeping_log(server, args.output / 'vllm-server.log')
        finally:
            report['finished_utc'] = datetime.now(timezone.utc).isoformat()
            (args.output / 'report.json').write_bytes(canonical_json(report))
    print(json.dumps({'verdict': report['verdict']}))


if __name__ == '__main__':
    main()
