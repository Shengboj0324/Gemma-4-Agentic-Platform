"""Consistency checks for assistant-authored native trajectories.

Synthetic captures retain their own provenance; they are never relabeled as
teacher replays. Passing these checks does not authorize training.
"""
import hashlib
from pathlib import Path

from .artifacts import canonical_json, file_record, load_json
from .rebench_grade_evidence import verify_rebench_outcomes
from .replay_history import native_replay_history


def validate_synthetic_projection(events, messages, tools, charged_calls):
    """Require exact captured exchanges followed by separately authored prose."""
    if (not isinstance(messages, list) or len(messages) < 5
            or messages[0].get('role') != 'system' or messages[1].get('role') != 'user'
            or set(messages[-1]) != {'role', 'content'}
            or messages[-1]['role'] != 'assistant'
            or not isinstance(messages[-1]['content'], str) or not messages[-1]['content'].strip()):
        raise ValueError('Synthetic history requires initial prompts and final prose')
    allowed = {tool['function']['name'] for tool in tools}
    if len(allowed) != len(tools) or not allowed:
        raise ValueError('Unique tool schemas required')
    if (not isinstance(events, list) or not events
            or any(event.get('kind') != 'synthetic' for event in events)):
        raise ValueError('Explicit synthetic events required')
    projected = native_replay_history(events, system=messages[0]['content'],
                                      problem=messages[1]['content'], allowed_tools=allowed)
    if projected['messages'] != messages[:-1]:
        raise ValueError('Synthetic history differs from captured exchanges')
    calls = [call for event in events for call in event['native_calls']]
    if sum(call['name'] == 'submit_patch' for call in calls) != 1:
        raise ValueError('Exactly one terminal submission required')
    # Native status inspection and submission do not consume the tool-call budget.
    actual = sum(call['name'] not in ('get_status', 'submit_patch') for call in calls)
    if type(charged_calls) is not int or charged_calls != actual:
        raise ValueError('Synthetic charged call count mismatch')
    if calls[-1]['result'].get('status') != 'ok':
        raise ValueError('Successful terminal submission required')
    return actual


def validate_synthetic_task_binding(*, receipt, messages, events, tools, task,
                                    snapshot, image, patch_identity,
                                    history_identity, tools_identity):
    """Bind a synthetic capture to a grader task without relabeling provenance.

    Callers must hash the supplied artifacts and recheck them after execution.
    This verifies local consistency, not authenticity or training eligibility.
    """
    if (receipt.get('kind') != 'synthetic_native_trajectory'
            or receipt.get('author') != 'assistant'
            or receipt.get('reference_informed') is not True
            or receipt.get('source_observations_reused') is not False
            or receipt.get('new_model_evaluated') is not False
            or receipt.get('training_approved') is not False
            or receipt.get('status') != 'captured_not_graded'
            or receipt.get('cleanup', {}).get('removed') is not True):
        raise ValueError('Completed explicitly synthetic capture required')
    if (receipt.get('image') != image or receipt.get('snapshot') != snapshot
            or task.get('base_commit') != snapshot.get('base_commit')
            or receipt.get('patch') != patch_identity
            or receipt.get('history') != history_identity
            or receipt.get('tools') != tools_identity):
        raise ValueError('Synthetic task artifact binding mismatch')
    calls = validate_synthetic_projection(events, messages, tools, receipt.get('tool_calls'))
    if messages[1]['content'] != task.get('problem_statement'):
        raise ValueError('Synthetic capture issue differs from grading task')
    return calls


