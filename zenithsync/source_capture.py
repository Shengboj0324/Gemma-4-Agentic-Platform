"""Bounded export of selected committed blobs; never a rights approval."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


def capture_tracked_sources(root, output, paths, *, expected_commit,
                            expected_tree, max_file_bytes=2 * 1024**2,
                            max_total_bytes=8 * 1024**2, max_files=128):
    """Export explicit regular Git blobs from an identity-checked clean snapshot.

    All sizes are checked before blob reads. Symlinks and submodules are excluded.
    The successful report is written last; partial output is not acceptance.
    Commit/tree identity must come from separately qualified snapshot evidence.
    This does not inspect embedded licenses or dependency notices automatically.
    """
    for value in (max_file_bytes, max_total_bytes, max_files):
        if type(value) is not int or value <= 0:
            raise ValueError('Positive integer capture limits required')
    for value in (expected_commit, expected_tree):
        if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', value) is None:
            raise ValueError('Full hexadecimal Git identities required')
    if not isinstance(paths, list) or not 0 < len(paths) <= max_files:
        raise ValueError('Nonempty bounded explicit path list required')
    for name in paths:
        if (not isinstance(name, str) or not name or '\x00' in name
                or '\\' in name or PurePosixPath(name).is_absolute()
                or any(part in ('', '.', '..', '.git') for part in name.split('/'))):
            raise ValueError('Canonical relative source paths required')
    if len(set(paths)) != len(paths):
        raise ValueError('Duplicate source paths')
    root = Path(root).resolve(strict=True)
    output = Path(output)

    def git(*args):
        return subprocess.check_output(
            ['git', '--no-replace-objects', '-C', str(root), *args], timeout=30)

    if Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve() != root:
        raise ValueError('Source root must be the Git top level')

    def check_snapshot():
        if (git('rev-parse', 'HEAD').decode().strip() != expected_commit
                or git('rev-parse', 'HEAD^{tree}').decode().strip() != expected_tree):
            raise ValueError('Snapshot identity mismatch')
        if git('status', '--porcelain', '--untracked-files=no').strip():
            raise ValueError('Tracked checkout modifications')

    check_snapshot()
    selected = []
    total = 0
    for name in sorted(paths):
        raw = git('ls-tree', '-z', expected_commit, '--', ':(literal)' + name)
        entries = raw.split(b'\0')
        if len(entries) != 2 or entries[-1] != b'':
            raise ValueError('Exactly one tracked source required: ' + name)
        metadata, returned_name = entries[0].split(b'\t', 1)
        mode, kind, blob = metadata.decode('ascii').split()
        if returned_name.decode('utf-8') != name or mode not in ('100644', '100755') or kind != 'blob':
            raise ValueError('Regular tracked source required: ' + name)
        size = int(git('cat-file', '-s', blob).decode('ascii'))
        total += size
        if size < 0 or size > max_file_bytes or total > max_total_bytes:
            raise ValueError('Source byte budget exceeded')
        selected.append((name, mode, blob, size))
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for name, mode, blob, size in selected:
        content = git('cat-file', 'blob', blob)
        algorithm = 'sha1' if len(blob) == 40 else 'sha256'
        object_hash = hashlib.new(algorithm, b'blob ' + str(size).encode('ascii') + b'\0' + content).hexdigest()
        if len(content) != size or object_hash != blob:
            raise ValueError('Blob content identity mismatch')
        destination = output / 'source' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(content)
        records.append({'path': name, 'mode': mode, 'git_blob': blob,
                        'size_bytes': size, 'sha256': hashlib.sha256(content).hexdigest()})
    check_snapshot()
    report = {'schema_version': 1, 'commit': expected_commit, 'tree': expected_tree,
              'files': records, 'total_bytes': total, 'training_approved': False,
              'scope': 'Explicit committed source blobs only; no exhaustive notice or rights clearance.'}
    with (output / 'report.json').open('x') as stream:
        json.dump(report, stream, sort_keys=True)
    return report
