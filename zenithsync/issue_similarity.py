"""Exact lexical overlap signals, never semantic or split admission decisions.

Positive thresholds let an inverted index omit zero-intersection pairs without
changing the answer. NFKC/case/whitespace normalization is an explicit heuristic:
it can change code semantics. Short issues use their complete token tuple.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
import re
import unicodedata


def audit_issue_similarity(rows, *, shingle_width=5,
                           jaccard_threshold=Fraction(1, 2),
                           containment_threshold=Fraction(4, 5),
                           max_documents=50000, max_total_tokens=5000000,
                           max_candidate_pairs=1000000, max_pair_visits=50000000):
    """Return pairs meeting either exact rational threshold, or fail atomically.

    Each row contains exactly task_id and issue. Candidate pairs are those with
    at least one common shingle. Limits bound indexed documents, tokenization
    output and distinct candidate pairs; callers must separately bound input
    bytes before parsing. Pair visits also bound repeated work from boilerplate.
    This routine does not read any evaluation data.
    """
    for value in (shingle_width, max_documents, max_total_tokens, max_candidate_pairs,
                  max_pair_visits):
        if type(value) is not int or value <= 0:
            raise ValueError('Positive integer limits and shingle width required')
    for threshold in (jaccard_threshold, containment_threshold):
        if type(threshold) is not Fraction or not 0 < threshold <= 1:
            raise ValueError('Thresholds must be exact Fractions in (0, 1]')
    if not isinstance(rows, list) or not 0 < len(rows) <= max_documents:
        raise ValueError('Nonempty bounded document list required')
    documents = {}
    total_tokens = 0
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {'task_id', 'issue'}
                or not isinstance(row['task_id'], str) or not row['task_id'].strip()
                or row['task_id'] in documents
                or not isinstance(row['issue'], str) or not row['issue'].strip()):
            raise ValueError('Unique task identity and nonempty issue required')
        normalized = ' '.join(unicodedata.normalize('NFKC', row['issue']).casefold().split())
        tokens = []
        for match in re.finditer(r'\w+|[^\w\s]', normalized):
            total_tokens += 1
            if total_tokens > max_total_tokens:
                raise ValueError('Token budget exceeded')
            tokens.append(match.group())
        if not tokens:
            raise ValueError('Issue has no comparison tokens')
        width = min(shingle_width, len(tokens))
        documents[row['task_id']] = {
            tuple(tokens[i:i + width]) for i in range(len(tokens) - width + 1)
        }
    postings = defaultdict(list)
    for task in sorted(documents):
        for shingle in sorted(documents[task]):
            postings[shingle].append(task)
    pair_visits = sum(len(p) * (len(p) - 1) // 2 for p in postings.values())
    if pair_visits > max_pair_visits:
        raise ValueError('Pair-visit budget exceeded; no partial audit')
    intersections = {}
    for posting in postings.values():
        for pair in combinations(posting, 2):
            if pair not in intersections:
                if len(intersections) == max_candidate_pairs:
                    raise ValueError('Candidate-pair budget exceeded; no partial audit')
                intersections[pair] = 0
            intersections[pair] += 1
    flagged = []
    for (first, second), common in sorted(intersections.items()):
        left, right = len(documents[first]), len(documents[second])
        union = left + right - common
        smaller = min(left, right)
        jaccard = Fraction(common, union)
        containment = Fraction(common, smaller)
        if jaccard >= jaccard_threshold or containment >= containment_threshold:
            flagged.append({'first': first, 'second': second, 'intersection': common,
                            'union': union, 'first_shingles': left, 'second_shingles': right,
                            'jaccard': [jaccard.numerator, jaccard.denominator],
                            'containment': [containment.numerator, containment.denominator],
                            'jaccard_flag': jaccard >= jaccard_threshold,
                            'containment_flag': containment >= containment_threshold})
    return {
        'schema_version': 1, 'document_count': len(documents),
        'total_tokens': total_tokens, 'shingle_width': shingle_width,
        'thresholds': {'jaccard': [jaccard_threshold.numerator, jaccard_threshold.denominator],
                       'containment': [containment_threshold.numerator, containment_threshold.denominator]},
        'total_unordered_pairs': len(documents) * (len(documents) - 1) // 2,
        'positive_intersection_pairs': len(intersections), 'pair_visits': pair_visits,
        'flagged_pairs': flagged,
        'training_approved': False, 'split_frozen': False,
        'scope': 'Exact overlap under heuristic NFKC/casefold/token-shingle normalization. '
                 'Unflagged pairs can still be semantic duplicates; flagged pairs can share only boilerplate.',
    }
