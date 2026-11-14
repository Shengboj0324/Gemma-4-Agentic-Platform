import json
from pathlib import Path
import tempfile
import unittest

from scripts.build_eval_candidates import ADAPTER, add_adapter_line, build
from zenithsync.artifacts import file_record, inventory

ROOT = Path(__file__).resolve().parents[1]


class BuildCandidatesTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.adapter = self.root / 'adapter-src'
        self.adapter.mkdir()
        (self.adapter / 'adapter_config.json').write_text('{"r": 4}')
        (self.adapter / 'adapter_model.safetensors').write_bytes(b'weights')
        self.receipt = {'files': {n: file_record(self.adapter / n)
                                  for n in ('adapter_config.json', 'adapter_model.safetensors')}}
        self.base = ROOT / 'candidates/p1-base'
        self.manifest = json.loads((ROOT / 'evidence/p1/base-agent-001/manifest.json').read_text())

    def test_only_the_adapter_and_its_declaration_differ(self):
        manifests, differing = build(self.base, self.manifest, self.adapter, self.receipt, self.root / 'out')
        self.assertEqual(differing, ['adapters/main_lora/adapter_config.json',
                                     'adapters/main_lora/adapter_model.safetensors', 'agent.yaml'])
        base_yaml = (self.root / 'out/base/agent.yaml').read_text()
        adapter_yaml = (self.root / 'out/adapter/agent.yaml').read_text()
        self.assertEqual(adapter_yaml.replace(f'adapter: {ADAPTER}\n', ''), base_yaml)
        self.assertEqual(adapter_yaml.splitlines()[2], 'adapter: main_lora')

    def test_drifted_adapter_or_base_is_refused(self):
        (self.adapter / 'adapter_model.safetensors').write_bytes(b'other')
        with self.assertRaisesRegex(ValueError, 'export receipt'):
            build(self.base, self.manifest, self.adapter, self.receipt, self.root / 'o1')
        tampered = dict(self.manifest, files=[dict(r, sha256='0' * 64) if r['path'] == 'agent.yaml' else r
                                              for r in self.manifest['files']])
        with self.assertRaises(ValueError):
            build(self.base, tampered, self.adapter, self.receipt, self.root / 'o2')

    def test_adapter_line_is_inserted_once_after_the_model(self):
        self.assertEqual(add_adapter_line('name: x\nmodel: m\ntools: []\n'),
                         'name: x\nmodel: m\nadapter: main_lora\ntools: []\n')
        with self.assertRaises(ValueError):
            add_adapter_line('model: m\nadapter: other\n')
        with self.assertRaises(ValueError):
            add_adapter_line('name: x\n')


if __name__ == '__main__':
    unittest.main()
