"""Credentials must not leak, and the bounded surface must be exactly four calls."""

import importlib.util
import unittest

from zenithsync.r2_client import (BoundedR2Client, NONSECRET, REQUIRED,
                                  load_credentials)

SECRET = 'AKIAEXAMPLEDONOTUSE/supersecret+value'


def environment(**overrides):
    base = {'R2_ENDPOINT_URL': 'https://example.r2.cloudflarestorage.com',
            'R2_BUCKET_NAME': 'example-bucket',
            'R2_ACCESS_KEY_ID': 'exampleaccesskeyid',
            'R2_SECRET_ACCESS_KEY': SECRET}
    base.update(overrides)
    return base


class LoadCredentialsTests(unittest.TestCase):
    def test_every_required_field_is_returned_with_its_source(self):
        result = load_credentials(environ=environment())
        for name in REQUIRED:
            self.assertIn(name, result)
            self.assertEqual(result['sources'][name], 'environment')
        self.assertEqual(result['R2_SECRET_ACCESS_KEY'], SECRET)

    def test_a_missing_field_error_names_fields_and_never_values(self):
        incomplete = environment()
        incomplete.pop('R2_SECRET_ACCESS_KEY')
        with self.assertRaises(ValueError) as caught:
            load_credentials(environ=incomplete)
        message = str(caught.exception)
        self.assertIn('R2_SECRET_ACCESS_KEY', message)
        for value in environment().values():
            self.assertNotIn(value, message)

    def test_a_blank_field_is_treated_as_missing(self):
        with self.assertRaisesRegex(ValueError, 'R2_ACCESS_KEY_ID'):
            load_credentials(environ=environment(R2_ACCESS_KEY_ID=''))

    # `--env-file` is the only path that needs python-dotenv, so this is the
    # only test that requires it. Every other optional dependency in the
    # suite skips when absent; erroring here would make a stdlib-only run
    # look like a real failure.
    @unittest.skipUnless(importlib.util.find_spec('dotenv'),
                         'python-dotenv is required for --env-file loading')
    def test_the_process_environment_wins_and_the_source_says_so(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'creds.env'
            path.write_text('\n'.join(
                f'{name}=from-file' for name in REQUIRED) + '\n')
            result = load_credentials(env_file=path,
                                      environ={'R2_BUCKET_NAME': 'from-environment'})
            # Precedence is house style; the point is that it is recorded.
            self.assertEqual(result['R2_BUCKET_NAME'], 'from-environment')
            self.assertEqual(result['sources']['R2_BUCKET_NAME'], 'environment')
            self.assertEqual(result['R2_ACCESS_KEY_ID'], 'from-file')
            self.assertEqual(result['sources']['R2_ACCESS_KEY_ID'], 'env_file')

    def test_only_endpoint_and_bucket_are_declared_nonsecret(self):
        self.assertEqual(set(NONSECRET), {'R2_ENDPOINT_URL', 'R2_BUCKET_NAME'})
        self.assertNotIn('R2_SECRET_ACCESS_KEY', NONSECRET)
        self.assertNotIn('R2_ACCESS_KEY_ID', NONSECRET)


class RefusingClient:
    """Raises on any operation the bounded wrapper is not allowed to perform."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def refuse(*args, **kwargs):
            raise AssertionError('bounded client reached a forbidden operation: '
                                 + name)
        return refuse

    def get_object(self, **kwargs):
        self.calls.append(('get_object', kwargs))
        return {'ContentLength': 0}

    def put_object(self, **kwargs):
        self.calls.append(('put_object', kwargs))
        return {}

    def head_object(self, **kwargs):
        self.calls.append(('head_object', kwargs))
        return {'ContentLength': 0}

    def upload_file(self, filename, bucket, key, Config=None, Callback=None):
        self.calls.append(('upload_file', (filename, bucket, key)))


class BoundedSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.inner = RefusingClient()
        self.client = BoundedR2Client(self.inner, transfer=None, log=lambda *a, **k: None)

    def test_the_declared_operations_are_exactly_what_is_implemented(self):
        implemented = {name for name in dir(self.client)
                       if not name.startswith('_') and callable(getattr(self.client, name))}
        self.assertEqual(implemented, set(BoundedR2Client.OPERATIONS))

    def test_each_declared_operation_reaches_the_inner_client(self):
        self.client.get_object(Bucket='b', Key='k')
        self.client.put_object(Bucket='b', Key='k', Body=b'x')
        self.client.head_object(Bucket='b', Key='k')
        self.client.upload_file('f', 'b', 'k')
        self.assertEqual([name for name, _ in self.inner.calls],
                         ['get_object', 'put_object', 'head_object', 'upload_file'])

    def test_a_destructive_operation_is_not_exposed(self):
        for name in ('delete_object', 'delete_objects', 'list_objects_v2',
                     'put_bucket_policy', 'create_bucket', 'copy_object'):
            self.assertFalse(hasattr(type(self.client), name), name)

    def test_upload_counting_is_exact_under_concurrency(self):
        import threading

        def upload():
            for _ in range(50):
                self.client.upload_file('f', 'b', 'k')

        threads = [threading.Thread(target=upload) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(self.client.uploads, 400)


if __name__ == '__main__':
    unittest.main()


@unittest.skipUnless(importlib.util.find_spec('boto3'), 'boto3 is required')
class BuildClientRetryTests(unittest.TestCase):
    """R2 refuses simultaneous reads on one object; the client must back off.

    A content-addressed store makes one key hot by design, and botocore's
    default three attempts with no client-side rate limit failed a 48-minute
    shipment at 5,659 of 6,725 packages. Constructing a client makes no network
    call, so this is checked directly rather than inferred.
    """

    def build(self, **extra):
        from zenithsync.r2_client import build_client
        return build_client(environ=environment(), **extra)

    def test_adaptive_retries_are_configured_with_more_than_the_default(self):
        client, bucket, description = self.build()
        # Reaching through the wrapper's private client is what the wrapper's
        # own docstring warns against, and it is the point here: the
        # description below goes into a receipt, and a receipt claiming a retry
        # policy the client does not have is worse than no claim.
        config = client._client.meta.config
        self.assertEqual(config.retries['mode'], 'adaptive')
        self.assertEqual(config.retries['total_max_attempts'], 8)
        self.assertEqual(config.retries['mode'], description['retry_mode'])
        self.assertEqual(config.retries['total_max_attempts'],
                         description['retry_max_attempts'])
        self.assertEqual(bucket, 'example-bucket')

    def test_the_retry_policy_is_recorded_in_the_connection_description(self):
        _, _, description = self.build(max_attempts=5)
        self.assertEqual(description['retry_mode'], 'adaptive')
        self.assertEqual(description['retry_max_attempts'], 5)
        # A description goes into a receipt, so it must carry no secret.
        self.assertNotIn(SECRET, str(description))

    def test_a_nonsensical_attempt_count_is_refused(self):
        for value in (0, -1, 2.5, '8', True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'max_attempts'):
                    self.build(max_attempts=value)
