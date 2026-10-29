"""Audit a corpus independently, then require the training loader to agree.

Layer one is `zenithsync.training_corpus`, the code training actually uses.
Layer two is `zenithsync.corpus_audit`, which re-derives every count, digest and
invariant from the stored bytes without calling layer one. Disagreement between
them is a failure, not a warning. Passing both is consistency evidence, not a
claim about data quality, rights or model performance.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.corpus_audit import (audit_corpus, compare_with_loader,
                                     verify_loader_offers, verify_schedule_coverage)
from zenithsync.training_corpus import IndexedCorpus

SOURCES = ['scripts/verify_admitted_corpus.py', 'zenithsync/corpus_audit.py',
           'zenithsync/training_corpus.py', 'zenithsync/training_schedule.py',
           'zenithsync/training_batch.py', 'zenithsync/splits.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--corpus-sha256', required=True)
    parser.add_argument('--content-sha256', help='Expected corpus content identity')
    parser.add_argument('--expected-status', choices=['quarantine', 'admitted'])
    parser.add_argument('--purpose', choices=['inspection', 'training'], default='training')
    parser.add_argument('--schedule', type=Path,
                        help='Optional schedule.json to check for exact coverage')
    parser.add_argument('--context-limit', type=int, default=32768)
    parser.add_argument('--output-reserve', type=int, default=8192)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-bytes', type=int, default=1024**3)
    parser.add_argument('--max-example-bytes', type=int, default=16 * 1024**2)
    args = parser.parse_args()
    if args.context_limit <= 0 or not 0 <= args.output_reserve < args.context_limit:
        parser.error('Invalid context limit or output reserve')
    if args.max_bytes <= 0 or args.max_example_bytes <= 0:
        parser.error('Byte budgets must be positive integers')
    if not (args.corpus / 'corpus.json').is_file():
        parser.error('--corpus does not contain a readable corpus.json')
    if args.schedule is not None and not args.schedule.is_file():
        parser.error('--schedule is not a readable file')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')
    sources = {name: file_record(ROOT / name) for name in SOURCES}
    args.output.mkdir(parents=True, exist_ok=False)

    try:
        _verify(args, sources)
    except BaseException:
        shutil.rmtree(args.output, ignore_errors=True)
        raise


def _verify(args, sources):
    audit = audit_corpus(args.corpus, expected_manifest_sha256=args.corpus_sha256,
                         expected_content_sha256=args.content_sha256,
                         expected_status=args.expected_status,
                         context_limit=args.context_limit,
                         output_reserve=args.output_reserve,
                         max_total_bytes=args.max_bytes)
    corpus = IndexedCorpus(args.corpus, args.corpus / 'corpus.json',
                           expected_manifest_sha256=args.corpus_sha256,
                           purpose=args.purpose, max_total_bytes=args.max_bytes,
                           max_example_bytes=args.max_example_bytes)
    agreement = compare_with_loader(audit, corpus.summary)

    fetched = verify_loader_offers(audit, corpus, purpose=args.purpose)

    coverage = None
    if args.schedule is not None:
        schedule = load_json(args.schedule)
        coverage = verify_schedule_coverage(audit, schedule)
        coverage['schedule_file'] = file_record(args.schedule)
    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during verification')

    # Write the sidecar first so the receipt can bind it; a report that cannot
    # contradict an edited sidecar is not evidence about the sidecar.
    examples_path = args.output / 'examples.json'
    examples_path.write_bytes(canonical_json(audit['examples_detail']))
    receipt = {'schema_version': 1, 'status': 'two_layer_corpus_verification_passed',
               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'sources': sources, 'purpose': args.purpose,
               'expected_status': args.expected_status,
               'content_sha256_bound': args.content_sha256 is not None,
               'byte_policy': {'max_total_bytes': args.max_bytes,
                               'max_example_bytes': args.max_example_bytes},
               'examples_file': file_record(examples_path),
               'context_policy': {'context_limit': args.context_limit,
                                  'output_reserve': args.output_reserve},
               'independent_audit': {key: value for key, value in audit.items()
                                     if key != 'examples_detail'},
               'loader_summary': corpus.summary, 'agreement': agreement,
               'examples_refetched_and_rechecked': fetched,
               'schedule_coverage': coverage,
               'training_started': False,
               'scope': 'Two independent layers agree on identities, counts, split '
                        'isolation, duplicates, gate bindings and schedule coverage. '
                        'No rights clearance, review-truth or performance claim.'}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'status': receipt['status'], 'examples': audit['examples'],
           'unique_tasks': audit['unique_tasks'],
           'repository_groups': audit['repository_groups'],
           'split_counts': audit['split_counts'],
           'input_tokens': audit['input_tokens'],
           'supervised_tokens': audit['supervised_tokens'],
           'max_input_tokens': audit['max_input_tokens'],
           'min_context_margin': audit['min_context_margin'],
           'training_admitted': audit['training_admitted'],
           'refetched': fetched,
           'loader_agreement': agreement['agreed'],
           'schedule_coverage_exact': coverage and coverage['coverage_exact']})


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Corpus verification failed ({type(error).__name__}: {error}); '
              'no passing receipt written.', file=sys.stderr)
        raise SystemExit(1)
