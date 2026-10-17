import json
import unittest
from zenithsync.source_credentials import scan_text
from zenithsync.source_credentials import require_no_credential_indicators
from unittest.mock import patch
from scripts.replay_source_teacher import preflight


class SourceCredentialTests(unittest.TestCase):
    def test_authorization_literals_have_locations_but_no_values(self):
        token = 'fakeCredentialValueForTesting12345'
        for prefix in ['"Authorization": "', "'authorization': '", 'Authorization: Bearer ',
                       'Proxy-Authorization: Basic ', 'authorization = ']:
            text = 'Unicode: λ\n' + prefix + token
            findings = scan_text(text)
            self.assertEqual(len(findings), 1)
            self.assertEqual(text[findings[0]['start']:findings[0]['end']], token)
            self.assertEqual(findings[0]['line'], 2)
            self.assertNotIn(token, json.dumps(findings))

    def test_known_token_and_key_indicators(self):
        samples = ['AKIA' + 'A' * 16, 'ghp_' + 'x' * 30,
                   'github_pat_' + 'x' * 30, '-----BEGIN OPENSSH PRIVATE KEY-----']
        for sample in samples:
            with self.subTest(sample_type=sample[:4]):
                self.assertEqual(len(scan_text(sample)), 1)

    def test_short_placeholders_and_unlabelled_text_are_not_flagged(self):
        self.assertEqual(scan_text('Authorization: Bearer EMPTY'), [])
        self.assertEqual(scan_text('a' * 80), [])
        self.assertEqual(scan_text('Authorization: ${TOKEN}'), [])

    def test_type_and_deterministic_order(self):
        with self.assertRaises(TypeError):
            scan_text(None)
        text = 'ghp_' + 'z' * 30 + '\n' + 'AKIA' + 'B' * 16
        rows = scan_text(text)
        self.assertEqual([r['line'] for r in rows], [1, 2])
        self.assertEqual(rows, scan_text(text))

    def test_replay_rejects_prompt_observation_and_action_before_adaptation(self):
        token = 'fakeCredentialValueForTesting12345'
        cases = [
            [{'role': 'user', 'content': 'Authorization: ' + token}],
            [{'role': 'tool', 'content': {'headers': {'Authorization': token}}}],
            [{'tool_calls': [{'function': {'name': 'execute_bash', 'arguments':
                {'command': 'Authorization: ' + token}}}]}],
        ]
        for messages in cases:
            original = json.dumps(messages)
            with self.assertRaisesRegex(ValueError, '^Source credential indicator requires review before replay$') as caught:
                preflight(messages)
            self.assertNotIn(token, str(caught.exception))
            self.assertEqual(json.dumps(messages), original)

    def test_clean_replay_keeps_existing_action(self):
        messages = [{'tool_calls': [{'function': {'name': 'execute_bash',
                     'arguments': {'command': 'python --version'}}}]}]
        self.assertEqual(preflight(messages)[0]['command'], 'python --version')

    def test_encoded_authorization_and_duplicate_members_are_not_hidden(self):
        token = 'fakeCredentialValueForTesting12345'
        encoded = '{"Author\\u0069zation":"' + token + '","Authorization":"EMPTY"}'
        for payload in (encoded, json.dumps({'stdout': encoded}),
                        json.dumps(json.dumps({'stdout': encoded}))):
            with self.subTest(layers=payload.count('stdout')):
                messages = [{'role': 'tool', 'content': payload}]
                before = json.dumps(messages)
                with self.assertRaisesRegex(ValueError, 'indicator requires review') as caught:
                    require_no_credential_indicators(messages)
                self.assertNotIn(token, str(caught.exception))
                self.assertEqual(json.dumps(messages), before)

    def test_json_unicode_escaped_private_key_header_is_rejected(self):
        payload = json.dumps({'stdout': '-----BEGIN OPENSSH PRIVATE KEY-----'})
        payload = payload.replace('PRIVATE', '\\u0050RIVATE')
        with self.assertRaisesRegex(ValueError, 'indicator requires review'):
            require_no_credential_indicators({'content': payload})

    def test_clean_nested_json_malformed_text_and_cycles(self):
        clean = {'content': json.dumps({'stdout': json.dumps({'Authorization': 'EMPTY'})})}
        require_no_credential_indicators(clean)
        require_no_credential_indicators('{not valid JSON')
        cyclic = [clean]
        cyclic.append(cyclic)
        require_no_credential_indicators(cyclic)

    def test_json_work_limits_fail_closed_without_payloads(self):
        payload = json.dumps(json.dumps({'safe': 'text'}))
        with patch('zenithsync.source_credentials._MAX_JSON_LAYERS', 1):
            with self.assertRaisesRegex(ValueError, 'JSON limit exceeded'):
                require_no_credential_indicators(payload)
        with patch('zenithsync.source_credentials._MAX_JSON_CHARACTERS', 5):
            with self.assertRaisesRegex(ValueError, 'JSON limit exceeded'):
                require_no_credential_indicators('{"safe":"text"}')

    def test_separate_decoded_branches_are_all_scanned(self):
        branches = [json.dumps({'safe': str(i)}) for i in range(100)]
        branches.insert(0, '{"Author\\u0069zation":"fakeCredentialValueForTesting12345"}')
        with self.assertRaisesRegex(ValueError, 'indicator requires review'):
            require_no_credential_indicators(branches)


if __name__ == '__main__':
    unittest.main()
