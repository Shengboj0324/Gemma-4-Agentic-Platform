"""Windowed sliding attention against dense masked SDPA and transformers' own paths."""

import os
from pathlib import Path
import tempfile
import unittest

from tests.test_packed_base_torch import TORCH, batch, build_checkpoint


def dense_reference(torch, q, k, v, window, scale):
    length = q.shape[2]
    positions = torch.arange(length)
    delta = positions[:, None] - positions[None, :]
    mask = (delta >= 0) & (delta < window)  # transformers: kv <= q and kv > q - window
    return torch.nn.functional.scaled_dot_product_attention(q, k, v, attn_mask=mask, scale=scale)


@unittest.skipUnless(os.environ.get('ZENITHSYNC_TEST_TORCH') == '1', 'Explicit Torch runtime required')
class WindowedKernelTests(unittest.TestCase):
    def test_matches_dense_masked_attention_values_and_gradients(self):
        import torch
        from zenithsync.windowed_attention import windowed_attention
        torch.manual_seed(3)
        # Lengths below, at, just above, at a multiple of, and off a multiple of the window.
        for length, window in [(5, 8), (8, 8), (9, 8), (32, 8), (37, 8), (40, 16), (3, 1), (17, 4)]:
            shape = (2, 3, length, 4)
            inputs = [torch.randn(shape, dtype=torch.float64, requires_grad=True) for _ in range(3)]
            copies = [t.detach().clone().requires_grad_(True) for t in inputs]
            actual = windowed_attention(*inputs, window=window, scale=0.7)
            expected = dense_reference(torch, *copies, window, 0.7)
            torch.testing.assert_close(actual, expected, rtol=1e-12, atol=1e-12, msg=f'{length}/{window}')
            weights = torch.randn(shape, dtype=torch.float64)
            (actual * weights).sum().backward()
            (expected * weights).sum().backward()
            for a, b in zip(inputs, copies):
                torch.testing.assert_close(a.grad, b.grad, rtol=1e-11, atol=1e-11, msg=f'{length}/{window}')

    def test_band_mask_is_the_transformers_rule_in_block_coordinates(self):
        import torch
        from zenithsync.windowed_attention import band_mask
        window = 5
        mask = band_mask(window, 'cpu')
        for row in range(window):
            for column in range(2 * window):
                distance = (window + row) - column  # query position minus key position
                self.assertEqual(bool(mask[row, column]), 0 <= distance < window)

    def test_rejects_inconsistent_inputs(self):
        import torch
        from zenithsync.windowed_attention import windowed_attention
        q = torch.zeros(1, 2, 8, 4)
        for kwargs in [dict(window=0), dict(window=2.0)]:
            with self.assertRaises(ValueError):
                windowed_attention(q, q, q, scale=1.0, **kwargs)
        with self.assertRaises(ValueError):
            windowed_attention(q, torch.zeros(1, 1, 8, 4), q, window=4, scale=1.0)

    def test_interface_refuses_masks_dropout_non_causal_and_packing(self):
        import torch
        from zenithsync.windowed_attention import windowed_sdpa_forward
        module = torch.nn.Module()
        module.is_causal, module.num_key_value_groups = True, 1
        q = torch.zeros(1, 2, 8, 4)
        for args, kwargs in [((torch.ones(1, 1, 8, 8, dtype=torch.bool),), {}),
                             ((None,), {'dropout': 0.1}),
                             ((None,), {'cu_seq_lens_q': torch.tensor([0, 8])}),
                             ((None,), {'output_attentions': True})]:
            with self.assertRaises(ValueError):
                windowed_sdpa_forward(module, q, q, q, *args, sliding_window=4, **kwargs)
        module.is_causal = False
        with self.assertRaises(ValueError):
            windowed_sdpa_forward(module, q, q, q, None, sliding_window=4)


