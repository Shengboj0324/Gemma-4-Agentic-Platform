import unittest

from scripts.verify_training_round import loss_of, thirds


class RoundGateTests(unittest.TestCase):
    def test_loss_key_variants(self):
        self.assertEqual(loss_of({'loss': 0.5}), 0.5)
        self.assertEqual(loss_of({'token_weighted_loss': 0.25, 'tokens': 9}), 0.25)
        self.assertEqual(loss_of({'mean_supervised_loss': 0.75}), 0.75)
        self.assertIsNone(loss_of({'tokens': 3}))

    def test_thirds(self):
        self.assertEqual(thirds([3.0, 3.0, 2.0, 2.0, 1.0, 1.0]), (3.0, 1.0))
        self.assertEqual(thirds([2.0]), (2.0, 2.0))


if __name__ == '__main__':
    unittest.main()