def assess_synthetic_bundle(*, attempt, history, grade, tokens, profile, review,
                            max_input_tokens=32768, output_reserve=8192, max_tool_calls=40):
    """Recompute projection/counts/outcomes and bind the separate content review."""
    if (any(type(value) is not int or value <= 0 for value in (max_input_tokens, max_tool_calls))
            or type(output_reserve) is not int or not 0 <= output_reserve < max_input_tokens):
        raise ValueError('Invalid synthetic admission policy')
    paths = {'attempt': attempt / 'receipt.json', 'events': attempt / 'events.json',
             'patch': attempt / 'submitted.patch', 'captured_history': attempt / 'history.json',
             'runner': attempt / 'run.py', 'fixture': attempt / 'verify_axes.py',
             'history': history / 'history.json', 'tools': history / 'tools.json',
             'grade': grade / 'report.json', 'tokens': tokens / 'tokens.json',
             'audit': tokens / 'report.json', 'profile': profile, 'review': review}
    identities = {key: file_record(path) for key, path in paths.items()}
    data = {key: load_json(path) for key, path in paths.items()
            if key not in ('patch', 'runner', 'fixture')}
    receipt, grading, audit, candidate = (data[key] for key in ('attempt', 'grade', 'audit', 'tokens'))
    if (receipt.get('kind') != 'synthetic_native_trajectory' or receipt.get('author') != 'assistant'
            or receipt.get('reference_informed') is not True
            or receipt.get('source_observations_reused') is not False
            or receipt.get('new_model_evaluated') is not False
            or receipt.get('training_approved') is not False
            or receipt.get('status') != 'captured_not_graded'
            or receipt.get('cleanup', {}).get('removed') is not True):
        raise ValueError('Explicit completed synthetic provenance required')
    for key in ('patch', 'runner', 'fixture', 'profile', 'history'):
        if receipt.get(key) != identities[key]:
            raise ValueError('Synthetic ' + key + ' identity mismatch')
    if identities['captured_history'] != identities['history']:
        raise ValueError('Captured and tokenized histories differ')
    task = data['profile']['instance_id']
    if (grading.get('backend') != 'swe_rebench_full_nodeid_reference'
            or grading.get('trajectory_kind') != 'synthetic_native_trajectory'
            or grading.get('reference_informed') is not True
            or grading.get('task') != task or grading.get('attempt') != identities['attempt']
            or grading.get('inputs', {}).get('patch') != identities['patch']):
        raise ValueError('Synthetic grade binding mismatch')
    outcome_evidence = verify_rebench_outcomes(grading, grade)
    actual_calls = validate_synthetic_projection(data['events'], data['history'], data['tools'], receipt['tool_calls'])
    for source in (audit, candidate):
        if (source.get('history') != identities['history'] or source.get('tools') != identities['tools']
                or source.get('training_approved') is not False):
            raise ValueError('Synthetic token provenance mismatch')
    ids, labels = candidate['input_ids'], candidate['labels']
    if (not isinstance(ids, list) or not isinstance(labels, list) or len(ids) != len(labels)
            or not ids or any(type(value) is not int or value < 0 for value in ids)
            or any(type(label) is not int or (label != -100 and label != token)
                   for token, label in zip(ids, labels))):
        raise ValueError('Invalid synthetic token arrays')
    inputs, targets = len(ids), sum(value != -100 for value in labels[1:])
    if (audit.get('token_candidate') != identities['tokens'] or audit.get('truncated') is not False
            or type(audit.get('input_tokens')) is not int or audit['input_tokens'] != inputs
            or type(audit.get('supervised_tokens')) is not int or audit['supervised_tokens'] != targets
            or not 0 < targets < inputs
            or audit.get('input_sha256') != hashlib.sha256(canonical_json(ids)).hexdigest()
            or audit.get('labels_sha256') != hashlib.sha256(canonical_json(labels)).hexdigest()):
        raise ValueError('Synthetic token audit mismatch')
    content = data['review']
    if (content.get('task') != task or content.get('history') != identities['history']
            or content.get('synthetic') is not True or content.get('reference_informed') is not True
            or content.get('content_quality_accepted') is not True
            or content.get('grade') != identities['grade'] or content.get('training_approved') is not False):
        raise ValueError('Bound synthetic content acceptance required')
    blockers = []
    if not grading['grading']['all_cases_match_reference']:
        blockers.append('reference_outcomes_not_matched')
    if inputs + output_reserve > max_input_tokens:
        blockers.append('input_plus_output_reserve_exceeds_context')
    if actual_calls > max_tool_calls:
        blockers.append('native_call_budget_exceeded')
    if any(file_record(paths[key]) != identity for key, identity in identities.items()):
        raise ValueError('Synthetic evidence changed during assessment')
    if any(file_record(Path(path)) != identity for path, identity in outcome_evidence.items()):
        raise ValueError('Synthetic outcome evidence changed during assessment')
    return {'schema_version': 1, 'instance_id': task, 'kind': 'synthetic_native_trajectory',
            'author': 'assistant', 'reference_informed': True, 'identities': identities,
            'recomputed_outcome_evidence': outcome_evidence, 'input_tokens': inputs,
            'supervised_tokens': targets, 'native_tool_calls': actual_calls,
            'policy': {'max_input_tokens': max_input_tokens, 'output_reserve': output_reserve,
                       'max_tool_calls': max_tool_calls}, 'mechanical_blockers': blockers,
            'mechanical_checks_passed': not blockers, 'training_approved': False,
            'implementation': file_record(Path(__file__)),
            'limitations': ['Local consistency, not authenticity of arbitrary receipts.',
                            'Content review is bound, not replaced by automated checks.',
                            'Native tokenizer encoding is not rerun here.',
                            'Rights, split isolation and training runtime remain separate gates.']}
