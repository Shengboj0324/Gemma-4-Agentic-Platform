"""Hand pod outputs to R2 and prove they arrived, without storing them locally.

  presign-put KEY [--hours H]  print a presigned PUT URL for KEY (bucket-scoped)
  verify KEY SHA256 SIZE       stream KEY from R2, hash it in memory, compare;
                               nothing is written to disk. Exit 1 on mismatch.
  presign-blob SHA256 SIZE     start a multipart upload to the content address
                               `artifacts/v1/blobs/sha256/SHA256` and print a
                               presigned URL per part (a pod PUTs the parts
                               and keeps each ETag). Objects over 5 GB need it.
  complete-blob SHA256 SIZE UPLOAD_ID ETAGS_JSON
                               complete the upload, then stream the object back
                               and require the digest and size; aborts the
                               upload on any failure before completion.
  commit-manifest MANIFEST     re-verify every blob of a manifest by streamed
                               read and write the manifest's commit marker.

Used for the archive-verify-delete sequence of every pod. Plain keys are
confined to `artifacts/v1/tmp/` and `artifacts/v1/runs/`; blob keys are only
ever derived from a digest.
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


PART_SIZE = 512 * 1024 * 1024


def blob_key(sha256):
    if len(sha256) != 64 or any(c not in '0123456789abcdef' for c in sha256):
        raise ValueError(f'Not a sha256 digest: {sha256}')
    return 'artifacts/v1/blobs/sha256/' + sha256


def part_ranges(size, part_size=PART_SIZE):
    """1-based part numbers with byte ranges; every part but the last is part_size."""
    if size <= 0:
        raise ValueError('size must be positive')
    return [(n + 1, start, min(start + part_size, size) - 1)
            for n, start in enumerate(range(0, size, part_size))]


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
    pb = sub.add_parser('presign-blob')
    pb.add_argument('sha256')
    pb.add_argument('size', type=int)
    pb.add_argument('--hours', type=float, default=12.0)
    cb = sub.add_parser('complete-blob')
    cb.add_argument('sha256')
    cb.add_argument('size', type=int)
    cb.add_argument('upload_id')
    cb.add_argument('etags', type=Path, help='JSON {part number: ETag}')
    cm = sub.add_parser('commit-manifest')
    cm.add_argument('manifest', type=Path)
    args = parser.parse_args()
    if args.command in ('presign-put', 'verify'):
        check_key(args.key)
    s3 = client(args.env_file)
    if args.command == 'presign-blob':
        key = blob_key(args.sha256)
        upload = s3.create_multipart_upload(Bucket=ALLOWED_BUCKET, Key=key)['UploadId']
        parts = [{'part': n, 'start': a, 'end': b,
                  'url': s3.generate_presigned_url('upload_part', ExpiresIn=int(args.hours * 3600), Params={
                      'Bucket': ALLOWED_BUCKET, 'Key': key, 'UploadId': upload, 'PartNumber': n})}
                 for n, a, b in part_ranges(args.size)]
        print(json.dumps({'key': key, 'sha256': args.sha256, 'size': args.size, 'upload_id': upload, 'parts': parts}))
        return
    if args.command == 'complete-blob':
        key = blob_key(args.sha256)
        etags = {int(k): v for k, v in json.loads(args.etags.read_text()).items()}
        expected = [n for n, _, _ in part_ranges(args.size)]
        try:
            if sorted(etags) != expected:
                raise ValueError(f'ETags for parts {sorted(etags)}, expected {expected}')
            s3.complete_multipart_upload(Bucket=ALLOWED_BUCKET, Key=key, UploadId=args.upload_id, MultipartUpload={
                'Parts': [{'PartNumber': n, 'ETag': etags[n]} for n in expected]})
        except Exception:
            s3.abort_multipart_upload(Bucket=ALLOWED_BUCKET, Key=key, UploadId=args.upload_id)
            raise
        args.key, args.command = key, 'verify'
    if args.command == 'commit-manifest':
        from zenithsync.object_store import ArtifactStore
        result = ArtifactStore(s3, ALLOWED_BUCKET).commit_manifest(json.loads(args.manifest.read_text()))
        print(json.dumps(result))
        return
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
