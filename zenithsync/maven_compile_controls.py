"""Recognize bounded Maven test-compilation missing-symbol controls.

This is a deliberately explicit log profile, not log authentication or a Java
compiler proof. The caller must bind fresh execution, source and test bytes.
A compile failure has no runtime testcase outcomes.
"""

import re

MAX_LOG_BYTES = 4 * 1024**2
_HEADER = re.compile(r'\[ERROR\] (?P<file>/[^\r\n]+\.java):\[(?P<line>[1-9][0-9]*),(?P<column>[1-9][0-9]*)\] cannot find symbol')
_GOAL = re.compile(r'\[ERROR\] Failed to execute goal org\.apache\.maven\.plugins:maven-compiler-plugin:[^\s:]+:testCompile \([^\r\n]+\) on project [^\s:]+: Compilation failure(?:s)?')


def missing_symbol_test_compile(stdout, *, exit_code, reports, expected):
    """Require the declared missing-symbol diagnostics and no test reports.

    ``expected`` contains exact file/line/column/symbol/location records from an
    independently reviewed evaluator profile. No class-level failure labels are
    transformed into testcase failures by this function.
    """
    if (not isinstance(stdout, str) or len(stdout.encode('utf-8')) > MAX_LOG_BYTES
            or '\0' in stdout or '\x1b' in stdout):
        raise ValueError('Bounded plain UTF-8 Maven output required')
    if type(exit_code) is not int or exit_code != 1 or reports != {}:
        raise ValueError('Normal compilation failure with an empty report map required')
    if not isinstance(reports, dict):
        raise ValueError('Explicit report inventory required')
    if not isinstance(expected, list) or not 1 <= len(expected) <= 1000:
        raise ValueError('Bounded explicit diagnostic expectations required')
    for row in expected:
        if not isinstance(row, dict) or set(row) != {'file', 'line', 'column', 'symbol', 'location'}:
            raise ValueError('Exact diagnostic fields required')
        if (not isinstance(row['file'], str) or not row['file'].startswith('/')
                or not row['file'].endswith('.java')
                or any(type(row[k]) is not int or not 0 < row[k] <= 10**7 for k in ('line', 'column'))
                or any(not isinstance(row[k], str) or not row[k].strip()
                       or any(ord(c) < 32 or ord(c) == 127 for c in row[k])
                       for k in ('file', 'symbol', 'location'))):
            raise ValueError('Invalid diagnostic identity')
    identities = [tuple(row[k] for k in ('file', 'line', 'column', 'symbol', 'location')) for row in expected]
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate diagnostic expectations')
    lines = stdout.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == '[ERROR] COMPILATION ERROR :']
    goals = [i for i, line in enumerate(lines) if _GOAL.fullmatch(line)]
    if (len(starts) != 1 or len(goals) != 1 or starts[0] >= goals[0]
            or lines.count('[INFO] BUILD FAILURE') != 1
            or any('BUILD SUCCESS' in line or re.search(r'--- (?:maven-)?surefire', line)
                   or re.match(r'(?:\[INFO\] )?Tests run:', line) for line in lines)):
        raise ValueError('Unambiguous test-compilation failure phase required')
    if any(line.startswith('[ERROR]') for line in lines[:starts[0]]):
        raise ValueError('Unreviewed error before compilation phase')
    found = []
    index = starts[0] + 1
    while index < goals[0] and (not lines[index].strip() or re.fullmatch(r'\[INFO\] -+', lines[index])):
        index += 1
    while index < goals[0]:
        match = _HEADER.fullmatch(lines[index])
        if match is None:
            break
        if index + 2 >= goals[0]:
            raise ValueError('Incomplete compiler diagnostic')
        symbol = re.fullmatch(r'\s+symbol:\s+(.+)', lines[index + 1])
        location = re.fullmatch(r'\s+location:\s+(.+)', lines[index + 2])
        if symbol is None or location is None:
            raise ValueError('Missing symbol or location')
        values = match.groupdict()
        found.append({'file': values['file'], 'line': int(values['line']),
                      'column': int(values['column']), 'symbol': symbol[1], 'location': location[1]})
        index += 3
    if (found != expected or index >= goals[0]
            or lines[index] not in (f'[INFO] {len(found)} error', f'[INFO] {len(found)} errors')):
        raise ValueError('Compiler diagnostics differ from reviewed expectations')
    if any(line.startswith('[ERROR]') for line in lines[index:goals[0]]):
        raise ValueError('Additional compiler errors before goal summary')
    # Maven may repeat the diagnostics after its failed-goal summary. Require
    # those repeats to agree, and reject additional errors hidden in the footer.
    repeated = []
    index = goals[0] + 1
    footer = (
        r'\[ERROR\]\s*',
        r'\[ERROR\] -> \[Help 1\]',
        r'\[ERROR\] To see the full stack trace of the errors, re-run Maven with the -e switch\.',
        r'\[ERROR\] Re-run Maven using the -X switch to enable full debug logging\.',
        r'\[ERROR\] For more information about the errors and possible solutions, please read the following articles:',
        r'\[ERROR\] \[Help 1\] https?://\S+',
    )
    while index < len(lines):
        match = _HEADER.fullmatch(lines[index])
        if match is not None:
            if index + 2 >= len(lines):
                raise ValueError('Incomplete repeated diagnostic')
            symbol = re.fullmatch(r'\[ERROR\]\s+symbol:\s+(.+)', lines[index + 1])
            location = re.fullmatch(r'\[ERROR\]\s+location:\s+(.+)', lines[index + 2])
            if symbol is None or location is None:
                raise ValueError('Malformed repeated diagnostic')
            values = match.groupdict()
            repeated.append({'file': values['file'], 'line': int(values['line']),
                             'column': int(values['column']), 'symbol': symbol[1], 'location': location[1]})
            index += 3
        else:
            if lines[index].startswith('[ERROR]') and not any(
                    re.fullmatch(pattern, lines[index]) for pattern in footer):
                raise ValueError('Unreviewed error after compilation summary')
            index += 1
    if repeated and repeated != found:
        raise ValueError('Repeated compiler diagnostics disagree')
    return {'phase': 'test_compile_failed', 'diagnostics': found,
            'runtime_case_outcomes': None, 'training_approved': False,
            'scope': 'Log consistency only; fresh execution and source identity require separate binding.'}


