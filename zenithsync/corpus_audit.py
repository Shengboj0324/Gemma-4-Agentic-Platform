"""Independent re-derivation of an admitted corpus from its raw bytes.

This is a deliberately separate second layer. It does not call the training
loader, the collator or the schedule iterator, and it does not trust any
summary those produce. Every count, digest and invariant below is recomputed
from the stored JSON, so a defect shared with the loader cannot hide behind the
loader's own agreement.

Agreement between the two layers is evidence of consistent accounting. It is not
evidence that the data is well chosen, the rights are cleared or the model will
learn anything.
"""

import hashlib
from pathlib import Path

from .artifacts import canonical_json, load_json
from .training_corpus import GATES

EXAMPLE_FIELDS = {'example_id', 'task_id', 'repository_group', 'leakage_group',
                  'split', 'tokens', 'audit'}
# Hard ceiling on any single file this audit will read into memory. A reference
# may declare an enormous size; refusing on the declaration is cheaper than
# discovering it after the read.
FILE_MAX_BYTES = 64 * 1024**2
SPLITS = ('train', 'development', 'confirmation')


class CorpusAuditError(ValueError):
    """An independent re-derivation disagrees with the stored corpus."""


def _require(condition, message):
    if not condition:
        raise CorpusAuditError(message)


