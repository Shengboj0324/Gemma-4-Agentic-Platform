"""Hand pod outputs to R2 and prove they arrived, without storing them locally.

  presign-put KEY [--hours H]  print a presigned PUT URL for KEY (bucket-scoped)
  verify KEY SHA256 SIZE       stream KEY from R2, hash it in memory, compare;
                               nothing is written to disk. Exit 1 on mismatch.

Used for the archive-verify-delete sequence of every pod. Keys are confined
to `artifacts/v1/tmp/` and `artifacts/v1/runs/`.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.r2_client import ALLOWED_BUCKET, load_credentials

PREFIXES = ('artifacts/v1/tmp/', 'artifacts/v1/runs/')


def client(env_file):
    import boto3
    from botocore.config import Config
    credentials = load_credentials(env_file=env_file)
    if credentials['R2_BUCKET_NAME'] != ALLOWED_BUCKET:
        raise ValueError('Only ' + ALLOWED_BUCKET + ' may be used')
    return boto3.client('s3', endpoint_url=credentials['R2_ENDPOINT_URL'], region_name='auto',
                        aws_access_key_id=credentials['R2_ACCESS_KEY_ID'],
                        aws_secret_access_key=credentials['R2_SECRET_ACCESS_KEY'],
                        config=Config(signature_version='s3v4'))


def check_key(key):
    if not key.startswith(PREFIXES) or '..' in key:
        raise ValueError(f'Key outside {PREFIXES}: {key}')


def stream_digest(body, chunk=8 * 1024 * 1024):
    digest, size = hashlib.sha256(), 0
    while block := body.read(chunk):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env')
    sub = parser.add_subparsers(dest='command', required=True)
    put = sub.add_parser('presign-put')
    put.add_argument('key')
    put.add_argument('--hours', type=float, default=6.0)
    ver = sub.add_parser('verify')
    ver.add_argument('key')
    ver.add_argument('sha256')
    ver.add_argument('size', type=int)
    args = parser.parse_args()
    check_key(args.key)
    s3 = client(args.env_file)
    if args.command == 'presign-put':
        print(s3.generate_presigned_url('put_object', Params={'Bucket': ALLOWED_BUCKET, 'Key': args.key},
                                        ExpiresIn=int(args.hours * 3600)))
        return
    digest, size = stream_digest(s3.get_object(Bucket=ALLOWED_BUCKET, Key=args.key)['Body'])
    ok = digest == args.sha256 and size == args.size
    print(json.dumps({'key': args.key, 'sha256': digest, 'size': size, 'verified': ok}))
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
