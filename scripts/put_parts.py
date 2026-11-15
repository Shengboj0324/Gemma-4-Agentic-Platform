"""Upload a file's parts to presigned multipart URLs and record each ETag.

Input: the JSON from `r2_handoff.py presign-blob` (key, size, parts with
byte ranges and URLs). The file's size must equal the declared size. Parts go
up in parallel with retries; each response must carry an ETag. Prints
{part number: ETag} for `r2_handoff.py complete-blob`. No credential is
involved: the URLs grant only these parts until they expire. Standard library
only.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
import time
import urllib.request


def put_part(path, part, attempts=6):
    with open(path, 'rb') as handle:
        handle.seek(part['start'])
        data = handle.read(part['end'] - part['start'] + 1)
    if len(data) != part['end'] - part['start'] + 1:
        raise IOError(f"Short read for part {part['part']}")
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(part['url'], data=data, method='PUT')
            with urllib.request.urlopen(request, timeout=600) as response:
                etag = response.headers.get('ETag')
                if response.status != 200 or not etag:
                    raise IOError(f"Part {part['part']}: status {response.status}, ETag {etag!r}")
                return part['part'], etag
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(min(60, 2 * 2 ** attempt))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', help='presign-blob JSON')
    parser.add_argument('path')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    plan = json.load(open(args.plan))
    if os.path.getsize(args.path) != plan['size']:
        raise IOError(f"{args.path} is {os.path.getsize(args.path)} bytes, plan says {plan['size']}")
    with ThreadPoolExecutor(args.workers) as pool:
        etags = dict(pool.map(lambda p: put_part(args.path, p), plan['parts']))
    print(json.dumps({str(k): v for k, v in sorted(etags.items())}))


if __name__ == '__main__':
    main()
