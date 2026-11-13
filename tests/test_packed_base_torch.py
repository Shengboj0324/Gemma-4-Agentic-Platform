"""Packed W4 base, chunked loss and SDPA policy against the decompressed path.

Builds a reduced Gemma 4 conditional-generation checkpoint in the exact
compressed-tensors format the 31B model ships in (int4, symmetric, group 32,
pack-quantized), then holds the packed path to the dense path the first GPU
session used. No downloads; CPU only.
"""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


# compressed-tensors is pinned in the training lock only; other full-stack
# environments (serving, tokenizer) legitimately lack it.
TORCH = (os.environ.get('ZENITHSYNC_TEST_TORCH') == '1'
         and importlib.util.find_spec('compressed_tensors') is not None)


def build_checkpoint(directory, *, softcap=30.0, seed=7301):
    import torch
    from transformers import Gemma4Config, Gemma4TextConfig, Gemma4ForConditionalGeneration
    from compressed_tensors.quantization import (
        QuantizationConfig, QuantizationScheme, QuantizationArgs, apply_quantization_config)
    from compressed_tensors.compressors import ModelCompressor
    torch.manual_seed(seed)
    text = Gemma4TextConfig(vocab_size=96, hidden_size=64, intermediate_size=128,
        num_hidden_layers=3, num_attention_heads=4, num_key_value_heads=2,
        num_global_key_value_heads=1, head_dim=16, global_head_dim=32,
        hidden_size_per_layer_input=0, attention_k_eq_v=True, enable_moe_block=False,
        num_kv_shared_layers=0, attention_bias=False,
        layer_types=['sliding_attention', 'sliding_attention', 'full_attention'],
        max_position_embeddings=128, sliding_window=8, use_cache=False,
        attention_dropout=0.0, final_logit_softcapping=softcap)
    config = Gemma4Config(text_config=text.to_dict(), vision_config=None, audio_config=None)
    model = Gemma4ForConditionalGeneration(config).to(torch.bfloat16)
    quantization = QuantizationConfig(config_groups={'group_0': QuantizationScheme(
        targets=['Linear'], weights=QuantizationArgs(num_bits=4, type='int', symmetric=True,
        strategy='group', group_size=32))}, ignore=['lm_head'], format='pack-quantized',
        quantization_status='frozen')
    apply_quantization_config(model, quantization)
    with torch.no_grad():
        for module in model.modules():
            if hasattr(module, 'weight_scale'):
                scale = module.weight.reshape(module.weight.shape[0], -1, 32).abs().amax(-1)
                module.weight_scale.copy_(scale.clamp_min(1e-6) / 7)
    compressor = ModelCompressor(quantization_config=quantization, force_compression_format='pack-quantized')
    compressor.compress_model(model)
    model.save_pretrained(directory)
    compressor.update_config(str(directory))
    return json.loads((Path(directory) / 'config.json').read_text())


def batch(torch, length=40, supervised_from=12):
    ids = torch.arange(2, 2 + length).remainder(90).add(2).unsqueeze(0)
    labels = ids.clone()
    labels[:, :supervised_from] = -100
    return {'input_ids': ids, 'labels': labels, 'attention_mask': torch.ones_like(ids)}


