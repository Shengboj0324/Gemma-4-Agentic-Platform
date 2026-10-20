"""Bind synthetic captures, publisher controls, content review and token audits.

Mechanical qualification never changes a corpus or grants training approval.
"""
import hashlib
import re
from pathlib import Path

from .artifacts import canonical_json, file_record, load_json
from .pytest_controls import compare_candidate, compare_controls
from .synthetic_admission import validate_synthetic_task_binding


def assess_v2_synthetic_bundle(*, attempt, grade, tokens, task, snapshot, review,
                               capture_sources, max_input_tokens=32768,
                               output_reserve=8192, max_tool_calls=40):
    """Assess the V2 publisher schema with its two declared outcome categories."""
    return _assess_publisher_synthetic_bundle(
        attempt=attempt, grade=grade, tokens=tokens, task=task, snapshot=snapshot,
        review=review, capture_sources=capture_sources, max_input_tokens=max_input_tokens,
        output_reserve=output_reserve, max_tool_calls=max_tool_calls, legacy=False)


def assess_legacy_synthetic_bundle(*, attempt, grade, tokens, task, snapshot, review,
                                   capture_sources, max_input_tokens=32768,
                                   output_reserve=8192, max_tool_calls=40):
    """Assess legacy publisher evidence without discarding stable failures.

    The producer must bind a complete task document with all four transition
    categories, plus the same raw execution evidence required for V2 captures.
    This is a separate report contract, not permission to relabel old replays.
    """
    return _assess_publisher_synthetic_bundle(
        attempt=attempt, grade=grade, tokens=tokens, task=task, snapshot=snapshot,
        review=review, capture_sources=capture_sources, max_input_tokens=max_input_tokens,
        output_reserve=output_reserve, max_tool_calls=max_tool_calls, legacy=True)


