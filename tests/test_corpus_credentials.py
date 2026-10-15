import json
import unittest
from zenithsync.corpus_credentials import decode_checked, screen_corpus


class Corpus:
    summary = {'returned_examples': 2, 'purpose': 'inspection'}

    def metadata(self):
        return [{'example_id': str(i)} for i in range(2)]

    def fetch(self, identifier):
        return {'example_id': identifier, 'task_id': 'task-' + identifier,
                'split': 'train' if identifier == '0' else 'dev',
                'input_ids': [int(identifier)], 'labels': [-100]}


class CorpusCredentialTests(unittest.TestCase):
    def test_masked_observations_and_nontraining_splits_are_scanned(self):
        marker = 'ghp_' + 'x' * 30
        result = screen_corpus(Corpus(), lambda ids: marker if ids == [0] else 'clean')
        self.assertEqual(result['flagged_examples'], 1)
        self.assertEqual(result['indicator_count'], 1)
        self.assertEqual(len(result['examples']), 2)
        self.assertFalse(result['privacy_approved'])
        self.assertFalse(result['training_approved'])
        self.assertNotIn(marker, json.dumps(result))
        finding = result['examples'][0]['findings'][0]
        self.assertEqual(finding, {'rule': 'github_token', 'start': 0, 'end': 34, 'line': 1})

    def test_decoder_rejects_unknown_ids_and_retains_special_tokens(self):
        class Tokenizer:
            def id_to_token(self, value):
                return 'known' if value in (0, 1) else None
            def decode(self, values, *, skip_special_tokens):
                self.assertion = skip_special_tokens
                return '<special>text'
        tokenizer = Tokenizer()
        self.assertEqual(decode_checked(tokenizer, [0, 1]), '<special>text')
        self.assertIs(tokenizer.assertion, False)
        for ids in [[2], [-1], [True], [1.0]]:
            with self.assertRaises(ValueError):
                decode_checked(tokenizer, ids)

    def test_training_subset_is_rejected(self):
        class TrainingOnly(Corpus):
            summary = {'returned_examples': 2, 'purpose': 'training'}
        with self.assertRaisesRegex(ValueError, 'every corpus split'):
            screen_corpus(TrainingOnly(), str)

    def test_bounds_do_not_truncate(self):
        self.assertEqual(screen_corpus(Corpus(), lambda _: 'abc', max_decoded_characters=3)['indicator_count'], 0)
        with self.assertRaisesRegex(ValueError, 'ceiling'):
            screen_corpus(Corpus(), lambda _: 'abcd', max_decoded_characters=3)
        for bound in [True, 0, -1, 1.5]:
            with self.assertRaises(ValueError):
                screen_corpus(Corpus(), str, max_decoded_characters=bound)
        with self.assertRaises(TypeError):
            screen_corpus(Corpus(), lambda _: None)

    def test_fetch_failure_and_incomplete_coverage_do_not_return_success(self):
        class Changed(Corpus):
            def fetch(self, identifier):
                raise ValueError('Corpus file hash mismatch')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            screen_corpus(Changed(), str)
        class Incomplete(Corpus):
            summary = {'returned_examples': 3, 'purpose': 'inspection'}
        with self.assertRaisesRegex(ValueError, 'coverage'):
            screen_corpus(Incomplete(), str)


if __name__ == '__main__':
    unittest.main()
