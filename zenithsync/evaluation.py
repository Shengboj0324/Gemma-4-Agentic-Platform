"""Strict paired JUnit accounting, not a benchmark solve or significance test.

Tests from one repository task are dependent observations. Counts here must not
be interpreted as independent task samples or evidence of generalization.
"""

from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET


def junit_outcomes(path: Path) -> dict[str, str]:
    """Read pytest case identities; reject ambiguous or incomplete reports."""
    root = ET.parse(path).getroot()
    if root.tag not in {'testsuite', 'testsuites'}:
        raise ValueError('Expected a JUnit test suite')
    cases = {}
    for case in root.iter('testcase'):
        classname, name = case.get('classname'), case.get('name')
        if not classname or not name:
            raise ValueError('Test case lacks a stable identity')
        identity = classname + '::' + name
        if identity in cases:
            raise ValueError('Duplicate test case identity: ' + identity)
        states = [child.tag for child in case
                  if child.tag in {'failure', 'error', 'skipped'}]
        if len(states) > 1:
            raise ValueError('Ambiguous test case outcome: ' + identity)
        cases[identity] = {'failure': 'failed', 'error': 'error',
                           'skipped': 'skipped'}.get(states[0], 'passed') if states else 'passed'
    if not cases:
        raise ValueError('Empty JUnit report')
    for suite in root.iter():
        if suite.tag not in {'testsuite', 'testsuites'}:
            continue
        children = list(suite.iter('testcase'))
        counts = Counter(cases[case.get('classname') + '::' + case.get('name')]
                         for case in children)
        expected = {'tests': len(children), 'failures': counts['failed'],
                    'errors': counts['error'], 'skipped': counts['skipped']}
        for attribute, observed in expected.items():
            declared = suite.get(attribute)
            # Some producers omit outcome summaries or the aggregate root count.
            # Every supplied count must agree; individual suites require tests.
            if declared is None and (attribute != 'tests' or suite.tag == 'testsuites'):
                continue
            if (declared is None or not declared.isascii() or not declared.isdecimal()
                    or int(declared) != observed):
                raise ValueError('Declared ' + attribute + ' count disagrees with recorded cases')
    return cases


def compare_junit(baseline: Path, candidate: Path) -> dict:
    """Require identical case coverage and preserve every observed transition."""
    before, after = junit_outcomes(baseline), junit_outcomes(candidate)
    if before.keys() != after.keys():
        raise ValueError('Unpaired test coverage; comparisons require identical cases')
    changes = [{'test': name, 'baseline': before[name], 'candidate': after[name]}
               for name in sorted(before) if before[name] != after[name]]
    return {
        'case_count': len(before),
        'baseline_counts': dict(sorted(Counter(before.values()).items())),
        'candidate_counts': dict(sorted(Counter(after.values()).items())),
        'changed_cases': changes,
        'unchanged_failures': [name for name in sorted(before)
                               if before[name] == after[name] == 'failed'],
        'scope': 'Paired test cases only; skipped includes xfail; no task solve or statistical independence claim',
    }