def _assess_publisher_synthetic_bundle(*, attempt, grade, tokens, task, snapshot, review,
                                      capture_sources, max_input_tokens,
                                      output_reserve, max_tool_calls, legacy):
    """Recompute bounded evidence, keeping training gates outside this decision."""
    if (any(type(v) is not int or v <= 0 for v in (max_input_tokens, max_tool_calls))
            or type(output_reserve) is not int or not 0 <= output_reserve < max_input_tokens):
        raise ValueError('Invalid synthetic admission policy')
    paths = {'attempt': attempt/'receipt.json', 'events': attempt/'events.json',
             'history': attempt/'history.json', 'tools': attempt/'tools.json',
             'patch': attempt/'submitted.patch', 'grade': grade/'report.json',
             'tokens': tokens/'tokens.json', 'audit': tokens/'report.json',
             'task': task, 'snapshot': snapshot/'snapshot.json', 'review': review}
    identities = {key: file_record(path) for key, path in paths.items()}
    data = {key: load_json(path) for key, path in paths.items() if key != 'patch'}
    receipt, grading, audit, candidate = (data[k] for k in ('attempt','grade','audit','tokens'))
    if (not isinstance(receipt.get('image'), str)
            or re.fullmatch(r'sha256:[0-9a-f]{64}', receipt['image']) is None
            or not isinstance(data['task'].get('instance_id'), str)
            or not data['task']['instance_id'].strip()):
        raise ValueError('Pinned image and explicit task identity required')
    required_sources = {'runner', 'fixture'} | ({'oracle'} if 'oracle' in receipt else set())
    if not isinstance(capture_sources, dict) or set(capture_sources) != required_sources:
        raise ValueError('Exact declared capture sources required')
    for key, path in capture_sources.items():
        paths[key] = path
        identities[key] = file_record(path)
        if receipt.get(key) != identities[key]:
            raise ValueError('Capture source identity mismatch')
    bindings = grading.get('inputs')
    if (grading.get('trajectory_kind') != 'synthetic_native_trajectory'
            or grading.get('training_approved') is not False
            or grading.get('sanitized_snapshot') is not True or not isinstance(bindings, dict)):
        raise ValueError('Explicit synthetic publisher grade required')
    expected_format = 'legacy_four_transitions' if legacy else 'v2_two_transitions'
    if grading.get('publisher_format', 'v2_two_transitions') != expected_format:
        raise ValueError('Publisher format mismatch')
    # Input locations are producer records; require unique matches to the inputs
    # selected by this caller, rather than selecting any passing report by name.
    for key in ('attempt','events','history','tools','patch','task','snapshot'):
        expected_path = paths[key].resolve()
        matches = [identity for name, identity in bindings.items()
                   if Path(name).resolve() == expected_path]
        if matches != [identities[key]]:
            raise ValueError('Grade does not bind selected ' + key)
    calls = validate_synthetic_task_binding(
        receipt=receipt, messages=data['history'], events=data['events'], tools=data['tools'],
        task=data['task'], snapshot=data['snapshot'], image=receipt.get('image'),
        patch_identity=identities['patch'], history_identity=identities['history'],
        tools_identity=identities['tools'])
    outcomes = {}
    for role in ('base','reference','candidate'):
        for name in ('outcomes','runtime','receipt'):
            key = role + '_' + name
            paths[key] = grade/role/(name + '.json')
            identities[key] = file_record(paths[key])
            data[key] = load_json(paths[key])
        execution, runtime = data[role+'_receipt'], data[role+'_runtime']
        if (grading.get('controls', {}).get(role) != execution
                or execution.get('image_id') != receipt.get('image')
                or execution.get('state', {}).get('OOMKilled') is not False
                or execution.get('state', {}).get('Status') != 'exited'
                or type(execution.get('state', {}).get('ExitCode')) is not int
                or execution['state']['ExitCode'] != 0
                or any(type(execution.get(k)) is not int or execution[k] != 0
                       for k in ('returncode','copy_returncode','cleanup_returncode'))
                or runtime.get('role') != role or runtime.get('tests_started') is not True
                or runtime.get('tracked_diff_unchanged_by_tests') is not True):
            raise ValueError('Unqualified publisher runtime')
        outcomes[role] = data[role+'_outcomes']
        if (type(runtime.get('pytest_exit')) is not int
                or runtime['pytest_exit'] != outcomes[role].get('exitstatus')):
            raise ValueError('Publisher runtime and outcomes disagree')
    expectations = {key: data['task'][key] for key in ('FAIL_TO_PASS','PASS_TO_PASS')}
    if legacy:
        if any(key not in data['task'] for key in ('FAIL_TO_FAIL', 'PASS_TO_FAIL')):
            raise ValueError('All four legacy transition categories required')
        expectations.update({key: data['task'][key] for key in ('FAIL_TO_FAIL', 'PASS_TO_FAIL')})
    else:
        expectations.update(FAIL_TO_FAIL=[], PASS_TO_FAIL=[])
    control = compare_controls(outcomes['base'],outcomes['reference'],expectations)
    comparison = compare_candidate(outcomes['reference'],outcomes['candidate'])
    if control != grading.get('comparison') or comparison != grading.get('candidate_comparison'):
        raise ValueError('Publisher summary differs from recomputed outcomes')
    for value in (audit,candidate):
        if (value.get('history') != identities['history'] or value.get('tools') != identities['tools']
                or value.get('training_approved') is not False):
            raise ValueError('Synthetic token provenance mismatch')
    ids, labels = candidate.get('input_ids'), candidate.get('labels')
    if (not isinstance(ids,list) or not isinstance(labels,list) or not ids or len(ids) != len(labels)
            or any(type(v) is not int or v < 0 for v in ids)
            or any(type(label) is not int or label not in (-100,token) for token,label in zip(ids,labels))):
        raise ValueError('Invalid synthetic token arrays')
    inputs, targets = len(ids), sum(v != -100 for v in labels[1:])
    if (audit.get('token_candidate') != identities['tokens'] or audit.get('truncated') is not False
            or type(audit.get('input_tokens')) is not int or audit['input_tokens'] != inputs
            or type(audit.get('supervised_tokens')) is not int or audit['supervised_tokens'] != targets
            or not 0 < targets < inputs
            or audit.get('input_sha256') != hashlib.sha256(canonical_json(ids)).hexdigest()
            or audit.get('labels_sha256') != hashlib.sha256(canonical_json(labels)).hexdigest()):
        raise ValueError('Synthetic token audit mismatch')
    content = data['review']
    if (content.get('task') != data['task']['instance_id'] or content.get('history') != identities['history']
            or content.get('grade') != identities['grade'] or content.get('synthetic') is not True
            or content.get('reference_informed') is not True or content.get('content_quality_accepted') is not True
            or content.get('training_approved') is not False):
        raise ValueError('Bound synthetic content acceptance required')
    blockers = []
    if not comparison['all_cases_match_reference']:
        blockers.append('reference_outcomes_not_matched')
    if inputs + output_reserve > max_input_tokens:
        blockers.append('input_plus_output_reserve_exceeds_context')
    if calls > max_tool_calls:
        blockers.append('native_call_budget_exceeded')
    if any(file_record(paths[key]) != identity for key,identity in identities.items()):
        raise ValueError('Synthetic evidence changed during assessment')
    return {'schema_version':1,'instance_id':data['task']['instance_id'],
            'publisher_format':expected_format,
            'kind':'synthetic_native_trajectory','author':'assistant','reference_informed':True,
            'identities':identities,'grading':comparison,'controls':control,
            'input_tokens':inputs,'supervised_tokens':targets,'native_tool_calls':calls,
            'policy':{'max_input_tokens':max_input_tokens,'output_reserve':output_reserve,
                      'max_tool_calls':max_tool_calls},'mechanical_blockers':blockers,
            'mechanical_checks_passed':not blockers,'training_approved':False,
            'implementation':file_record(Path(__file__)),
            'limitations':['Local consistency, not authenticity of arbitrary receipts.',
                           'Tokenization is bound but not rerun by this checker.',
                           'Publisher coverage is not full repository acceptance.',
                           'Rights, split isolation and training runtime require separate approval.']}
