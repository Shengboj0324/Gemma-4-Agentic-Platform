"""Package an agent candidate as a Kaggle notebook that writes submission.zip.

The competition scores a notebook version whose output is `submission.zip`
(agent.yaml at the archive root). This embeds the candidate's text files in
a standard-library-only notebook, which writes them into a zip with fixed
timestamps and sorted entries. The archive is therefore byte-identical
wherever it is built, and its sha256, computed here, is printed by the
notebook for comparison. Refused: binaries (adapters need a dataset route,
not embedding), symlinks, paths outside the candidate, a missing root
agent.yaml, and non-UTF-8 text. Writes `<output>/kernel-metadata.json` and
`<output>/<slug>.ipynb`, plus `<output>/submission.zip` (the same bytes the
notebook will write) and `<output>/package.json`.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json

TEXT_SUFFIXES = {'.yaml', '.yml', '.md', '.txt', '.json'}
FIXED_TIME = (2026, 1, 1, 0, 0, 0)

ZIP_CODE = '''import hashlib, json, zipfile
from pathlib import Path

FILES = json.loads(FILES_JSON)
out = Path('/kaggle/working/submission.zip')
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for name in sorted(FILES):
        info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, FILES[name].encode('utf-8'))
digest = hashlib.sha256(out.read_bytes()).hexdigest()
print('submission.zip', out.stat().st_size, 'bytes, sha256', digest)
assert digest == EXPECTED_SHA256, 'archive differs from the packaged candidate'
'''


def collect(candidate):
    files = {}
    for path in sorted(candidate.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink in candidate: {path}')
        if not path.is_file():
            continue
        relative = path.relative_to(candidate).as_posix()
        if path.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError(f'Not a text file this route can embed: {relative}')
        files[relative] = path.read_bytes().decode('utf-8')
    if 'agent.yaml' not in files:
        raise ValueError('No agent.yaml at the candidate root')
    return files


def build_zip(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, files[name].encode('utf-8'))
    return buffer.getvalue()


def notebook(files, digest, title, description):
    code = ZIP_CODE.replace('FILES_JSON', repr(json.dumps(files, sort_keys=True))).replace(
        'EXPECTED_SHA256', repr(digest))
    cells = [{'cell_type': 'markdown', 'metadata': {}, 'source': [f'# {title}\n\n{description}\n']},
             {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': [code]}]
    return {'cells': cells, 'metadata': {'kernelspec': {'name': 'python3', 'display_name': 'Python 3',
                                                         'language': 'python'},
                                          'language_info': {'name': 'python'}},
            'nbformat': 4, 'nbformat_minor': 5}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--owner', required=True)
    parser.add_argument('--slug', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--description', required=True)
    parser.add_argument('--competition', default='gemma-4-developer-agent')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    files = collect(args.candidate)
    archive = build_zip(files)
    digest = hashlib.sha256(archive).hexdigest()
    args.output.mkdir(parents=True)
    (args.output / f'{args.slug}.ipynb').write_text(
        json.dumps(notebook(files, digest, args.title, args.description), indent=1))
    (args.output / 'kernel-metadata.json').write_text(json.dumps({
        'id': f'{args.owner}/{args.slug}', 'title': args.title, 'code_file': f'{args.slug}.ipynb',
        'language': 'python', 'kernel_type': 'notebook', 'is_private': True, 'enable_gpu': False,
        'enable_tpu': False, 'enable_internet': False, 'dataset_sources': [], 'kernel_sources': [],
        'competition_sources': [args.competition], 'model_sources': []}, indent=1))
    (args.output / 'submission.zip').write_bytes(archive)
    record = {'schema_version': 1, 'candidate': str(args.candidate), 'kernel': f'{args.owner}/{args.slug}',
              'zip_sha256': digest, 'zip_bytes': len(archive),
              'files': {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}
    (args.output / 'package.json').write_bytes(canonical_json(record))
    print(json.dumps({'kernel': record['kernel'], 'zip_sha256': digest, 'files': sorted(files)}))


if __name__ == '__main__':
    main()
