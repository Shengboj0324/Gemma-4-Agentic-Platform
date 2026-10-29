"""Prove from the bucket alone that a training run has everything it needs.

This is the end-to-end integration check. It reads nothing local except the
artifact manifest it is given and the credentials, then:

1. restores the admitted corpus from R2 into a fresh directory and requires the
   declared manifest digest, content identity and admission status to match;
2. runs the independent second audit layer and requires it to agree with the
   training loader on every shared quantity;
3. requires the loader to offer exactly the audited training set, checks each
   row's split, and re-hashes every fetched token array — via
   `corpus_audit.verify_loader_offers`, because comparing each example only
   against its own audit row passes a held-out example substituted one-for-one
   into the training set;
4. fetches each tokenizer asset the corpus manifest binds, by content digest,
   and verifies its bytes — without these the corpus is untrainable;
5. when given a model manifest, confirms every one of its files is present in
   the bucket at the declared size, by metadata rather than by download: the
   quantized checkpoint is over 21 GiB and is not held on the development
   machine, so presence in the bucket is what makes a run possible at all;
6. regenerates the exposure schedule and requires it to reproduce the declared
   schedule digest exactly;
7. runs the real worker's own `preflight_corpus_run` against the restored tree.

A model-manifest check confirms the bytes are *addressable*, by their declared
size and key. It does not re-hash 21 GiB, so it is presence and size evidence,
not a fresh integrity proof of the checkpoint.

A pass means the data path is complete and self-consistent from the bucket. It
is not a claim that rights are cleared, that the host can run the job, that the
model will fit, or that training will improve anything. Those are separate and
are not checked here.

No GPU is touched, no model is loaded, and no cloud compute is allocated.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json, validate_manifest
from zenithsync.corpus_audit import (audit_corpus, compare_with_loader,
                                     verify_loader_offers, verify_schedule_coverage)
from zenithsync.corpus_run import preflight_corpus_run
from zenithsync.corpus_transport import restore_corpus
from zenithsync.object_store import ArtifactStore
from zenithsync.r2_client import build_client
from zenithsync.training_schedule import make_schedule

SOURCES = ['scripts/verify_r2_training_readiness.py', 'zenithsync/corpus_transport.py',
           'zenithsync/corpus_audit.py', 'zenithsync/corpus_run.py',
           'zenithsync/training_corpus.py', 'zenithsync/training_schedule.py',
           'zenithsync/r2_client.py', 'zenithsync/object_store.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']


def fetch_blob(client, bucket, store, identity, *, max_bytes):
    """Stream one content-addressed blob and verify its digest and size."""
    if identity['size_bytes'] > max_bytes:
        raise ValueError('Blob exceeds the declared fetch ceiling')
    response = client.get_object(Bucket=bucket, Key=store.blob_key(identity['sha256']))
    body = response['Body']
    hasher, size = hashlib.sha256(), 0
    try:
        while chunk := body.read(1024 * 1024):
            size += len(chunk)
            if size > identity['size_bytes']:
                raise ValueError('Remote blob exceeds its declared size')
            hasher.update(chunk)
    finally:
        body.close()
    if size != identity['size_bytes'] or hasher.hexdigest() != identity['sha256']:
        raise ValueError('Remote blob digest or size differs')
    return {'sha256': hasher.hexdigest(), 'size_bytes': size}


def check_blob_present(client, bucket, store, identity):
    """Confirm a blob exists at its declared size without downloading it.

    Used for the quantized checkpoint, which is far too large to re-hash on
    every readiness check. ETags are never treated as digests.
    """
    response = client.head_object(Bucket=bucket,
                                  Key=store.blob_key(identity['sha256']))
    length = response.get('ContentLength')
    if length != identity['size_bytes']:
        raise ValueError('Remote blob length differs from the manifest: '
                         + identity['sha256'])
    return {'sha256': identity['sha256'], 'size_bytes': length,
            'verified_by': 'remote_metadata_only'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-manifest', type=Path, required=True)
    parser.add_argument('--model-manifest', type=Path,
                        help='Model manifest whose files must be present in R2')
    parser.add_argument('--corpus-sha256', required=True)
    parser.add_argument('--content-sha256', required=True)
    parser.add_argument('--worker-config', type=Path, required=True,
                        help='The config the worker will be given')
    parser.add_argument('--schedule-seed', type=int, required=True)
    parser.add_argument('--schedule-sha256', required=True,
                        help='Expected digest of the regenerated schedule')
    parser.add_argument('--max-epochs', type=int, default=1)
    parser.add_argument('--target-supervised-tokens', type=int,
                        help='Defaults to one full pass over the training split')
    parser.add_argument('--max-update-supervised-tokens', type=int, default=32768)
    parser.add_argument('--context-limit', type=int, default=32768)
    parser.add_argument('--output-reserve', type=int, default=8192)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prefix', default='artifacts/v1')
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--max-restore-bytes', type=int, default=1024**3)
    parser.add_argument('--max-asset-bytes', type=int, default=256 * 1024**2)
    parser.add_argument('--max-corpus-manifest-bytes', type=int,
                        default=16 * 1024**2,
                        help='Byte ceiling for the restored corpus manifest, '
                             'matching what the audit layer enforces')
    parser.add_argument('--keep', type=Path,
                        help='Keep the restored tree here instead of discarding it')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sources = {name: file_record(ROOT / name) for name in SOURCES}
    manifest_identity = file_record(args.artifact_manifest)
    manifest = validate_manifest(load_json(args.artifact_manifest))
    config_identity = file_record(args.worker_config)

    client, bucket, connection = build_client(env_file=args.env_file)
    store = ArtifactStore(client, bucket, prefix=args.prefix)

    holder = tempfile.TemporaryDirectory(prefix='r2-readiness-')
    try:
        destination = (args.keep if args.keep is not None
                       else Path(holder.name) / 'corpus')
        restored = restore_corpus(
            store, manifest, destination,
            expected_corpus_manifest_sha256=args.corpus_sha256,
            expected_content_sha256=args.content_sha256,
            expected_status='admitted', purpose='training',
            max_restore_bytes=args.max_restore_bytes)
        root = Path(restored['root'])
        corpus = restored['corpus']
        summary = corpus.summary

        audit = audit_corpus(root, expected_manifest_sha256=args.corpus_sha256,
                             expected_content_sha256=args.content_sha256,
                             expected_status='admitted',
                             context_limit=args.context_limit,
                             output_reserve=args.output_reserve)
        agreement = compare_with_loader(audit, summary)

        refetched = verify_loader_offers(audit, corpus, purpose='training')

        # Without the exact tokenizer assets the corpus binds, it cannot train.
        manifest_path = root / 'corpus.json'
        if file_record(manifest_path)['size_bytes'] > args.max_corpus_manifest_bytes:
            raise ValueError('Corpus manifest exceeds the explicit byte ceiling')
        assets = load_json(manifest_path)['tokenizer_assets']
        # fetch_blob already raises unless the streamed bytes match this exact
        # digest and size, so comparing its return to `identity` is not a check.
        fetched = {name: fetch_blob(client, bucket, store, identity,
                                    max_bytes=args.max_asset_bytes)
                   for name, identity in sorted(assets.items())}

        model = None
        if args.model_manifest is not None:
            model_manifest = validate_manifest(load_json(args.model_manifest))
            present = {}
            for record in model_manifest['files']:
                identity = {key: record[key] for key in ('sha256', 'size_bytes')}
                present[record['path']] = check_blob_present(
                    client, bucket, store, identity)
            # The corpus binds three of these by digest; they must be the same
            # files, or the corpus was tokenized with a different tokenizer.
            model_files = {record['path']: {key: record[key] for key in
                                            ('sha256', 'size_bytes')}
                           for record in model_manifest['files']}
            for name, identity in sorted(assets.items()):
                if model_files.get(name) != identity:
                    raise ValueError('Corpus tokenizer asset differs from the model '
                                     'manifest: ' + name)
            model = {'manifest_file': file_record(args.model_manifest),
                     'source': model_manifest['source'],
                     'revision': model_manifest['revision'],
                     'files': len(model_manifest['files']),
                     'declared_bytes': sum(record['size_bytes'] for record
                                           in model_manifest['files']),
                     'present_in_bucket': present,
                     'tokenizer_assets_match_corpus': True,
                     'limitation': 'Presence and declared size from remote '
                                   'metadata. The checkpoint was not re-hashed.'}

        rows = [{key: row[key] for key in ('example_id', 'input_tokens',
                                           'supervised_tokens')}
                for row in audit['examples_detail'] if row['split'] == 'train']
        # An explicit 0 is a mistake, not a request for the default.
        if args.target_supervised_tokens is not None:
            if args.target_supervised_tokens <= 0:
                raise ValueError('--target-supervised-tokens must be positive')
            target = args.target_supervised_tokens
        else:
            target = sum(row['supervised_tokens'] for row in rows)
        schedule = make_schedule(
            rows, corpus_content_sha256=audit['corpus_content_sha256'],
            seed=args.schedule_seed, target_supervised_tokens=target,
            max_epochs=args.max_epochs,
            max_update_supervised_tokens=args.max_update_supervised_tokens)
        if schedule['schedule_sha256'] != args.schedule_sha256:
            raise ValueError('Regenerated schedule digest differs from the expected '
                             'value: ' + schedule['schedule_sha256'])
        coverage = verify_schedule_coverage(audit, schedule)

        # The worker preflight needs the schedule on disk. Write it outside
        # --output until the run succeeds, so a failed run leaves no file there
        # that looks like a product.
        pending = Path(holder.name) / 'schedule.json'
        pending.write_bytes(canonical_json(schedule))
        preflight_corpus_run(
            corpus_root=root, corpus_sha256=args.corpus_sha256,
            schedule_path=pending,
            schedule_sha256=file_record(pending)['sha256'],
            config_path=args.worker_config, config_sha256=config_identity['sha256'])
        schedule_path = args.output / 'schedule.json'
        schedule_path.write_bytes(canonical_json(schedule))

        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during verification')
        receipt = {
            'schema_version': 1, 'status': 'r2_training_readiness_verified',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'sources': sources, 'connection': connection, 'prefix': args.prefix,
            'artifact_manifest_file': manifest_identity,
            'worker_config': config_identity,
            'restore': restored['restore'],
            'loader_summary': summary,
            'independent_audit': {key: value for key, value in audit.items()
                                  if key != 'examples_detail'},
            'agreement': agreement,
            'examples_refetched_and_rechecked': refetched,
            'tokenizer_assets_fetched_from_r2': fetched,
            'model': model,
            'schedule': {'seed': args.schedule_seed,
                         'schedule_sha256': schedule['schedule_sha256'],
                         'target_supervised_tokens': target,
                         'max_epochs': args.max_epochs,
                         'max_update_supervised_tokens':
                             args.max_update_supervised_tokens,
                         'schedule_file': file_record(schedule_path)},
            'context_policy': {'context_limit': args.context_limit,
                               'output_reserve': args.output_reserve},
            'byte_policy': {'max_restore_bytes': args.max_restore_bytes,
                            'max_asset_bytes': args.max_asset_bytes,
                            'max_corpus_manifest_bytes':
                                args.max_corpus_manifest_bytes},
            'schedule_coverage': coverage,
            'worker_preflight_passed': True,
            'restored_tree_retained': args.keep is not None,
            'training_started': False, 'gpu_used': False,
            'scope': 'The data path is complete and self-consistent from the bucket. '
                     'Not rights clearance, not host capability, not model fit, and '
                     'not any claim about learned performance.'}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
        print({'status': receipt['status'],
               'restored_files': restored['restore']['restored_files'],
               'verified_bytes': restored['restore']['verified_bytes'],
               'examples': audit['examples'],
               'input_tokens': audit['input_tokens'],
               'supervised_tokens': audit['supervised_tokens'],
               'min_context_margin': audit['min_context_margin'],
               'refetched': refetched,
               'loader_agreement': agreement['agreed'],
               'tokenizer_assets': sorted(fetched),
               'model_files_in_bucket': model and model['files'],
               'model_declared_bytes': model and model['declared_bytes'],
               'schedule_sha256': schedule['schedule_sha256'],
               'schedule_coverage_exact': coverage['coverage_exact'],
               'worker_preflight_passed': True})
    finally:
        # Without --keep the restored tree lives inside the temporary directory,
        # so cleaning that up removes it whether this run passed or failed.
        holder.cleanup()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'R2 training readiness failed ({type(error).__name__}); '
              'no passing receipt written.', file=sys.stderr)
        raise SystemExit(1)
