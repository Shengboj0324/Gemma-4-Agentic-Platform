from copy import deepcopy
import unittest

from zenithsync.pytest_matrix import compare_matrix


def document(active, failed=()):
    reports = []
    for node in ('old', 'new', 'common'):
        reports.append(dict(nodeid=node, when='setup', outcome='passed' if node in active else 'skipped'))
        if node in active:
            reports.append(dict(nodeid=node, when='call', outcome='failed' if node in failed else 'passed'))
        reports.append(dict(nodeid=node, when='teardown', outcome='passed'))
    return dict(collected=['old', 'new', 'common'], reports=reports,
                collection_errors=[], exitstatus=int(bool(failed)))


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.active = {'older': ['old', 'common'], 'newer': ['new', 'common']}
        self.matrix = {env: {role: document(nodes, ['new'] if env == 'newer' and role == 'base' else [])
                            for role in ('base', 'reference', 'candidate')}
                       for env, nodes in self.active.items()}

    def test_complete_matrix_preserves_nonexecution_and_inputs(self):
        before = deepcopy(self.matrix)
        result = compare_matrix(self.matrix, self.active)
        self.assertEqual(result['environments']['older']['not_executed'], ['new'])
        self.assertEqual(result['repair_transitions'], [{'environment': 'newer', 'nodeid': 'new'}])
        self.assertFalse(result['training_approved'])
        self.assertEqual(before, self.matrix)

    def test_skipped_in_every_environment_rejects(self):
        self.active['newer'] = ['common']
        for role in self.matrix['newer']:
            self.matrix['newer'][role] = document(['common'], ['common'] if role == 'base' else [])
        with self.assertRaisesRegex(ValueError, 'never execute'):
            compare_matrix(self.matrix, self.active)

    def test_failures_skips_duplicate_and_missing_phases_reject(self):
        for defect in ('failed', 'skipped', 'duplicate', 'missing'):
            with self.subTest(defect=defect):
                matrix = deepcopy(self.matrix)
                rows = matrix['newer']['candidate']['reports']
                index = next(i for i, r in enumerate(rows) if r['nodeid'] == 'new' and r['when'] == 'call')
                if defect == 'duplicate': rows.append(deepcopy(rows[index]))
                elif defect == 'missing': rows.pop(index)
                else: rows[index]['outcome'] = defect
                with self.assertRaises(ValueError): compare_matrix(matrix, self.active)

    def test_inactive_call_or_teardown_failure_rejects(self):
        for defect in ('call', 'teardown'):
            matrix = deepcopy(self.matrix)
            rows = matrix['older']['candidate']['reports']
            if defect == 'call': rows.append(dict(nodeid='new', when='call', outcome='passed'))
            else: next(r for r in rows if r['nodeid'] == 'new' and r['when'] == 'teardown')['outcome'] = 'failed'
            with self.assertRaises(ValueError): compare_matrix(matrix, self.active)

    def test_inconsistent_collections_and_applicability_reject(self):
        matrix = deepcopy(self.matrix)
        matrix['older']['reference']['collected'].remove('new')
        with self.assertRaises(ValueError): compare_matrix(matrix, self.active)
        for active in ({'older': ['old']}, {**self.active, 'older': ['old', 'old']},
                       {**self.active, 'older': ['unknown']}):
            with self.assertRaises(ValueError): compare_matrix(self.matrix, active)

    def test_collection_errors_exit_mismatch_and_no_repair_reject(self):
        for defect in ('collection', 'exit', 'repair'):
            matrix = deepcopy(self.matrix)
            if defect == 'collection': matrix['older']['base']['collection_errors'] = ['broken']
            elif defect == 'exit': matrix['newer']['base']['exitstatus'] = 0
            else: matrix['newer']['base'] = document(self.active['newer'])
            with self.assertRaises(ValueError): compare_matrix(matrix, self.active)


class PublisherMatrixTests(unittest.TestCase):
    setUp = MatrixTests.setUp
    def expectations(self):
        return dict(FAIL_TO_PASS=['new'], PASS_TO_PASS=[], FAIL_TO_FAIL=[], PASS_TO_FAIL=[])

    def compare(self, expectations=None, supplemental=None):
        from zenithsync.pytest_matrix import compare_publisher_matrix
        return compare_publisher_matrix(self.matrix, self.active,
                                        self.expectations() if expectations is None else expectations,
                                        supplemental_pass_to_pass=['old', 'common'] if supplemental is None else supplemental)

    def test_explicit_publisher_and_supplemental_coverage(self):
        result = self.compare()
        self.assertTrue(result['publisher_transitions_match'])
        self.assertEqual(result['publisher_key_count'], 1)
        self.assertFalse(result['training_approved'])

    def test_wrong_transition_missing_group_and_duplicate_declaration_reject(self):
        for expectations in (
            dict(FAIL_TO_PASS=[], PASS_TO_PASS=['new'], FAIL_TO_FAIL=[], PASS_TO_FAIL=[]),
            dict(FAIL_TO_PASS=['missing'], PASS_TO_PASS=[], FAIL_TO_FAIL=[], PASS_TO_FAIL=[]),
            dict(FAIL_TO_PASS=['new'], PASS_TO_PASS=['new'], FAIL_TO_FAIL=[], PASS_TO_FAIL=[])):
            with self.assertRaises(ValueError): self.compare(expectations)
        for supplemental in ([], ['old'], ['old', 'common', 'new'], ['old', 'old', 'common']):
            with self.assertRaises(ValueError): self.compare(supplemental=supplemental)

    def test_supplemental_failure_cannot_be_rebranded_as_repair(self):
        self.matrix['older']['base'] = document(self.active['older'], ['old'])
        with self.assertRaisesRegex(ValueError, 'contradicts publisher'):
            self.compare()

    def test_full_group_members_must_agree(self):
        # Two complete node IDs map to the same whitespace-truncated key.
        for roles in self.matrix.values():
            for d in roles.values():
                d['collected'] = [n.replace('new', 'new case-one') for n in d['collected']]
                d['collected'].append('new case-two')
                copies = []
                for row in d['reports']:
                    if row['nodeid'] == 'new':
                        row['nodeid'] = 'new case-one'
                        copies.append({**row, 'nodeid': 'new case-two'})
                d['reports'].extend(copies)
        self.active['newer'] = ['new case-one', 'new case-two', 'common']
        self.assertTrue(self.compare()['publisher_transitions_match'])
        for row in self.matrix['newer']['base']['reports']:
            if row['nodeid'] == 'new case-two' and row['when'] == 'call':
                row['outcome'] = 'passed'
        with self.assertRaisesRegex(ValueError, 'contradicts publisher'):
            self.compare()
