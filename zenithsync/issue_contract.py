"""Compare issue-contract evidence without equating it to reference agreement.

This layer accounts for finite test outcomes. It does not certify the correctness
of a declared contract, its rationale, runtime provenance, or training eligibility.
"""
from collections import Counter

from .artifacts import file_record
from .evaluation import junit_outcomes


def assess_issue_contract(*, contract_reports, compatibility_reports, contract_cases,
                          declared_changes):
    """Require exact coverage and explicitly explained compatibility changes.

    Contract cases must fail on baseline and pass on candidate. Reference failures
    are reported, never hidden. Each allowed compatibility change must name the
    supporting contract cases; only passed-to-failed transitions are eligible.
    All other changes, including new skips or errors, remain blockers.
    """
    if not isinstance(contract_reports, dict) or set(contract_reports) != {'base', 'reference', 'candidate'}:
        raise ValueError('Three exact contract report roles required')
    if not isinstance(compatibility_reports, dict) or set(compatibility_reports) != {'base', 'candidate'}:
        raise ValueError('Two exact compatibility report roles required')
    if (not isinstance(contract_cases, list) or not contract_cases
            or any(not isinstance(case, str) or not case.strip() for case in contract_cases)
            or len(set(contract_cases)) != len(contract_cases)):
        raise ValueError('Unique nonempty contract case inventory required')
    if not isinstance(declared_changes, list):
        raise ValueError('Explicit compatibility change list required')
    paths = {('contract', role): path for role, path in contract_reports.items()}
    paths.update({('compatibility', role): path for role, path in compatibility_reports.items()})
    identities = {key: file_record(path) for key, path in paths.items()}
    outcomes = {key: junit_outcomes(path) for key, path in paths.items()}
    for role in contract_reports:
        if set(outcomes['contract', role]) != set(contract_cases):
            raise ValueError('Contract report coverage differs from declared inventory')
    before, after = outcomes['compatibility', 'base'], outcomes['compatibility', 'candidate']
    if before.keys() != after.keys():
        raise ValueError('Unpaired compatibility coverage')
    declarations = {}
    for row in declared_changes:
        if (not isinstance(row, dict) or set(row) != {'test', 'rationale', 'contract_cases'}
                or not isinstance(row['test'], str) or row['test'] not in before
                or row['test'] in declarations
                or not isinstance(row['rationale'], str) or not row['rationale'].strip()
                or not isinstance(row['contract_cases'], list) or not row['contract_cases']
                or any(not isinstance(case, str) or case not in contract_cases for case in row['contract_cases'])
                or len(set(row['contract_cases'])) != len(row['contract_cases'])):
            raise ValueError('Exact unique compatibility declarations with contract links required')
        if (before[row['test']], after[row['test']]) != ('passed', 'failed'):
            raise ValueError('Declared compatibility change is not observed passed-to-failed')
        declarations[row['test']] = row
    contract_failures = [case for case in sorted(contract_cases)
                         if outcomes['contract', 'base'][case] != 'failed'
                         or outcomes['contract', 'candidate'][case] != 'passed']
    reference_disagreements = [case for case in sorted(contract_cases)
                              if outcomes['contract', 'reference'][case] != outcomes['contract', 'candidate'][case]]
    changes = [{'test': case, 'baseline': before[case], 'candidate': after[case],
                'declared': case in declarations} for case in sorted(before) if before[case] != after[case]]
    unexpected = [row for row in changes if not row['declared']]
    if any(file_record(paths[key]) != identity for key, identity in identities.items()):
        raise ValueError('Issue-contract evidence changed during assessment')
    return {
        'schema_version': 1,
        'contract_checks_passed': not contract_failures,
        'contract_failures': contract_failures,
        'reference_equivalent_on_contract': not reference_disagreements,
        'reference_disagreements': reference_disagreements,
        'declared_transition_policy_satisfied': not unexpected,
        'unexpected_compatibility_changes': unexpected,
        'compatibility_changes': changes,
        'candidate_compatibility_counts': dict(sorted(Counter(after.values()).items())),
        'unresolved_compatibility_cases': {case: after[case] for case in sorted(after) if after[case] != 'passed'},
        'all_compatibility_cases_passed': all(value == 'passed' for value in after.values()),
        'inputs': {section: {role: identities[section, role] for category, role in paths if category == section}
                   for section in ('contract', 'compatibility')},
        'training_approved': False,
        'scope': 'Finite outcome accounting; contract meaning, rationale, runtime, rights and training admission require separate evidence.',
    }
