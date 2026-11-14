"""Verify directories against the manifests a presigned fetch bundle delivered.

Reads the bundle's manifests.json ({name: {dest, manifest}}), groups manifests
that share a destination, and requires each destination to hold exactly their
union — no missing, extra or changed file. --remap OLD=NEW checks a copy that
was moved elsewhere. Used before a run, and after it as tamper evidence: agents'
commands run on the same machine, so the evaluation data is re-verified once
they are done. Prints one JSON line; exits non-zero on any difference.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import verify


def group(bundle, remap):
    by_dest = {}
    for name, entry in bundle.items():
        dest = remap.get(entry['dest'], entry['dest'])
        by_dest.setdefault(dest, []).append((name, entry['manifest']))
    return by_dest


def check(bundle, remap=None):
    report = {}
    for dest, items in sorted(group(bundle, remap or {}).items()):
        files = [row for _, manifest in items for row in manifest['files']]
        if len({row['path'] for row in files}) != len(files):
            raise ValueError(f'{dest}: manifests overlap')
        verify(Path(dest), {**items[0][1], 'files': files})
        report[dest] = {'manifests': [name for name, _ in items], 'files': len(files)}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifests', type=Path, required=True)
    parser.add_argument('--remap', action='append', default=[], help='OLD=NEW destination')
    args = parser.parse_args()
    remap = dict(item.split('=', 1) for item in args.remap)
    print(json.dumps({'verified': check(json.loads(args.manifests.read_text()), remap)}))


if __name__ == '__main__':
    main()
