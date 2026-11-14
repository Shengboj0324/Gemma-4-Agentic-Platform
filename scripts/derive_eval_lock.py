"""Derive the evaluation install set: serving lock + official wheelhouse overrides.

The official runtime installs its wheelhouse over the Kaggle image, so for the
packages that decide harness behaviour the wheelhouse wins. Four differ from
requirements/serving-linux-py312-httpfix.lock.txt as of the 2026-11-14 ingest:
vllm 0.19.1 (the lock's digest matches no file anywhere; the wheelhouse holds
the official build), adk-eval-core and adk-submission (same versions, rebuilt),
and swegemma (0.2.11 vs 0.2.10). Those four are taken from the wheelhouse by
exact file and digest; every other pin is the serving lock's, unchanged.

Writes requirements/eval-official-wheels.txt (installed first, --no-deps, from
${WHEELHOUSE}) and requirements/eval-linux-py312.lock.txt (the remainder).
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import file_record, load_json
from zenithsync.lock_audit import parse_lock, render_lock

OVERRIDES = ('vllm', 'swegemma', 'adk-eval-core', 'adk-submission')


def wheelhouse_index(manifest):
    index = {}
    for row in manifest['files']:
        name, version = row['path'].split('-')[:2]
        index[name.lower().replace('_', '-')] = {'version': version, 'file': row['path'], 'sha256': row['sha256']}
    return index


def derive(lock_text, manifest):
    pins = parse_lock(lock_text)
    wheels = wheelhouse_index(manifest)
    missing = [name for name in OVERRIDES if name not in wheels]
    if missing:
        raise ValueError(f'Wheelhouse lacks {missing}')
    if any(name not in {p['name'] for p in pins} for name in OVERRIDES):
        raise ValueError('Every override must replace an existing serving-lock pin')
    official = [f"{name} @ file://${{WHEELHOUSE}}/{wheels[name]['file']} --hash=sha256:{wheels[name]['sha256']}"
                for name in OVERRIDES]
    remainder = [p for p in pins if p['name'] not in OVERRIDES]
    changes = {name: {'lock': next(f"{p['version']}" for p in pins if p['name'] == name),
                      'wheelhouse': wheels[name]['version']} for name in OVERRIDES}
    return official, remainder, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, default=ROOT / 'requirements/serving-linux-py312-httpfix.lock.txt')
    parser.add_argument('--wheelhouse-manifest', type=Path,
                        default=ROOT / 'evidence/p1/official-wheelhouse-ingest-001/manifest.json')
    args = parser.parse_args()
    official, remainder, changes = derive(args.lock.read_text(), load_json(args.wheelhouse_manifest))
    source = file_record(args.lock)
    wheelhouse = file_record(args.wheelhouse_manifest)
    header = ('Evaluation lock: serving lock minus the four official-wheelhouse overrides,\n'
              'which are installed first from requirements/eval-official-wheels.txt.\n'
              f'Derived by scripts/derive_eval_lock.py from {args.lock.name} '
              f'(sha256 {source["sha256"]}) and wheelhouse manifest sha256 {wheelhouse["sha256"]}.\n')
    (ROOT / 'requirements/eval-linux-py312.lock.txt').write_text(
        render_lock(remainder, [p['name'] for p in remainder], header=header))
    (ROOT / 'requirements/eval-official-wheels.txt').write_text(
        '# Official wheelhouse builds that decide harness behaviour; install with\n'
        '#   WHEELHOUSE=<dir> pip install --no-deps --require-hashes -r this-file\n'
        f'# Version changes against the serving lock: {changes}\n' + '\n'.join(official) + '\n')
    print(changes)


if __name__ == '__main__':
    main()
