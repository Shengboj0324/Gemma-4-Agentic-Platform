"""Fetch one artifact manifest out of R2 by its digest, and prove it is that one.

This closes a bootstrap gap. The bucket is the durable home for data, but every
command that reads from it — `stage_corpus_from_r2.py`,
`verify_r2_training_readiness.py` — needs the artifact manifest as a *local
file*, and manifests live under `evidence/`, which is deliberately not in Git. A
fresh clone, and a fresh Pod, therefore had no way to obtain the one file needed
to reach anything else. The manifests are in the bucket under
`{prefix}/manifests/sha256/{digest}.json`; this reads one out.

The digest is required, not optional, and is checked against the bytes received.
A manifest fetched without naming its digest would be whatever the bucket
currently serves, which is the opposite of what a content-addressed store is for.

Nothing is restored and nothing is written on failure. A manifest proves what a
bundle *should* be; it is not itself evidence that the bundle is present or
correct.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, validate_manifest
from zenithsync.contracts import digest
from zenithsync.r2_client import build_client

SOURCES = ['scripts/fetch_manifest_from_r2.py', 'zenithsync/r2_client.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']

EXIT_FETCHED = 0
EXIT_DIGEST_MISMATCH = 1
EXIT_BAD_ARGUMENTS = 2
EXIT_RUN_FAILED = 3

#: A manifest describes a bundle; it is never bundle-sized. 16 MiB is the same
#: ceiling the loader applies to a manifest it reads from disk.
MAX_MANIFEST_BYTES = 16 * 1024**2


def fetch(client, bucket, key, *, expected_sha256, max_bytes):
    """Return the manifest bytes, or raise if they are not the ones asked for."""
    response = client.get_object(Bucket=bucket, Key=key)
    body = response['Body']
    try:
        declared = response.get('ContentLength')
        if type(declared) is not int or declared < 1:
            raise ValueError('Remote manifest declares no usable length')
        if declared > max_bytes:
            raise ValueError(f'Remote manifest declares {declared} bytes, over '
                             f'the {max_bytes}-byte ceiling')
        payload = bytearray()
        while chunk := body.read(1024 * 1024):
            payload += chunk
            if len(payload) > declared:
                raise ValueError('Remote manifest stream exceeds declared size')
    finally:
        body.close()
    if len(payload) != declared:
        raise ValueError('Remote manifest is shorter than it declared')
    observed = hashlib.sha256(payload).hexdigest()
    if observed != expected_sha256:
        raise ValueError('Remote manifest digest differs from the expected one')
    return bytes(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-sha256', required=True,
                        help='The manifest to fetch. Required: a fetch without '
                             'it would accept whatever the bucket serves.')
    parser.add_argument('--output', type=Path, required=True,
                        help='New directory for the manifest and its receipt')
    parser.add_argument('--prefix', default='artifacts/v1')
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--max-manifest-bytes', type=int,
                        default=MAX_MANIFEST_BYTES)
    args = parser.parse_args()
    try:
        digest(args.manifest_sha256)
    except Exception:
        parser.error('--manifest-sha256 is not a sha256 digest')
    if args.max_manifest_bytes < 1:
        parser.error('--max-manifest-bytes must be positive')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')

    sources = {name: file_record(ROOT / name) for name in SOURCES}
    client, bucket, connection = build_client(env_file=args.env_file)
    key = f'{args.prefix}/manifests/sha256/{args.manifest_sha256}.json'

    args.output.mkdir(parents=True, exist_ok=False)
    try:
        payload = fetch(client, bucket, key,
                        expected_sha256=args.manifest_sha256,
                        max_bytes=args.max_manifest_bytes)
        # Byte-identical to what was published, so the digest keeps holding.
        path = args.output / 'artifact-manifest.json'
        path.write_bytes(payload)
        # validate_manifest takes the parsed document, not a path.
        manifest = validate_manifest(json.loads(payload.decode('utf-8')))
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during the fetch')
        receipt = {'schema_version': 1, 'status': 'manifest_fetched',
                   'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                   'sources': sources, 'connection': connection,
                   'prefix': args.prefix, 'key': key,
                   'manifest_sha256': args.manifest_sha256,
                   'manifest_file': file_record(path),
                   'declared_files': len(manifest['files']),
                   'declared_bytes': sum(row['size_bytes']
                                         for row in manifest['files']),
                   'training_approved': False,
                   'scope': 'One manifest, fetched by digest and verified '
                            'against it. Not a statement that the bundle it '
                            'describes is present in the bucket, complete or '
                            'correct — restore or readiness verification '
                            'establishes that.'}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    print({'status': receipt['status'], 'key': key,
           'manifest_sha256': args.manifest_sha256,
           'declared_files': receipt['declared_files'],
           'declared_bytes': receipt['declared_bytes']})


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Manifest fetch failed ({type(error).__name__}: {error}); '
              'no manifest written.', file=sys.stderr)
        raise SystemExit(EXIT_DIGEST_MISMATCH
                         if isinstance(error, ValueError) else EXIT_RUN_FAILED)
