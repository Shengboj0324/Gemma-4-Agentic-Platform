import unittest

from scripts.mask_corpus_thinking import IGNORE, mask_thinking

# token ids: 1 <|channel>, 2 <channel|>, 3 <|tool_call>; others are text
TEXT = {1: '<|channel>', 2: '<channel|>', 3: '<|tool_call>', 10: 'thought\n', 11: 'look', 12: '\n', 13: 'x', 14: '<turn|>'}
decode = lambda ids: ''.join(TEXT[i] for i in ids)
KW = dict(open_id=1, close_id=2, call_id=3, decode=decode)


def supervised(ids, start):
    return [IGNORE] * start + ids[start:]


class MaskThinkingTests(unittest.TestCase):
    def test_masks_each_block_and_nothing_else(self):
        ids = [13, 13, 1, 10, 11, 12, 2, 3, 13, 14, 13, 1, 10, 11, 12, 2, 3, 13, 14]
        labels = supervised(ids, 2)
        labels[10] = IGNORE  # a tool result token between turns
        out, blocks, masked, unsup = mask_thinking(ids, labels, **KW)
        self.assertEqual((blocks, masked, unsup), (2, 10, 0))
        self.assertEqual(out[2:7], [IGNORE] * 5)
        self.assertEqual(out[11:16], [IGNORE] * 5)
        self.assertEqual(out[7], 3)
        self.assertEqual([k for k, (a, b) in enumerate(zip(labels, out)) if a != b], [2, 3, 4, 5, 6, 11, 12, 13, 14, 15])

    def test_unsupervised_channel_text_is_left_alone(self):
        ids = [13, 1, 10, 11, 12, 2, 13, 1, 10, 11, 12, 2, 3, 14]
        labels = [IGNORE] * 7 + ids[7:]
        out, blocks, masked, unsup = mask_thinking(ids, labels, **KW)
        self.assertEqual((blocks, unsup), (1, 1))
        self.assertEqual(out[:7], labels[:7])

    def test_refuses_malformed_blocks(self):
        bad = {
            'unclosed': [1, 10, 11, 3, 14],
            'nested': [1, 10, 1, 11, 12, 2, 3],
            'no tool call after': [1, 10, 11, 12, 2, 13, 14],
            'not a thought block': [1, 11, 12, 2, 3],
            'stray close': [13, 2, 3, 14],
        }
        for name, ids in bad.items():
            with self.subTest(name), self.assertRaises(ValueError):
                mask_thinking(ids, list(ids), **KW)
        ids = [1, 10, 11, 12, 2, 3]
        partial = list(ids); partial[3] = IGNORE
        with self.assertRaisesRegex(ValueError, 'fully supervised'):
            mask_thinking(ids, partial, **KW)
        unsup_call = list(ids); unsup_call[5] = IGNORE
        with self.assertRaisesRegex(ValueError, 'supervised tool call'):
            mask_thinking(ids, unsup_call, **KW)

    def test_inner_opener_inside_recorded_thinking_is_masked_with_its_block(self):
        # the recorded thinking text itself contains '<|channel>thought\n' (seen in 2 of 177 trajectories)
        ids = [13, 1, 10, 13, 1, 10, 11, 12, 2, 3, 14]
        nested = []
        out, blocks, masked, _ = mask_thinking(ids, supervised(ids, 1), nested=nested, **KW)
        self.assertEqual((blocks, masked, nested), (1, 8, [1]))
        self.assertEqual(out[1:9], [IGNORE] * 8)
        self.assertEqual(out[9:], [3, 14])

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            mask_thinking([1, 2], [1], **KW)


if __name__ == '__main__':
    unittest.main()
