"""Publish a complete corpus tree to R2 and retain its artifact manifest.

The published object set is exactly the files the corpus manifest reaches. An
extra file in the tree fails the publish instead of being uploaded. The artifact
manifest written here is what a later restore must be given; keep it with the
receipt, not inside the corpus it describes.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync.corpus_transport import publish_corpus
from zenithsync.evidence_shipment import shipment_lock
from zenithsync.object_store import ArtifactStore
from zenithsync.r2_client import build_client

SOURCES = ['scripts/publish_corpus_to_r2.py', 'zenithsync/corpus_transport.py',
           'zenithsync/evidence_shipment.py',
           'zenithsync/r2_client.py', 'zenithsync/object_store.py',
           'zenithsync/training_corpus.py', 'zenithsync/splits.py',
           'zenithsync/training_batch.py', 'zenithsync/artifacts.py',
           'zenithsync/contracts.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--corpus-sha256', required=True)
    parser.add_argument('--source', required=True, help='Artifact manifest source label')
    parser.add_argument('--revision', required=True, help='Artifact manifest revision label')
    parser.add_argument('--expected-status', choices=['quarantine', 'admitted'],
                        required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prefix',
                        help='Bucket prefix; defaults to quarantine/v1 for a '
                             'quarantined corpus and artifacts/v1 for an admitted '
                             'one, since blobs are content-addressed under the '
                             'prefix and a wrong one re-uploads every object')
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--max-bytes', type=int, default=1024**3)
    parser.add_argument('--max-example-bytes', type=int, default=16 * 1024**2)
    args = parser.parse_args()
    if args.prefix is None:
        args.prefix = ('artifacts/v1' if args.expected_status == 'admitted'
                       else 'quarantine/v1')
    if args.max_bytes <= 0 or args.max_example_bytes <= 0:
        parser.error('Byte budgets must be positive integers')
    if not (args.corpus / 'corpus.json').is_file():
        parser.error('--corpus does not contain a readable corpus.json')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')
    args.output.mkdir(parents=True, exist_ok=False)
    sources = {name: file_record(ROOT / name) for name in SOURCES}
    client, bucket, connection = build_client(env_file=args.env_file)
    store = ArtifactStore(client, bucket, prefix=args.prefix)
    # One writer per prefix. Two publishers of the same content-addressed key
    # can make a readback race an in-flight overwrite, which the object store
    # reports as an integrity failure indistinguishable from a real one.
    with shipment_lock(bucket, args.prefix, label='publish_corpus_to_r2'):
        result = publish_corpus(store, args.corpus,
                                corpus_manifest_sha256=args.corpus_sha256,
                                source=args.source, revision=args.revision,
                                expected_status=args.expected_status,
                                max_total_bytes=args.max_bytes,
                                max_example_bytes=args.max_example_bytes)
    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during publication')
    (args.output / 'artifact-manifest.json').write_bytes(
        canonical_json(result['artifact_manifest']))
    receipt = {'schema_version': 1, 'operation': 'publish_corpus',
               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'status': result['status'], 'connection': connection,
               'prefix': args.prefix, 'sources': sources,
               'exclusive_lock_held': True,
               'artifact_manifest_file': file_record(args.output / 'artifact-manifest.json'),
               'corpus_manifest_sha256': result['corpus_manifest_sha256'],
               'corpus_content_sha256': result['corpus_content_sha256'],
               'corpus_status': result['corpus_status'],
               'file_count': result['file_count'], 'publish': result['publish'],
               'summary': result['summary'], 'scope': result['scope']}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'status': result['status'], 'bucket': bucket, 'prefix': args.prefix,
           'files': result['file_count'],
           'uploaded': result['publish']['uploaded_files'],
           'reused': result['publish']['reused_files'],
           'verified_bytes': result['publish']['verified_bytes'],
           'artifact_manifest_sha256': result['publish']['manifest_sha256'],
           'corpus_manifest_sha256': result['corpus_manifest_sha256'],
           'corpus_content_sha256': result['corpus_content_sha256']})


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Corpus publication failed ({type(error).__name__}); no passing receipt written.',
              file=sys.stderr)
        raise SystemExit(1)
