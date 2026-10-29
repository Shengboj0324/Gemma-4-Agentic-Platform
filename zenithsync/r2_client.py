"""Bounded S3-compatible client construction for Cloudflare R2.

Credentials are read from the process environment or an explicit dotenv file.
They are never logged, never written into a receipt, and never placed in an
exception message — a missing-field error names the fields only. They do pass
through `load_credentials`' return value, which is the only place they appear:
treat that value as a secret, keep it in a local, and never put it in a
structure that something else might render. A traceback renderer that prints
frame locals would expose it.

The client exposes only the four operations the object store needs, so a holder
of the bounded client cannot delete an object, list a bucket or change a bucket
policy. The underlying boto3 client is kept in a private attribute rather than
behind a hard capability boundary: this is a guard against a mistake, not a
sandbox against a determined caller, and the attribute name says so.

Precedence is deliberate and worth knowing: an explicit process environment wins
over `--env-file`, matching `scripts/transfer_artifact.py`. A stale exported
`R2_BUCKET_NAME` therefore overrides the file. `load_credentials` reports which
source supplied each field so a receipt can record it, and `build_client` puts
that in its connection description.
"""

import threading
import time

REQUIRED = ('R2_ENDPOINT_URL', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID',
            'R2_SECRET_ACCESS_KEY')
# Field names safe to name in an error or a receipt. Values never are.
NONSECRET = ('R2_ENDPOINT_URL', 'R2_BUCKET_NAME')


def load_credentials(env_file=None, environ=None):
    """Return the four required fields plus where each one came from.

    The explicit process environment wins over optional dotenv values, so a
    leftover shell export silently overrides an `--env-file`. The returned
    `sources` map is what lets a caller record which won.
    """
    import os

    values = dict(os.environ if environ is None else environ)
    file_values = {}
    if env_file is not None:
        from dotenv import dotenv_values
        file_values = {key: value for key, value in dotenv_values(env_file).items()
                       if value}
        values = {**file_values, **values}
    missing = [name for name in REQUIRED if not values.get(name)]
    if missing:
        # Field names only. A value must never reach an error message.
        raise ValueError('Required R2 credential fields are missing: '
                         + ','.join(missing))
    environment = dict(os.environ if environ is None else environ)
    sources = {name: ('environment' if environment.get(name)
                      else 'env_file' if file_values.get(name) else 'unknown')
               for name in REQUIRED}
    return {**{name: values[name] for name in REQUIRED}, 'sources': sources}


class BoundedR2Client:
    """Expose exactly the object-store surface, with periodic upload progress.

    `_client` is private by convention. Reaching through it defeats the point of
    this wrapper, which exists so an ordinary coding mistake cannot delete an
    object or rewrite a bucket policy.
    """

    #: The complete set of operations this wrapper will perform.
    OPERATIONS = ('get_object', 'put_object', 'head_object', 'upload_file')

    def __init__(self, client, transfer, *, progress_seconds=15, log=print):
        self._client = client
        self._transfer = transfer
        self._progress_seconds = progress_seconds
        self._log = log
        self._guard = threading.Lock()
        self.uploads = 0

    def get_object(self, **kwargs):
        return self._client.get_object(**kwargs)

    def put_object(self, **kwargs):
        return self._client.put_object(**kwargs)

    def head_object(self, **kwargs):
        return self._client.head_object(**kwargs)

    def upload_file(self, filename, bucket, key):
        lock = threading.Lock()
        sent, reported = 0, time.monotonic()

        def progress(amount):
            nonlocal sent, reported
            with lock:
                sent += amount
                now = time.monotonic()
                if now - reported >= self._progress_seconds:
                    self._log(f'Upload progress: {sent} bytes in current object.',
                              flush=True)
                    reported = now

        # Counted under a lock so a concurrent caller's tally stays exact.
        with self._guard:
            self.uploads += 1
        self._client.upload_file(filename, bucket, key, Config=self._transfer,
                                 Callback=progress)


def build_client(*, env_file=None, environ=None, connect_timeout=15, read_timeout=120,
                 multipart_threshold=16 * 1024**2, multipart_chunksize=64 * 1024**2,
                 max_concurrency=2, max_pool_connections=None, log=print):
    """Return (bounded client, bucket name, nonsecret connection description).

    `max_pool_connections` must cover every thread that will share this client.
    botocore's default is 10, and a caller publishing packages concurrently will
    otherwise block on the connection pool rather than on the network. It
    defaults to the larger of 10 and twice `max_concurrency`.

    The description contains only nonsecret facts — endpoint, bucket, pool size,
    boto3 version, and which source supplied each credential field — so it is
    safe to write into a receipt.
    """
    import boto3
    from boto3.s3.transfer import TransferConfig
    from botocore.config import Config

    credentials = load_credentials(env_file=env_file, environ=environ)
    if max_pool_connections is None:
        max_pool_connections = max(10, 2 * max_concurrency)
    if type(max_pool_connections) is not int or max_pool_connections < 1:
        raise ValueError('max_pool_connections must be a positive integer')
    client = boto3.client(
        's3', endpoint_url=credentials['R2_ENDPOINT_URL'], region_name='auto',
        aws_access_key_id=credentials['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=credentials['R2_SECRET_ACCESS_KEY'],
        config=Config(connect_timeout=connect_timeout, read_timeout=read_timeout,
                      max_pool_connections=max_pool_connections,
                      retries={'mode': 'standard', 'total_max_attempts': 3}))
    transfer = TransferConfig(multipart_threshold=multipart_threshold,
                              multipart_chunksize=multipart_chunksize,
                              max_concurrency=max_concurrency)
    bounded = BoundedR2Client(client, transfer, log=log)
    description = {'endpoint_url': credentials['R2_ENDPOINT_URL'],
                   'bucket': credentials['R2_BUCKET_NAME'], 'region': 'auto',
                   'max_pool_connections': max_pool_connections,
                   'operations': list(BoundedR2Client.OPERATIONS),
                   'credential_sources': credentials['sources'],
                   'boto3_version': boto3.__version__}
    return bounded, credentials['R2_BUCKET_NAME'], description
