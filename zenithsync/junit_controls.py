"""Strict Maven Surefire XML outcomes; execution provenance is a separate gate.

Only UTF-8, single-suite reports without retries are supported. Missing reports
(e.g. compilation failures) are not converted into fabricated failed test cases.
Skipped cases remain explicit and cannot establish a fail-to-pass transition.
"""

import re
import xml.etree.ElementTree as ET

MAX_REPORT_BYTES = 16 * 1024**2
MAX_REPORTS = 1024
MAX_CASES = 100_000
OUTCOMES = {'failure': 'fail', 'error': 'error', 'skipped': 'skip'}


def _name(value):
    return (isinstance(value, str) and bool(value.strip())
            and not any(ord(char) < 32 or ord(char) == 127 for char in value))


def _count(suite, key):
    value = suite.get(key)
    if not isinstance(value, str) or re.fullmatch(r'0|[1-9][0-9]*', value) is None:
        raise ValueError('Explicit nonnegative suite count required: ' + key)
    if len(value) > 6 or int(value) > MAX_CASES:
        raise ValueError('Suite count exceeds case budget')
    return int(value)


def surefire_outcomes(reports, *, exit_code):
    """Validate bounded raw reports, exact count accounting, and Maven exit status.

    Case identity is the pair (classname, name), never a concatenated short name.
    XML stdout, properties and durations are not evidence of passing assertions.
    """
    if (not isinstance(reports, dict) or not 1 <= len(reports) <= MAX_REPORTS
            or any(not _name(name) or '/' in name or '\\' in name
                   or not name.endswith('.xml') for name in reports)):
        raise ValueError('Nonempty bounded report map with simple XML names required')
    if any(not isinstance(data, bytes) or not data for data in reports.values()):
        raise ValueError('Nonempty raw XML bytes required')
    if sum(map(len, reports.values())) > MAX_REPORT_BYTES:
        raise ValueError('XML report byte budget exceeded')
    if type(exit_code) is not int or exit_code not in (0, 1):
        raise ValueError('Normal Maven completion status (0 or 1) required')
    cases, suites = {}, set()
    for filename, data in sorted(reports.items()):
        try:
            text = data.decode('utf-8-sig')
        except UnicodeDecodeError as error:
            raise ValueError('UTF-8 XML required') from error
        if '\0' in text or re.search(r'<!\s*(DOCTYPE|ENTITY)\b', text, re.I):
            raise ValueError('DTD, entities and NUL encodings are unsupported')
        declaration = re.match(r'\s*<\?xml\s+.*?\?>', text, re.S)
        if declaration:
            encoding = re.search(r'encoding\s*=\s*[\'"]([^\'"]+)', declaration[0])
            if encoding and encoding[1].lower() != 'utf-8':
                raise ValueError('Only UTF-8 declarations supported')
        try:
            suite = ET.fromstring(text)
        except ET.ParseError as error:
            raise ValueError('Malformed Surefire XML') from error
        if suite.tag != 'testsuite' or not _name(suite.get('name')):
            raise ValueError('One named Surefire testsuite per report required')
        if suite.get('name') in suites:
            raise ValueError('Duplicate suite identity')
        suites.add(suite.get('name'))
        counts = {key: _count(suite, key) for key in ('tests', 'failures', 'errors', 'skipped')}
        observed = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
        for child in suite:
            if child.tag in ('properties', 'system-out', 'system-err'):
                if child.tag == 'properties':
                    if any(node.tag != 'property' or list(node) for node in child):
                        raise ValueError('Unsupported suite property structure')
                elif list(child):
                    raise ValueError('Nested suite output is unsupported')
                continue
            if child.tag != 'testcase':
                raise ValueError('Unsupported suite element: ' + child.tag)
            if set(child.attrib) - {'classname', 'name', 'time'}:
                raise ValueError('Unsupported testcase attributes')
            identity = (child.get('classname'), child.get('name'))
            if not all(_name(part) for part in identity) or identity in cases:
                raise ValueError('Missing or duplicate case identity')
            if any(node.tag not in (*OUTCOMES, 'system-out', 'system-err') or list(node)
                   for node in child):
                raise ValueError('Retries or unsupported testcase elements')
            flags = [node.tag for node in child if node.tag in OUTCOMES]
            if len(flags) > 1:
                raise ValueError('Ambiguous testcase outcomes')
            status = OUTCOMES[flags[0]] if flags else 'pass'
            cases[identity] = status
            observed['tests'] += 1
            if flags:
                observed[{'failure': 'failures', 'error': 'errors', 'skipped': 'skipped'}[flags[0]]] += 1
            if len(cases) > MAX_CASES:
                raise ValueError('Total case budget exceeded')
        if observed != counts:
            raise ValueError('Suite counts do not match testcase outcomes: ' + filename)
    if not cases:
        raise ValueError('No executed or explicitly skipped test identities')
    failed = any(status in ('fail', 'error') for status in cases.values())
    if (exit_code != 0) != failed:
        raise ValueError('Maven exit code contradicts reported test outcomes')
    return {'cases': [{'class': cls, 'name': name, 'status': status}
                      for (cls, name), status in sorted(cases.items())],
            'suite_count': len(suites), 'training_approved': False}


def compare_surefire_runs(runs, *, fail_to_pass, pass_to_pass, skipped):
    """Require exhaustive case-level expectations and exact observed transitions.

    Compilation failures and class-level publisher labels must be handled as
    separate evidence; this function cannot promote them into runtime outcomes.
    """
    if not isinstance(runs, dict) or set(runs) != {'base', 'reference', 'candidate'}:
        raise ValueError('Three independent runs required')
    groups = []
    for values in (fail_to_pass, pass_to_pass, skipped):
        if (not isinstance(values, list) or any(not isinstance(pair, list) or len(pair) != 2
                or not all(_name(part) for part in pair) for pair in values)):
            raise ValueError('Explicit classname/name pairs required')
        group = {tuple(pair) for pair in values}
        if len(group) != len(values):
            raise ValueError('Duplicate expected case')
        groups.append(group)
    failing, passing, skipping = groups
    if not failing or failing & passing or failing & skipping or passing & skipping:
        raise ValueError('Nonempty regression set and disjoint outcome partitions required')
    expected = failing | passing | skipping
    for role, run in runs.items():
        if not isinstance(run, dict) or set(run) != {'reports', 'exit_code'}:
            raise ValueError('Raw report set and process status required')
        parsed = surefire_outcomes(**run)
        actual = {(case['class'], case['name']): case['status'] for case in parsed['cases']}
        if set(actual) != expected:
            raise ValueError('Report coverage differs from expected case universe')
        for identity, status in actual.items():
            wanted = {'skip'} if identity in skipping else (
                {'fail', 'error'} if role == 'base' and identity in failing else {'pass'})
            if status not in wanted:
                raise ValueError('Unexpected test transition')
    return {'test_count': len(expected), 'fail_to_pass_count': len(failing),
            'pass_to_pass_count': len(passing), 'skipped_count': len(skipping),
            'transitions_verified': True, 'training_approved': False}
