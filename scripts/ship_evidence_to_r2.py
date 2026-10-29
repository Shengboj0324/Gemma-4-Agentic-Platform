"""Ship every retained evidence package in one or more trees to R2.

Each package is published under its own content-addressed manifest, and an index
records where every package landed so any one of them can be restored later. A
package containing a credential path, a symlink or a non-regular file is refused
whole and listed with its reason; it is never partially published.

Re-running is cheap and safe: publication verifies what the bucket already holds
by reading it back, and uploads only what is genuinely absent.

Use `--plan` first to see what a run would do without spending bandwidth.
Nothing here deletes or rewrites a local file.
"""
import argparse
import contextlib
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record
from zenithsync.evidence_shipment import (ship_tree, shipment_index,
                                           shipment_lock)
from zenithsync.object_store import ArtifactStore
from zenithsync.r2_client import build_client

SOURCES = ['scripts/ship_evidence_to_r2.py', 'zenithsync/evidence_shipment.py',
           'zenithsync/r2_client.py', 'zenithsync/object_store.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, action='append', required=True,
                        help='Evidence tree root to ship; repeatable')
    parser.add_argument('--package-depth', type=int, default=1,
                        help='Depth below each tree root at which to group packages')
    parser.add_argument('--source-prefix', required=True,
                        help='Artifact manifest source label prefix')
    parser.add_argument('--revision', required=True,
                        help='Artifact manifest revision label')
    parser.add_argument('--output', type=Path, required=True,
                        help='New directory for the index and receipt')
    parser.add_argument('--prefix', default='artifacts/v1')
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--max-package-bytes', type=int, default=512 * 1024**2,
                        help='Refuse any single package declaring more than this')
    parser.add_argument('--max-total-bytes', type=int, default=16 * 1024**3,
                        help='Budget for the whole run across every --tree, not '
                             'per tree')
    parser.add_argument('--workers', type=int, default=1,
                        help='Publish this many packages concurrently; each '
                             'package keeps its full sequential verify contract')
    parser.add_argument('--plan', action='store_true',
                        help='Group and classify without publishing anything')
    parser.add_argument('--quiet', action='store_true',
                        help='Do not log each package as it is published')
    args = parser.parse_args()
    if args.package_depth < 1:
        parser.error('--package-depth must be a positive integer')
    if args.workers < 1:
        parser.error('--workers must be a positive integer')
    args.output.mkdir(parents=True, exist_ok=False)
    sources = {name: file_record(ROOT / name) for name in SOURCES}

    store = connection = None
    if not args.plan:
        # The connection pool must cover every worker thread, or packages block
        # on the pool instead of the network.
        client, bucket, connection = build_client(
            env_file=args.env_file,
            max_pool_connections=max(10, 2 * args.workers))
        store = ArtifactStore(client, bucket, prefix=args.prefix)

    def log(message):
        if not args.quiet:
            print(message, flush=True)

    # Two shipments against one prefix would upload the same content-addressed
    # keys, and a readback racing an in-flight overwrite can report an integrity
    # failure that is a false alarm but indistinguishable from a real one.
    holder = (shipment_lock(bucket, args.prefix, label='ship_evidence_to_r2')
              if not args.plan else contextlib.nullcontext())
    results = []
    with holder:
        # The byte budget is for the whole run, not per tree: passing the same
        # ceiling to each tree would let N trees ship up to N times it.
        remaining = args.max_total_bytes
        for tree in args.tree:
            result = ship_tree(store, tree, source_prefix=args.source_prefix,
                               revision=args.revision,
                               package_depth=args.package_depth,
                               max_package_bytes=args.max_package_bytes,
                               max_total_bytes=max(1, remaining),
                               publish=not args.plan, workers=args.workers, log=log)
            remaining -= result['planned_bytes']
            results.append(result)
            log(f'{result["status"]}: {tree} -> {result["shipped_packages"]} packages, '
                f'{result["refused_packages"]} refused, '
                f'{result["uploaded_files"]} uploaded, {result["reused_files"]} reused, '
                f'{remaining} bytes of budget left')

    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during shipment')

    index = shipment_index(results) if not args.plan else None
    shipped_total = sum(r['shipped_packages'] for r in results)
    # Sidecars first, so the receipt can bind them. Numbered by position, since
    # two --tree values can share a basename and would otherwise overwrite one
    # file, silently discarding a tree's rows.
    sidecars = {}
    for position, result in enumerate(results):
        name = f'{position:02d}-{Path(result["tree"]).name or "root"}-packages.json'
        path = args.output / name
        path.write_bytes(canonical_json(result['packages']))
        sidecars[name] = {**file_record(path), 'tree': result['tree']}
    if index is not None:
        path = args.output / 'index.json'
        path.write_bytes(canonical_json(index))
        sidecars['index.json'] = file_record(path)
    receipt = {'schema_version': 1,
               'status': ('evidence_shipped' if not args.plan else 'evidence_planned')
                         if shipped_total else
                         ('evidence_shipped_nothing' if not args.plan
                          else 'evidence_planned_nothing'),
               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'sources': sources, 'connection': connection, 'prefix': args.prefix,
               'package_depth': args.package_depth, 'workers': args.workers,
               'exclusive_lock_held': not args.plan,
               'byte_policy': {'max_package_bytes': args.max_package_bytes,
                               'max_total_bytes': args.max_total_bytes,
                               'budget_is_for_the_whole_run': True},
               'index_sha256': index and index['index_sha256'],
               'sidecar_files': sidecars,
               'trees': [{key: value for key, value in result.items()
                          if key not in ('packages', 'refused')}
                         for result in results],
               'refused': [row for result in results for row in result['refused']],
               'scope': 'Per-package content-addressed publication with readback, '
                        'covering exactly the files classification admitted. Not a '
                        'durability or access-control guarantee, and not a '
                        'statement that the evidence is correct.'}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'status': receipt['status'],
           'trees': len(results),
           'packages': sum(r['shipped_packages'] for r in results),
           'refused': sum(r['refused_packages'] for r in results),
           'uploaded_files': sum(r['uploaded_files'] for r in results),
           'reused_files': sum(r['reused_files'] for r in results),
           'verified_bytes': sum(r['verified_bytes'] for r in results),
           'index_sha256': index and index['index_sha256']})


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # The type alone is not diagnosable: an S3UploadFailedError names the
        # key and the underlying service error, and without them a failed run
        # can only be re-run blind. `load_credentials` already guarantees no
        # credential value reaches an error message.
        print(f'Evidence shipment failed ({type(error).__name__}: {error}); '
              'no passing receipt written.', file=sys.stderr)
        raise SystemExit(1)
