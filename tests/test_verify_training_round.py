import unittest

from scripts.verify_training_round import chain_sessions, loss_of, thirds


def worker(first, count, status, bindings='b'):
    return {'status': 'corpus_session_returned', 'bindings': bindings, 'execution_config': 'e',
            'session': {'status': status, 'checkpoints': [
                {'cursor': {'completed_updates': first + i}} for i in range(count)]}}


class RoundGateTests(unittest.TestCase):
    def test_loss_key_variants(self):
        self.assertEqual(loss_of({'loss': 0.5}), 0.5)
        self.assertEqual(loss_of({'token_weighted_loss': 0.25, 'tokens': 9}), 0.25)
        self.assertEqual(loss_of({'mean_supervised_loss': 0.75}), 0.75)
        self.assertIsNone(loss_of({'tokens': 3}))

    def test_thirds(self):
        self.assertEqual(thirds([3.0, 3.0, 2.0, 2.0, 1.0, 1.0]), (3.0, 1.0))
        self.assertEqual(thirds([2.0]), (2.0, 2.0))

    def test_single_session(self):
        checkpoints, problems = chain_sessions([worker(1, 39, 'schedule_complete')])
        self.assertEqual((len(checkpoints), problems), (39, []))

    def test_resumed_chain(self):
        checkpoints, problems = chain_sessions([worker(1, 34, 'checkpoint_budget'), worker(35, 5, 'schedule_complete')])
        self.assertEqual((len(checkpoints), problems), (39, []))
        self.assertEqual([c['cursor']['completed_updates'] for c in checkpoints], list(range(1, 40)))

    def test_chain_rejects_gap_overlap_and_identity_drift(self):
        self.assertTrue(chain_sessions([worker(1, 34, 'checkpoint_budget'), worker(36, 4, 'schedule_complete')])[1])
        self.assertTrue(chain_sessions([worker(1, 34, 'checkpoint_budget'), worker(34, 6, 'schedule_complete')])[1])
        self.assertTrue(chain_sessions([worker(1, 34, 'checkpoint_budget', 'x'), worker(35, 5, 'schedule_complete')])[1])
        self.assertTrue(chain_sessions([worker(1, 39, 'schedule_complete'), worker(40, 1, 'schedule_complete')])[1])


if __name__ == '__main__':
    unittest.main()
