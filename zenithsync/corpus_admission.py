"""Immutable quarantine-to-admitted promotion bound to exact gate evidence.

Promotion never edits a corpus in place: it stages a complete new corpus tree,
copies the referenced example files and the supplied evidence documents, writes
one receipt per gate bound to the corpus content identity, and publishes the
result atomically only after the strict training loader accepts it.

This module verifies identity, coverage and binding. It does not and cannot
establish that a reviewer's conclusion is true, that rights were cleared, that
a split is uncontaminated or that the runtime will fit. Supplying evidence is a
reviewer's act; this code refuses to invent, summarise or weaken it.
"""

import os
from pathlib import Path
import shutil
import tempfile

from .artifacts import canonical_json, file_record, load_json, relative_path
from .contracts import digest
from .training_corpus import (GATES, SCHEMA_VERSION, IndexedCorpus,
                              corpus_content_identity, validate_task_alignment)

RECEIPT_MAX_BYTES = 1024**2
EVIDENCE_MAX_BYTES = 16 * 1024**2
MANIFEST_MAX_BYTES = 16 * 1024**2

# Keys under which an evidence document may declare the corpus manifest it was
# produced against. A document that names a different corpus is rejected rather
# than silently accepted as though it described this one.
CORPUS_BINDING_KEYS = ('corpus', 'corpus_manifest')


