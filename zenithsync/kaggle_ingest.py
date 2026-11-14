"""Stream a Kaggle file listing into the content-addressed store, one file at a time.

The official development set is 22.4 GB and the development machine had 16 GiB
free, so nothing here assumes the whole set can exist locally. Each worker
downloads one file into its own scratch directory, checks it against the size
Kaggle lists, hashes it, uploads it to its content address with readback, and
deletes it before taking the next. The manifest is committed only after every
file has passed; a failure leaves no commit marker.

Kaggle publishes sizes, not digests, so the digests recorded here are *ours*,
computed at ingest. They establish what was stored, not that Kaggle served the
bytes its authors intended.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath
import shutil
import zipfile

from .artifacts import file_record, relative_path


def normalise_listing(rows):
    """[(name, size)] -> sorted, validated, duplicate-free listing."""
    seen, result = set(), []
    for name, size in rows:
        path = relative_path(str(name))
        if path in seen:
            raise ValueError('Duplicate listed file: ' + path)
        if type(size) is not int or size < 0:
            raise ValueError('Invalid listed size: ' + path)
        seen.add(path)
        result.append({'path': path, 'size_bytes': size})
    if not result:
        raise ValueError('Empty listing')
    return sorted(result, key=lambda row: row['path'])


def materialise(downloaded_dir: Path, path: str) -> Path:
    """Return the downloaded file, unwrapping a single-member ``<name>.zip`` if used.

    Decided by name, never by sniffing content: a wheel is itself a zip, and
    treating one as a download wrapper would corrupt it. The Python client
    observed on 2026-11-14 delivered raw files under their own names; the CLI
    zips some. The listed size, checked afterwards, catches anything else.
    """
    name = PurePosixPath(path).name
    direct = downloaded_dir / name
    wrapped = downloaded_dir / (name + '.zip')
    if direct.is_file() and not direct.is_symlink():
        if wrapped.exists():
            raise ValueError('Both a file and a zip wrapper were downloaded for ' + path)
        return direct
    if not wrapped.is_file() or wrapped.is_symlink():
        raise ValueError('Download produced neither the file nor its zip: ' + path)
    with zipfile.ZipFile(wrapped) as archive:
        members = [m for m in archive.infolist() if not m.is_dir()]
        if len(members) != 1 or PurePosixPath(members[0].filename).name != name:
            raise ValueError('Unexpected zip wrapper contents for ' + path)
        with archive.open(members[0]) as source, direct.open('xb') as sink:
            shutil.copyfileobj(source, sink, 1024 * 1024)
    wrapped.unlink()
    return direct


def ingest_one(row, fetch, store, scratch: Path):
    """Download, check, publish and delete one listed file. Returns its record."""
    work = scratch / ('w-' + row['path'].replace('/', '__'))
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    try:
        fetch(row['path'], work)
        local = materialise(work, row['path'])
        identity = file_record(local)
        if identity['size_bytes'] != row['size_bytes']:
            raise ValueError(f"Size differs from listing for {row['path']}: "
                             f"{identity['size_bytes']} != {row['size_bytes']}")
        record = {'path': row['path'], **identity}
        uploaded = store.put_file(local, record)
        return record, uploaded
    finally:
        shutil.rmtree(work, ignore_errors=True)


def ingest(listing, fetch, store, scratch: Path, *, workers=4, log=print):
    """Ingest every listed file; return (records, uploaded_count)."""
    if type(workers) is not int or workers < 1:
        raise ValueError('Positive worker count required')
    rows = normalise_listing([(r['path'], r['size_bytes']) for r in listing])
    records, uploaded, done = {}, 0, 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(ingest_one, row, fetch, store, scratch): row for row in rows}
        for future in as_completed(futures):
            record, was_uploaded = future.result()
            records[record['path']] = record
            uploaded += int(was_uploaded)
            done += 1
            if done % 10 == 0 or done == len(rows):
                log(f'ingested {done}/{len(rows)}')
    return [records[row['path']] for row in rows], uploaded