@unittest.skipUnless(TORCH, 'Explicit Torch runtime with compressed-tensors required')
class PackedBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import torch
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.checkpoint = Path(cls.tmp.name) / 'base'
        from zenithsync.quantized_layout import expected_projections
        cls.config = build_checkpoint(cls.checkpoint)
        cls.shapes = expected_projections(cls.config)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def dense(self, attention='eager'):
        import torch
        from transformers import Gemma4ForConditionalGeneration, CompressedTensorsConfig
        return Gemma4ForConditionalGeneration.from_pretrained(self.checkpoint, local_files_only=True,
            dtype=torch.bfloat16, quantization_config=CompressedTensorsConfig(run_compressed=False),
            attn_implementation=attention)

    def packed(self):
        from transformers import Gemma4ForConditionalGeneration
        from zenithsync.packed_base import load_packed_base
        return load_packed_base(Gemma4ForConditionalGeneration, self.checkpoint, self.shapes, device='cpu')

    def test_layout_contract_matches_reduced_checkpoint(self):
        # 3 layers x 7 projections, minus v_proj on the full-attention layer
        # (attention_k_eq_v). Transformers forces the last layer to be full.
        self.assertEqual(len(self.shapes), 20)

    def test_dequantize_matches_compressed_tensors_bit_for_bit(self):
        import torch
        from compressed_tensors.compressors.pack_quantized.helpers import pack_to_int32, unpack_from_int32
        from compressed_tensors.quantization.lifecycle.forward import dequantize
        from zenithsync.packed_base import dequantize_packed
        generator = torch.Generator().manual_seed(5)
        for rows, columns in [(7, 96), (64, 32), (3, 160)]:
            values = torch.randint(-8, 8, (rows, columns), generator=generator, dtype=torch.int8)
            scale = (torch.rand(rows, columns // 32, generator=generator) * 3 + 1e-3).to(torch.bfloat16)
            packed = pack_to_int32(values, 4)
            expected = dequantize(x_q=unpack_from_int32(packed, 4, torch.Size([rows, columns])), scale=scale)
            actual = dequantize_packed(packed, scale, rows, columns)
            self.assertEqual(actual.dtype, torch.bfloat16)
            self.assertTrue(torch.equal(actual, expected), (rows, columns))

    def test_dequantize_rejects_inconsistent_shapes(self):
        import torch
        from zenithsync.packed_base import dequantize_packed
        packed = torch.zeros(4, 4, dtype=torch.int32)
        scale = torch.ones(4, 1, dtype=torch.bfloat16)
        for args in [(packed.float(), scale, 4, 32), (packed, scale, 4, 40), (packed, scale, 5, 32),
                     (packed, torch.ones(4, 2, dtype=torch.bfloat16), 4, 32)]:
            with self.assertRaises(ValueError):
                dequantize_packed(*args)

    def test_packed_load_reconstructs_the_decompressed_model_exactly(self):
        import torch
        from zenithsync.packed_base import packed_linear_class
        dense, packed = self.dense(), self.packed()
        modules = dict(packed.named_modules())
        dense_state = dense.state_dict()
        for name in self.shapes:
            module = modules[name]
            self.assertIsInstance(module, packed_linear_class())
            self.assertIsNone(module.weight)
            self.assertTrue(torch.equal(module.dense_weight(), dense_state[name + '.weight']), name)
        packed_state = packed.state_dict()
        shared = [key for key in dense_state if not any(key.startswith(n + '.') for n in self.shapes)]
        self.assertTrue(shared)
        for key in shared:
            self.assertTrue(torch.equal(packed_state[key], dense_state[key]), key)
        self.assertFalse(any(p.requires_grad for p in packed.parameters()))
        self.assertEqual(packed.config._attn_implementation, 'sdpa')

    def test_packed_forward_and_input_gradient_equal_dense(self):
        import torch
        dense, packed = self.dense('sdpa'), self.packed()
        data = batch(torch)
        outputs = []
        for model in (dense, packed):
            model.eval()
            # The input embedding sits below every projection, so its gradient
            # has passed backward through all of them.
            embedding = model.get_input_embeddings().weight
            embedding.requires_grad_(True)
            output = model(**data)
            output.loss.backward()
            outputs.append((output, embedding.grad))
        (out_dense, grad_dense), (out_packed, grad_packed) = outputs
        self.assertTrue(torch.equal(out_packed.logits, out_dense.logits))
        self.assertEqual(out_packed.loss.item(), out_dense.loss.item())
        self.assertGreater(grad_dense.abs().sum().item(), 0)
        self.assertTrue(torch.equal(grad_packed, grad_dense))

    def test_chunked_loss_equals_transformers_loss_and_gradients(self):
        import torch
        from zenithsync.chunked_loss import chunked_causal_loss
        model = self.dense('sdpa').train()
        model.lm_head.weight.requires_grad_(False)
        data = batch(torch, length=60, supervised_from=9)
        data['labels'][:, 30:35] = -100
        hidden_weight = model.model.language_model.norm.weight
        hidden_weight.requires_grad_(True)
        reference = model(**data).loss
        (expected,) = torch.autograd.grad(reference, hidden_weight)
        for chunk in (1, 7, 16, 1024):
            loss = chunked_causal_loss(model, chunk_tokens=chunk, **data)
            (actual,) = torch.autograd.grad(loss, hidden_weight)
            torch.testing.assert_close(loss, reference, rtol=1e-6, atol=1e-6)
            torch.testing.assert_close(actual, expected, rtol=1e-2, atol=1e-3)

    def test_chunked_loss_skips_unsupervised_chunks(self):
        import torch
        from zenithsync.chunked_loss import chunked_causal_loss
        model = self.dense('sdpa').eval()
        data = batch(torch, length=64, supervised_from=50)
        calls = []
        original = model.lm_head.forward
        model.lm_head.forward = lambda x: (calls.append(x.shape[1]), original(x))[1]
        loss = chunked_causal_loss(model, chunk_tokens=16, **data)
        self.assertEqual(calls, [15])  # positions 48..62; 0..47 hold no target
        model.lm_head.forward = original
        torch.testing.assert_close(loss, model(**data).loss, rtol=1e-6, atol=1e-6)

    def test_installed_forward_is_strict(self):
        import torch
        from zenithsync.chunked_loss import install_chunked_causal_loss
        model = install_chunked_causal_loss(self.dense('sdpa'), chunk_tokens=8)
        data = batch(torch)
        self.assertIsNone(model(**data).logits)
        unlabelled = model(input_ids=data['input_ids'], attention_mask=data['attention_mask'])
        self.assertEqual(tuple(unlabelled.logits.shape), (1, 40, 96))
        with self.assertRaises(ValueError):
            model(pixel_values=torch.zeros(1), **data)
        with self.assertRaises(ValueError):
            install_chunked_causal_loss(model)
        empty = dict(data, labels=torch.full_like(data['labels'], -100))
        with self.assertRaises(ValueError):
            model(**empty)
        with self.assertRaises(ValueError):
            install_chunked_causal_loss(torch.nn.Linear(2, 2))

    def test_coverage_mismatch_is_rejected(self):
        from transformers import Gemma4ForConditionalGeneration
        from zenithsync.packed_base import load_packed_base
        name = sorted(self.shapes)[0]
        fewer = {key: value for key, value in self.shapes.items() if key != name}
        more = dict(self.shapes, **{'model.language_model.layers.0.mlp.extra_proj': (4, 4)})
        wrong = dict(self.shapes, **{name: (1, 1)})
        for shapes in (fewer, more, wrong):
            with self.assertRaises(ValueError):
                load_packed_base(Gemma4ForConditionalGeneration, self.checkpoint, shapes, device='cpu')

    def test_adapter_training_over_packed_base_matches_dense_and_freezes_base(self):
        import torch
        from zenithsync.adapter_checkpoint import frozen_state
        from zenithsync.chunked_loss import install_chunked_causal_loss
        from zenithsync.corpus_optimization import token_weighted_step
        from zenithsync.gemma_training import attach_training_adapter
        from zenithsync.packed_base import packed_linear_class

        def adapted(base):
            torch.manual_seed(11)
            return attach_training_adapter(base, self.shapes)

        dense = adapted(self.dense('sdpa'))
        packed = adapted(install_chunked_causal_loss(self.packed(), chunk_tokens=8))
        names = sorted(n for n, p in dense.named_parameters() if p.requires_grad)
        self.assertEqual(names, sorted(n for n, p in packed.named_parameters() if p.requires_grad))
        self.assertEqual(len(names), 2 * len(self.shapes))
        packed_params = dict(packed.named_parameters())
        with torch.no_grad():
            for name, value in dense.named_parameters():
                if value.requires_grad:
                    self.assertEqual(packed_params[name].dtype, value.dtype)
                    packed_params[name].copy_(value)  # identical starting adapters
            for name, value in dense.named_parameters():
                if name.endswith('lora_B.default.weight'):
                    value.normal_(0, 0.02, generator=torch.Generator().manual_seed(len(name)))
                    packed_params[name].copy_(value)
        self.assertTrue(any(isinstance(m, packed_linear_class()) for m in packed.modules()))
        frozen = frozen_state(packed)
        data = batch(torch, length=48, supervised_from=10)

        def step(model):
            optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                          lr=1e-3, weight_decay=0, foreach=False, fused=False)
            return token_weighted_step(model, optimizer, [dict(data)])

        expected, actual = step(dense), step(packed)
        self.assertAlmostEqual(actual['token_mean_loss'], expected['token_mean_loss'], places=5)
        dense_params = dict(dense.named_parameters())
        for name in names:
            torch.testing.assert_close(packed_params[name], dense_params[name], rtol=1e-4, atol=1e-5)
        self.assertEqual(frozen, frozen_state(packed))
        self.assertTrue(all(p.grad is None for p in packed.parameters() if not p.requires_grad))

    def test_one_update_qualification_and_reload_over_packed_base(self):
        import torch
        from zenithsync.chunked_loss import install_chunked_causal_loss
        from zenithsync.training_pilot import qualify_adapter
        data = batch(torch, length=32, supervised_from=8)
        with tempfile.TemporaryDirectory() as directory:
            receipt = qualify_adapter(
                load_base=lambda: install_chunked_causal_loss(self.packed(), chunk_tokens=8),
                batch=data, target_shapes=self.shapes, output=Path(directory) / 'q')
        self.assertEqual(receipt['status'], 'one_update_and_reload_passed')
        self.assertEqual(receipt['reload_max_abs_error'], 0.0)
        self.assertGreater(receipt['adapter_effect_max_abs'], 0)


def accelerator():
    if not TORCH:
        return None
    import torch
    if torch.cuda.is_available():
        return 'cuda:0'
    return 'mps' if torch.backends.mps.is_available() else None


@unittest.skipUnless(accelerator(), 'CUDA or MPS device required')
class AcceleratorPlacementTests(unittest.TestCase):
    def test_adapters_follow_the_packed_base_onto_the_device(self):
        # PEFT places a new adapter by the base layer's weight, or its qweight
        # when there is none. On CPU a misplaced adapter is invisible; here it
        # would leave LoRA on the host and fail the single-device check.
        import torch
        from transformers import Gemma4ForConditionalGeneration
        from zenithsync.chunked_loss import install_chunked_causal_loss
        from zenithsync.gemma_training import attach_training_adapter
        from zenithsync.packed_base import load_packed_base
        from zenithsync.quantized_layout import expected_projections
        device = accelerator()
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / 'base'
            shapes = expected_projections(build_checkpoint(checkpoint))
            base = load_packed_base(Gemma4ForConditionalGeneration, checkpoint, shapes, device=device)
            model = attach_training_adapter(install_chunked_causal_loss(base, chunk_tokens=8), shapes)
        self.assertEqual({p.device.type for p in model.parameters()}, {torch.device(device).type})
        self.assertEqual({p.dtype for p in model.parameters() if p.requires_grad}, {torch.float32})
        data = {key: value.to(device) for key, value in batch(torch).items()}
        loss = model(**data).loss
        loss.backward()
        self.assertTrue(torch.isfinite(loss).item())
        self.assertTrue(all(p.grad is not None for p in model.parameters() if p.requires_grad))


@unittest.skipUnless(TORCH, 'Explicit Torch runtime required')
class AttentionPolicyTests(unittest.TestCase):
    def test_restriction_disables_math_and_cudnn_and_is_reversible(self):
        import torch
        from zenithsync.packed_base import restrict_attention_kernels
        backends = torch.backends.cuda
        saved = (backends.math_sdp_enabled(), backends.cudnn_sdp_enabled(),
                 backends.flash_sdp_enabled(), backends.mem_efficient_sdp_enabled())
        try:
            self.assertEqual(restrict_attention_kernels(),
                             {'math': False, 'cudnn': False, 'flash': True, 'mem_efficient': True})
        finally:
            for setter, value in zip((backends.enable_math_sdp, backends.enable_cudnn_sdp,
                                      backends.enable_flash_sdp, backends.enable_mem_efficient_sdp), saved):
                setter(value)


if __name__ == '__main__':
    unittest.main()
