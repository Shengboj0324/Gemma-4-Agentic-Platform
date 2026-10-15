"""Credential-indicator screening of complete decoded corpus inputs.

This finite rule screen is review evidence, not a privacy guarantee or an
admission decision. It includes prompts, observations and assistant text; it
never redacts immutable training examples or returns matched values.
"""
from .source_credentials import scan_text


def screen_corpus(corpus, decode, *, max_decoded_characters=4 * 1024 * 1024):
    """Screen an inspected IndexedCorpus with a caller-bound tokenizer decoder.

    The decoder must retain special tokens. Its asset identity and version must
    be recorded by the caller. Each example is fetched through the corpus's
    integrity checks. Decoded text is discarded after each example.
    """
    if type(max_decoded_characters) is not int or max_decoded_characters <= 0:
        raise ValueError('Decoded character ceiling must be a positive integer')
    if not callable(decode):
        raise TypeError('A bound tokenizer decoder is required')
    summary = corpus.summary
    if summary.get('purpose') != 'inspection':
        raise ValueError('Screening requires inspection of every corpus split')
    rows = []
    for metadata in corpus.metadata():
        example = corpus.fetch(metadata['example_id'])
        text = decode(example['input_ids'])
        if not isinstance(text, str):
            raise TypeError('Tokenizer decoder must return text')
        if len(text) > max_decoded_characters:
            raise ValueError('Decoded input exceeds the character ceiling')
        findings = scan_text(text)
        rows.append({'example_id': example['example_id'], 'task_id': example['task_id'],
                     'split': example['split'], 'decoded_characters': len(text),
                     'input_tokens': len(example['input_ids']), 'findings': findings})
    if len(rows) != summary['returned_examples']:
        raise ValueError('Incomplete corpus screening coverage')
    return {'schema_version': 1, 'corpus': summary, 'examples': rows,
            'flagged_examples': sum(bool(row['findings']) for row in rows),
            'indicator_count': sum(len(row['findings']) for row in rows),
            'training_approved': False, 'privacy_approved': False,
            'scope': 'Four source_credentials rule families over complete decoded inputs. '
                     'No entropy, PII, obfuscated-secret or external validity guarantee.'}


def decode_checked(tokenizer, identifiers):
    """Reject unknown IDs instead of letting the backend silently omit them."""
    if any(type(value) is not int or value < 0 for value in identifiers):
        raise ValueError('Invalid tokenizer ID')
    if any(tokenizer.id_to_token(value) is None for value in set(identifiers)):
        raise ValueError('Corpus contains an ID absent from the bound tokenizer')
    return tokenizer.decode(identifiers, skip_special_tokens=False)
