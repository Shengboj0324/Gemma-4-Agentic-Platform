"""Recompute publisher matrix outcomes from explicitly hash-bound files.

This verifies local evidence consistency, not provenance or training admission.
Probe reconstruction and patch/snapshot binding remain separate requirements.
"""
from pathlib import Path

from .artifacts import file_record, load_json
from .pytest_applicability import applicable_nodes
from .pytest_matrix import compare_publisher_matrix


def verify_matrix_outcomes(bundle):
    """Derive applicability again; never trust stored active-node lists.

    Each file reference is exactly {path, identity}. Environment records bind
    a version export, predicate source, predicate receipt and all three role
    receipts/outcomes. Sources must be identical across environments and every
    role must use the corresponding predicate probe's image. These checks do
    not prove that an arbitrary producer executed the asserted probe.
    """
    if (not isinstance(bundle, dict)
            or set(bundle) != {'metadata', 'obligations', 'module_path',
                               'environments', 'expected'}):
        raise ValueError('Exact matrix evidence descriptor required')
    evidence = {}

    def read(ref, *, source=False):
        if (not isinstance(ref, dict) or set(ref) != {'path', 'identity'}
                or not isinstance(ref['path'], str) or not ref['path']):
            raise ValueError('Explicit file reference required')
        path = Path(ref['path'])
        identity = file_record(path)
        if identity != ref['identity']:
            raise ValueError('Matrix evidence identity mismatch')
        if str(path) in evidence and evidence[str(path)] != identity:
            raise ValueError('Conflicting matrix file identity')
        evidence[str(path)] = identity
        return path.read_text(encoding='utf-8') if source else load_json(path)

    metadata = read(bundle['metadata'])
    categories = ('FAIL_TO_PASS', 'FAIL_TO_FAIL', 'PASS_TO_PASS', 'PASS_TO_FAIL')
    if not isinstance(metadata, dict) or not set(categories) <= set(metadata):
        raise ValueError('Publisher expectations required')
    expectations = {key: metadata[key] for key in categories}
    obligations = read(bundle['obligations'])
    if (not isinstance(obligations, dict)
            or obligations.get('publisher_expectations') != expectations):
        raise ValueError('Declared publisher obligations differ')
    environments = bundle['environments']
    if not isinstance(environments, dict) or len(environments) < 2:
        raise ValueError('At least two bound environments required')
    matrix, active, versions = {}, {}, []
    first_source = None
    for name, environment in environments.items():
        if (not isinstance(environment, dict)
                or set(environment) != {'version', 'source', 'receipt', 'roles'}):
            raise ValueError('Exact environment evidence required')
        runtime = read(environment['version'])
        if not isinstance(runtime, dict) or not isinstance(runtime.get('version'), list):
            raise ValueError('Exported runtime version required')
        version = tuple(runtime['version'])
        if version in versions:
            raise ValueError('Duplicate runtime version')
        versions.append(version)
        source = read(environment['source'], source=True)
        if first_source is not None and source != first_source:
            raise ValueError('Predicate sources differ across environments')
        first_source = source
        receipt = read(environment['receipt'])
        if (not isinstance(receipt, dict) or not isinstance(receipt.get('image_id'), str)
                or not receipt['image_id'].startswith('sha256:')):
            raise ValueError('Predicate runtime image required')
        roles = environment['roles']
        if not isinstance(roles, dict) or set(roles) != {'base', 'reference', 'candidate'}:
            raise ValueError('Exactly three bound roles required')
        matrix[name] = {}
        for role, refs in roles.items():
            if not isinstance(refs, dict) or set(refs) != {'receipt', 'outcomes'}:
                raise ValueError('Role receipt and outcomes required')
            role_receipt = read(refs['receipt'])
            if (not isinstance(role_receipt, dict)
                    or role_receipt.get('image_id') != receipt['image_id']):
                raise ValueError('Role and predicate runtime images differ')
            matrix[name][role] = read(refs['outcomes'])
        base = matrix[name]['base']
        if not isinstance(base, dict):
            raise ValueError('Base outcomes required')
        active[name] = applicable_nodes(source, module_path=bundle['module_path'],
                                       collected=base.get('collected'), version=version)
    computed = compare_publisher_matrix(
        matrix, active, expectations,
        supplemental_pass_to_pass=obligations.get('supplemental_pass_to_pass'))
    if computed != bundle['expected']:
        raise ValueError('Matrix summary differs from recomputed evidence')
    if any(file_record(Path(path)) != identity for path, identity in evidence.items()):
        raise ValueError('Matrix evidence changed during verification')
    return {'grading': computed, 'bindings': evidence, 'training_approved': False}
