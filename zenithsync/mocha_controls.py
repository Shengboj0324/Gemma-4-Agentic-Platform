"""Validate complete Mocha JSON reports, not log authenticity or test quality.

This profile rejects pending tests, retries, duplicate full titles and hook-only
failures. Execution provenance and source integrity must be bound separately.
Publisher short titles must be resolved explicitly before comparison.
"""

import json
import math


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError('Nonfinite JSON number: ' + value)


def _name(value):
    return (isinstance(value, str) and bool(value.strip()) and
            not any(ord(c) < 32 or ord(c) == 127 for c in value))


def _rows(value):
    if not isinstance(value, list):
        raise ValueError('Test array required')
    rows = {}
    for row in value:
        if not isinstance(row, dict):
            raise ValueError('Test object required')
        title, full = row.get('title'), row.get('fullTitle')
        if (not _name(title) or not _name(full) or
                not (full == title or full.endswith(' ' + title))):
            raise ValueError('Invalid full test identity')
        if full in rows:
            raise ValueError('Duplicate full test identity')
        if type(row.get('currentRetry')) is not int or row['currentRetry'] != 0:
            raise ValueError('Retries or unknown retry status are unsupported')
        if not isinstance(row.get('err'), dict):
            raise ValueError('Explicit test error object required')
        if 'duration' in row:
            duration = row['duration']
            if (type(duration) not in (int, float) or
                    (type(duration) is float and not math.isfinite(duration)) or
                    duration < 0):
                raise ValueError('Invalid test duration')
        rows[full] = row
    return rows


def mocha_outcomes(text, *, exit_code):
    """Require a complete, internally consistent report and matching exit code."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Nonempty Mocha JSON required')
    if type(exit_code) is not int or not 0 <= exit_code <= 255:
        raise ValueError('Invalid process exit')
    report = json.loads(text, object_pairs_hook=_object,
                        parse_constant=_invalid_constant)
    if not isinstance(report, dict) or not isinstance(report.get('stats'), dict):
        raise ValueError('Report and stats objects required')
    stats = report['stats']
    for key in ('tests', 'passes', 'failures', 'pending'):
        if type(stats.get(key)) is not int or stats[key] < 0:
            raise ValueError('Invalid test count')
    tests = _rows(report.get('tests'))
    passed = _rows(report.get('passes'))
    failed = _rows(report.get('failures'))
    pending = _rows(report.get('pending'))
    if not tests or pending or stats['pending']:
        raise ValueError('Empty or pending test suite is unsupported')
    if (stats['tests'] != len(tests) or stats['passes'] != len(passed) or
            stats['failures'] != len(failed)):
        raise ValueError('Reported counts disagree with test arrays')
    if set(passed) & set(failed) or set(passed) | set(failed) != set(tests):
        raise ValueError('Outcomes do not partition executed tests')
    outcomes = {}
    for status, rows in (('pass', passed), ('fail', failed)):
        for name, row in rows.items():
            if tests[name] != row:
                raise ValueError('Outcome differs from executed test record')
            if bool(row['err']) != (status == 'fail'):
                raise ValueError('Error object contradicts outcome')
            outcomes[name] = status
    # Mocha caps its failure-count exit status at 255.
    if exit_code != min(len(failed), 255):
        raise ValueError('Process exit contradicts failures')
    return {'tests': outcomes,
            'titles': {name: row['title'] for name, row in tests.items()}}


def compare_mocha_runs(runs, *, fail_to_pass, pass_to_pass):
    """Compare three raw reports against exhaustive, explicit full test names."""
    if not isinstance(runs, dict) or set(runs) != {'base', 'reference', 'candidate'}:
        raise ValueError('Base, reference and candidate runs required')
    for names in (fail_to_pass, pass_to_pass):
        if (not isinstance(names, list) or any(not _name(n) for n in names) or
                len(names) != len(set(names))):
            raise ValueError('Unique full test names required')
    if not fail_to_pass or set(fail_to_pass) & set(pass_to_pass):
        raise ValueError('Nonempty disjoint regression expectations required')
    expected = set(fail_to_pass) | set(pass_to_pass)
    parsed = {}
    for role, run in runs.items():
        if not isinstance(run, dict) or set(run) != {'text', 'exit_code'}:
            raise ValueError('Raw report and exit code required')
        parsed[role] = mocha_outcomes(**run)
        if set(parsed[role]['tests']) != expected:
            raise ValueError('Test coverage differs from explicit expectations')
        for name, outcome in parsed[role]['tests'].items():
            want = 'fail' if role == 'base' and name in fail_to_pass else 'pass'
            if outcome != want:
                raise ValueError('Unexpected test transition: ' + role + ': ' + name)
    if any(p['titles'] != parsed['reference']['titles'] for p in parsed.values()):
        raise ValueError('Test titles changed between runs')
    return {'test_count': len(expected), 'fail_to_pass_count': len(fail_to_pass),
            'pass_to_pass_count': len(pass_to_pass), 'transitions_verified': True,
            'training_approved': False}


def compare_mocha_publisher(runs, *, fail_to_pass, pass_to_pass):
    """Resolve publisher short titles to all matches, never an arbitrary match."""
    for names in (fail_to_pass, pass_to_pass):
        if (not isinstance(names, list) or any(not _name(n) for n in names) or
                len(set(names)) != len(names)):
            raise ValueError('Unique publisher titles required')
    if not fail_to_pass or set(fail_to_pass) & set(pass_to_pass):
        raise ValueError('Disjoint publisher expectations required')
    if not isinstance(runs, dict) or set(runs) != {'base', 'reference', 'candidate'}:
        raise ValueError('Three recorded runs required')
    reference = runs['reference']
    if not isinstance(reference, dict) or set(reference) != {'text', 'exit_code'}:
        raise ValueError('Raw reference report required')
    parsed = mocha_outcomes(**reference)
    resolved = {}
    for title in fail_to_pass + pass_to_pass:
        matches = sorted(name for name, short in parsed['titles'].items() if short == title)
        if not matches or (title in fail_to_pass and len(matches) != 1):
            raise ValueError('Missing or ambiguous regression title')
        resolved[title] = matches
    comparison = compare_mocha_runs(runs,
        fail_to_pass=[name for title in fail_to_pass for name in resolved[title]],
        pass_to_pass=[name for title in pass_to_pass for name in resolved[title]])
    return {**comparison, 'resolved_titles': resolved,
            'all_cases_match_reference': True,
            'ambiguous_pass_titles': {k: v for k, v in resolved.items() if len(v) > 1}}
