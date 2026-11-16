"""Turn resolved rollout traces (swegemma ATIF v1.7) into native training histories.

For every resolved task in one or more rollout results roots (`run_rebench_rollouts.py`
output), writes OUTPUT/<instance_id>/{history.json, tools.json, receipt.json}, the
layout `audit_replay_history_tokens.py` tokenizes:

  system  <- the trace's system step (the agent instruction the harness sent)
  user    <- the trace's user steps (task prompt; later harness nudges stay user turns)
  assistant {reasoning, tool_calls}  <- each agent step that called tools
  tool    <- that step's observation, bound to the call id
  assistant {content}                <- a final agent step without calls

Only recorded text is used; nothing is re-rendered or invented. A trace is refused
(and listed in the summary with its reason) when a step has several tool calls but
not one observation per call, when a call id repeats, or when the task is not
resolved. The tools are the exact function schemas from a captured harness request,
filtered to the candidate's declared tool names. One history per task: the first
resolved attempt in root order.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record

EXCLUDED_REPOS = ('textualize__rich', 'fastapi__fastapi', 'psf__requests', 'encode__httpx')


def observations(step, calls):
    """[(call_id, text)] for one agent step, or raise ValueError."""
    obs = step.get('observation')
    if obs is None:
        raise ValueError('tool call without observation')
    if isinstance(obs, dict) and 'results' in obs:
        results = obs['results']
    elif isinstance(obs, list):
        results = obs
    else:
        results = [obs]
    if len(results) != len(calls):
        raise ValueError(f'{len(calls)} calls but {len(results)} observations')
    out = []
    for call, result in zip(calls, results):
        text = result.get('content') if isinstance(result, dict) else result
        if not isinstance(text, str):
            raise ValueError('non-text observation')
        out.append((call['tool_call_id'], text))
    return out


def trace_history(trace, allowed):
    steps = trace['steps']
    messages, seen = [], set()
    for step in steps:
        source = step['source']
        if source == 'system':
            if messages:
                raise ValueError('system step after conversation start')
            messages.append({'role': 'system', 'content': step['message']})
        elif source == 'user':
            messages.append({'role': 'user', 'content': step['message']})
        elif source == 'agent':
            calls = step.get('tool_calls') or []
            text = step.get('message') or ''
            if calls:
                out_calls = []
                for call in calls:
                    if call['function_name'] not in allowed:
                        raise ValueError('undeclared tool ' + call['function_name'])
                    if call['tool_call_id'] in seen:
                        raise ValueError('repeated call id')
                    seen.add(call['tool_call_id'])
                    args = call['arguments']
                    out_calls.append({'id': call['tool_call_id'], 'type': 'function',
                                      'function': {'name': call['function_name'],
                                                   'arguments': args if isinstance(args, str)
                                                   else json.dumps(args, ensure_ascii=False)}})
                assistant = {'role': 'assistant', 'content': '', 'tool_calls': out_calls}
                if text:
                    assistant['reasoning'] = text
                messages.append(assistant)
                names = {c['tool_call_id']: c['function_name'] for c in calls}
                for call_id, result in observations(step, calls):
                    messages.append({'role': 'tool', 'tool_call_id': call_id, 'name': names[call_id],
                                     'content': result})
            elif (step.get('extra') or {}).get('event_type') == 'final':
                messages.append({'role': 'assistant', 'content': text})
            elif text:
                messages.append({'role': 'assistant', 'content': '', 'reasoning': text})
        else:
            raise ValueError('unknown step source ' + str(source))
    if not messages or messages[0]['role'] != 'system' or not any(m['role'] == 'user' for m in messages):
        raise ValueError('missing system or user step')
    while messages and messages[-1]['role'] == 'assistant' and not messages[-1].get('content') \
            and not messages[-1].get('tool_calls'):
        messages.pop()  # a trailing reasoning-only fragment has no supervised action
    return messages


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--results-root', type=Path, action='append', required=True)
    parser.add_argument('--protocol', type=Path,
                        default=ROOT / 'evidence/data/source-http-client-001/success/http-fixture/exchanges.json')
    parser.add_argument('--tools', default='run_command,read_file,edit_file,write_file,get_status,submit_patch')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    allowed = set(args.tools.split(','))
    captured = json.loads(args.protocol.read_text())[0]['request']['tools']
    tools = [t for t in captured if t['function']['name'] in allowed]
    if {t['function']['name'] for t in tools} != allowed:
        raise SystemExit('captured request lacks a declared tool')
    args.output.mkdir(parents=True, exist_ok=False)
    summary = {'written': [], 'refused': {}, 'duplicates': 0, 'excluded_repository': 0,
               'tools': sorted(allowed), 'protocol': file_record(args.protocol)}
    done = set()
    for root in args.results_root:
        for results in sorted(root.glob('*/results/task_results.jsonl')):
            for line in results.read_text().splitlines():
                row = json.loads(line)
                iid = row['instance_id']
                if not row.get('resolved'):
                    continue
                if iid.rsplit('-', 1)[0].lower() in EXCLUDED_REPOS:
                    summary['excluded_repository'] += 1
                    continue
                if iid in done:
                    summary['duplicates'] += 1
                    continue
                trace_path = results.parent / 'traces' / f'trace_{iid}.json'
                try:
                    messages = trace_history(json.loads(trace_path.read_text()), allowed)
                except (ValueError, KeyError, OSError) as error:
                    summary['refused'][iid] = f'{type(error).__name__}: {error}'
                    continue
                out = args.output / iid
                out.mkdir()
                (out / 'history.json').write_bytes(canonical_json(messages))
                (out / 'tools.json').write_bytes(canonical_json(tools))
                (out / 'receipt.json').write_bytes(canonical_json({
                    'instance_id': iid, 'trace': file_record(trace_path), 'results': file_record(results),
                    'history': file_record(out / 'history.json'), 'tools': file_record(out / 'tools.json'),
                    'messages': len(messages), 'training_approved': False}))
                done.add(iid)
                summary['written'].append(iid)
    (args.output / 'summary.json').write_bytes(canonical_json(summary))
    print(json.dumps({'written': len(summary['written']), 'refused': len(summary['refused']),
                      'duplicates': summary['duplicates'], 'excluded': summary['excluded_repository']}))


if __name__ == '__main__':
    main()
