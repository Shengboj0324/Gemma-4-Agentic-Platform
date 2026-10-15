"""Compose matrix outcomes, known probes and replay/task provenance checks."""
import base64
from pathlib import Path

from scripts.grade_rebench_replay import source_allowlist
from scripts.run_rebench_controls import validate_profile
from .artifacts import file_record, load_json
from .matrix_grade_evidence import verify_matrix_outcomes
from .matrix_probe_contract import verify_matrix_probe
from .probe_receipt import verify_probe_receipt


def predicate_probe(patch, module_path):
    """Reconstruct the version/source exporter used by matrix protocol v1."""
    # module_path is validated by applicable_nodes before this function is used.
    filename = module_path.rsplit('/', 1)[-1]
    body = '''
import base64,platform,pathlib,subprocess,json,django
out=pathlib.Path('/audit');out.mkdir()
p=pathlib.Path('/tmp/tests.patch');p.write_bytes(base64.b64decode(PATCH))
subprocess.run(['git','-C','/testbed','apply','--check',str(p)],check=True)
subprocess.run(['git','-C','/testbed','apply',str(p)],check=True)
source=pathlib.Path(SOURCE_PATH);(out/OUTPUT_NAME).write_bytes(source.read_bytes())
(out/'version.json').write_text(json.dumps(dict(version=django.VERSION,django_version=django.get_version(),module=django.__file__,python=platform.python_version(),machine=platform.machine())))
'''
    body = body.replace('SOURCE_PATH', repr('/testbed/' + module_path)).replace('OUTPUT_NAME', repr(filename))
    return 'PATCH=' + repr(base64.b64encode(patch).decode('ascii')) + '\n' + body


