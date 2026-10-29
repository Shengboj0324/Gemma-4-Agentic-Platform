"""Restore a random sample of shipped packages from R2 and byte-verify each one.

Listing objects proves presence. It does not prove a package is *usable*: that
its manifest is readable, that every blob it names is fetchable, and that the
restored tree matches the manifest exactly. This samples published manifests,
restores each into a fresh directory and re-checks the file inventory, sizes and
digests, then discards the copy.

The sample is deterministic for a given seed and manifest listing, so a failing
audit can be repeated. A pass is evidence about the sampled packages only — it
is not a statement about every object in the bucket, and it is not a durability
or access-control guarantee.

Nothing is written to the bucket and nothing local is modified.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, validate_manifest, verify
from zenithsync.object_store import ArtifactStore
from zenithsync.r2_client import build_client

SOURCES = ['scripts/audit_r2_shipment.py', 'zenithsync/object_store.py',
           'zenithsync/r2_client.py', 'zenithsync/artifacts.py',
           'zenithsync/contracts.py']


def list_manifests(client, bucket, prefix, *, max_keys):
    """List published manifest keys under a prefix.

    Listing is deliberately outside the bounded client's surface, so this reaches
    the underlying client directly and only for this read-only enumeration.
    """
    keys, token = [], None
    while True:
        arguments = {'Bucket': bucket, 'Prefix': prefix.rstrip('/') + '/manifests/sha256/',
                     'MaxKeys': 1000}
        if token:
            arguments['ContinuationToken'] = token
        page = client._client.list_objects_v2(**arguments)
        for row in page.get('Contents', []):
            keys.append(row['Key'])
            if len(keys) > max_keys:
                raise ValueError('Manifest listing exceeds the explicit ceiling')
        if not page.get('IsTruncated'):
            return sorted(keys)
        token = page['NextContinuationToken']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prefix', default='artifacts/v1')
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--sample', type=int, default=20,
                        help='How many published manifests to restore and verify')
    parser.add_argument('--seed', type=int, default=7401,
                        help='Makes the sample reproducible')
    parser.add_argument('--max-package-bytes', type=int, default=64 * 1024**2,
                        help='Skip a sampled package larger than this, and say so')
    parser.add_argument('--max-manifests', type=int, default=200000)
    args = parser.parse_args()
    if args.sample <= 0:
        parser.error('--sample must be a positive integer')
    if args.seed < 0:
        parser.error('--seed must be a nonnegative integer')
    if args.max_package_bytes <= 0:
        parser.error('--max-package-bytes must be a positive integer')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')
    sources = {name: file_record(ROOT / name) for name in SOURCES}

    client, bucket, connection = build_client(env_file=args.env_file)
    store = ArtifactStore(client, bucket, prefix=args.prefix)
    keys = list_manifests(client, bucket, args.prefix, max_keys=args.max_manifests)
    if not keys:
        raise ValueError('No published manifests under ' + args.prefix)
    chosen = sorted(random.Random(args.seed).sample(keys, min(args.sample, len(keys))))

    verified, skipped = [], []
    files = byte_total = 0
    for key in chosen:
        body = client.get_object(Bucket=bucket, Key=key)['Body']
        try:
            manifest = validate_manifest(json.loads(body.read()))
        finally:
            body.close()
        declared = sum(row['size_bytes'] for row in manifest['files'])
        label = manifest['source']
        if declared > args.max_package_bytes:
            skipped.append({'manifest_key': key, 'source': label,
                            'declared_bytes': declared,
                            'reason': 'exceeds_sample_package_ceiling'})
            continue
        with tempfile.TemporaryDirectory(prefix='r2-audit-') as temporary:
            destination = Path(temporary) / 'package'
            result = store.restore(manifest, destination,
                                   max_bytes=2 * args.max_package_bytes)
            # The object store verifies during restore; re-check independently.
            verify(destination, manifest)
            verified.append({'manifest_key': key, 'source': label,
                             'revision': manifest['revision'],
                             'files': result['restored_files'],
                             'bytes': result['verified_bytes']})
            files += result['restored_files']
            byte_total += result['verified_bytes']

    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during the audit')
    args.output.mkdir(parents=True, exist_ok=False)
    receipt = {'schema_version': 1, 'status': 'r2_shipment_sample_verified',
               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'sources': sources, 'connection': connection, 'prefix': args.prefix,
               'published_manifests': len(keys), 'requested_sample': args.sample,
               'seed': args.seed, 'verified_packages': len(verified),
               'skipped_packages': len(skipped),
               'restored_files': files, 'verified_bytes': byte_total,
               'verified': verified, 'skipped': skipped,
               'scope': 'Restoration and byte verification of the sampled packages '
                        'only. Not a statement about every object in the bucket, '
                        'and not a durability or access-control guarantee.'}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'status': receipt['status'], 'published_manifests': len(keys),
           'verified_packages': len(verified), 'skipped_packages': len(skipped),
           'restored_files': files, 'verified_bytes': byte_total})
    raise SystemExit(0 if verified else 1)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'R2 shipment audit failed ({type(error).__name__}: {error}); '
              'no receipt written.', file=sys.stderr)
        raise SystemExit(1)
