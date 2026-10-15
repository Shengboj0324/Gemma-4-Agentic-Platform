"""Screen an explicitly supplied, hash-pinned issue JSON list for lexical overlap.

Input records contain task_id and issue only. Source authorization, provenance,
reserved-repository exclusion and cohort selection must precede this command.
"""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync.issue_similarity import audit_issue_similarity
from zenithsync.source_bytes import verified_source_bytes


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--issues', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--size-bytes', type=int, required=True)
    parser.add_argument('--max-bytes', type=int, default=16777216)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--jaccard', type=Fraction, default=Fraction(1, 2))
    parser.add_argument('--containment', type=Fraction, default=Fraction(4, 5))
    parser.add_argument('--shingle-width', type=int, default=5)
    parser.add_argument('--max-documents', type=int, default=50000)
    parser.add_argument('--max-total-tokens', type=int, default=5000000)
    parser.add_argument('--max-candidate-pairs', type=int, default=1000000)
    parser.add_argument('--max-pair-visits', type=int, default=50000000)
    args = parser.parse_args()
    identity = {'sha256': args.sha256, 'size_bytes': args.size_bytes}
    payload = verified_source_bytes(args.issues, identity, max_bytes=args.max_bytes)
    rows = json.loads(payload, object_pairs_hook=unique_fields, parse_constant=reject_constant)
    report = audit_issue_similarity(rows, shingle_width=args.shingle_width,
        jaccard_threshold=args.jaccard, containment_threshold=args.containment,
        max_documents=args.max_documents, max_total_tokens=args.max_total_tokens,
        max_candidate_pairs=args.max_candidate_pairs, max_pair_visits=args.max_pair_visits)
    report.update(input=identity, script=file_record(Path(__file__)),
                  implementation=file_record(ROOT/'zenithsync/issue_similarity.py'))
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'report.json').write_bytes(canonical_json(report))
    print({'documents': report['document_count'], 'flagged_pairs': len(report['flagged_pairs']),
           'pair_visits': report['pair_visits'], 'training_approved': False})


if __name__ == '__main__':
    main()
