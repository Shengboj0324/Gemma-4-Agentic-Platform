"""Malformed source editor actions must fail before container provisioning."""
import unittest
from scripts.replay_source_teacher import PREFIX, preflight


def editor(arguments):
    return [{'tool_calls': [{'function': {'name': 'str_replace_editor', 'arguments': arguments}}]}]


class EditorPreflightTests(unittest.TestCase):
    def test_incomplete_and_nontext_mutations_rejected(self):
        base = {'command': 'str_replace', 'path': PREFIX + '/a.py'}
        cases = [None, [], {}, base, {**base, 'old_str': 'a'},
                 {**base, 'old_str': '', 'new_str': 'b'},
                 {**base, 'old_str': 'a', 'new_str': None},
                 {'command': 'create', 'path': PREFIX + '/a.py', 'file_text': 1}]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                preflight(editor(args))

    def test_range_requires_exact_integers_and_valid_order(self):
        for bounds in ([True, 2], [1, False], [0, 2], [3, 2], [1], '1:2', [1, 2, 3], [1, -2]):
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                preflight(editor({'command': 'view', 'path': PREFIX + '/a.py', 'view_range': bounds}))

    def test_empty_create_and_deletion_preserve_exact_text(self):
        for args in ({'command': 'create', 'file_text': ''},
                     {'command': 'str_replace', 'old_str': 'line\n', 'new_str': ''},
                     {'command': 'view', 'view_range': [1, -1]}):
            action = preflight(editor({**args, 'path': PREFIX + '/a.py'}))[0]
            self.assertEqual(action['arguments'], {k: v for k, v in args.items() if k != 'command'})


if __name__ == '__main__':
    unittest.main()
