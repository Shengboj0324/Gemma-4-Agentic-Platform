"""Stage a corpus from R2 onto a working volume and prove its identity.

This is the only supported way to put training data on a Pod: the bucket holds
the data, the volume holds a verified ephemeral copy. The declared corpus
manifest digest, content identity and admission status must all match before the
restored tree is reported as usable, and `--purpose training` additionally
requires the loader to reach training admission.

The artifact manifest must be authenticated out of band; a digest in a file is
not authentication.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json, validate_manifest
from zenithsync.corpus_transport import restore_corpus
from zenithsync.object_store import ArtifactStore
from zenithsync.r2_client import build_client

SOURCES = ['scripts/stage_corpus_from_r2.py', 'zenithsync/corpus_transport.py',
           'zenithsync/r2_client.py', 'zenithsync/object_store.py',
           'zenithsync/training_corpus.py', 'zenithsync/artifacts.py',
           'zenithsync/contracts.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-manifest', type=Path, required=True)
    parser.add_argument('--artifact-manifest-sha256', required=True,
                        help='Independently trusted digest of the artifact manifest file')
    parser.add_argument('--destination', type=Path, required=True,
                        help='New directory for the staged corpus; must not exist')
    parser.add_argument('--corpus-sha256', required=True)
    parser.add_argument('--content-sha256', required=True)
    parser.add_argument('--expected-status', choices=['quarantine', 'admitted'],
                        required=True)
    parser.add_argument('--purpose', choices=['inspection', 'training'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prefix', default='quarantine/v1')
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--max-restore-bytes', type=int, required=True)
    parser.add_argument('--max-bytes', type=int, default=1024**3)
    parser.add_argument('--max-example-bytes', type=int, default=16 * 1024**2)
    args = parser.parse_args()
    manifest_identity = file_record(args.artifact_manifest)
    if manifest_identity['sha256'] != args.artifact_manifest_sha256:
        raise ValueError('Artifact manifest file identity differs from the trusted digest')
    manifest = validate_manifest(load_json(args.artifact_manifest))
    args.output.mkdir(parents=True, exist_ok=False)
    sources = {name: file_record(ROOT / name) for name in SOURCES}
    client, bucket, connection = build_client(env_file=args.env_file)
    store = ArtifactStore(client, bucket, prefix=args.prefix)
    result = restore_corpus(store, manifest, args.destination,
                            expected_corpus_manifest_sha256=args.corpus_sha256,
                            expected_content_sha256=args.content_sha256,
                            expected_status=args.expected_status, purpose=args.purpose,
                            max_restore_bytes=args.max_restore_bytes,
                            max_total_bytes=args.max_bytes,
                            max_example_bytes=args.max_example_bytes)
    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during staging')
    if file_record(args.artifact_manifest) != manifest_identity:
        raise RuntimeError('Artifact manifest changed during staging')
    summary = result['summary']
    receipt = {'schema_version': 1, 'operation': 'stage_corpus',
               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'status': result['status'], 'connection': connection,
               'prefix': args.prefix, 'sources': sources,
               'artifact_manifest_file': manifest_identity,
               'root': result['root'], 'purpose': args.purpose,
               'restore': result['restore'], 'summary': summary,
               'corpus_manifest_sha256': args.corpus_sha256,
               'corpus_content_sha256': args.content_sha256,
               'expected_status': args.expected_status, 'scope': result['scope']}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'status': result['status'], 'root': result['root'], 'bucket': bucket,
           'restored_files': result['restore']['restored_files'],
           'verified_bytes': result['restore']['verified_bytes'],
           'examples': summary['examples'],
           'returned_examples': summary['returned_examples'],
           'input_tokens': summary['input_tokens'],
           'supervised_tokens': summary['supervised_tokens'],
           'training_admitted': summary['training_admitted']})


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Corpus staging failed ({type(error).__name__}); no passing receipt written.',
              file=sys.stderr)
        raise SystemExit(1)
