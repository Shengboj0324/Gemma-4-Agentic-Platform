"""Worker and supervisor must derive the checkpoint-bound identity identically.

A hand-kept copy in the supervisor once kept 'attention': 'eager' after the
worker moved to SDPA, so a correctly completed GPU run was rejected afterwards.
"""
import unittest

from scripts import run_corpus_training, run_corpus_training_worker as worker


class ExecutionIdentityTests(unittest.TestCase):
    def test_supervisor_uses_the_worker_builder(self):
        self.assertIs(run_corpus_training.build_execution_config, worker.build_execution_config)

    def test_identity_carries_the_memory_policy(self):
        identity = worker.build_execution_config('a' * 64, {'torch': '2.10.0'})
        self.assertEqual(identity['attention'], {'implementation': 'sdpa', 'math': False,
                                                 'cudnn': False, 'flash': True, 'mem_efficient': True})
        self.assertEqual(identity['base_representation'], 'packed_w4_group32_dequantized_per_use')
        self.assertEqual(identity['loss'], {'kind': 'chunked_causal', 'chunk_tokens': 1024})
        for name in ('zenithsync/packed_base.py', 'zenithsync/chunked_loss.py'):
            self.assertIn(name, identity['sources'])


if __name__ == '__main__':
    unittest.main()
