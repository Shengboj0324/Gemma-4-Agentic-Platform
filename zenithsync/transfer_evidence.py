"""Retain transfer receipts outside the immutable artifacts they describe.

Use quiescent, owned directories. Receipt contents are audit evidence, not
cryptographic proof of a remote service; both local trees are verified here.
"""

from pathlib import Path

from .artifacts import canonical_json, file_record, load_json, verify


def record_transfer_verification(*, original: Path, restored: Path,
                                 manifest: Path, publish_receipt: Path,
                                 restore_receipt: Path, output: Path) -> dict:
    """Verify both trees and retain metadata in a fresh, disjoint directory."""
    roots = [original.resolve(strict=True), restored.resolve(strict=True)]
    if roots[0].is_relative_to(roots[1]) or roots[1].is_relative_to(roots[0]):
        raise ValueError('Original and restored artifacts must be disjoint trees')
    destination = output.resolve()
    for root in roots:
        if destination.is_relative_to(root) or root.is_relative_to(destination):
            raise ValueError('Verification output must be disjoint from artifact trees')
    sources = {'manifest.json': manifest, 'publish-receipt.json': publish_receipt,
               'restore-receipt.json': restore_receipt}
    if any(path.resolve(strict=True).is_relative_to(destination) for path in sources.values()):
        raise ValueError('Verification output overlaps an input file')
    identities = {name: file_record(path) for name, path in sources.items()}
    inventory = load_json(manifest)
    for operation, path in [('publish', publish_receipt), ('restore', restore_receipt)]:
        receipt = load_json(path)
        if (not isinstance(receipt, dict) or receipt.get('status') != 'verified'
                or receipt.get('operation') != operation
                or receipt.get('manifest_file') != identities['manifest.json']):
            raise ValueError('Transfer receipt does not bind the expected manifest and operation')
    for root in roots:
        verify(root, inventory)
    # Retain exact bytes; never rename a receipt into an artifact member.
    payloads = {name: path.read_bytes() for name, path in sources.items()}
    if identities != {name: file_record(path) for name, path in sources.items()}:
        raise ValueError('Transfer metadata changed during verification')
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        with (output / name).open('xb') as stream:
            stream.write(data)
        if file_record(output / name) != identities[name]:
            raise ValueError('Retained transfer metadata differs from source')
    for root in roots:
        verify(root, inventory)
    report = {'schema_version': 1, 'status': 'verified',
              'manifest': identities['manifest.json'], 'receipts': identities,
              'verified_files_per_tree': len(inventory['files']),
              'artifact_trees_modified': False, 'training_approved': False}
    with (output / 'verification.json').open('xb') as stream:
        stream.write(canonical_json(report))
    return report
