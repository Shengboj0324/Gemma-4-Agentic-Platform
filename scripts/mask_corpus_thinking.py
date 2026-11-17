"""Derive an actions-only token corpus from an admitted one: thinking text leaves the loss.

Why (docs/45, 11-17 round 4): adapter-003 wrote 48% more completion tokens per agent step than
the base (mean 265 -> 392) while its training trajectories were no longer than the base's own
(mean 256 per step) and per-token serving speed was unchanged. The extra tokens are thinking
text, and every thinking token was a supervised target. This keeps the training sequences
exactly as rendered (input ids unchanged, so the model still conditions on its earlier
thinking, as it does when served) and removes only the thinking blocks from the labels; tool
calls, final answers and turn markers stay supervised.

For every example of a verified corpus, writes OUTPUT/<key>/{tokens.json, report.json} and
OUTPUT/selection.json, the inputs `assemble_training_corpus.py --candidate-root OUTPUT`
takes. A supervised thinking block is the native template's
`<|channel>thought\\n ... \\n<channel|>` immediately followed by a tool call; each one must be
fully supervised before masking, and nothing else changes. Any other shape is refused.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json

OPEN, CLOSE, CALL = '<|channel>', '<channel|>', '<|tool_call>'
IGNORE = -100


def mask_thinking(input_ids, labels, *, open_id, close_id, call_id, decode, nested=None):
    """Return (new_labels, blocks, masked_tokens, unsupervised_opens) or raise ValueError.

    A recorded thinking text can itself contain the literal `<|channel>` marker (seen in 2 of 177
    rollout trajectories: a stray byte, then `<|channel>thought\\n`, inside the model's own
    thinking). The template renders that text inside the block, so the block holds an inner
    opener; it is still thinking text up to the block's single `<channel|>`, and is masked as part
    of the block. Inner openers are counted in `nested` (a list) when given.
    """
    if len(input_ids) != len(labels):
        raise ValueError('ids and labels differ in length')
    out = list(labels)
    blocks = masked = unsupervised = 0
    i = 0
    while i < len(input_ids):
        if input_ids[i] != open_id:
            if labels[i] != IGNORE and input_ids[i] == close_id:
                raise ValueError(f'supervised {CLOSE} outside a thinking block at {i}')
            i += 1
            continue
        if labels[i] == IGNORE:
            unsupervised += 1
            i += 1
            continue
        try:
            j = input_ids.index(close_id, i + 1)
        except ValueError:
            raise ValueError(f'unclosed thinking block at {i}') from None
        inner = input_ids[i + 1:j].count(open_id)
        if inner and nested is None:
            raise ValueError(f'nested {OPEN} in block at {i}')
        if inner:
            nested.append(inner)
        if any(labels[k] != input_ids[k] for k in range(i, j + 1)):
            raise ValueError(f'thinking block at {i} is not fully supervised')
        text = decode(input_ids[i:j + 1])
        if not (text.startswith(OPEN + 'thought\n') and text.endswith('\n' + CLOSE)):
            raise ValueError(f'block at {i} is not a native thinking block')
        if j + 1 >= len(input_ids) or input_ids[j + 1] != call_id or labels[j + 1] == IGNORE:
            raise ValueError(f'block at {i} is not followed by a supervised tool call')
        for k in range(i, j + 1):
            out[k] = IGNORE
        blocks += 1
        masked += j + 1 - i
        i = j + 1
    remaining = [t for t, label in zip(input_ids, out) if label != IGNORE]
    if open_id in remaining or close_id in remaining:
        raise ValueError('a channel marker is still supervised')
    changed = [k for k, (a, b) in enumerate(zip(labels, out)) if a != b]
    if len(changed) != masked or any(out[k] != IGNORE for k in changed):
        raise ValueError('labels changed outside thinking blocks')
    return out, blocks, masked, unsupervised


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--corpus', type=Path, required=True, help='admitted corpus directory (corpus.json)')
    p.add_argument('--corpus-sha256', required=True)
    p.add_argument('--tokenizer', type=Path, required=True, help="the corpus's tokenizer.json")
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-bytes', type=int, default=4 * 1024**3)
    args = p.parse_args()
    from tokenizers import Tokenizer
    from zenithsync.training_batch import collate_training_examples
    from zenithsync.training_corpus import IndexedCorpus
    corpus_json = args.corpus / 'corpus.json'
    corpus = IndexedCorpus(args.corpus, corpus_json, expected_manifest_sha256=args.corpus_sha256,
                           purpose='inspection', max_total_bytes=args.max_bytes)
    manifest = load_json(corpus_json)
    want = manifest['tokenizer_assets']['tokenizer.json']
    if file_record(args.tokenizer) != want:
        raise ValueError('Tokenizer differs from the corpus tokenizer asset')
    tok = Tokenizer.from_file(str(args.tokenizer))
    ids = {name: tok.token_to_id(name) for name in (OPEN, CLOSE, CALL)}
    if any(v is None for v in ids.values()) or len(set(ids.values())) != 3:
        raise ValueError(f'Special tokens not found: {ids}')
    decode = lambda xs: tok.decode(xs, skip_special_tokens=False)
    args.output.mkdir(parents=True, exist_ok=False)
    selection, rows = [], []
    for record in manifest['examples']:
        src_tokens = args.corpus / record['tokens']['path']
        src_audit = args.corpus / record['audit']['path']
        if file_record(src_tokens) != record['tokens']['identity'] or file_record(src_audit) != record['audit']['identity']:
            raise ValueError('Corpus file changed: ' + record['example_id'])
        candidate = load_json(src_tokens)
        audit = load_json(src_audit)
        nested = []
        labels, blocks, masked, unsupervised = mask_thinking(
            candidate['input_ids'], candidate['labels'], open_id=ids[OPEN], close_id=ids[CLOSE],
            call_id=ids[CALL], decode=decode, nested=nested)
        if blocks == 0:
            raise ValueError('No thinking block in ' + record['example_id'])
        new = {**candidate, 'labels': labels}
        check = collate_training_examples([new], pad_token_id=new['pad_token_id'], vocab_size=new['vocab_size'],
                                          max_length=manifest['max_length'])
        before = audit['supervised_tokens']
        if check['supervised_tokens'] != before - masked or check['supervised_tokens'] <= 0:
            raise ValueError('Supervised-token accounting mismatch in ' + record['example_id'])
        key = hashlib.sha256(record['example_id'].encode()).hexdigest()
        out = args.output / key
        out.mkdir()
        (out / 'tokens.json').write_bytes(canonical_json(new))
        report = {**audit,
                  'labels_sha256': hashlib.sha256(canonical_json(labels)).hexdigest(),
                  'supervised_tokens': check['supervised_tokens'],
                  'token_candidate': file_record(out / 'tokens.json'),
                  'label_transform': {'script': file_record(Path(__file__)), 'kind': 'thinking_blocks_unsupervised',
                                      'source_corpus': file_record(corpus_json),
                                      'source_token_candidate': record['tokens']['identity'],
                                      'source_labels_sha256': audit['labels_sha256'],
                                      'source_supervised_tokens': before,
                                      'thinking_blocks': blocks, 'masked_tokens': masked,
                                      'blocks_with_inner_openers': len(nested),
                                      'unsupervised_channel_opens': unsupervised},
                  'scope': audit['scope'] + '; thinking blocks then removed from the labels (input ids unchanged)'}
        if report['input_sha256'] != hashlib.sha256(canonical_json(new['input_ids'])).hexdigest():
            raise ValueError('Input ids changed in ' + record['example_id'])
        (out / 'report.json').write_bytes(canonical_json(report))
        selection.append({k: record[k] for k in ('example_id', 'task_id', 'repository_group', 'leakage_group', 'split')}
                         | {'candidate_directory': key})
        rows.append({'example_id': record['example_id'], 'blocks': blocks, 'masked': masked, 'inner_openers': len(nested),
                     'supervised_before': before, 'supervised_after': check['supervised_tokens']})
    (args.output / 'selection.json').write_bytes(canonical_json(selection))
    summary = {'examples': len(rows), 'thinking_blocks': sum(r['blocks'] for r in rows),
               'masked_tokens': sum(r['masked'] for r in rows),
               'blocks_with_inner_openers': sum(r['inner_openers'] for r in rows),
               'supervised_before': sum(r['supervised_before'] for r in rows),
               'supervised_after': sum(r['supervised_after'] for r in rows),
               'source_corpus': file_record(corpus_json), 'source_summary': corpus.summary,
               'special_token_ids': ids, 'script': file_record(Path(__file__)), 'rows': rows}
    (args.output / 'summary.json').write_bytes(canonical_json(summary))
    print(json.dumps({k: v for k, v in summary.items() if k not in ('rows', 'source_summary')}))


if __name__ == '__main__':
    main()
