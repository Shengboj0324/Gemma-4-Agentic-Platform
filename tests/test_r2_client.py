"""Credentials must not leak, and the bounded surface must be exactly four calls."""

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
