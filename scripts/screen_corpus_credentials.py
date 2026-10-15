"""Screen pinned corpus inputs without printing possible credential values."""
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.corpus_credentials import decode_checked, screen_corpus
from zenithsync.training_corpus import IndexedCorpus


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--tokenizer', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = args.corpus / 'corpus.json'
    corpus = IndexedCorpus(args.corpus, manifest,
                           expected_manifest_sha256=args.manifest_sha256, purpose='inspection')
    document = load_json(manifest)
    if file_record(manifest) != corpus.summary['manifest']:
        raise ValueError('Corpus manifest changed before tokenizer binding')
    expected = document['tokenizer_assets']['tokenizer.json']
    if file_record(args.tokenizer) != expected:
        raise ValueError('Tokenizer does not match corpus assets')
    import tokenizers
    tokenizer = tokenizers.Tokenizer.from_file(str(args.tokenizer))
    if file_record(args.tokenizer) != expected:
        raise ValueError('Tokenizer changed during loading')
    report = screen_corpus(corpus, lambda ids: decode_checked(tokenizer, ids))
    report['tokenizer'] = expected
    report['tokenizers_version'] = tokenizers.__version__
    report['sources'] = {name: file_record(ROOT / name) for name in (
        'zenithsync/corpus_credentials.py', 'zenithsync/source_credentials.py',
        'zenithsync/training_corpus.py', 'scripts/screen_corpus_credentials.py')}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'report.json').write_bytes(canonical_json(report))
    print('Screened', len(report['examples']), 'examples;', report['flagged_examples'],
          'flagged examples;', report['indicator_count'], 'indicators. Privacy approval remains false.')


if __name__ == '__main__':
    main()
