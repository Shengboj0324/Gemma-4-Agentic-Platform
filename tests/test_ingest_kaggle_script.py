import unittest

from scripts.ingest_kaggle_to_r2 import redirect_target


class Response:
    def __init__(self, status, headers):
        self.status_code, self.headers, self.closed = status, headers, False

    def close(self):
        self.closed = True


class Session:
    def __init__(self, response):
        self.response, self.calls = response, []

    def send(self, prepared, **kwargs):
        self.calls.append(kwargs)
        return self.response


class RedirectTargetTests(unittest.TestCase):
    def test_stops_at_the_redirect_without_reading_the_body(self):
        response = Response(302, {'Location': 'https://storage/archive.zip?sig=x'})
        session = Session(response)
        url = redirect_target(session, object(), {'stream': False, 'verify': True, 'proxies': {}})
        self.assertEqual(url, 'https://storage/archive.zip?sig=x')
        call = session.calls[0]
        self.assertFalse(call['allow_redirects'])
        self.assertTrue(call['stream'])
        self.assertTrue(response.closed)

    def test_a_non_redirect_is_refused(self):
        for response in (Response(200, {}), Response(302, {})):
            with self.assertRaisesRegex(ValueError, 'redirect'):
                redirect_target(Session(response), object(), {})
            self.assertTrue(response.closed)


if __name__ == '__main__':
    unittest.main()
