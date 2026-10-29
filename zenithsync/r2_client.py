"""Bounded S3-compatible client construction for Cloudflare R2.

Credentials come from the process environment or an explicit dotenv file and are
never logged, returned or written to a receipt. Only the four operations the
object store needs are exposed, so an injected client cannot delete, list or
reconfigure a bucket. The nonsecret endpoint, bucket and region are returned so
a receipt can record which bucket was used.
"""

import threading
import time

REQUIRED = ('R2_ENDPOINT_URL', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID',
            'R2_SECRET_ACCESS_KEY')


def load_credentials(env_file=None, environ=None):
    """Explicit process environment wins over optional dotenv values."""
    import os

    values = dict(os.environ if environ is None else environ)
    if env_file is not None:
        from dotenv import dotenv_values
        values = {**dotenv_values(env_file), **values}
    missing = [name for name in REQUIRED if not values.get(name)]
    if missing:
        raise ValueError('Required R2 credential fields are missing: ' + ','.join(missing))
    return {name: values[name] for name in REQUIRED}


class BoundedR2Client:
    """Expose exactly the object-store surface, with periodic upload progress."""

    def __init__(self, client, transfer, *, progress_seconds=15, log=print):
        self._client = client
        self._transfer = transfer
        self._progress_seconds = progress_seconds
        self._log = log
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
                    self._log(f'Upload progress: {sent} bytes in current object.', flush=True)
                    reported = now

        self.uploads += 1
        self._client.upload_file(filename, bucket, key, Config=self._transfer,
                                 Callback=progress)


def build_client(*, env_file=None, environ=None, connect_timeout=15, read_timeout=120,
                 multipart_threshold=16 * 1024**2, multipart_chunksize=64 * 1024**2,
                 max_concurrency=2, log=print):
    """Return (bounded client, bucket name, nonsecret connection description)."""
    import boto3
    from boto3.s3.transfer import TransferConfig
    from botocore.config import Config

    credentials = load_credentials(env_file=env_file, environ=environ)
    client = boto3.client(
        's3', endpoint_url=credentials['R2_ENDPOINT_URL'], region_name='auto',
        aws_access_key_id=credentials['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=credentials['R2_SECRET_ACCESS_KEY'],
        config=Config(connect_timeout=connect_timeout, read_timeout=read_timeout,
                      retries={'mode': 'standard', 'total_max_attempts': 3}))
    transfer = TransferConfig(multipart_threshold=multipart_threshold,
                              multipart_chunksize=multipart_chunksize,
                              max_concurrency=max_concurrency)
    bounded = BoundedR2Client(client, transfer, log=log)
    description = {'endpoint_url': credentials['R2_ENDPOINT_URL'],
                   'bucket': credentials['R2_BUCKET_NAME'], 'region': 'auto',
                   'boto3_version': boto3.__version__}
    return bounded, credentials['R2_BUCKET_NAME'], description
