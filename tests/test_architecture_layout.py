import copy
import unittest
from zenithsync.architecture_layout import validate_architecture


class ArchitectureLayoutTests(unittest.TestCase):
    def setUp(self):
        self.header = {'p.weight_shape': {'dtype': 'I64', 'shape': [2]},
                       'p.weight_packed': {'dtype': 'I32', 'shape': [2, 4]},
                       'p.weight_scale': {'dtype': 'BF16', 'shape': [2, 1]},
                       'norm.weight': {'dtype': 'BF16', 'shape': [32]}}
        self.expected = {'p.weight': [2, 32], 'norm.weight': [32]}

    def check(self, header=None, expected=None, original=None):
        return validate_architecture(self.header if header is None else header,
            self.expected if expected is None else expected, {'p': (2, 32)},
            {'p': (2, 32)} if original is None else original)

    def test_complete_coverage_and_no_input_mutation(self):
        before = copy.deepcopy(self.header)
        self.assertEqual(self.check(), {'quantized_projections': 1, 'unquantized_tensors': 1,
            'checkpoint_tensors': 4, 'logical_model_tensors': 2})
        self.assertEqual(self.header, before)

    def test_missing_and_extra_tensors(self):
        for name in self.header:
            header = copy.deepcopy(self.header); del header[name]
            with self.assertRaises(ValueError): self.check(header)
        with self.assertRaises(ValueError): self.check({**self.header, 'extra': {}})

    def test_unquantized_shape_and_dtype(self):
        for key, value in [('shape', [31]), ('dtype', 'F32')]:
            header = copy.deepcopy(self.header); header['norm.weight'][key] = value
            with self.assertRaises(ValueError): self.check(header)

    def test_independent_quantized_dimensions(self):
        with self.assertRaises(ValueError): self.check(expected={**self.expected, 'p.weight': [3, 32]})
        with self.assertRaises(ValueError): self.check(original={'p': (3, 32)})
        with self.assertRaises(ValueError): self.check(original={})
        for suffix in ['weight_shape', 'weight_packed', 'weight_scale']:
            header = copy.deepcopy(self.header); header['p.' + suffix]['shape'] = [9]
            with self.assertRaises(ValueError): self.check(header)


if __name__ == '__main__': unittest.main()
