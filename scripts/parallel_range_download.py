"""Download one large file over HTTP in parallel byte ranges, then hash it.

Single connections to object storage were throttled to ~1.5 MB/s on a pod;
ranges fetched in parallel are not. The output is preallocated, each part is
written at its offset, every part's length is checked, and the whole file
must equal the expected size. Prints {"path", "size", "sha256"}. Standard
library only, so it runs before any environment is installed.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import time
import urllib.request


def fetch_range(url, start, end, out, attempts=6):
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end}'})
            with urllib.request.urlopen(request, timeout=120) as response:
                if response.status != 206:
                    raise IOError(f'Expected 206 for a range request, got {response.status}')
                position = start
                with open(out, 'r+b') as handle:
                    handle.seek(start)
                    while block := response.read(4 * 1024 * 1024):
                        handle.write(block)
                        position += len(block)
                if position != end + 1:
                    raise IOError(f'Short range {start}-{end}: got {position - start} bytes')
                return end - start + 1
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(min(60, 2 * 2 ** attempt))


def parts(size, count):
    step = -(-size // count)
    return [(i, min(i + step, size) - 1) for i in range(0, size, step)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('size', type=int)
    parser.add_argument('out')
    parser.add_argument('--parts', type=int, default=16)
    args = parser.parse_args()
    with open(args.out, 'wb') as handle:
        handle.truncate(args.size)
    with ThreadPoolExecutor(args.parts) as pool:
        total = sum(pool.map(lambda r: fetch_range(args.url, r[0], r[1], args.out), parts(args.size, args.parts)))
    if total != args.size or os.path.getsize(args.out) != args.size:
        raise IOError(f'Size mismatch: fetched {total}, file {os.path.getsize(args.out)}, expected {args.size}')
    digest = hashlib.sha256()
    with open(args.out, 'rb') as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    print(json.dumps({'path': args.out, 'size': args.size, 'sha256': digest.hexdigest()}))


if __name__ == '__main__':
    main()
