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
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.corpus_audit import (audit_corpus, compare_with_loader,
                                     verify_schedule_coverage)
from zenithsync.training_corpus import IndexedCorpus

SOURCES = ['scripts/verify_admitted_corpus.py', 'zenithsync/corpus_audit.py',
           'zenithsync/training_corpus.py', 'zenithsync/training_schedule.py',
           'zenithsync/splits.py', 'zenithsync/artifacts.py', 'zenithsync/contracts.py']


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
    args.output.mkdir(parents=True, exist_ok=False)
    sources = {name: file_record(ROOT / name) for name in SOURCES}

    audit = audit_corpus(args.corpus, expected_manifest_sha256=args.corpus_sha256,
                         expected_content_sha256=args.content_sha256,
                         expected_status=args.expected_status,
                         context_limit=args.context_limit,
                         output_reserve=args.output_reserve)
    corpus = IndexedCorpus(args.corpus, args.corpus / 'corpus.json',
                           expected_manifest_sha256=args.corpus_sha256,
                           purpose=args.purpose, max_total_bytes=args.max_bytes,
                           max_example_bytes=args.max_example_bytes)
    agreement = compare_with_loader(audit, corpus.summary)

    # Fetch every example through the loader and re-check it against the audit.
    detail = {row['example_id']: row for row in audit['examples_detail']}
    fetched = 0
    for metadata in corpus.metadata():
        row = detail[metadata['example_id']]
        example = corpus.fetch(metadata['example_id'])
        if (len(example['input_ids']) != row['input_tokens']
                or sum(label != -100 for label in example['labels'][1:]) != row['supervised_tokens']
                or example['task_id'] != row['task_id']
                or example['split'] != row['split']):
            raise ValueError('Fetched example differs from the independent audit: '
                             + metadata['example_id'])
        fetched += 1
    expected_fetches = (audit['split_counts']['train'] if args.purpose == 'training'
                        else audit['examples'])
    if fetched != expected_fetches or fetched != corpus.summary['returned_examples']:
        raise ValueError(f'Refetched {fetched} examples; audit expected {expected_fetches} '
                         f"and the loader reported {corpus.summary['returned_examples']}")
    coverage = None
    if args.schedule is not None:
        schedule = load_json(args.schedule)
        coverage = verify_schedule_coverage(audit, schedule)
        coverage['schedule_file'] = file_record(args.schedule)
    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during verification')

    receipt = {'schema_version': 1, 'status': 'two_layer_corpus_verification_passed',
               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'sources': sources, 'purpose': args.purpose,
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
    (args.output / 'examples.json').write_bytes(canonical_json(audit['examples_detail']))
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
    main()
