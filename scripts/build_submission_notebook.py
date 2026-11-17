"""Package an agent candidate as a Kaggle notebook that writes submission.zip.

The competition scores a notebook version whose output is `submission.zip`
(agent.yaml at the archive root). This embeds the candidate's text files in
a standard-library-only notebook, which writes them into a zip with fixed
timestamps and sorted entries. The archive is therefore byte-identical
wherever it is built, and its sha256, computed here, is printed by the
notebook for comparison. Refused: binaries in the candidate directory,
symlinks, paths outside the candidate, a missing root agent.yaml, and
non-UTF-8 text. Writes `<output>/kernel-metadata.json` and
`<output>/<slug>.ipynb`, plus `<output>/submission.zip` (the same bytes the
notebook will write) and `<output>/package.json`.

Dataset route for binaries (adapter weights): `--dataset owner/slug` plus one
`--binary ARCHIVE_PATH=SHA256` per file. The binaries are never read here; the
notebook reads each from `/kaggle/input/<slug>/<basename>`, refuses it unless
its sha256 matches, stores it uncompressed, then re-opens the finished archive
and checks that the member list and every member's sha256 equal the expected
values. No local submission.zip is written on this route (package.json records
the expected member digests instead).
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


BINARY_CODE = '''import hashlib, json, zipfile
from pathlib import Path

FILES = json.loads(FILES_JSON)
BINARIES = json.loads(BINARIES_JSON)
SOURCE = Path(SOURCE_DIR)
EXPECTED = json.loads(EXPECTED_JSON)
out = Path('/kaggle/working/submission.zip')

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 22), b''):
            digest.update(block)
    return digest.hexdigest()

for name, expected in sorted(BINARIES.items()):
    source = SOURCE / Path(name).name
    actual = sha256_file(source)
    print(name, source.stat().st_size, 'bytes, sha256', actual)
    assert actual == expected, f'{source} differs from the trained artifact'
with zipfile.ZipFile(out, 'w') as archive:
    for name in sorted(set(FILES) | set(BINARIES)):
        info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        info.external_attr = 0o644 << 16
        if name in FILES:
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, FILES[name].encode('utf-8'))
        else:
            info.compress_type = zipfile.ZIP_STORED
            with open(SOURCE / Path(name).name, 'rb') as source, archive.open(info, 'w', force_zip64=True) as target:
                for block in iter(lambda: source.read(1 << 22), b''):
                    target.write(block)
with zipfile.ZipFile(out) as archive:
    assert sorted(archive.namelist()) == sorted(EXPECTED), 'archive member list differs'
    for name, expected in sorted(EXPECTED.items()):
        digest = hashlib.sha256()
        with archive.open(name) as member:
            for block in iter(lambda: member.read(1 << 22), b''):
                digest.update(block)
        assert digest.hexdigest() == expected, f'archive member {name} differs'
print('submission.zip', out.stat().st_size, 'bytes, sha256', sha256_file(out), 'members verified', len(EXPECTED))
'''


def parse_binaries(values):
    binaries = {}
    for value in values:
        name, _, digest = value.partition('=')
        if not name or name.startswith('/') or '..' in Path(name).parts or len(digest) != 64 \
                or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError(f'Binary must be ARCHIVE_PATH=SHA256 (lowercase hex): {value}')
        if name in binaries:
            raise ValueError(f'Binary listed twice: {name}')
        binaries[name] = digest
    if len({Path(n).name for n in binaries}) != len(binaries):
        raise ValueError('Binary basenames must be unique (the dataset is flat)')
    return binaries


def binary_notebook(files, binaries, source_dir, title, description):
    expected = {n: hashlib.sha256(t.encode('utf-8')).hexdigest() for n, t in files.items()}
    overlap = set(files) & set(binaries)
    if overlap:
        raise ValueError(f'Paths both embedded and binary: {sorted(overlap)}')
    expected.update(binaries)
    # FILES_JSON last: the embedded text must not be scanned for the other placeholders
    code = (BINARY_CODE.replace('BINARIES_JSON', repr(json.dumps(binaries, sort_keys=True)))
            .replace('SOURCE_DIR', repr(source_dir))
            .replace('EXPECTED_JSON', repr(json.dumps(expected, sort_keys=True)))
            .replace('FILES_JSON', repr(json.dumps(files, sort_keys=True))))
    cells = [{'cell_type': 'markdown', 'metadata': {}, 'source': [f'# {title}\n\n{description}\n']},
             {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': [code]}]
    return {'cells': cells, 'metadata': {'kernelspec': {'name': 'python3', 'display_name': 'Python 3',
                                                         'language': 'python'},
                                          'language_info': {'name': 'python'}},
            'nbformat': 4, 'nbformat_minor': 5}, expected


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
    parser.add_argument('--dataset', help='owner/slug of the private dataset holding the binaries')
    parser.add_argument('--binary', action='append', default=[], help='ARCHIVE_PATH=SHA256 (repeatable)')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    files = collect(args.candidate)
    if args.binary or args.dataset:
        if not (args.binary and args.dataset and args.dataset.count('/') == 1):
            raise ValueError('The dataset route needs --dataset owner/slug and at least one --binary')
        binaries = parse_binaries(args.binary)
        source_dir = '/kaggle/input/' + args.dataset.split('/')[1]
        book, expected = binary_notebook(files, binaries, source_dir, args.title, args.description)
        args.output.mkdir(parents=True)
        (args.output / f'{args.slug}.ipynb').write_text(json.dumps(book, indent=1))
        (args.output / 'kernel-metadata.json').write_text(json.dumps({
            'id': f'{args.owner}/{args.slug}', 'title': args.title, 'code_file': f'{args.slug}.ipynb',
            'language': 'python', 'kernel_type': 'notebook', 'is_private': True, 'enable_gpu': False,
            'enable_tpu': False, 'enable_internet': False, 'dataset_sources': [args.dataset],
            'kernel_sources': [], 'competition_sources': [args.competition], 'model_sources': []}, indent=1))
        record = {'schema_version': 1, 'candidate': str(args.candidate), 'kernel': f'{args.owner}/{args.slug}',
                  'dataset': args.dataset, 'zip_sha256': None, 'members': expected}
        (args.output / 'package.json').write_bytes(canonical_json(record))
        print(json.dumps({'kernel': record['kernel'], 'dataset': args.dataset, 'members': expected}))
        return
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
