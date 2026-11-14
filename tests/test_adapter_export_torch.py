"""A trained checkpoint exports to a PEFT adapter that reloads to identical outputs."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.test_packed_base_torch import TORCH, batch, build_checkpoint

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(TORCH, 'Explicit Torch runtime with compressed-tensors required')
class AdapterExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import torch
        from zenithsync.quantized_layout import expected_projections
        # Global torch state: saved here and restored in tearDownClass, because a
        # leaked determinism flag broke a later fresh-process resume test.
        cls._saved_torch = (torch.get_num_threads(), torch.are_deterministic_algorithms_enabled())
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name).resolve()  # macOS /var is a symlink; storage refuses those
        cls.checkpoint = cls.root / 'base'
        cls.shapes = expected_projections(build_checkpoint(cls.checkpoint))

    @classmethod
    def tearDownClass(cls):
        import torch
        threads, deterministic = cls._saved_torch
        torch.set_num_threads(threads)
        torch.use_deterministic_algorithms(deterministic)
        cls.tmp.cleanup()

    def base(self):
        from transformers import Gemma4ForConditionalGeneration
        from zenithsync.packed_base import load_packed_base
        from zenithsync.windowed_attention import IMPLEMENTATION
        return load_packed_base(Gemma4ForConditionalGeneration, self.checkpoint, self.shapes,
                                device='cpu', attn_implementation=IMPLEMENTATION)

    def trained(self):
        import torch
        from zenithsync.chunked_loss import install_chunked_causal_loss
        from zenithsync.corpus_optimization import token_weighted_step
        from zenithsync.gemma_training import attach_training_adapter
        torch.manual_seed(5)
        model = attach_training_adapter(install_chunked_causal_loss(self.base(), chunk_tokens=8), self.shapes)
        optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                      lr=1e-2, weight_decay=0, foreach=False, fused=False)
        for _ in range(2):  # two steps, so lora_B is nonzero and the adapter matters
            token_weighted_step(model, optimizer, [batch(torch, length=32, supervised_from=8)])
        return model

    def test_export_reloads_to_identical_outputs_and_config(self):
        import torch
        from peft import PeftModel
        from zenithsync.adapter_export import lora_config
        from zenithsync.checkpoint_storage import save_checkpoint
        model = self.trained()
        payload = {'schema_version': 1, 'bindings': {'fixture': True}, 'cursor': {'completed_updates': 2},
                   'adapter': {n: p.detach().cpu().clone() for n, p in model.named_parameters() if p.requires_grad}}
        path = self.root / 'update-00000002.pt'
        identity = save_checkpoint(path, payload, max_bytes=64 * 1024**2)
        config = self.root / 'base' / 'config.json'
        out = self.root / 'export'
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/export_adapter_checkpoint.py'),
                                 '--checkpoint', str(path), '--checkpoint-sha256', identity['sha256'],
                                 '--checkpoint-size', str(identity['size_bytes']),
                                 '--model-config', str(config), '--output', str(out)],
                                capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        receipt = json.loads((out / 'receipt.json').read_text())
        self.assertEqual(receipt['tensors'], 2 * len(self.shapes))
        self.assertEqual(receipt['parameters'], 4 * sum(a + b for a, b in self.shapes.values()))

        trained = model.peft_config['default'].to_dict()
        exported = lora_config(self.shapes).to_dict()
        for field in ('r', 'lora_alpha', 'lora_dropout', 'bias', 'target_modules', 'use_rslora', 'use_dora'):
            self.assertEqual(exported[field], trained[field], field)

        restored = PeftModel.from_pretrained(self.base(), str(out / 'adapter')).eval()
        model.eval()
        inputs = {k: v for k, v in batch(torch, length=32).items() if k != 'labels'}
        with torch.no_grad():
            expected = model(**inputs).logits
            actual = restored(**inputs).logits
            with restored.disable_adapter():
                plain = restored(**inputs).logits
        self.assertTrue(torch.equal(actual, expected))
        self.assertGreater((actual - plain).abs().max().item(), 0)  # the adapter is live

    def test_refuses_existing_output_wrong_identity_and_bad_coverage(self):
        import torch
        from zenithsync.adapter_export import adapter_tensors
        from zenithsync.checkpoint_storage import save_checkpoint
        path = self.root / 'bad.pt'
        identity = save_checkpoint(path, {'schema_version': 1, 'adapter': {}}, max_bytes=1024**2)
        common = [sys.executable, str(ROOT / 'scripts/export_adapter_checkpoint.py'), '--checkpoint', str(path),
                  '--checkpoint-size', str(identity['size_bytes']),
                  '--model-config', str(self.root / 'base' / 'config.json')]
        wrong = subprocess.run(common + ['--checkpoint-sha256', '0' * 64, '--output', str(self.root / 'x1')],
                               capture_output=True, text=True, timeout=120)
        self.assertNotEqual(wrong.returncode, 0)
        self.assertFalse((self.root / 'x1').exists())
        empty = subprocess.run(common + ['--checkpoint-sha256', identity['sha256'], '--output', str(self.root / 'x2')],
                               capture_output=True, text=True, timeout=120)
        self.assertNotEqual(empty.returncode, 0)
        self.assertIn('coverage', empty.stderr)
        (self.root / 'x3').mkdir()
        exists = subprocess.run(common + ['--checkpoint-sha256', identity['sha256'], '--output', str(self.root / 'x3')],
                                capture_output=True, text=True, timeout=120)
        self.assertIn('FileExistsError', exists.stderr)
        name = sorted(self.shapes)[0]
        rows, columns = self.shapes[name]
        good = {f'base_model.model.{n}.lora_A.default.weight': torch.zeros(4, c) for n, (r, c) in self.shapes.items()}
        good.update({f'base_model.model.{n}.lora_B.default.weight': torch.zeros(r, 4) for n, (r, c) in self.shapes.items()})
        self.assertEqual(len(adapter_tensors(good, self.shapes)), 2 * len(self.shapes))
        for key, value in [(f'base_model.model.{name}.lora_A.default.weight', torch.zeros(4, columns + 1)),
                           (f'base_model.model.{name}.lora_A.default.weight', torch.zeros(4, columns, dtype=torch.bfloat16)),
                           (f'base_model.model.{name}.lora_B.default.weight', torch.full((rows, 4), float('nan')))]:
            with self.assertRaises(ValueError):
                adapter_tensors({**good, key: value}, self.shapes)


if __name__ == '__main__':
    unittest.main()
