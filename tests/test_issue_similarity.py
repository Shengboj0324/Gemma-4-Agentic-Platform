import random
import unittest
from fractions import Fraction
from itertools import combinations

from zenithsync.issue_similarity import audit_issue_similarity


class IssueSimilarityTests(unittest.TestCase):
    def test_index_matches_exhaustive_independent_oracle(self):
        rng = random.Random(7401)
        for width in (1, 2, 5):
            words = {str(i): [rng.choice('abcdef') for _ in range(rng.randint(1, 18))]
                     for i in range(35)}
            rows = [{'task_id': key, 'issue': ' '.join(value)} for key, value in words.items()]
            sets = {}
            for key, value in words.items():
                n = min(width, len(value))
                sets[key] = set(zip(*(value[offset:len(value)-n+offset+1] for offset in range(n))))
            expected = []
            positive = 0
            for a, b in combinations(sorted(sets), 2):
                common = len(sets[a].intersection(sets[b]))
                union = len(sets[a].union(sets[b]))
                small = min(len(sets[a]), len(sets[b]))
                positive += common > 0
                if common * 3 >= union or common * 5 >= small * 4:
                    expected.append((a, b, common, union))
            result = audit_issue_similarity(rows, shingle_width=width,
                                            jaccard_threshold=Fraction(1, 3))
            self.assertEqual(positive, result['positive_intersection_pairs'])
            self.assertEqual(expected, [(p['first'], p['second'], p['intersection'], p['union'])
                                        for p in result['flagged_pairs']])
            self.assertEqual(result, audit_issue_similarity(rows[::-1], shingle_width=width,
                                                           jaccard_threshold=Fraction(1, 3)))

    def test_exact_boundary_and_containment(self):
        rows = [{'task_id': 'a', 'issue': 'a b'}, {'task_id': 'b', 'issue': 'a c'}]
        result = audit_issue_similarity(rows, shingle_width=1,
                                        jaccard_threshold=Fraction(1, 3),
                                        containment_threshold=Fraction(1))
        pair = result['flagged_pairs'][0]
        self.assertEqual(pair['jaccard'], [1, 3])
        self.assertFalse(pair['containment_flag'])
        self.assertFalse(audit_issue_similarity(rows, shingle_width=1,
                         jaccard_threshold=Fraction(1, 3) + Fraction(1, 10**30),
                         containment_threshold=Fraction(1))['flagged_pairs'])
        rows[1]['issue'] = 'a b c d e'
        pair = audit_issue_similarity(rows, shingle_width=1)['flagged_pairs'][0]
        self.assertFalse(pair['jaccard_flag'])
        self.assertTrue(pair['containment_flag'])

    def test_repeated_shingles_do_not_inflate_intersection(self):
        result = audit_issue_similarity([{'task_id': 'a', 'issue': 'x x x x x x'},
                                        {'task_id': 'b', 'issue': 'x x x x x'}])
        self.assertEqual(result['flagged_pairs'][0]['intersection'], 1)
        self.assertEqual(result['flagged_pairs'][0]['union'], 1)

    def test_short_unicode_and_zero_overlap(self):
        rows = [{'task_id': 'a', 'issue': 'É Ａ'}, {'task_id': 'b', 'issue': 'e\u0301 a'},
                {'task_id': 'c', 'issue': 'different'}]
        result = audit_issue_similarity(rows)
        self.assertEqual(result['positive_intersection_pairs'], 1)
        self.assertEqual(result['total_unordered_pairs'], 3)
        self.assertEqual(result['flagged_pairs'][0]['jaccard'], [1, 1])
        self.assertFalse(result['training_approved'])

    def test_limits_fail_instead_of_returning_partial_results(self):
        rows = [{'task_id': str(i), 'issue': 'common tokens'} for i in range(3)]
        for kwargs in ({'max_documents': 2}, {'max_total_tokens': 5},
                       {'max_candidate_pairs': 2}, {'shingle_width': True},
                       {'jaccard_threshold': 0.5}, {'containment_threshold': Fraction(0)}):
            with self.assertRaises(ValueError):
                audit_issue_similarity(rows, **kwargs)
        self.assertEqual(audit_issue_similarity(rows, max_total_tokens=6,
                         max_candidate_pairs=3)['positive_intersection_pairs'], 3)

    def test_invalid_identity_and_empty_text(self):
        for rows in ([], [{'task_id': 'x', 'issue': ' '}],
                     [{'task_id': 'x', 'issue': 'a'}, {'task_id': 'x', 'issue': 'b'}],
                     [{'task_id': 'x', 'issue': 'a', 'extra': True}]):
            with self.assertRaises(ValueError):
                audit_issue_similarity(rows)

    def test_repeated_postings_have_separate_work_budget(self):
        rows = [{'task_id': str(i), 'issue': 'a b c'} for i in range(3)]
        with self.assertRaisesRegex(ValueError, 'Pair-visit'):
            audit_issue_similarity(rows, shingle_width=1, max_pair_visits=8)
        result = audit_issue_similarity(rows, shingle_width=1, max_pair_visits=9)
        self.assertEqual(result['pair_visits'], 9)
        self.assertEqual(result['positive_intersection_pairs'], 3)


if __name__ == '__main__':
    unittest.main()
