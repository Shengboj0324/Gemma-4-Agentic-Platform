"""Presign one PUT per converted-task pack, and check shipped packs by HEAD (no download).

  urls --cohort train --run-key runs/2026-11-16/rebench-packs [--hours 36]
      one presigned PUT per repository of the cohort (slug = lower-case instance id
      without its number), for key artifacts/v1/<run-key>/<slug>.tar; the map is uploaded
      to a random tmp key and only a presigned GET for it is printed.
  check SHIPPED_JSONL --run-key ...
      HEAD every shipped pack and require its size and ETag (= md5 of a single PUT) to
      match what the pod recorded. Prints a summary; exit 1 on any mismatch.

Bucket scope is enforced by r2_handoff.client; keys stay under artifacts/v1/runs/.
"""
import argparse
import json
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.r2_handoff import check_key, client
from zenithsync.r2_client import ALLOWED_BUCKET

COHORTS = ROOT / 'evidence/data/task-pool-v2-python-001/cohorts.json'


def slugs(cohort):
    ids = next(c for c in json.loads(COHORTS.read_text())['cohorts'] if c['name'] == cohort)['instance_ids']
    return sorted({i.rsplit('-', 1)[0].lower() for i in ids})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env')
    sub = parser.add_subparsers(dest='command', required=True)
    u = sub.add_parser('urls')
    u.add_argument('--cohort', choices=('train', 'development'), required=True)
    u.add_argument('--run-key', required=True)
    u.add_argument('--hours', type=float, default=36)
    c = sub.add_parser('check')
    c.add_argument('shipped', type=Path)
    c.add_argument('--run-key', required=True)
    args = parser.parse_args()
    s3 = client(args.env_file)
    prefix = f'artifacts/v1/{args.run_key.strip("/")}/'
    check_key(prefix)
    if args.command == 'urls':
        expiry = int(args.hours * 3600)
        urls = {slug: s3.generate_presigned_url('put_object', Params={'Bucket': ALLOWED_BUCKET,
                                                                     'Key': prefix + slug + '.tar'},
                                                ExpiresIn=expiry)
                for slug in slugs(args.cohort)}
        tmp = f'artifacts/v1/tmp/{secrets.token_hex(16)}/uploads.json'
        check_key(tmp)
        s3.put_object(Bucket=ALLOWED_BUCKET, Key=tmp, Body=json.dumps(urls).encode())
        get = s3.generate_presigned_url('get_object', Params={'Bucket': ALLOWED_BUCKET, 'Key': tmp},
                                        ExpiresIn=expiry)
        print(json.dumps({'packs': len(urls), 'uploads_url': get}))
        return
    bad, ok, total = [], 0, 0
    for line in args.shipped.read_text().splitlines():
        row = json.loads(line)
        if row.get('status') != 'shipped':
            continue
        head = s3.head_object(Bucket=ALLOWED_BUCKET, Key=prefix + row['slug'] + '.tar')
        if head['ContentLength'] != row['size'] or head['ETag'].strip('"') != row['md5']:
            bad.append(row['slug'])
        else:
            ok += 1
            total += row['size']
    print(json.dumps({'verified': ok, 'bytes': total, 'mismatched': bad}))
    if bad:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
