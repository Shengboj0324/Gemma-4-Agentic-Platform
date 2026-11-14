import copy
import unittest

from zenithsync.official_split import (ROLES, TARGETS, freeze_split, group_tasks,
                                       require_cohort, validate_freeze)


def make_tasks():
    tasks = []
    for repo, n in (('fastapi/fastapi', 67), ('Textualize/rich', 48), ('psf/requests', 13), ('encode/httpx', 1)):
        for i in range(n):
            tasks.append({'instance_id': f'{repo.split("/")[1]}_{i}', 'repo': repo,
                          'base_commit': f'{repo}-{i}', 'problem_statement': f'issue {repo} {i}'})
    # Two fastapi tasks share a base commit; two rich tasks share an issue text.
    tasks[1]['base_commit'] = tasks[0]['base_commit']
    tasks[70]['problem_statement'] = '  Issue Textualize/rich 3 '
    tasks[71]['problem_statement'] = 'issue textualize/rich 3'
    return tasks


INPUTS = {'tasks.jsonl': {'sha256': 'a' * 64, 'size_bytes': 1}}


class OfficialSplitTests(unittest.TestCase):
    def test_allocation_is_grouped_stratified_complete_and_deterministic(self):
        tasks = make_tasks()
        record = freeze_split(tasks, seed='s', inputs=INPUTS)
        self.assertEqual(record, freeze_split(list(reversed(tasks)), seed='s', inputs=INPUTS))
        members = [t for role in ROLES for t in record['roles'][role]]
        self.assertEqual(sorted(members), sorted(t['instance_id'] for t in tasks))
        for group in record['groups']:
            roles = {role for role in ROLES for t in group if t in record['roles'][role]}
            self.assertEqual(len(roles), 1, group)
        self.assertIn(['fastapi_0', 'fastapi_1'], record['groups'])
        self.assertIn(['rich_3', 'rich_4'], record['groups'])
        for role in ROLES:
            self.assertLessEqual(abs(record['overshoot'][role]), 1)
        self.assertEqual(sum(sum(v.values()) for v in record['per_repository'].values()), 129)
        self.assertEqual(record['per_repository']['encode/httpx'], {'pilot': 0, 'development': 0, 'holdout': 1})
        self.assertNotEqual(record['roles'], freeze_split(tasks, seed='other', inputs=INPUTS)['roles'])
        validate_freeze(record)

    def test_the_holdout_cannot_be_spent_and_tampering_is_detected(self):
        record = freeze_split(make_tasks(), seed='s', inputs=INPUTS)
        usable = record['roles']['pilot'] + record['roles']['development']
        self.assertEqual(require_cohort(record, usable), sorted(usable))
        with self.assertRaisesRegex(ValueError, 'Refusing to spend'):
            require_cohort(record, usable + record['roles']['holdout'][:1])
        with self.assertRaisesRegex(ValueError, 'not in the frozen split'):
            require_cohort(record, ['nope'])
        moved = copy.deepcopy(record)
        moved['roles']['pilot'].append(moved['roles']['holdout'].pop())
        with self.assertRaisesRegex(ValueError, 'frozen identity'):
            validate_freeze(moved)

    def test_inputs_are_strict(self):
        tasks = make_tasks()
        with self.assertRaises(ValueError):
            freeze_split(tasks + [tasks[0]], seed='s', inputs=INPUTS)
        with self.assertRaises(ValueError):
            freeze_split(tasks, seed=' ', inputs=INPUTS)
        with self.assertRaises(ValueError):
            freeze_split(tasks, seed='s', targets={**TARGETS, 'holdout': 79}, inputs=INPUTS)
        self.assertEqual(len(group_tasks(tasks)), 127)


if __name__ == '__main__':
    unittest.main()
