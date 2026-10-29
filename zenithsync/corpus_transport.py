"""Corpus-aware R2 transport: publish and restore a complete corpus bundle.

The object store moves arbitrary content-addressed bundles. This layer adds the
corpus invariants that matter when the bucket is the only durable home for the
data: the published object set is exactly the corpus and nothing else, and a
restored tree is provably the same corpus — same manifest digest, same content
identity, same admission status — before any caller may train on it.

`store` is an injected `ArtifactStore`. This module performs no credential
handling, no bucket creation and no deletion.
"""

from pathlib import Path
import shutil

from .artifacts import file_record, inventory, load_json, relative_path, validate_manifest
from .contracts import digest
from .training_corpus import GATES, IndexedCorpus

CORPUS_MANIFEST_NAME = 'corpus.json'
RECEIPT_MAX_BYTES = 1024**2


def corpus_file_paths(root: Path, manifest) -> set:
    """Return every relative path a corpus manifest reaches, including evidence.

    Reading admission receipts here is how the evidence files become part of the
    declared bundle; a receipt that cannot be read is a transport failure, not a
    silently smaller upload.
    """
    paths = {CORPUS_MANIFEST_NAME}
    for record in manifest['examples']:
        for key in ('tokens', 'audit'):
            paths.add(relative_path(record[key]['path']))
    admission = manifest['admission']
    if set(admission) - set(GATES):
        raise ValueError('Unknown admission gate in corpus manifest')
    for gate, reference in admission.items():
        if reference is None:
            continue
        name = relative_path(reference['path'])
        paths.add(name)
        path = root / name
        if file_record(path) != reference['identity']:
            raise ValueError('Admission receipt identity differs: ' + gate)
        if reference['identity']['size_bytes'] > RECEIPT_MAX_BYTES:
            raise ValueError('Admission receipt exceeds its byte ceiling: ' + gate)
        receipt = load_json(path)
        if not isinstance(receipt, dict) or not isinstance(receipt.get('evidence'), list):
            raise ValueError('Admission receipt has no evidence list: ' + gate)
        supporting = receipt.get('supporting_evidence', [])
        if not isinstance(supporting, list):
            raise ValueError('Invalid supporting evidence list in gate ' + gate)
        for evidence in [*receipt['evidence'], *supporting]:
            if not isinstance(evidence, dict) or set(evidence) != {'path', 'identity'}:
                raise ValueError('Invalid evidence reference in gate ' + gate)
            paths.add(relative_path(evidence['path']))
    return paths


def _validated(root: Path, *, corpus_manifest_sha256, purpose, max_total_bytes,
               max_example_bytes):
    digest(corpus_manifest_sha256)
    manifest_path = root / CORPUS_MANIFEST_NAME
    corpus = IndexedCorpus(root, manifest_path,
                           expected_manifest_sha256=corpus_manifest_sha256,
                           purpose=purpose, max_total_bytes=max_total_bytes,
                           max_example_bytes=max_example_bytes)
    return corpus, load_json(manifest_path)


