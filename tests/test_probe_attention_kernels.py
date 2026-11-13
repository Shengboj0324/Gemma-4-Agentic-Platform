import unittest

from scripts.probe_attention_kernels import layer_shapes


def config(**overrides):
    text = {'num_attention_heads': 32, 'num_key_value_heads': 16, 'num_global_key_value_heads': 4,
            'head_dim': 256, 'global_head_dim': 512, 'attention_k_eq_v': True, 'sliding_window': 1024,
            'layer_types': ['sliding_attention'] * 5 + ['full_attention']}
    text.update(overrides)
    return {'text_config': text}


class LayerShapeTests(unittest.TestCase):
    def test_each_layer_kind_gets_its_own_head_geometry(self):
        self.assertEqual(layer_shapes(config()), {
            'full_attention': {'heads': 32, 'kv_heads': 4, 'head_dim': 512, 'window': None},
            'sliding_attention': {'heads': 32, 'kv_heads': 16, 'head_dim': 256, 'window': 1024}})

    def test_full_layers_without_shared_kv_use_ordinary_kv_heads(self):
        self.assertEqual(layer_shapes(config(attention_k_eq_v=False))['full_attention']['kv_heads'], 16)

    def test_unknown_layer_type_rejected(self):
        with self.assertRaises(ValueError):
            layer_shapes(config(layer_types=['chunked_attention']))


if __name__ == '__main__':
    unittest.main()