def _sha256(path: Path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def _bound(root: Path, reference, label, *, max_bytes=FILE_MAX_BYTES):
    if (not isinstance(reference, dict) or set(reference) != {'path', 'identity'}
            or not isinstance(reference['identity'], dict)
            or set(reference['identity']) != {'sha256', 'size_bytes'}):
        raise CorpusAuditError('Malformed file reference: ' + label)
    declared = reference['identity']['size_bytes']
    _require(type(declared) is int and 0 < declared <= max_bytes,
             'Declared size out of bounds: ' + label)
    path = root / reference['path']
    _require(path.is_file() and not path.is_symlink(), 'Not a regular file: ' + label)
    _require(path.stat().st_size == declared, 'Size differs: ' + label)
    actual = {'sha256': _sha256(path), 'size_bytes': path.stat().st_size}
    _require(actual == reference['identity'], 'Identity differs: ' + label)
    return load_json(path)


def _supervised_targets(input_ids, labels):
    """Count next-token targets directly, independently of the collator."""
    _require(len(input_ids) == len(labels), 'Token and label lengths differ')
    _require(len(input_ids) >= 2, 'Example shorter than two tokens')
    _require(labels[0] == -100, 'First position carries a supervised label')
    count = 0
    for index, (token, label) in enumerate(zip(input_ids, labels)):
        _require(type(token) is int and token >= 0, 'Invalid input token')
        _require(label == -100 or label == token,
                 'Label neither the ignore index nor its own input token')
        if index > 0 and label != -100:
            count += 1
    _require(count > 0, 'Example has no supervised next-token target')
    return count


def audit_corpus(root: Path, *, expected_manifest_sha256, expected_content_sha256=None,
                 expected_status=None, context_limit=None, output_reserve=0):
    """Recompute a corpus's accounting, identities and invariants from disk."""
    root = Path(root).resolve(strict=True)
    manifest_path = root / 'corpus.json'
    manifest_identity = {'sha256': _sha256(manifest_path),
                         'size_bytes': manifest_path.stat().st_size}
    _require(manifest_identity['sha256'] == expected_manifest_sha256,
             'Corpus manifest digest differs from the expected value')
    manifest = load_json(manifest_path)
    _require(set(manifest) == {'schema_version', 'status', 'tokenizer_assets',
                               'max_length', 'examples', 'admission'},
             'Unexpected corpus manifest fields')
    _require(manifest['schema_version'] == 2, 'Audit supports corpus schema 2 only')
    status = manifest['status']
    _require(status in ('quarantine', 'admitted'), 'Invalid corpus status')
    if expected_status is not None:
        _require(status == expected_status, 'Corpus status differs from the expected value')
    max_length = manifest['max_length']
    _require(type(max_length) is int and max_length > 0, 'Invalid max_length')

    content = {key: manifest[key] for key in
               ('schema_version', 'tokenizer_assets', 'max_length', 'examples')}
    content_identity = hashlib.sha256(canonical_json(content)).hexdigest()
    if expected_content_sha256 is not None:
        _require(content_identity == expected_content_sha256,
                 'Recomputed content identity differs from the expected value')

    assets = manifest['tokenizer_assets']
    _require(set(assets) == {'chat_template.jinja', 'tokenizer.json',
                             'tokenizer_config.json'},
             'Unexpected tokenizer asset set')

    records = manifest['examples']
    _require(isinstance(records, list) and records, 'Corpus has no examples')
    rows = []
    seen_ids, seen_files, seen_inputs = set(), set(), {}
    task_splits, group_splits, leakage_splits = {}, {}, {}
    vocab = pad = None
    input_total = supervised_total = bytes_total = 0
    for record in records:
        _require(set(record) == EXAMPLE_FIELDS, 'Unexpected example fields')
        name = record['example_id']
        _require(name not in seen_ids, 'Duplicate example identity: ' + str(name))
        seen_ids.add(name)
        _require(record['split'] in SPLITS, 'Unknown split: ' + str(record['split']))
        for key in ('tokens', 'audit'):
            path = record[key]['path']
            _require(path not in seen_files, 'Example files alias: ' + path)
            seen_files.add(path)
            bytes_total += record[key]['identity']['size_bytes']
        candidate = _bound(root, record['tokens'], name + '/tokens')
        audit = _bound(root, record['audit'], name + '/audit')
        _require(candidate.get('training_approved') is False,
                 'Token candidate claims training approval: ' + name)
        _require(audit.get('truncated') is False, 'Audit does not deny truncation: ' + name)
        _require(audit.get('assets') == assets, 'Audit tokenizer assets differ: ' + name)
        _require(audit.get('token_candidate') == record['tokens']['identity'],
                 'Audit does not bind this token candidate: ' + name)
        for key in ('history', 'tools'):
            _require(candidate.get(key) == audit.get(key),
                     'Token and audit ' + key + ' lineage differ: ' + name)
        if vocab is None:
            vocab, pad = candidate.get('vocab_size'), candidate.get('pad_token_id')
        _require(candidate.get('vocab_size') == vocab and candidate.get('pad_token_id') == pad,
                 'Mixed vocabularies or padding identifiers: ' + name)
        _require(type(vocab) is int and vocab > 0, 'Invalid vocabulary size')
        _require(type(pad) is int and 0 <= pad < vocab, 'Invalid padding token')
        ids, labels = candidate['input_ids'], candidate['labels']
        _require(all(token < vocab for token in ids), 'Input token outside vocabulary: ' + name)
        supervised = _supervised_targets(ids, labels)
        _require(len(ids) <= max_length,
                 'Example exceeds the declared maximum length: ' + name)
        if context_limit is not None:
            _require(len(ids) + output_reserve <= context_limit,
                     'Example plus output reserve exceeds the context limit: ' + name)
        for field, value in (('input_tokens', len(ids)), ('supervised_tokens', supervised)):
            _require(audit.get(field) == value,
                     'Recomputed ' + field + ' differs from the audit: ' + name)
        digests = {'input_sha256': hashlib.sha256(canonical_json(ids)).hexdigest(),
                   'labels_sha256': hashlib.sha256(canonical_json(labels)).hexdigest()}
        for field, value in digests.items():
            _require(audit.get(field) == value,
                     'Recomputed ' + field + ' differs from the audit: ' + name)
        _require(digests['input_sha256'] not in seen_inputs,
                 'Duplicate token sequence shared with ' + str(seen_inputs.get(digests['input_sha256'])))
        seen_inputs[digests['input_sha256']] = name
        # Content, repository and reviewed duplicate families may not straddle splits.
        for mapping, key in ((task_splits, record['task_id'].casefold()),
                             (group_splits, record['repository_group'].casefold()),
                             (leakage_splits, record['leakage_group'])):
            if key in mapping:
                _require(mapping[key] == record['split'],
                         'Cross-split leakage on ' + str(key))
            mapping[key] = record['split']
        input_total += len(ids)
        supervised_total += supervised
        rows.append({'example_id': name, 'task_id': record['task_id'],
                     'repository_group': record['repository_group'],
                     'leakage_group': record['leakage_group'], 'split': record['split'],
                     'input_tokens': len(ids), 'supervised_tokens': supervised,
                     'input_sha256': digests['input_sha256']})

    admission = manifest['admission']
    _require(set(admission) == set(GATES), 'Admission gate map differs from the contract')
    gates = {}
    for gate in GATES:
        reference = admission[gate]
        if reference is None:
            _require(status == 'quarantine', 'Admitted corpus has an unresolved gate: ' + gate)
            gates[gate] = {'resolved': False}
            continue
        receipt = _bound(root, reference, 'admission/' + gate)
        _require(receipt.get('gate') == gate, 'Receipt names a different gate: ' + gate)
        _require(receipt.get('status') == 'passed', 'Receipt is not passed: ' + gate)
        _require(receipt.get('corpus_content_sha256') == content_identity,
                 'Receipt binds a different corpus content identity: ' + gate)
        primary = receipt.get('evidence')
        _require(isinstance(primary, list) and primary, 'Receipt has no evidence: ' + gate)
        support = receipt.get('supporting_evidence', [])
        _require(isinstance(support, list), 'Invalid supporting evidence list: ' + gate)
        documents = []
        for index, entry in enumerate(primary):
            documents.append(_bound(root, entry, f'admission/{gate}/evidence/{index}'))
        for index, entry in enumerate(support):
            _bound(root, entry, f'admission/{gate}/support/{index}')
        if gate == 'task_alignment':
            expected = {(row['task_id'], row['repository_group']) for row in rows}
            reviewed = set()
            for document in documents:
                _require(document.get('schema_version') == 1,
                         'Task alignment evidence is not version 1')
                reviews = document.get('task_reviews')
                _require(isinstance(reviews, list) and reviews,
                         'Task alignment evidence has no reviews')
                for review in reviews:
                    _require(set(review) == {'task_id', 'repository_group', 'decision',
                                             'rationale'},
                             'Unexpected task review fields')
                    _require(review['decision'] == 'accepted', 'Task review is not accepted')
                    _require(isinstance(review['rationale'], str) and review['rationale'].strip(),
                             'Task review has no rationale')
                    key = (review['task_id'], review['repository_group'])
                    _require(key in expected, 'Task review names a foreign task')
                    _require(key not in reviewed, 'Duplicate task review')
                    reviewed.add(key)
            _require(reviewed == expected, 'Task alignment review coverage is incomplete')
        gates[gate] = {'resolved': True, 'evidence_documents': len(primary),
                       'supporting_documents': len(support)}

    final = {'sha256': _sha256(manifest_path), 'size_bytes': manifest_path.stat().st_size}
    _require(final == manifest_identity, 'Corpus manifest changed during the audit')
    splits = {name: sum(row['split'] == name for row in rows) for name in SPLITS}
    return {
        'schema_version': 1, 'status': 'independently_reaudited',
        'root': str(root), 'manifest': manifest_identity,
        'corpus_status': status, 'corpus_content_sha256': content_identity,
        'examples': len(rows), 'unique_tasks': len(task_splits),
        'repository_groups': len(group_splits), 'leakage_groups': len(leakage_splits),
        'split_counts': splits, 'input_tokens': input_total,
        'supervised_tokens': supervised_total, 'example_bytes': bytes_total,
        'max_input_tokens': max(row['input_tokens'] for row in rows),
        'min_context_margin': (None if context_limit is None else
                               min(context_limit - output_reserve - row['input_tokens']
                                   for row in rows)),
        'vocab_size': vocab, 'pad_token_id': pad, 'gates': gates,
        'training_admitted': status == 'admitted' and all(
            gates[gate]['resolved'] for gate in GATES),
        'examples_detail': rows,
        'scope': 'Independent recomputation of identities, token accounting, split '
                 'isolation, duplicate detection and gate bindings from stored bytes. '
                 'No rights clearance, review-truth, capacity or performance claim.'}


def compare_with_loader(audit, loader_summary):
    """Require the two independent layers to agree on every shared quantity."""
    pairs = [('corpus_content_sha256', 'content_sha256'),
             ('input_tokens', 'input_tokens'),
             ('supervised_tokens', 'supervised_tokens'),
             ('examples', 'examples'),
             ('unique_tasks', 'unique_tasks'),
             ('corpus_status', 'status'),
             ('training_admitted', 'training_admitted')]
    disagreements = {}
    for mine, theirs in pairs:
        if audit[mine] != loader_summary[theirs]:
            disagreements[theirs] = {'audit': audit[mine], 'loader': loader_summary[theirs]}
    if audit['manifest'] != loader_summary['manifest']:
        disagreements['manifest'] = {'audit': audit['manifest'],
                                     'loader': loader_summary['manifest']}
    if disagreements:
        raise CorpusAuditError('Independent audit disagrees with the loader: '
                               + str(sorted(disagreements)))
    return {'compared_quantities': len(pairs) + 1, 'disagreements': {}, 'agreed': True}


def verify_schedule_coverage(audit, schedule):
    """Check a schedule against the audited corpus without reusing its iterator."""
    _require(schedule.get('corpus_content_sha256') == audit['corpus_content_sha256'],
             'Schedule belongs to another corpus')
    training = {row['example_id']: row for row in audit['examples_detail']
                if row['split'] == 'train'}
    scheduled = schedule.get('examples')
    _require(isinstance(scheduled, list) and scheduled, 'Schedule has no examples')
    names = [row['example_id'] for row in scheduled]
    _require(len(set(names)) == len(names), 'Schedule repeats an example identity')
    _require(set(names) == set(training),
             'Schedule does not cover exactly the audited training split')
    for row in scheduled:
        expected = training[row['example_id']]
        for key in ('input_tokens', 'supervised_tokens'):
            _require(row[key] == expected[key],
                     'Schedule count differs from the audited corpus: ' + row['example_id'])
    epochs = schedule['max_epochs']
    target = schedule['target_supervised_tokens']
    available = sum(row['supervised_tokens'] for row in scheduled)
    _require(available * epochs >= target,
             'Token target exceeds the declared epoch allowance')
    return {'scheduled_examples': len(scheduled),
            'training_examples': len(training),
            'supervised_tokens_per_epoch': available,
            'target_supervised_tokens': target, 'max_epochs': epochs,
            'declared_epoch_allowance': available * epochs,
            'repetition_factor_at_target': target / available,
            'coverage_exact': True,
            'scope': 'Exact one-to-one coverage and count agreement. Repeated epochs '
                     'are repeated exposures of the same data, not new data.'}
