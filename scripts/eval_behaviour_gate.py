"""Early behaviour gate for a running paired evaluation (docs/45, round 5).

Round 4's adapter stopped thinking on 91% of its tool steps and repeated its previous call on 42%
(v2: 0.5% and 2.0% over 3,791 steps). This reads the traces of the candidate's finished tasks and
reports, over all tool-calling agent steps:
  no_thinking  share of steps whose step text is empty
  repeat_call  share of steps whose calls equal the previous step's calls exactly
Once at least --min-tasks tasks are finished it exits 3 if either share exceeds its limit, else 0;
before that it exits 0 with "pending". Read-only.
"""
import argparse
import json
from pathlib import Path


def step_rates(traces):
    steps = empty = repeats = 0
    for trace in traces:
        previous = None
        for step in trace.get('steps', []):
            if step.get('source') != 'agent' or not step.get('tool_calls'):
                continue
            key = json.dumps([(c.get('function_name'), c.get('arguments')) for c in step['tool_calls']], sort_keys=True)
            steps += 1
            empty += not (step.get('message') or '').strip()
            repeats += key == previous
            previous = key
    return {'tool_steps': steps, 'no_thinking': empty / steps if steps else 0.0,
            'repeat_call': repeats / steps if steps else 0.0}


def evaluate(candidate_dir, *, min_tasks, max_no_thinking, max_repeat):
    results = candidate_dir / 'task_results.jsonl'
    rows = [json.loads(line) for line in results.read_text().splitlines() if line.strip()] if results.exists() else []
    traces = []
    for row in rows:
        path = candidate_dir / 'traces' / f"trace_{row['instance_id']}.json"
        if path.exists():
            traces.append(json.loads(path.read_text()))
    report = {'finished_tasks': len(rows), 'traces': len(traces), **step_rates(traces),
              'limits': {'min_tasks': min_tasks, 'no_thinking': max_no_thinking, 'repeat_call': max_repeat}}
    if len(rows) < min_tasks:
        report['verdict'] = 'pending'
    elif report['no_thinking'] > max_no_thinking or report['repeat_call'] > max_repeat:
        report['verdict'] = 'fail'
    else:
        report['verdict'] = 'pass'
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--candidate-dir', type=Path, required=True, help='results-root/<candidate>')
    p.add_argument('--min-tasks', type=int, default=12)
    p.add_argument('--max-no-thinking', type=float, default=0.05)
    p.add_argument('--max-repeat', type=float, default=0.05)
    args = p.parse_args()
    report = evaluate(args.candidate_dir, min_tasks=args.min_tasks, max_no_thinking=args.max_no_thinking,
                      max_repeat=args.max_repeat)
    print(json.dumps(report))
    raise SystemExit(3 if report['verdict'] == 'fail' else 0)


if __name__ == '__main__':
    main()
