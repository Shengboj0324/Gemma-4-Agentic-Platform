"""Bind recorded matrix probes to the known evaluator and exact task inputs.

Parse literal settings without executing the stored program. Snapshot and
publisher provenance must still be checked by the admission caller.
"""
import ast
import base64

from scripts.qualify_swe_rebench_evaluator import PLUGIN, PROBE
from .probe_receipt import verify_probe_receipt
from .legacy_matrix_probe import PROBE as LEGACY_PROBE


def verify_matrix_probe(probe, receipt, *, image, snapshot, role, patches,
                        profile, allowed_paths, version_assertion=None):
    """Reject altered evaluator bodies, executable settings and wrong patches."""
    if (role not in ('base', 'reference', 'candidate')
            or not isinstance(probe, str)
            or not isinstance(patches, dict)
            or set(patches) != {'candidate', 'reference', 'tests'}
            or any(not isinstance(value, bytes) for value in patches.values())):
        raise ValueError('Known evaluator body and exact patch inputs required')
    body = next((known for known in (PROBE, LEGACY_PROBE) if probe.endswith(known)), None)
    if body is None:
        raise ValueError('Known evaluator body and exact patch inputs required')
    settings_source = probe[:-len(body)]
    if version_assertion is not None:
        if (not isinstance(version_assertion, str)
                or not version_assertion or any(c not in '0123456789.' for c in version_assertion)):
            raise ValueError('Literal release version required')
        prefix = 'import django; assert django.get_version() == ' + repr(version_assertion) + '\n'
        if not settings_source.startswith(prefix):
            raise ValueError('Runtime version assertion differs')
        settings_source = settings_source[len(prefix):]
    try:
        tree = ast.parse(settings_source)
        settings = {}
        for statement in tree.body:
            if (not isinstance(statement, ast.Assign) or len(statement.targets) != 1
                    or not isinstance(statement.targets[0], ast.Name)):
                raise ValueError('Only literal probe settings are accepted')
            key = statement.targets[0].id
            if key in settings:
                raise ValueError('Duplicate probe setting')
            settings[key] = ast.literal_eval(statement.value)
    except (SyntaxError, TypeError) as error:
        raise ValueError('Invalid probe settings') from error
    expected = dict(BASE=snapshot['snapshot_commit'], TREE=snapshot['source_tree'],
                    ROLE=role, PYTHON=profile['python'], MODULE=profile['module'],
                    EXPECTED_ORIGIN=profile['expected_origin'],
                    SOURCE_PYTHONPATH='/testbed/' + profile['import_root'],
                    ALLOWED_PATHS=allowed_paths, TEST_TARGETS=profile['test_targets'],
                    PLUGIN=PLUGIN, RESOURCE_PAYLOAD='', RESOURCE_ADAPTER='')
    if set(settings) != set(expected) | {'PATCHES'}:
        raise ValueError('Probe setting set differs')
    if any(settings[key] != value for key, value in expected.items()):
        raise ValueError('Probe settings differ from task, snapshot or grading profile')
    payload = settings['PATCHES']
    required = {'tests'} | ({role} if role != 'base' else set())
    if (not isinstance(payload, dict) or not required <= set(payload) <= set(patches)
            or any(payload[key] != base64.b64encode(patches[key]).decode('ascii') for key in payload)):
        raise ValueError('Probe patch payload differs from bound task patches')
    return verify_probe_receipt(receipt, probe, image=image,
                                platform=profile['platform'], python=profile['python'])
