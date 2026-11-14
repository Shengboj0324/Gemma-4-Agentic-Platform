"""Freeze the official development tasks into pilot / development / holdout.

Reads tasks.jsonl, checks it against the ingest manifest by digest, and writes
split.json (task identities, groups and counts only — no patches or issue text)
to a new --output. Run before any evaluation outcome exists.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.official_split import freeze_split

SEED = 'zenithsync-official-devset-split-2026-11-14'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', type=Path, required=True)
    parser.add_argument('--ingest-manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    manifest = load_json(args.ingest_manifest)
    listed = {row['path']: {k: row[k] for k in ('sha256', 'size_bytes')} for row in manifest['files']}
    identity = file_record(args.tasks)
    if listed.get('tasks.jsonl') != identity:
        raise ValueError('tasks.jsonl differs from the ingested official file')
    tasks = [json.loads(line) for line in args.tasks.read_text().splitlines() if line.strip()]
    record = freeze_split(tasks, seed=SEED, inputs={
        'tasks.jsonl': identity, 'ingest_manifest': file_record(args.ingest_manifest),
        'module': file_record(ROOT / 'zenithsync/official_split.py')})
    args.output.mkdir(parents=True)
    (args.output / 'split.json').write_bytes(canonical_json(record))
    print(json.dumps({role: len(ids) for role, ids in record['roles'].items()}
                     | {'freeze_sha256': record['freeze_sha256']}))


if __name__ == '__main__':
    main()
