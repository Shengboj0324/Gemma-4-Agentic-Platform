"""Where an agent's calls and time went, per run, joined with how the run ended.

Reads a finished candidate's `traces/trace_<id>.json` (adk_eval_core
SessionTrace) and `task_results.jsonl`. For each run it counts tool calls by
kind: reads, searches, graph lookups, edits, test runs, pip attempts, other
commands and submission. It also records the step of the first edit and of the
first test run, total completion tokens, and whether `submit_patch` was called.
Then it aggregates by outcome class. This is descriptive: it says what the
agents did, not why, and the command classification is by pattern, so it is
recorded with the counts.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json
from zenithsync.paired_eval import _outcome

COMMAND_KINDS = [  # first match wins; patterns are part of the record
    ('pip', r'\bpip3?\s+install\b|\bpython3?\s+-m\s+pip\b'),
    ('test', r'\bpytest\b|\bpython3?\s+-m\s+(pytest|unittest)\b|\bunittest\b|\btox\b'),
    ('search', r'^\s*(grep|rg|find|ag|git\s+grep)\b|\|\s*grep\b'),
    ('inspect', r'^\s*(cat|head|tail|sed\s+-n|ls|tree|wc|git\s+(log|show|diff|status))\b'),
    ('python', r'\bpython3?\s+(-c|\S+\.py)\b'),
]
TOOL_KINDS = {'read_file': 'read', 'edit_file': 'edit', 'write_file': 'edit', 'submit_patch': 'submit',
              'get_status': 'status', 'get_code_neighbors': 'graph', 'search_similar_code': 'graph',
              'get_code_subgraph': 'graph'}


def classify(name, arguments):
    if name != 'run_command':
        return TOOL_KINDS.get(name, 'other_tool')
    command = str((arguments or {}).get('command', ''))
    for kind, pattern in COMMAND_KINDS:
        if re.search(pattern, command):
            return kind
    return 'other_command'


def tool_calls(step):
    for call in step.get('tool_calls') or []:
        name = call.get('function_name') or call.get('name') or (call.get('function') or {}).get('name')
        args = call.get('arguments') or call.get('args') or (call.get('function') or {}).get('arguments') or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        yield name, args


def analyse_trace(trace):
    kinds = Counter()
    first = {}
    completion = 0
    index = 0
    for step in trace.get('steps') or []:
        completion += (step.get('metrics') or {}).get('completion_tokens') or 0
        for name, args in tool_calls(step):
            index += 1
            kind = classify(name, args)
            kinds[kind] += 1
            first.setdefault(kind, index)
    return {'calls': index, 'kinds': dict(kinds), 'first_edit_call': first.get('edit'),
            'first_test_call': first.get('test'), 'submitted': 'submit' in kinds,
            'completion_tokens': completion}


def analyse(results_dir):
    rows = {}
    for line in (results_dir / 'task_results.jsonl').read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row['instance_id']] = row
    runs = []
    for tid, row in sorted(rows.items()):
        path = results_dir / 'traces' / f'trace_{tid}.json'
        trace = json.loads(path.read_text()) if path.exists() else {}
        runs.append({'instance_id': tid, 'outcome': _outcome(rows, tid)['class'],
                     'duration_seconds': row.get('duration_seconds'), 'error': row.get('error'),
                     'trace_present': path.exists(), **analyse_trace(trace)})
    by_outcome = defaultdict(list)
    for run in runs:
        by_outcome[run['outcome']].append(run)
    summary = {}
    for outcome, group in sorted(by_outcome.items()):
        kinds = Counter()
        for run in group:
            kinds.update(run['kinds'])
        def med(key):
            values = [r[key] for r in group if r[key] is not None]
            return statistics.median(values) if values else None
        summary[outcome] = {'runs': len(group), 'mean_calls_by_kind': {k: v / len(group) for k, v in sorted(kinds.items())},
                            'median_calls': med('calls'), 'median_duration_s': med('duration_seconds'),
                            'median_first_edit_call': med('first_edit_call'),
                            'median_first_test_call': med('first_test_call'),
                            'submitted_share': sum(r['submitted'] for r in group) / len(group),
                            'ran_tests_share': sum(1 for r in group if r['kinds'].get('test')) / len(group),
                            'tried_pip_share': sum(1 for r in group if r['kinds'].get('pip')) / len(group)}
    return runs, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', action='append', required=True, help='NAME=DIR')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    report = {'schema_version': 1, 'command_patterns': COMMAND_KINDS, 'tool_kinds': TOOL_KINDS, 'candidates': {}}
    for spec in args.results:
        name, directory = spec.split('=', 1)
        runs, summary = analyse(Path(directory))
        (args.output / f'{name}-runs.jsonl').write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in runs))
        report['candidates'][name] = summary
    (args.output / 'summary.json').write_bytes(canonical_json(report))
    print(json.dumps(report['candidates'], indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
