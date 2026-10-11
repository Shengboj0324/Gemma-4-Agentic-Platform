"""Bounded immutable input snapshots for parsers that otherwise reopen files."""

import hashlib
from pathlib import Path

from .contracts import digest, natural


def verified_source_bytes(path: Path, identity: dict, *, max_bytes: int) -> bytes:
    """Bind the parser's actual bytes to a trusted size and SHA-256 identity.

    This does not authenticate the caller's manifest or promise that the original
    path will remain unchanged. Callers retain their provenance and final drift
    checks. Reading at most the declared size plus one bounds allocation even if
    a file grows after its metadata was inspected.
    """
    natural(max_bytes, 'max_bytes')
    size = identity['size_bytes']
    natural(size, 'size_bytes')
    digest(identity['sha256'])
    if size > max_bytes:
        raise ValueError('Source exceeds byte budget')
    with path.open('rb') as stream:
        payload = stream.read(size + 1)
    if len(payload) != size or hashlib.sha256(payload).hexdigest() != identity['sha256']:
        raise ValueError('Source bytes differ from pinned identity')
    return payload
