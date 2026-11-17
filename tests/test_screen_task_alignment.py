import unittest

from scripts.screen_task_alignment import TEST_PATH, decide, patch_files

PATCH = """diff --git a/pkg/core.py b/pkg/core.py
--- a/pkg/core.py
+++ b/pkg/core.py
@@ -1,2 +1,2 @@
-x = 1
+x = 2
diff --git a/tests/test_core.py b/tests/test_core.py
--- a/tests/test_core.py
+++ b/tests/test_core.py
@@ -1 +1,2 @@
+assert True
"""


def facts(**overrides):
    base = {'licence': 'confirmed', 'cohort': 'train', 'resolved': True, 'agent_files': ['pkg/core.py'],
            'agent_lines': 2, 'agent_test_files': [], 'reference_lines': 2,
            'shared_source_files': ['pkg/core.py'], 'tokenized': True}
    return {**base, **overrides}


class ScreenTests(unittest.TestCase):
    def test_patch_files_counts_changed_lines_per_file(self):
        self.assertEqual(patch_files(PATCH), {'pkg/core.py': 2, 'tests/test_core.py': 1})

    def test_test_paths(self):
        for path in ('tests/test_a.py', 'pkg/test_a.py', 'a_test.py', 'conftest.py', 'pyproject.toml', 'src/testing/x.py'):
            self.assertTrue(TEST_PATH.search(path), path)
        for path in ('pkg/core.py', 'src/latest.py', 'docs/testimony.md'):
            self.assertFalse(TEST_PATH.search(path), path)

    def test_decision_requires_every_check(self):
        self.assertEqual(decide(facts()), ('accepted', None))
        for override in ({'licence': 'copyleft'}, {'cohort': 'confirmation'}, {'resolved': False},
                         {'agent_test_files': ['tests/x.py']}, {'shared_source_files': []},
                         {'agent_lines': 500}, {'tokenized': False}):
            self.assertEqual(decide(facts(**override))[0], 'rejected', override)

    def test_development_cohort_only_when_allowed(self):
        self.assertEqual(decide(facts(cohort='development'))[0], 'rejected')
        self.assertEqual(decide(facts(cohort='development'), ('train', 'development')), ('accepted', None))
        self.assertEqual(decide(facts(cohort='none'), ('train', 'development'))[0], 'rejected')

    def test_confirmation_cohort_can_never_be_allowed(self):
        with self.assertRaises(ValueError):
            decide(facts(cohort='confirmation'), ('train', 'confirmation'))


if __name__ == '__main__':
    unittest.main()
