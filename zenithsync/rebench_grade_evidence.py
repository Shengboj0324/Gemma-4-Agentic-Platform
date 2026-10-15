"""Recompute a recorded SWE-rebench grade from hash-bound pytest outcomes."""
from pathlib import Path

from .artifacts import file_record, load_json
from .pytest_controls import compare_candidate, compare_controls


def verify_rebench_outcomes(grading, grade_directory):
    """Check evidence consistency, without claiming receipt authenticity.

    Paths come from the producer's existing bindings. Ambiguous role matches
    fail closed; no directory search or fallback to a passing report is used.
    Returned identities let the caller recheck for changes before returning.
    """
    bindings = grading.get('inputs', {}).get('bindings')
    if not isinstance(bindings, dict):
        raise ValueError('Bound publisher outcome evidence required')
    evidence = {}

    def read(path, expected):
        path = Path(path)
        actual = file_record(path)
        if actual != expected:
            raise ValueError('Publisher outcome evidence identity mismatch')
        evidence[str(path)] = actual
        return load_json(path)

    def select(name, parent=None):
        matches = [(path, identity) for path, identity in bindings.items()
                   if isinstance(path, str) and Path(path).name == name
                   and (parent is None or Path(path).parent.name == parent)]
        if len(matches) != 1:
            raise ValueError('Unique bound publisher outcome evidence required')
        return read(*matches[0])

    metadata = select('metadata.json')
    keys = ('FAIL_TO_PASS', 'FAIL_TO_FAIL', 'PASS_TO_PASS', 'PASS_TO_FAIL')
    if not isinstance(metadata, dict) or not set(keys) <= set(metadata):
        raise ValueError('Publisher transition expectations required')
    base = select('outcomes.json', 'base')
    reference = select('outcomes.json', 'reference')
    compare_controls(base, reference, {key: metadata[key] for key in keys})
    candidate = read(Path(grade_directory) / 'candidate' / 'outcomes.json',
                     grading.get('outcomes'))
    computed = compare_candidate(reference, candidate)
    if computed != grading.get('grading'):
        raise ValueError('Grading summary differs from recomputed outcomes')
    if any(file_record(Path(path)) != identity for path, identity in evidence.items()):
        raise ValueError('Publisher outcome evidence changed during verification')
    return evidence
