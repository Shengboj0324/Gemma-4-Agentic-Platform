import copy
import random
import unittest
from unittest.mock import patch

from zenithsync.splits import merge_leakage_groups, validate_splits


class LeakageMergeTests(unittest.TestCase):
    def manifest(self):
        return {'schema_version': 1, 'status': 'draft', 'tasks': [
            {'task_id': key, 'repository_group': 'repo/'+key, 'leakage_group': key,
             'split': 'train', 'input_sha256': str(i)*64}
            for i, key in enumerate('abcd')]}

    def test_transitive_links_preserve_existing_families(self):
        original = self.manifest()
        original['tasks'][1]['leakage_group'] = 'a'
        before = copy.deepcopy(original)
        result = merge_leakage_groups(original, [['b', 'c'], ['c', 'd']])
        self.assertEqual(original, before)
        self.assertEqual(len({r['leakage_group'] for r in result['manifest']['tasks']}), 1)
        self.assertEqual(result['merged_families'][0]['tasks'], list('abcd'))
        self.assertFalse(result['training_approved'])
        self.assertEqual(validate_splits(result['manifest'])['task_count'], 4)

    def test_order_independence_and_idempotence(self):
        original = self.manifest()
        result = merge_leakage_groups(original, [['a', 'b'], ['b', 'c']])
        original['tasks'].reverse()
        reverse = merge_leakage_groups(original, [['c', 'b'], ['b', 'a']])
        self.assertEqual(result, reverse)
        again = merge_leakage_groups(result['manifest'], [['a', 'b'], ['b', 'c']])
        self.assertEqual(result['manifest'], again['manifest'])
        self.assertEqual(again['merged_families'], [])

    def test_cross_split_link_rejected_without_reassignment(self):
        original = self.manifest()
        original['tasks'][2]['split'] = 'confirmation'
        before = copy.deepcopy(original)
        validate_splits(original)
        with self.assertRaisesRegex(ValueError, 'crosses splits'):
            merge_leakage_groups(original, [['a', 'b'], ['b', 'c']])
        self.assertEqual(original, before)

    def test_no_links_preserves_labels(self):
        original = self.manifest()
        self.assertEqual(merge_leakage_groups(original, [])['manifest'], original)

    def test_invalid_links_limits_and_frozen_manifest(self):
        for links in ([['a', 'missing']], [['a', 'a']], [['a']], [['a', []]], 'ab'):
            with self.assertRaises(ValueError):
                merge_leakage_groups(self.manifest(), links)
        with self.assertRaises(ValueError):
            merge_leakage_groups(self.manifest(), [['a', 'b', 'c']], max_link_members=2)
        original = self.manifest()
        original['status'] = 'frozen'
        with self.assertRaises(ValueError):
            merge_leakage_groups(original, [])

    def test_partitions_match_independent_graph_reachability(self):
        rng = random.Random(7401)
        for _ in range(50):
            manifest = self.manifest()
            edges = [list(pair) for pair in [('a', 'b'), ('a', 'c'), ('a', 'd'),
                                             ('b', 'c'), ('b', 'd'), ('c', 'd')]]
            links = [edge for edge in edges if rng.randrange(2)]
            reached = {}
            for start in 'abcd':
                seen, pending = {start}, [start]
                while pending:
                    current = pending.pop()
                    for first, second in links:
                        for neighbor in ([second] if first == current else
                                         [first] if second == current else []):
                            if neighbor not in seen:
                                seen.add(neighbor)
                                pending.append(neighbor)
                reached[start] = seen
            result = merge_leakage_groups(manifest, links)['manifest']
            labels = {row['task_id']: row['leakage_group'] for row in result['tasks']}
            for a in 'abcd':
                for b in 'abcd':
                    self.assertEqual(labels[a] == labels[b], b in reached[a])

    def test_hash_collision_cannot_merge_unrelated_components(self):
        with patch('zenithsync.splits.hashlib.sha256') as hasher:
            hasher.return_value.hexdigest.return_value = '0'*64
            with self.assertRaisesRegex(ValueError, 'collide'):
                merge_leakage_groups(self.manifest(), [['a', 'b'], ['c', 'd']])


if __name__ == '__main__':
    unittest.main()
