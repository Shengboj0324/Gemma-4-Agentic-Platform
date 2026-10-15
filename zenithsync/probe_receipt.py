"""Bind successful local container receipts to reconstructed probe bytes.

This checks consistency of retained local evidence, not cryptographic
attestation that an untrusted author actually ran a container.
"""
import hashlib
import re


def verify_probe_receipt(receipt, probe, *, image, platform, python, grading_tests=True):
    if (not isinstance(receipt, dict) or not isinstance(probe, str)
            or not isinstance(image, str)
            or re.fullmatch(r'sha256:[0-9a-f]{64}', image) is None
            or platform not in ('linux/amd64', 'linux/arm64')
            or not isinstance(python, str) or not python.startswith('/')
            or type(grading_tests) is not bool):
        raise ValueError('Explicit probe and runtime identities required')
    encoded = probe.encode('utf-8')
    expected = {'sha256': hashlib.sha256(encoded).hexdigest(), 'size_bytes': len(encoded)}
    if receipt.get('probe_source') != expected:
        raise ValueError('Executed probe identity differs from reconstructed source')
    if (receipt.get('image') != image or receipt.get('image_id') != image
            or receipt.get('platform') != platform or receipt.get('entrypoint') != python
            or receipt.get('generated_grading_tests_executed') is not grading_tests
            or receipt.get('agent_executed') is not False):
        raise ValueError('Grading runtime identity or execution scope differs')
    for key in ('returncode', 'copy_returncode', 'cleanup_returncode'):
        if type(receipt.get(key)) is not int or receipt[key] != 0:
            raise ValueError('Unsuccessful execution, export or cleanup')
    state = receipt.get('state')
    if (not isinstance(state, dict) or state.get('Status') != 'exited'
            or type(state.get('ExitCode')) is not int or state['ExitCode'] != 0
            or state.get('OOMKilled') is not False or state.get('Error') != ''):
        raise ValueError('Container did not exit cleanly')
    return expected
