"""Write a presigned fetch script for a set of R2 manifests, for a pod to run.

Each --manifest NAME=PATH=DEST adds every file of that manifest, fetched by
digest to DEST/<path>. The script and a JSON of the manifests are uploaded to a
random R2 tmp prefix; only presigned GET URLs for those two objects are printed.
No credential leaves this machine: a pod holding the URLs can read exactly these
objects until they expire, and nothing else.
"""
import argparse
import json
from pathlib import Path
import secrets
import shlex
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import load_json, validate_manifest
from zenithsync.r2_client import ALLOWED_BUCKET, load_credentials


def build_script(entries, presign, parallel=8):
    """entries: [(name, manifest, dest)] -> shell script text.

    Files are fetched `parallel` at a time (a single R2 connection was
    throttled to ~1.5 MB/s on one pod), each with curl retries and an exact
    size check. Any failed file marks the batch; the script exits non-zero
    after the batch rather than continuing.
    """
    if parallel < 1:
        raise ValueError('parallel must be at least 1')
    lines = ['#!/bin/sh', 'set -e', 'FAIL="${TMPDIR:-/tmp}/fetch-failed-$$"', 'rm -f "$FAIL"',
             'check() { [ ! -e "$FAIL" ] || { echo "fetch failed" >&2; rm -f "$FAIL"; exit 1; }; }']
    for name, manifest, dest in entries:
        for index, row in enumerate(manifest['files']):
            target = shlex.quote(f"{dest}/{row['path']}")
            url = shlex.quote(presign(row['sha256']))
            lines.append(f'( mkdir -p "$(dirname {target})" && curl -fsSL --retry 5 --retry-delay 3 -o {target} {url} && '
                         f'test "$(wc -c < {target} | tr -d " ")" = "{row["size_bytes"]}" ) || touch "$FAIL" &')
            if (index + 1) % parallel == 0:
                lines += ['wait', 'check']
        lines += ['wait', 'check', f'echo "{name}: {len(manifest["files"])} files"']
    lines.append('echo FETCH_DONE')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', action='append', required=True, help='NAME=PATH=DEST')
    parser.add_argument('--hours', type=float, default=8.0)
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env')
    args = parser.parse_args()
    import boto3
    from botocore.config import Config
    credentials = load_credentials(env_file=args.env_file)
    bucket = credentials['R2_BUCKET_NAME']
    if bucket != ALLOWED_BUCKET:
        raise ValueError('Only ' + ALLOWED_BUCKET + ' may be used')
    client = boto3.client('s3', endpoint_url=credentials['R2_ENDPOINT_URL'], region_name='auto',
                          aws_access_key_id=credentials['R2_ACCESS_KEY_ID'],
                          aws_secret_access_key=credentials['R2_SECRET_ACCESS_KEY'],
                          config=Config(signature_version='s3v4'))
    expiry = int(args.hours * 3600)

    def presign_key(key):
        return client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key},
                                             ExpiresIn=expiry)

    entries, manifests = [], {}
    for spec in args.manifest:
        name, path, dest = spec.split('=', 2)
        manifest = validate_manifest(load_json(Path(path)))
        entries.append((name, manifest, dest))
        manifests[name] = {'dest': dest, 'manifest': manifest}
    script = build_script(entries, lambda digest: presign_key(f'artifacts/v1/blobs/sha256/{digest}'))
    prefix = 'artifacts/v1/tmp/' + secrets.token_hex(16)
    client.put_object(Bucket=bucket, Key=prefix + '/fetch.sh', Body=script.encode(), ContentType='text/plain')
    client.put_object(Bucket=bucket, Key=prefix + '/manifests.json',
                      Body=json.dumps(manifests).encode(), ContentType='application/json')
    print(json.dumps({'files': sum(len(m['manifest']['files']) for m in manifests.values()),
                      'fetch_url': presign_key(prefix + '/fetch.sh'),
                      'manifests_url': presign_key(prefix + '/manifests.json')}))


if __name__ == '__main__':
    main()
