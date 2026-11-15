import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from scripts.rescore_patches import recorded_attempts
from scripts.bench_lora_latency import module_of


class RecordedAttemptsTests(unittest.TestCase):
    def test_patches_and_errors_are_paired_and_cross_checked(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'patches').mkdir()
            (d / 'patches' / 'a.patch').write_text('diff --git a/x b/x\n')
            rows = [{'instance_id': 'a', 'agent_patch_size': 19, 'error': 'Agent exceeded turns budget (40 turns)'},
                    {'instance_id': 'b', 'agent_patch_size': 0, 'error': 'Agent exceeded session timeout (10 min)'}]
            (d / 'task_results.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
            attempts = recorded_attempts(d)
            self.assertEqual(attempts['a'], ('diff --git a/x b/x\n', 'Agent exceeded turns budget (40 turns)'))
            self.assertEqual(attempts['b'], ('', 'Agent exceeded session timeout (10 min)'))
            (d / 'patches' / 'b.patch').write_text('diff --git a/y b/y\n')
            with self.assertRaisesRegex(ValueError, 'disagree'):
                recorded_attempts(d)


class ModuleOfTests(unittest.TestCase):
    def test_peft_tensor_names_map_to_module_and_projection(self):
        name = 'base_model.model.model.language_model.layers.3.self_attn.q_proj.lora_A.weight'
        self.assertEqual(module_of(name), ('base_model.model.model.language_model.layers.3.self_attn.q_proj', 'q_proj'))

    @unittest.skipUnless(importlib.util.find_spec('torch') and importlib.util.find_spec('safetensors'), 'torch')
    def test_subset_keeps_only_the_requested_projections_and_rewrites_targets(self):
        import torch
        from safetensors.torch import save_file
        from scripts.bench_lora_latency import subset_adapter
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            src = d / 'src'
            src.mkdir()
            tensors = {}
            for layer in range(2):
                for proj, kind in (('q_proj', 'self_attn'), ('down_proj', 'mlp')):
                    for ab in ('A', 'B'):
                        tensors[f'base_model.model.model.language_model.layers.{layer}.{kind}.{proj}.lora_{ab}.weight'] = torch.zeros(2, 2)
            save_file(tensors, str(src / 'adapter_model.safetensors'))
            (src / 'adapter_config.json').write_text(json.dumps({'r': 4, 'target_modules': 'x'}))
            count, modules = subset_adapter(src, d / 'attn', ('q_proj',))
            self.assertEqual((count, modules), (4, 2))
            config = json.loads((d / 'attn' / 'adapter_config.json').read_text())
            self.assertIn(r'layers\.1\.self_attn\.q_proj', config['target_modules'])
            self.assertNotIn('down_proj', config['target_modules'])


if __name__ == '__main__':
    unittest.main()
