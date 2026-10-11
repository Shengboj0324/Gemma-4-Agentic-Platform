"""Project pinned SWE-rebench native observations into a reconstructed history."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.source_bytes import verified_source_bytes
from zenithsync.replay_amendment import amended_replay_history

from zenithsync.replay_history import native_replay_history
from zenithsync.replay_completion import validate_completion_plan, completed_replay_history

MAX_SOURCE_BYTES = 512 * 1024**2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', type=Path, required=True)
    parser.add_argument('--task-receipt', type=Path,
                        default=ROOT / 'evidence/data/swe-rebench-evaluator-input-001/receipt.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    snapshot_path = ROOT / 'zenithsync/source_bytes.py'
    snapshot_implementation = file_record(snapshot_path)
    attempt = load_json(args.attempt / 'receipt.json')
    if (attempt['status'] != 'replayed_not_graded' or attempt['cleanup']['removed'] is not True
            or file_record(args.attempt / 'submitted.patch') != attempt['patch']):
        raise ValueError('Completed replay with verified patch required')
    expected = load_json(args.task_receipt)
    if (expected['task']['instance_id'] != attempt['instance_id']
            or expected['task']['repo'] != attempt['profile']['repo']
            or expected['task']['base_commit'] != attempt['profile']['base_commit']):
        raise ValueError('Task receipt does not match replay')
    registry_path = ROOT / 'evidence/data/swe-rebench-task-join-full-001/report.json'
    sources = [s for s in load_json(registry_path)['task_shards'] if s['identity'] == expected['source']]
    if len(sources) != 1:
        raise ValueError('Ambiguous pinned task shard')
    source = ROOT / sources[0]['path']
    intake_path = ROOT / sources[0]['intake_path']
    intake = load_json(intake_path)
    bindings = {str(p): file_record(p) for p in [args.task_receipt, registry_path, intake_path,
                args.attempt / 'receipt.json', args.attempt / 'events.json']}
    if bindings[str(intake_path)] != sources[0]['intake']:
        raise ValueError('Task intake changed')
    identity = file_record(source)
    if (identity != expected['source'] or identity not in intake['downloaded'].values()
            or intake['revision'] != '89cdfbab4ab1bd8f5a658bb212d1b63624f4f881'
            or intake['dataset'] != 'nebius/SWE-rebench'):
        raise ValueError('Pinned task source mismatch')
    official_path = ROOT / 'evidence/p1/task-index-001/receipt.json'
    bindings[str(official_path)] = file_record(official_path)
    official = load_json(official_path)
    repo = attempt['profile']['repo']
    if repo.casefold() in {r.casefold() for r in official['repo_counts']}:
        raise ValueError('Reserved repository rejected before issue read')
    import pyarrow as pa
    import pyarrow.parquet as pq
    payload = verified_source_bytes(source, identity, max_bytes=MAX_SOURCE_BYTES)
    identities = pq.read_table(pa.BufferReader(payload), columns=['instance_id', 'repo', 'base_commit'],
                         filters=[('instance_id', '=', attempt['instance_id'])]).to_pylist()
    if (len(identities) != 1 or identities[0]['repo'] != repo
            or identities[0]['base_commit'] != attempt['profile']['base_commit']):
        raise ValueError('Issue identity mismatch before body read')
    rows = pq.read_table(pa.BufferReader(payload), columns=['instance_id', 'repo', 'base_commit', 'problem_statement'],
                         filters=[('instance_id', '=', attempt['instance_id'])]).to_pylist()
    if (len(rows) != 1 or rows[0]['repo'] != repo
            or rows[0]['base_commit'] != attempt['profile']['base_commit']):
        raise ValueError('Issue/replay identity mismatch')
    problem = rows[0]['problem_statement']
    if not isinstance(problem, str) or not problem.strip():
        raise ValueError('Nonempty issue text required')
    protocol_path = ROOT / 'evidence/data/source-http-client-001/success/http-fixture/exchanges.json'
    bindings[str(protocol_path)] = file_record(protocol_path)
    protocol = load_json(protocol_path)[0]['request']
    tools = protocol['tools']
    allowed = {tool['function']['name'] for tool in tools}
    if allowed != set(attempt['available_tools']) or len(tools) != len(allowed):
        raise ValueError('Native tool schema set mismatch')
    events = load_json(args.attempt / 'events.json')
    projection_arguments = dict(system=protocol['messages'][0]['content'],
                                problem=problem, allowed_tools=allowed)
    completion = None
    if 'completion_plan' in attempt:
        plan = validate_completion_plan(attempt['completion_plan'])
        action_path = args.attempt / 'actions.json'
        bindings[str(action_path)] = file_record(action_path)
        if (bindings[str(action_path)] != plan['source_actions']
                or attempt['patch'] != plan['final_patch']
                or attempt.get('completion_module') != file_record(ROOT/'zenithsync/replay_completion.py')):
            raise ValueError('Completion provenance mismatch')
        completion = plan
    else:
        if any(e.get('kind') == 'completion' or 'adapter_authored' in e for e in events):
            raise ValueError('Completion events require a bound plan')
    if 'amendment_plan' in attempt:
        amendment = attempt['amendment_plan']
        original_path = args.attempt / 'original-actions.json'
        derived_path = args.attempt / 'actions.json'
        implementation_path = ROOT / 'zenithsync/replay_amendment.py'
        for path in (original_path, derived_path, implementation_path):
            bindings[str(path)] = file_record(path)
        if (bindings[str(original_path)] != attempt.get('original_actions')
                or bindings[str(derived_path)] != attempt.get('derived_actions')
                or bindings[str(implementation_path)] != attempt.get('amendment_module')
                or attempt['original_actions'] != amendment.get('source_actions')
                or attempt['derived_actions'] != amendment.get('derived_actions')):
            raise ValueError('Amendment provenance mismatch')
        projected = amended_replay_history(events, actions=load_json(original_path),
            plan=amendment, completion_plan=completion, **projection_arguments)
    else:
        if (any(key in attempt for key in ('original_actions', 'derived_actions',
                                          'amendment_module', 'amendment_plan_file'))
                or (args.attempt / 'original-actions.json').exists()):
            raise ValueError('Amended artifacts require an explicit amendment plan')
        if completion is None:
            projected = native_replay_history(events, **projection_arguments)
        else:
            projected = completed_replay_history(events, plan=completion, **projection_arguments)
    if (file_record(snapshot_path) != snapshot_implementation
            or file_record(source) != identity
            or any(file_record(Path(path)) != record for path, record in bindings.items())):
        raise ValueError('Task source changed during projection')
    args.output.mkdir(parents=True, exist_ok=False)
    for name, content in [('history', projected['messages']), ('tools', tools), ('mapping', projected['mapping'])]:
        (args.output / (name + '.json')).write_bytes(canonical_json(content))
    receipt = {'attempt': file_record(args.attempt / 'receipt.json'),
               'input_bindings': bindings,
               'events': file_record(args.attempt / 'events.json'), 'source_shard': identity,
               'protocol_snapshot': file_record(protocol_path), 'source_intake': file_record(intake_path),
               'history': file_record(args.output / 'history.json'),
               'tools': file_record(args.output / 'tools.json'), 'exchanges': len(projected['mapping']),
               'parser_input': {'kind': 'verified_immutable_bytes', 'max_bytes': MAX_SOURCE_BYTES,
                                'implementation': snapshot_implementation},
               'training_approved': False, 'scope': projected['scope'],
               'script': file_record(Path(__file__)),
               'limitations': ['Reconstructed prompt is not proof of original teacher conditioning.',
                               'Fresh native observations; original teacher reasoning omitted.',
                               'Tool-name equality does not establish identical source tool semantics.']}
    if 'completion_plan' in attempt:
        receipt['completion_plan'] = attempt['completion_plan']
    if 'amendment_plan' in attempt:
        receipt['amendment_plan'] = attempt['amendment_plan']
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'messages': len(projected['messages']), 'exchanges': len(projected['mapping'])})


if __name__ == '__main__':
    main()