def verify_matrix_grade(grading, replay, patch_path):
    """Return all checked file identities; never approve training.

    Receipts are retained local execution evidence, not external attestation.
    Full source qualification, history review, rights and splits remain gates.
    """
    bundle = grading['matrix']
    checked = verify_matrix_outcomes(bundle)
    evidence = dict(checked['bindings'])

    def read(ref, *, binary=False, text=False):
        if (not isinstance(ref, dict) or set(ref) != {'path', 'identity'}
                or not isinstance(ref['path'], str)):
            raise ValueError('Explicit provenance file reference required')
        path = Path(ref['path'])
        identity = file_record(path)
        if identity != ref['identity'] or (str(path) in evidence and evidence[str(path)] != identity):
            raise ValueError('Matrix provenance identity mismatch')
        evidence[str(path)] = identity
        return path.read_bytes() if binary else path.read_text() if text else load_json(path)

    proof = grading['provenance']
    if (not isinstance(proof, dict) or set(proof) !=
            {'publisher', 'profile', 'patches', 'environments', 'primary', 'allowed_source_paths'}):
        raise ValueError('Exact matrix provenance descriptor required')
    publisher = read(proof['publisher'])
    profile = validate_profile(read(proof['profile']))
    task = publisher['task']
    if (grading['task'] != replay['instance_id'] or task['instance_id'] != replay['instance_id']
            or profile['instance_id'] != replay['instance_id']
            or task['repo'] != replay['profile']['repo']
            or task['base_commit'] != replay['profile']['base_commit']):
        raise ValueError('Matrix task differs from replay')
    if set(proof['patches']) != {'reference', 'tests'}:
        raise ValueError('Exact publisher patches required')
    patches = {'candidate': Path(patch_path).read_bytes()}
    if file_record(Path(patch_path)) != replay['patch']:
        raise ValueError('Candidate patch differs from replay')
    evidence[str(patch_path)] = replay['patch']
    for key, ref in proof['patches'].items():
        patches[key] = read(ref, binary=True)
        if publisher['files'][key + '.patch'] != ref['identity']:
            raise ValueError('Publisher patch identity mismatch')
    if publisher['files']['metadata.json'] != bundle['metadata']['identity']:
        raise ValueError('Publisher metadata identity mismatch')
    allowed = source_allowlist(proof['allowed_source_paths'])
    if (set(proof['environments']) != set(bundle['environments'])
            or proof['primary'] not in proof['environments']):
        raise ValueError('Matrix provenance environment coverage differs')
    source_tree = None
    for name, env in proof['environments'].items():
        if set(env) != {'snapshot', 'verification', 'receipt', 'input_bindings', 'roles', 'version_assertion'}:
            raise ValueError('Exact snapshot and role provenance required')
        snapshot, verification, container = (read(env[key]) for key in ('snapshot', 'verification', 'receipt'))
        upstream_bindings = read(env['input_bindings'])
        if not isinstance(upstream_bindings, dict) or not upstream_bindings:
            raise ValueError('Bound snapshot verification inputs required')
        for path, identity in upstream_bindings.items():
            read({'path': path, 'identity': identity}, binary=True)
        if (snapshot['base_commit'] != task['base_commit'] or snapshot['exact_tree_preserved'] is not True
                or verification['tracked_manifest_matches'] is not True
                or type(verification['reachable_commits']) is not int or verification['reachable_commits'] != 1
                or task['base_commit'] not in verification['old_commits_inaccessible']
                or any(type(container[k]) is not int or container[k] != 0
                       for k in ('returncode', 'copy_returncode', 'cleanup_returncode'))
                or container.get('state', {}).get('Status') != 'exited'
                or container.get('state', {}).get('OOMKilled') is not False
                or container.get('state', {}).get('Error') != ''
                or type(container.get('state', {}).get('ExitCode')) is not int
                or container['state']['ExitCode'] != 0):
            raise ValueError('Unqualified matrix source snapshot')
        if source_tree is not None and source_tree != snapshot['source_tree']:
            raise ValueError('Matrix environments contain different source trees')
        source_tree = snapshot['source_tree']
        image = container['image_id']
        if name == proof['primary'] and image != replay['image']:
            raise ValueError('Primary grading image differs from native replay')
        outcome_env = bundle['environments'][name]
        version = read(outcome_env['version'])
        verify_probe_receipt(read(outcome_env['receipt']), predicate_probe(patches['tests'], bundle['module_path']),
                             image=image, platform=profile['platform'], python=profile['python'], grading_tests=False)
        if type(env['version_assertion']) is not bool:
            raise ValueError('Explicit version assertion mode required')
        if set(env['roles']) != {'base', 'reference', 'candidate'}:
            raise ValueError('Complete probe role coverage required')
        for role, refs in env['roles'].items():
            if set(refs) != {'probe', 'runtime', 'allowed_paths'}:
                raise ValueError('Exact role provenance required')
            if refs['allowed_paths'] != allowed and not (role != 'candidate' and refs['allowed_paths'] == []):
                raise ValueError('Role allowlist differs from candidate declaration')
            verify_matrix_probe(read(refs['probe'], text=True), read(outcome_env['roles'][role]['receipt']),
                                image=image, snapshot=snapshot, role=role, patches=patches, profile=profile,
                                allowed_paths=refs['allowed_paths'],
                                version_assertion=version['django_version'] if env['version_assertion'] else None)
            runtime = read(refs['runtime'])
            outcomes = read(outcome_env['roles'][role]['outcomes'])
            if (runtime.get('role') != role or runtime.get('tests_started') is not True
                    or runtime.get('tracked_diff_unchanged_by_tests') is not True
                    or runtime.get('import', {}).get('stdout') != profile['expected_origin']
                    or type(runtime.get('import', {}).get('returncode')) is not int
                    or runtime['import']['returncode'] != 0
                    or type(runtime.get('pytest_exit')) is not int
                    or runtime['pytest_exit'] != outcomes['exitstatus']):
                raise ValueError('Matrix runtime observations differ')
    normalized = dict(all_cases_match_reference=True, case_count=len(checked['grading']['nodes']), disagreements=[])
    if grading['grading'] != normalized:
        raise ValueError('Normalized matrix grade differs from recomputation')
    if any(file_record(Path(path)) != identity for path, identity in evidence.items()):
        raise ValueError('Matrix admission evidence changed')
    return evidence
