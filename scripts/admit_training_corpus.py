"""Promote a quarantined corpus with explicit per-gate evidence documents.

Every gate must be supplied at least once on the command line. This script does
not search for evidence, infer a missing gate, or approve a review conclusion.
It writes a new corpus tree and a receipt; it starts no training and touches no
cloud resource.
"""
import argparse
from pathlib import Path
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
    parser.add_argument('--max-bytes', type=int, default=1024**3)
    parser.add_argument('--max-example-bytes', type=int, default=16 * 1024**2)
    args = parser.parse_args()
    evidence = {gate: getattr(args, gate) for gate in GATES}
    supporting = {gate: getattr(args, gate + '_support') for gate in GATES}
    args.output.mkdir(parents=True, exist_ok=False)
    receipt = promote_corpus(
        source_root=args.corpus, source_manifest_sha256=args.corpus_sha256,
        destination=args.destination, gate_evidence=evidence, reviewer=args.reviewer,
        supporting_evidence=supporting,
        max_total_bytes=args.max_bytes, max_example_bytes=args.max_example_bytes)
    receipt['sources'] = {name: file_record(ROOT / name) for name in SOURCES}
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
    main()
