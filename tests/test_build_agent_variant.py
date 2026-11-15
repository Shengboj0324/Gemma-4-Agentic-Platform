import importlib.util
from pathlib import Path
import tempfile
import unittest

from scripts.build_agent_variant import build, set_dotted


def base_tree(root):
    (root / 'configs').mkdir(parents=True)
    (root / 'prompts').mkdir()
    (root / 'agent.yaml').write_text('name: a\ntools:\n  - run_command\n  - get_code_neighbors\ninstruction: !include prompts/system.md\n')
    (root / 'eval_config.yaml').write_text('evaluation:\n  max_time_minutes: 10\n  max_tool_calls: 40\n')
    (root / 'configs' / 'sampling.yaml').write_text('temperature: 0.0\nthinking_config:\n  thinking_budget: 2048\n')
    (root / 'prompts' / 'system.md').write_text('Base prompt.\n')


@unittest.skipUnless(importlib.util.find_spec('yaml'), 'PyYAML required')
class BuildAgentVariantTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        base_tree(self.root / 'base')

    def tearDown(self):
        self.directory.cleanup()

    def test_only_declared_files_change(self):
        import yaml
        addendum = self.root / 'add.md'
        addendum.write_text('Reproduce under /tmp first.\n')
        differing = build(self.root / 'base', self.root / 'v', eval_changes={'max_time_minutes': 20},
                          sampling_changes={'thinking_config.thinking_budget': 1024}, addendum=addendum)
        self.assertEqual(differing, ['configs/sampling.yaml', 'eval_config.yaml', 'prompts/system.md'])
        self.assertEqual(yaml.safe_load((self.root / 'v/eval_config.yaml').read_text())['evaluation'],
                         {'max_time_minutes': 20, 'max_tool_calls': 40})
        self.assertEqual(yaml.safe_load((self.root / 'v/configs/sampling.yaml').read_text())['thinking_config'],
                         {'thinking_budget': 1024})
        self.assertTrue((self.root / 'v/prompts/system.md').read_text().endswith('Reproduce under /tmp first.\n'))
        self.assertEqual((self.root / 'v/agent.yaml').read_bytes(), (self.root / 'base/agent.yaml').read_bytes())

    def test_unknown_keys_and_noop_changes_are_refused(self):
        with self.assertRaises(ValueError):
            build(self.root / 'base', self.root / 'v1', eval_changes={'model': 'x'}, sampling_changes={}, addendum=None)
        with self.assertRaises(ValueError):
            build(self.root / 'base', self.root / 'v2', eval_changes={}, sampling_changes={'tools': []}, addendum=None)
        with self.assertRaisesRegex(ValueError, 'declared'):
            build(self.root / 'base', self.root / 'v3', eval_changes={'max_time_minutes': 10},
                  sampling_changes={}, addendum=None)

    def test_prompt_file_replaces_the_system_prompt(self):
        prompt = self.root / 'p.md'
        prompt.write_text('Replacement prompt.\n')
        differing = build(self.root / 'base', self.root / 'v', eval_changes={}, sampling_changes={},
                          addendum=None, prompt_file=prompt)
        self.assertEqual(differing, ['prompts/system.md'])
        self.assertEqual((self.root / 'v/prompts/system.md').read_text(), 'Replacement prompt.\n')

    def test_tools_are_dropped_by_exact_line(self):
        differing = build(self.root / 'base', self.root / 'v', eval_changes={}, sampling_changes={},
                          addendum=None, drop_tools=['get_code_neighbors'])
        self.assertEqual(differing, ['agent.yaml'])
        text = (self.root / 'v/agent.yaml').read_text()
        self.assertNotIn('get_code_neighbors', text)
        self.assertIn('  - run_command', text)
        self.assertIn('!include prompts/system.md', text)
        with self.assertRaisesRegex(ValueError, 'exactly once'):
            build(self.root / 'base', self.root / 'v2', eval_changes={}, sampling_changes={},
                  addendum=None, drop_tools=['search_similar_code'])

    def test_dotted_assignment_refuses_a_scalar_parent(self):
        with self.assertRaises(ValueError):
            set_dotted({'temperature': 0.0}, 'temperature.x', 1)


if __name__ == '__main__':
    unittest.main()
