"""Strict qualification of native Go 1.23 test JSON, without invented phases.

The caller supplies complete ``go test -json -count=1`` output and its process
exit code. These checks validate recorded event consistency, not log authenticity
or source immutability; the execution bundle must bind those independently.
Package-only skips require an explicit reviewed no-test-package allowlist.
"""

import json


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def _identity(value):
    return (isinstance(value, str) and bool(value) and
            not any(character.isspace() for character in value) and
            '\x00' not in value and '::' not in value)


def go_outcomes(text, *, exit_code, no_test_packages):
    """Require complete per-package and per-test lifecycles and exact exits."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Nonempty Go JSON output required')
    if type(exit_code) is not int or exit_code not in (0, 1):
        raise ValueError('Unsupported Go process exit')
    if (not isinstance(no_test_packages, list) or
            any(not _identity(name) for name in no_test_packages) or
            len(set(no_test_packages)) != len(no_test_packages)):
        raise ValueError('Explicit unique no-test package list required')
    empty = set(no_test_packages)
    packages, tests, owners = {}, {}, {}
    for line in text.splitlines():
        if not line.strip():
            raise ValueError('Blank event line')
        event = json.loads(line, object_pairs_hook=_unique_object)
        if not isinstance(event, dict):
            raise ValueError('Go event must be an object')
        action, package = event.get('Action'), event.get('Package')
        test = event.get('Test')
        if not _identity(package) or (test is not None and not _identity(test)):
            raise ValueError('Invalid package or test identity')
        if event.get('FailedBuild') or event.get('OutputType'):
            raise ValueError('Build failure or unsupported event version')
        if action == 'start':
            if test is not None or package in packages:
                raise ValueError('Duplicate or malformed package start')
            packages[package] = 'running'
            owners[package] = set()
            continue
        if packages.get(package) != 'running':
            raise ValueError('Event outside live package')
        key = package + '::' + test if test is not None else None
        if action == 'output':
            if not isinstance(event.get('Output'), str):
                raise ValueError('Output event lacks text')
            if key is not None and key not in tests:
                raise ValueError('Output precedes test start')
            continue
        if key is not None:
            if package in empty:
                raise ValueError('Declared no-test package executed a test')
            if action == 'run':
                if key in tests:
                    raise ValueError('Duplicate test start')
                if '/' in test:
                    parent = package + '::' + test.rsplit('/', 1)[0]
                    if tests.get(parent) != 'running':
                        raise ValueError('Subtest lacks a running parent')
                tests[key] = 'running'
                owners[package].add(key)
            elif action == 'pause' and tests.get(key) == 'running':
                tests[key] = 'paused'
            elif action == 'cont' and tests.get(key) == 'paused':
                tests[key] = 'running'
            elif action in ('pass', 'fail') and tests.get(key) == 'running':
                children = [state for name, state in tests.items()
                            if name.startswith(key + '/')]
                if any(state not in ('pass', 'fail') for state in children):
                    raise ValueError('Parent ended before its subtests')
                if action == 'pass' and 'fail' in children:
                    raise ValueError('Passing parent contains failed subtest')
                tests[key] = action
            else:
                raise ValueError('Skipped test or invalid test lifecycle')
        elif action in ('pass', 'fail', 'skip'):
            states = [tests[name] for name in owners[package]]
            if any(state not in ('pass', 'fail') for state in states):
                raise ValueError('Package ended with unfinished tests')
            expected = 'skip' if package in empty else ('fail' if 'fail' in states else 'pass')
            if action != expected or (not states and package not in empty):
                raise ValueError('Package outcome contradicts test outcomes')
            packages[package] = action
        else:
            raise ValueError('Unsupported package event')
    if (not tests or any(state not in ('pass', 'fail') for state in tests.values()) or
            any(state not in ('pass', 'fail', 'skip') for state in packages.values())):
        raise ValueError('Incomplete or empty test execution')
    if {name for name, state in packages.items() if state == 'skip'} != empty:
        raise ValueError('No-test package coverage differs')
    if exit_code != int('fail' in packages.values()):
        raise ValueError('Process exit contradicts package outcomes')
    return {'tests': dict(sorted(tests.items())), 'packages': dict(sorted(packages.items())),
            'exit_code': exit_code, 'no_test_packages': sorted(empty)}


def compare_go_runs(base, reference, candidate, expectations, *, no_test_packages):
    """Reparse all three raw runs; require exact publisher and package coverage.

    Each run contains ``stdout`` and ``exit_code``. Publisher names must resolve
    uniquely across packages; no suffix matching or last-write-wins collapse.
    """
    transitions = {'FAIL_TO_PASS': ('fail', 'pass'), 'PASS_TO_PASS': ('pass', 'pass'),
                   'FAIL_TO_FAIL': ('fail', 'fail'), 'PASS_TO_FAIL': ('pass', 'fail')}
    if not isinstance(expectations, dict) or set(expectations) != set(transitions):
        raise ValueError('Exact publisher transition categories required')
    observed = {}
    for role, run in (('base', base), ('reference', reference), ('candidate', candidate)):
        if not isinstance(run, dict) or set(run) != {'stdout', 'exit_code'}:
            raise ValueError('Exact raw Go run required')
        observed[role] = go_outcomes(run['stdout'], exit_code=run['exit_code'],
                                     no_test_packages=no_test_packages)
    before, after, actual = (observed[role] for role in ('base', 'reference', 'candidate'))
    if any(set(run['tests']) != set(after['tests']) or
           set(run['packages']) != set(after['packages']) for run in (before, actual)):
        raise ValueError('Paired Go execution coverage differs')
    resolved, expected = {}, {}
    for category, names in expectations.items():
        if not isinstance(names, list):
            raise ValueError('Publisher names must be a list')
        for name in names:
            if not _identity(name) or name in resolved:
                raise ValueError('Invalid or duplicate publisher name')
            matches = [key for key in after['tests'] if key.split('::', 1)[1] == name]
            if len(matches) != 1:
                raise ValueError('Missing or ambiguous publisher name')
            key = matches[0]
            resolved[name] = key
            expected[key] = transitions[category]
    if set(expected) != set(after['tests']):
        raise ValueError('Publisher expectations do not cover every observed test')
    for key, pair in expected.items():
        if (before['tests'][key], after['tests'][key]) != pair:
            raise ValueError('Publisher transition mismatch')
    disagreements = [{'nodeid': key, 'expected': after['tests'][key], 'actual': value}
                     for key, value in actual['tests'].items() if value != after['tests'][key]]
    return {'all_transitions_match': True, 'all_cases_match_reference': not disagreements,
            'case_count': len(expected), 'resolved_nodes': resolved,
            'disagreements': disagreements, 'training_approved': False}
