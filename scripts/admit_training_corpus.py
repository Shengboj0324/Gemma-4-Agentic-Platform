"""Promote a quarantined corpus with explicit per-gate evidence documents.

Every gate must be supplied at least once on the command line. This script does
not search for evidence, infer a missing gate, or approve a review conclusion.
It writes a new corpus tree and a receipt; it starts no training and touches no
cloud resource.
"""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync.corpus_admission import promote_corpus
from zenithsync.training_corpus import GATES

SOURCES = ['zenithsync/corpus_admission.py', 'zenithsync/training_corpus.py',
           'zenithsync/splits.py', 'zenithsync/training_batch.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py',
           'scripts/admit_training_corpus.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True,
                        help='Quarantined corpus root containing corpus.json')
    parser.add_argument('--corpus-sha256', required=True,
                        help='Expected SHA-256 of the quarantined corpus.json')
    parser.add_argument('--destination', type=Path, required=True,
                        help='New directory for the admitted corpus; must not exist')
    parser.add_argument('--output', type=Path, required=True,
                        help='New directory for the admission receipt')
    parser.add_argument('--reviewer', required=True,
                        help='Accountable reviewer identity recorded in every receipt')
    for gate in GATES:
        flag = gate.replace('_', '-')
        parser.add_argument('--' + flag, type=Path, action='append',
                            required=True, metavar='EVIDENCE_JSON',
                            help='Evidence document for the ' + gate + ' gate; repeatable')
        parser.add_argument('--' + flag + '-support', type=Path, action='append',
                            default=[], metavar='EVIDENCE_JSON',
                            help='Supporting document for the ' + gate + ' gate that the '
                                 'loader binds by hash but does not schema-validate; repeatable')
    parser.add_argument('--max-bytes', type=int, default=1024**3,
                        help='Aggregate corpus byte ceiling for both load passes')
    parser.add_argument('--max-example-bytes', type=int, default=16 * 1024**2,
                        help='Per-example byte ceiling for token and audit files')
    args = parser.parse_args()
    if args.max_bytes <= 0 or args.max_example_bytes <= 0:
        parser.error('Byte budgets must be positive integers')
    if not (args.corpus / 'corpus.json').is_file():
        parser.error('--corpus does not contain a readable corpus.json')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')
    evidence = {gate: getattr(args, gate) for gate in GATES}
    supporting = {gate: getattr(args, gate + '_support') for gate in GATES}
    # Snapshot the implementation before it runs, and re-check it after, so the
    # receipt records the code that executed rather than whatever is on disk at
    # the end of a long promotion.
    sources = {name: file_record(ROOT / name) for name in SOURCES}
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        receipt = promote_corpus(
            source_root=args.corpus, source_manifest_sha256=args.corpus_sha256,
            destination=args.destination, gate_evidence=evidence,
            reviewer=args.reviewer, supporting_evidence=supporting,
            max_total_bytes=args.max_bytes,
            max_example_bytes=args.max_example_bytes)
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during promotion')
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    receipt['sources'] = sources
    receipt['byte_policy'] = {'max_total_bytes': args.max_bytes,
                              'max_example_bytes': args.max_example_bytes}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    summary = receipt['summary']
    print({'status': receipt['status'],
           'destination': receipt['destination']['root'],
           'corpus_manifest_sha256': receipt['destination']['manifest']['sha256'],
           'corpus_content_sha256': receipt['corpus_content_sha256'],
           'examples': summary['examples'], 'training_examples': summary['returned_examples'],
           'input_tokens': summary['input_tokens'],
           'supervised_tokens': summary['supervised_tokens'],
           'training_admitted': summary['training_admitted']})


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Corpus admission failed ({type(error).__name__}: {error}); '
              'no passing receipt written.', file=sys.stderr)
        raise SystemExit(1)
