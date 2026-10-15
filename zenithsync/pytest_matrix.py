"""Reconcile explicit version-dependent pytest obligations without counting skips.

Applicability is caller-supplied reviewed evidence, not inferred from outcomes.
This checks outcome structure and repair behavior only; callers must separately
bind runtime versions, test predicates, source/patch identities and provenance.
It does not grant corpus or training admission.
"""
from copy import deepcopy

from .pytest_controls import call_outcomes


def compare_matrix(environments, applicability):
    """Validate full base/reference/candidate documents for each environment.

    ``applicability`` maps each environment to its explicit active node list.
    All three roles must collect the same complete node set in every environment.
    An inactive node must have exactly skipped setup and passed teardown, with
    no call. Every node must be active somewhere. Active phases are validated by
    the existing strict single-environment verifier.
    """
    if (not isinstance(environments, dict) or len(environments) < 2
            or any(not isinstance(k, str) or not k.strip() for k in environments)
            or not isinstance(applicability, dict)
            or set(environments) != set(applicability)):
        raise ValueError('Exact multi-environment applicability required')
    nodes = None
    covered = set()
    results = {}
    repairs = []
    for name, roles in environments.items():
        if not isinstance(roles, dict) or set(roles) != {'base', 'reference', 'candidate'}:
            raise ValueError('Exactly three paired roles required')
        active = applicability[name]
        if (not isinstance(active, list) or not active
                or any(not isinstance(n, str) or not n.strip() for n in active)
                or len(active) != len(set(active))):
            raise ValueError('Unique nonempty applicable node list required')
        active = set(active)
        checked = {}
        for role, document in roles.items():
            if not isinstance(document, dict):
                raise ValueError('Pytest outcome document required')
            collected = document.get('collected')
            if (not isinstance(collected, list) or not collected
                    or any(not isinstance(n, str) or not n.strip() for n in collected)
                    or len(collected) != len(set(collected))):
                raise ValueError('Unique collected nodes required')
            if nodes is None:
                nodes = set(collected)
            if set(collected) != nodes or not active <= nodes:
                raise ValueError('Matrix collection or applicability differs')
            reports = document.get('reports')
            if not isinstance(reports, list):
                raise ValueError('Pytest phase reports required')
            phases = {}
            for row in reports:
                if not isinstance(row, dict):
                    raise ValueError('Phase report required')
                node, when, outcome = row.get('nodeid'), row.get('when'), row.get('outcome')
                if (not isinstance(node, str) or node not in nodes
                        or when not in ('setup', 'call', 'teardown')
                        or outcome not in ('passed', 'failed', 'skipped')):
                    raise ValueError('Unknown phase or outcome')
                key = (node, when)
                if key in phases:
                    raise ValueError('Duplicate test phase')
                phases[key] = outcome
            for node in nodes - active:
                if ({when: value for (n, when), value in phases.items() if n == node}
                        != {'setup': 'skipped', 'teardown': 'passed'}):
                    raise ValueError('Inactive node must be explicitly unexecuted')
            projection = deepcopy(document)
            projection['collected'] = [n for n in collected if n in active]
            projection['reports'] = [r for r in reports if r['nodeid'] in active]
            # Keep original collection errors and exit code. Do not convert
            # unexpected active skips, setup errors or failed exits to success.
            checked[role] = call_outcomes(projection)
        if any(v != 'passed' for role in ('reference', 'candidate')
               for v in checked[role].values()):
            raise ValueError('Reference or candidate fails an applicable obligation')
        repairs.extend({'environment': name, 'nodeid': n}
                       for n, v in checked['base'].items() if v == 'failed')
        covered.update(active)
        results[name] = {'applicable': sorted(active),
                         'not_executed': sorted(nodes - active), 'outcomes': checked}
    if covered != nodes:
        raise ValueError('Some collected nodes never execute')
    if not repairs:
        raise ValueError('No demonstrated repair transition')
    return {'schema_version': 1, 'nodes': sorted(nodes), 'environments': results,
            'repair_transitions': repairs, 'outcome_contract_passed': True,
            'training_approved': False,
            'scope': 'Explicit applicability and paired phase outcomes only; '
                     'runtime identity, applicability truth and training admission remain external.'}


def compare_publisher_matrix(environments, applicability, expectations, *,
                             supplemental_pass_to_pass):
    """Require each publisher transition in every applicable environment.

    Publisher whitespace-collapsed groups retain all complete node identities.
    Extra regression tests require individually declared pass-to-pass nodes;
    neither expected groups nor supplemental coverage is inferred from success.
    """
    from .pytest_controls import validate_supplemental_passes

    transitions = {'FAIL_TO_PASS': ('failed', 'passed'),
                   'PASS_TO_PASS': ('passed', 'passed'),
                   'FAIL_TO_FAIL': ('failed', 'failed'),
                   'PASS_TO_FAIL': ('passed', 'failed')}
    if not isinstance(expectations, dict) or set(expectations) != set(transitions):
        raise ValueError('Exact publisher expectation categories required')
    expected = {}
    for category, keys in expectations.items():
        if not isinstance(keys, list):
            raise ValueError('Publisher category must be a list')
        for key in keys:
            if (not isinstance(key, str) or not key or key.split() != [key]
                    or key in expected):
                raise ValueError('Invalid or duplicated publisher key')
            expected[key] = transitions[category]
    supplemental = validate_supplemental_passes(supplemental_pass_to_pass)
    result = compare_matrix(environments, applicability)
    groups = {}
    for node in result['nodes']:
        groups.setdefault(node.split()[0], []).append(node)
    for node in supplemental:
        if node in expected or groups.get(node) != [node]:
            raise ValueError('Supplemental node must be distinct and exact')
    if set(groups) != set(expected) | set(supplemental):
        raise ValueError('Publisher matrix expectation coverage differs')
    for environment in result['environments'].values():
        before = environment['outcomes']['base']
        after = environment['outcomes']['reference']
        for node in environment['applicable']:
            transition = expected.get(node.split()[0], ('passed', 'passed'))
            if (before[node], after[node]) != transition:
                raise ValueError('Applicable outcome contradicts publisher transition: ' + node)
    result['publisher_key_count'] = len(expected)
    result['supplemental_pass_to_pass'] = sorted(supplemental)
    result['publisher_transitions_match'] = True
    result['scope'] = ('Paired phase outcomes and explicit publisher transitions across '
                       'declared applicability; not runtime authenticity or training admission.')
    return result