def build_gate_receipt(*, gate, corpus_content_sha256, evidence, reviewer, scope,
                       supporting_evidence=None):
    """Return the exact receipt body the training loader will re-validate.

    `evidence` holds the documents the loader itself re-reads and, for the task
    alignment gate, schema-validates. `supporting_evidence` holds documents that
    belong to the same review but do not satisfy that schema — coverage control
    reports, for example. They are copied into the bundle and bound by hash, and
    they are deliberately kept out of the list the loader validates rather than
    being reshaped to pass it.
    """
    if gate not in GATES:
        raise ValueError('Unknown admission gate: ' + str(gate))
    digest(corpus_content_sha256)
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('Each gate requires at least one evidence reference')
    seen = set()
    for reference in evidence:
        if not isinstance(reference, dict) or set(reference) != {'path', 'identity'}:
            raise ValueError('Exact evidence reference fields required')
        path = relative_path(reference['path'])
        if path in seen:
            raise ValueError('Duplicate evidence reference')
        seen.add(path)
        identity = reference['identity']
        if not isinstance(identity, dict) or set(identity) != {'sha256', 'size_bytes'}:
            raise ValueError('Exact evidence identity required')
        digest(identity['sha256'])
        if type(identity['size_bytes']) is not int or not 0 < identity['size_bytes'] <= EVIDENCE_MAX_BYTES:
            raise ValueError('Evidence size out of bounds')
    for name, value in (('reviewer', reviewer), ('scope', scope)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(name + ' must be a nonempty string')
    if supporting_evidence is None:
        supporting_evidence = []
    elif not isinstance(supporting_evidence, list):
        raise ValueError('Supporting evidence must be a list of references')
    for reference in supporting_evidence:
        if not isinstance(reference, dict) or set(reference) != {'path', 'identity'}:
            raise ValueError('Exact supporting evidence reference fields required')
        path = relative_path(reference['path'])
        if path in seen:
            raise ValueError('Duplicate evidence reference')
        seen.add(path)
        identity = reference['identity']
        if not isinstance(identity, dict) or set(identity) != {'sha256', 'size_bytes'}:
            raise ValueError('Exact supporting evidence identity required')
        digest(identity['sha256'])
        if type(identity['size_bytes']) is not int or not 0 < identity['size_bytes'] <= EVIDENCE_MAX_BYTES:
            raise ValueError('Supporting evidence size out of bounds')
    return {'schema_version': 1, 'gate': gate, 'status': 'passed',
            'corpus_content_sha256': corpus_content_sha256,
            'evidence': evidence, 'supporting_evidence': supporting_evidence,
            'reviewer': reviewer, 'scope': scope,
            'training_approved_by_this_receipt_alone': False}


def _evidence_document(path: Path, *, source_manifest_identity):
    """Load one evidence document and reject a mismatched corpus binding."""
    identity = file_record(path)
    if not 0 < identity['size_bytes'] <= EVIDENCE_MAX_BYTES:
        raise ValueError('Evidence document size out of bounds: ' + path.name)
    document = load_json(path)
    if file_record(path) != identity:
        raise ValueError('Evidence document changed while loading: ' + path.name)
    if not isinstance(document, dict):
        raise ValueError('Evidence document must be a JSON object: ' + path.name)
    declared = [document[key] for key in CORPUS_BINDING_KEYS if key in document]
    for value in declared:
        if (not isinstance(value, dict) or set(value) != {'sha256', 'size_bytes'}
                or value != source_manifest_identity):
            raise ValueError('Evidence document names a different corpus: ' + path.name)
    return document, identity


def _stage_examples(manifest, source_root: Path, staging: Path):
    """Copy every referenced token and audit file, verifying identity after copy."""
    for record in manifest['examples']:
        for key in ('tokens', 'audit'):
            reference = record[key]
            name = relative_path(reference['path'])
            origin = source_root / name
            expected = reference['identity']
            if file_record(origin) != expected:
                raise ValueError('Corpus example file identity differs: ' + name)
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                raise ValueError('Example files must not alias: ' + name)
            shutil.copyfile(origin, target)
            if file_record(target) != expected:
                raise ValueError('Staged example copy identity differs: ' + name)


def promote_corpus(*, source_root: Path, source_manifest_sha256, destination: Path,
                   gate_evidence, reviewer, supporting_evidence=None,
                   max_total_bytes=1024**3, max_example_bytes=16 * 1024**2):
    """Produce an admitted corpus from a quarantined one plus complete evidence.

    `gate_evidence` maps every gate in `GATES` to a nonempty list of evidence
    document paths outside the corpus tree. Each document is copied into the new
    corpus under `admission/<gate>/` so the loader can rehash it. The corpus
    content identity is preserved exactly, which is what lets a receipt bind it.

    Splits are preserved verbatim. Promotion deliberately cannot reassign a
    split: that would describe different data than the supplied split evidence.
    """
    if not isinstance(gate_evidence, dict) or set(gate_evidence) != set(GATES):
        raise ValueError('Evidence for exactly the four admission gates required')
    if supporting_evidence is None:
        supporting_evidence = {}
    if not isinstance(supporting_evidence, dict) or set(supporting_evidence) - set(GATES):
        raise ValueError('Supporting evidence must be keyed by admission gate')
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError('Nonempty reviewer identity required')
    for name, value in (('max_total_bytes', max_total_bytes),
                        ('max_example_bytes', max_example_bytes)):
        if type(value) is not int or value <= 0:
            raise ValueError(name + ' must be a positive integer')
    digest(source_manifest_sha256)
    if source_root.is_symlink() or not source_root.is_dir():
        raise ValueError('Corpus source root must be an ordinary directory')
    source_root = source_root.resolve(strict=True)
    if os.path.lexists(destination):
        raise FileExistsError('Admitted corpus destination already exists')
    parent = destination.parent.resolve(strict=True)
    if any(part.is_symlink() for part in [parent, *parent.parents]):
        raise ValueError('Symlinked destination ancestry rejected')
    destination = parent / destination.name

    source_manifest_path = source_root / 'corpus.json'
    source_manifest_identity = file_record(source_manifest_path)
    if (source_manifest_identity['sha256'] != source_manifest_sha256
            or source_manifest_identity['size_bytes'] > MANIFEST_MAX_BYTES):
        raise ValueError('Untrusted or oversized source corpus manifest')
    # Full strict validation of the quarantined corpus before anything is copied.
    quarantined = IndexedCorpus(
        source_root, source_manifest_path, expected_manifest_sha256=source_manifest_sha256,
        purpose='inspection', max_total_bytes=max_total_bytes,
        max_example_bytes=max_example_bytes)
    summary = quarantined.summary
    if summary['status'] != 'quarantine':
        raise ValueError('Only a quarantined corpus can be promoted')
    manifest = load_json(source_manifest_path)
    if manifest['schema_version'] != SCHEMA_VERSION:
        raise ValueError('Promotion requires the current corpus schema')
    if any(value is not None for value in manifest['admission'].values()):
        raise ValueError('Source corpus already carries an admission receipt')
    content_identity = summary['content_sha256']
    if content_identity != corpus_content_identity(manifest):
        raise ValueError('Corpus content identity disagrees with the loader')

    def resolve(gate, paths, *, required):
        if not isinstance(paths, list) or (required and not paths):
            raise ValueError('Gate requires at least one evidence document: ' + gate)
        resolved = []
        for entry in paths:
            path = Path(entry).resolve(strict=True)
            if path.is_relative_to(source_root):
                raise ValueError('Evidence must come from outside the corpus tree: ' + path.name)
            if any(existing == path for existing, _, _ in resolved):
                raise ValueError('Duplicate evidence document for gate ' + gate)
            document, identity = _evidence_document(
                path, source_manifest_identity=source_manifest_identity)
            resolved.append((path, document, identity))
        return resolved

    documents, supporting = {}, {}
    for gate in GATES:
        documents[gate] = resolve(gate, gate_evidence[gate], required=True)
        supporting[gate] = resolve(gate, supporting_evidence.get(gate, []), required=False)
        primary = {path for path, _, _ in documents[gate]}
        if any(path in primary for path, _, _ in supporting[gate]):
            raise ValueError('Document listed as both primary and supporting: ' + gate)
    # Reviewing the same task set is the only gate with a machine-checkable
    # coverage contract. Check it here so promotion fails before any file write.
    validate_task_alignment([document for _, document, _ in documents['task_alignment']],
                            manifest['examples'])

    with tempfile.TemporaryDirectory(prefix='.admit-', dir=parent) as temporary:
        staging = Path(temporary) / 'corpus'
        staging.mkdir(mode=0o700)
        _stage_examples(manifest, source_root, staging)
        admission = {}
        copied = {}
        for gate in GATES:
            directory = staging / 'admission' / gate
            directory.mkdir(parents=True, exist_ok=False)

            def stage(rows, prefix):
                references = []
                if prefix:
                    (directory / prefix).mkdir(exist_ok=False)
                for index, (path, _, identity) in enumerate(rows):
                    name = f'admission/{gate}/{prefix}{index:03d}-{path.name}'
                    relative_path(name)
                    target = staging / name
                    if target.exists() or target.is_symlink():
                        raise ValueError('Evidence copies must not alias: ' + name)
                    shutil.copyfile(path, target)
                    if file_record(target) != identity:
                        raise ValueError('Staged evidence copy identity differs: ' + name)
                    references.append({'path': name, 'identity': identity})
                    copied[str(path)] = identity
                return references

            references = stage(documents[gate], '')
            support = stage(supporting[gate], 'support/')
            receipt = build_gate_receipt(
                gate=gate, corpus_content_sha256=content_identity, evidence=references,
                supporting_evidence=support, reviewer=reviewer,
                scope='Identity, coverage and corpus binding of the referenced evidence. '
                      'Not proof that the review conclusion is correct.')
            payload = canonical_json(receipt)
            if len(payload) > RECEIPT_MAX_BYTES:
                raise ValueError('Gate receipt exceeds its byte ceiling: ' + gate)
            receipt_name = f'admission/{gate}/receipt.json'
            (staging / receipt_name).write_bytes(payload)
            admission[gate] = {'path': receipt_name,
                               'identity': file_record(staging / receipt_name)}
        promoted = {'schema_version': SCHEMA_VERSION, 'status': 'admitted',
                    'tokenizer_assets': manifest['tokenizer_assets'],
                    'max_length': manifest['max_length'],
                    'examples': manifest['examples'], 'admission': admission}
        if corpus_content_identity(promoted) != content_identity:
            raise ValueError('Promotion changed the corpus content identity')
        staged_manifest = staging / 'corpus.json'
        staged_manifest.write_bytes(canonical_json(promoted))
        promoted_identity = file_record(staged_manifest)
        # The strict training loader is the acceptance authority, not this module.
        admitted = IndexedCorpus(
            staging, staged_manifest, expected_manifest_sha256=promoted_identity['sha256'],
            purpose='training', max_total_bytes=max_total_bytes,
            max_example_bytes=max_example_bytes)
        admitted_summary = admitted.summary
        if not admitted_summary['training_admitted']:
            raise ValueError('Promoted corpus did not reach training admission')
        for key in ('content_sha256', 'examples', 'input_tokens', 'supervised_tokens'):
            if key == 'content_sha256':
                if admitted_summary[key] != content_identity:
                    raise ValueError('Admitted content identity differs')
            elif admitted_summary[key] != summary[key]:
                raise ValueError('Admitted corpus accounting differs: ' + key)
        if file_record(source_manifest_path) != source_manifest_identity:
            raise ValueError('Source corpus manifest changed during promotion')
        if any(file_record(Path(path)) != identity for path, identity in copied.items()):
            raise ValueError('Evidence documents changed during promotion')
        if os.path.lexists(destination):
            raise FileExistsError('Destination appeared during promotion')
        staging.rename(destination)
    # Re-validate the published tree; this is a point-in-time check, not a lock.
    final = IndexedCorpus(destination, destination / 'corpus.json',
                          expected_manifest_sha256=promoted_identity['sha256'],
                          purpose='training', max_total_bytes=max_total_bytes,
                          max_example_bytes=max_example_bytes)
    if final.summary != admitted_summary:
        raise ValueError('Published corpus summary differs from the staged result')
    return {'schema_version': 1, 'status': 'corpus_admitted',
            'source': {'root': str(source_root), 'manifest': source_manifest_identity,
                       'status': 'quarantine'},
            'destination': {'root': str(destination), 'manifest': promoted_identity,
                            'status': 'admitted'},
            'corpus_content_sha256': content_identity,
            'reviewer': reviewer,
            'gates': {gate: admission[gate] for gate in GATES},
            'evidence_documents': {gate: [{'source': str(path), 'identity': identity}
                                          for path, _, identity in documents[gate]]
                                   for gate in GATES},
            'supporting_documents': {gate: [{'source': str(path), 'identity': identity}
                                            for path, _, identity in supporting[gate]]
                                     for gate in GATES},
            'summary': admitted_summary,
            'splits_preserved': True,
            'scope': 'Four bound gate receipts and a loader-accepted admitted corpus. '
                     'No held-out performance, rights clearance or GPU capacity claim.'}