def compare_compile_barrier_runs(runs, *, expected_diagnostics, passing_cases, skipped_cases):
    """Compare a declared compile barrier with two complete passing test runs.

    This verifies a phase change, not per-test base failures. Case expectations
    must be explicitly reviewed and hash-bound by the grading-bundle validator.
    """
    from .junit_controls import surefire_outcomes

    if not isinstance(runs, dict) or set(runs) != {'base', 'reference', 'candidate'}:
        raise ValueError('Three independent phase controls required')
    for run in runs.values():
        if not isinstance(run, dict) or set(run) != {'stdout', 'exit_code', 'reports'}:
            raise ValueError('Raw log, exit status and report inventory required')
    partitions = []
    for values in (passing_cases, skipped_cases):
        if (not isinstance(values, list) or any(not isinstance(pair, list) or len(pair) != 2
                or any(not isinstance(part, str) or not part.strip()
                       or any(ord(c) < 32 or ord(c) == 127 for c in part) for part in pair)
                for pair in values)):
            raise ValueError('Explicit classname/name pairs required')
        group = {tuple(pair) for pair in values}
        if len(group) != len(values):
            raise ValueError('Duplicate expected case')
        partitions.append(group)
    passed, skipped = partitions
    if not passed or passed & skipped:
        raise ValueError('Nonempty passing set and disjoint skip set required')
    compilation = missing_symbol_test_compile(**runs['base'], expected=expected_diagnostics)
    outcomes = {}
    for role in ('reference', 'candidate'):
        run = runs[role]
        parsed = surefire_outcomes(run['reports'], exit_code=run['exit_code'])
        actual = {(case['class'], case['name']): case['status'] for case in parsed['cases']}
        expected = {identity: 'pass' for identity in passed}
        expected.update({identity: 'skip' for identity in skipped})
        if actual != expected:
            raise ValueError('Runtime case outcomes differ from exhaustive expectations')
        outcomes[role] = parsed
    if outcomes['reference'] != outcomes['candidate']:
        raise ValueError('Reference and candidate suite structures differ')
    return {'base': compilation, 'reference_and_candidate': {
                'test_count': len(passed) + len(skipped), 'passed': len(passed),
                'skipped': len(skipped), 'case_outcomes_identical': True},
            'compile_to_test_phase_change_verified': True,
            'runtime_fail_to_pass_transitions_verified': False,
            'training_approved': False}