@unittest.skipUnless(TORCH, 'Explicit Torch runtime with compressed-tensors required')
class WindowedModelTests(unittest.TestCase):
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
        cls.checkpoint = Path(cls.tmp.name) / 'base'
        cls.shapes = expected_projections(build_checkpoint(cls.checkpoint))

    @classmethod
    def tearDownClass(cls):
        import torch
        threads, deterministic = cls._saved_torch
        torch.set_num_threads(threads)
        torch.use_deterministic_algorithms(deterministic)
        cls.tmp.cleanup()

    def load(self, attention, dtype=None):
        import torch
        from transformers import Gemma4ForConditionalGeneration, CompressedTensorsConfig
        from zenithsync import windowed_attention
        windowed_attention.register()
        model = Gemma4ForConditionalGeneration.from_pretrained(self.checkpoint, local_files_only=True,
            dtype=torch.bfloat16, quantization_config=CompressedTensorsConfig(run_compressed=False),
            attn_implementation=attention)
        return model if dtype is None else model.to(dtype)

    def test_model_outputs_and_gradients_match_transformers_masks(self):
        # Sliding window 8 against a 40-token sequence, so the window binds.
        import torch
        from zenithsync.windowed_attention import IMPLEMENTATION
        data = batch(torch, length=40, supervised_from=6)
        results = {}
        for attention in ('eager', 'sdpa', IMPLEMENTATION):
            model = self.load(attention, torch.float64).eval()
            embedding = model.get_input_embeddings().weight
            embedding.requires_grad_(True)
            output = model(**data)
            output.loss.backward()
            results[attention] = (output.logits.detach(), output.loss.detach(), embedding.grad)
        # Against SDPA with transformers' mask: float64 throughout, so tight.
        for actual, expected in zip(results[IMPLEMENTATION], results['sdpa']):
            torch.testing.assert_close(actual, expected, rtol=1e-10, atol=1e-10)
        # Eager upcasts only its softmax to float32, so it agrees to float32 precision.
        for actual, expected in zip(results[IMPLEMENTATION], results['eager']):
            torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-5)

    def test_window_binds_in_this_fixture(self):
        # Guard against a vacuous equivalence: full causal attention must differ.
        import torch
        from zenithsync.windowed_attention import windowed_attention
        torch.manual_seed(1)
        q, k, v = (torch.randn(1, 2, 40, 4, dtype=torch.float64) for _ in range(3))
        full = torch.nn.functional.scaled_dot_product_attention(q, k, v, is_causal=True)
        self.assertGreater((windowed_attention(q, k, v, window=8, scale=None) - full).abs().max().item(), 1e-3)
        self.assertEqual(self.load('sdpa').config.get_text_config().sliding_window, 8)

    def test_packed_training_gradients_with_windowed_attention_match_sdpa(self):
        # bf16 end to end on the packed base, as the worker runs. The two paths
        # reduce over keys in different blocks, so agreement is to bf16 rounding;
        # gradients are compared directly rather than after an optimizer step,
        # because Adam normalises tiny gradients into learning-rate-sized moves.
        import torch
        from transformers import Gemma4ForConditionalGeneration
        from zenithsync.chunked_loss import install_chunked_causal_loss
        from zenithsync.gemma_training import attach_training_adapter
        from zenithsync.packed_base import load_packed_base
        from zenithsync.windowed_attention import IMPLEMENTATION
        data = batch(torch, length=48, supervised_from=10)
        outcomes = []
        for attention in ('sdpa', IMPLEMENTATION):
            base = load_packed_base(Gemma4ForConditionalGeneration, self.checkpoint, self.shapes,
                                    device='cpu', attn_implementation=attention)
            torch.manual_seed(11)
            model = attach_training_adapter(install_chunked_causal_loss(base, chunk_tokens=8), self.shapes)
            with torch.no_grad():
                for name, value in model.named_parameters():
                    if name.endswith('lora_B.default.weight'):
                        value.normal_(0, 0.02, generator=torch.Generator().manual_seed(len(name)))
            loss = model(**data).loss
            loss.backward()
            grads = torch.cat([p.grad.flatten() for n, p in sorted(model.named_parameters()) if p.requires_grad])
            outcomes.append((loss.item(), grads))
        (sdpa_loss, sdpa_grads), (windowed_loss, windowed_grads) = outcomes
        self.assertAlmostEqual(windowed_loss, sdpa_loss, delta=2e-3 * abs(sdpa_loss))
        relative = ((windowed_grads - sdpa_grads).norm() / sdpa_grads.norm()).item()
        cosine = torch.nn.functional.cosine_similarity(windowed_grads, sdpa_grads, dim=0).item()
        # Measured: 0.68% / 0.99998. For scale, transformers' own eager and SDPA
        # paths disagree by 8.9% / 0.996 on this same fixture in bf16.
        self.assertLess(relative, 1e-2)
        self.assertGreater(cosine, 0.9999)

    def test_padded_batch_is_refused_under_windowed_attention(self):
        import torch
        from transformers import Gemma4ForConditionalGeneration
        from zenithsync.chunked_loss import install_chunked_causal_loss
        from zenithsync.packed_base import load_packed_base
        from zenithsync.windowed_attention import IMPLEMENTATION
        base = install_chunked_causal_loss(load_packed_base(Gemma4ForConditionalGeneration,
            self.checkpoint, self.shapes, device='cpu', attn_implementation=IMPLEMENTATION))
        data = batch(torch)
        data['attention_mask'][:, -3:] = 0
        data['labels'][:, -3:] = -100
        with self.assertRaises(ValueError):
            base(**data)

    def test_unqualified_attention_implementation_is_refused(self):
        from transformers import Gemma4ForConditionalGeneration
        from zenithsync.packed_base import load_packed_base
        with self.assertRaises(ValueError):
            load_packed_base(Gemma4ForConditionalGeneration, self.checkpoint, self.shapes,
                             device='cpu', attn_implementation='eager')


if __name__ == '__main__':
    unittest.main()