def publish_corpus(store, root: Path, *, corpus_manifest_sha256, source, revision,
                   expected_status=None, max_total_bytes=1024**3,
                   max_example_bytes=16 * 1024**2):
    """Validate a corpus tree, then publish exactly its own files.

    The inventory is compared against the paths the corpus manifest reaches. An
    extra file in the tree fails the publish rather than being uploaded, so a
    stray credential, cache or scratch file cannot ride along into the bucket.
    """
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Corpus root must be an ordinary directory')
    root = root.resolve(strict=True)
    corpus, manifest = _validated(root, corpus_manifest_sha256=corpus_manifest_sha256,
                                  purpose='inspection', max_total_bytes=max_total_bytes,
                                  max_example_bytes=max_example_bytes)
    summary = corpus.summary
    if expected_status is not None and summary['status'] != expected_status:
        raise ValueError('Corpus status differs from the declared publication status')
    declared = corpus_file_paths(root, manifest)
    artifact = inventory(root, kind='candidate', source=source, revision=revision)
    present = {record['path'] for record in artifact['files']}
    if present != declared:
        extra = sorted(present - declared)
        missing = sorted(declared - present)
        raise ValueError(f'Corpus tree differs from its manifest: extra={extra}, '
                         f'missing={missing}')
    result = store.publish(root, artifact)
    if file_record(root / CORPUS_MANIFEST_NAME)['sha256'] != corpus_manifest_sha256:
        raise ValueError('Corpus manifest changed during publication')
    return {'schema_version': 1, 'status': 'corpus_published',
            'artifact_manifest': artifact, 'publish': result,
            'corpus_manifest_sha256': corpus_manifest_sha256,
            'corpus_content_sha256': summary['content_sha256'],
            'corpus_status': summary['status'], 'file_count': len(artifact['files']),
            'summary': summary,
            'scope': 'Content-addressed publication and readback of exactly this corpus. '
                     'Not a durability, replication or access-control guarantee.'}


def restore_corpus(store, artifact_manifest, destination: Path, *,
                   expected_corpus_manifest_sha256, expected_content_sha256,
                   expected_status, purpose='training', max_restore_bytes,
                   max_total_bytes=1024**3, max_example_bytes=16 * 1024**2):
    """Restore a corpus bundle and prove it is the expected corpus before use.

    The caller must authenticate the artifact manifest separately; a digest in a
    local file is not authentication. Restoration leaves nothing behind on
    failure: the object store promotes only a byte-verified tree, and a tree that
    then fails any corpus check is removed before the error propagates, so a
    retry is not blocked by a rejected destination.
    """
    validate_manifest(artifact_manifest)
    digest(expected_corpus_manifest_sha256)
    digest(expected_content_sha256)
    if expected_status not in ('quarantine', 'admitted'):
        raise ValueError('Declared corpus status must be quarantine or admitted')
    if purpose == 'training' and expected_status != 'admitted':
        raise ValueError('Training restoration requires a declared admitted corpus')
    declared = {record['path'] for record in artifact_manifest['files']}
    if CORPUS_MANIFEST_NAME not in declared:
        raise ValueError('Artifact manifest does not contain a corpus manifest')
    restored = store.restore(artifact_manifest, destination, max_bytes=max_restore_bytes)
    root = Path(restored['destination'])
    try:
        corpus, manifest = _validated(
            root, corpus_manifest_sha256=expected_corpus_manifest_sha256,
            purpose=purpose, max_total_bytes=max_total_bytes,
            max_example_bytes=max_example_bytes)
        summary = corpus.summary
        if summary['content_sha256'] != expected_content_sha256:
            raise ValueError('Restored corpus content identity differs')
        if summary['status'] != expected_status:
            raise ValueError('Restored corpus status differs from the declared status')
        if purpose == 'training' and not summary['training_admitted']:
            raise ValueError('Restored corpus is not training admitted')
        if corpus_file_paths(root, manifest) != declared:
            raise ValueError('Restored tree differs from the paths its corpus '
                             'manifest reaches')
    except BaseException:
        # The object store promotes the tree before these corpus checks run, so
        # a failure here would otherwise leave a rejected corpus at the
        # destination and block every retry with FileExistsError. Remove it, and
        # say so if that removal itself fails rather than masking either error.
        try:
            shutil.rmtree(root)
        except OSError as cleanup_error:
            raise RuntimeError(
                'Restored corpus failed validation and could not be removed from '
                + str(root) + '; remove it before retrying') from cleanup_error
        raise
    return {'schema_version': 1, 'status': 'corpus_restored', 'restore': restored,
            'root': str(root), 'corpus': corpus, 'summary': summary,
            'scope': 'Byte-identical restoration bound to the declared corpus identity '
                     'and status. Not evidence that the review conclusions are correct.'}
