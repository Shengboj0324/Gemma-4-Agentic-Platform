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
import json
import os
import threading
from pathlib import Path, PurePosixPath
import shutil
import time
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


def retryable(exc):
    """Kaggle answers bursts with 429; treat that, 5xx and dropped connections as transient."""
    response = getattr(exc, 'response', None)
    status = getattr(response, 'status_code', None)
    if status is not None:
        return status == 429 or 500 <= status < 600
    return isinstance(exc, (ConnectionError, TimeoutError)) or type(exc).__name__ in (
        'ConnectionError', 'ReadTimeout', 'ConnectTimeout', 'ChunkedEncodingError')


def fetch_with_retries(fetch, path, directory, *, attempts=8, base_delay=2.0, sleep=time.sleep):
    for attempt in range(attempts):
        for stale in directory.iterdir():
            stale.unlink()
        try:
            return fetch(path, directory)
        except Exception as exc:
            if attempt + 1 == attempts or not retryable(exc):
                raise
            sleep(min(120.0, base_delay * 2 ** attempt))


def ingest_one(row, fetch, store, scratch: Path, *, sleep=time.sleep):
    """Download, check, publish and delete one listed file. Returns its record."""
    work = scratch / ('w-' + row['path'].replace('/', '__'))
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    try:
        fetch_with_retries(fetch, row['path'], work, sleep=sleep)
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


class Journal:
    """Append-only record of files already published, so a rerun skips them.

    Each line is a manifest record written only after its blob passed readback.
    The final manifest commit reads every blob back again, so a stale or wrong
    journal line cannot produce a committed manifest that lies.
    """

    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.records = {}
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    record = json.loads(line)
                    if set(record) != {'path', 'sha256', 'size_bytes'}:
                        raise ValueError('Malformed journal record')
                    self.records[record['path']] = record

    def add(self, record):
        with self.lock:
            with self.path.open('a') as stream:
                stream.write(json.dumps(record, sort_keys=True) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            self.records[record['path']] = record


def ingest_zip(listing, open_archive, store, scratch: Path, *, journal, workers=4, log=print):
    """Ingest listed files from one remote archive. ``open_archive()`` -> ZipFile.

    Each worker opens its own archive view (its own HTTP session and position).
    Sizes are checked against both Kaggle's listing and the archive's own
    directory; zipfile checks each member's CRC-32 while streaming it out.
    """
    from .remote_zip import extract_member
    rows = normalise_listing([(r['path'], r['size_bytes']) for r in listing])
    pending = [row for row in rows if row['path'] not in journal.records]
    for row in rows:
        known = journal.records.get(row['path'])
        if known is not None and known['size_bytes'] != row['size_bytes']:
            raise ValueError('Journal size differs from listing: ' + row['path'])
    shards = [pending[index::workers] for index in range(workers)]
    counter = {'done': len(rows) - len(pending), 'uploaded': 0}
    lock = threading.Lock()

    def run(shard):
        if not shard:
            return
        archive = open_archive()
        try:
            for row in shard:
                info = archive.getinfo(row['path'])
                if info.file_size != row['size_bytes']:
                    raise ValueError(f"Archive size differs from listing: {row['path']}")
                work = scratch / ('z-' + row['path'].replace('/', '__'))
                try:
                    extract_member(archive, info, work)
                    record = {'path': row['path'], **file_record(work)}
                    if record['size_bytes'] != row['size_bytes']:
                        raise ValueError('Extracted size differs: ' + row['path'])
                    uploaded = store.put_file(work, record)
                    journal.add(record)
                finally:
                    work.unlink(missing_ok=True)
                with lock:
                    counter['done'] += 1
                    counter['uploaded'] += int(uploaded)
                    if counter['done'] % 10 == 0 or counter['done'] == len(rows):
                        log(f"ingested {counter['done']}/{len(rows)}")
        finally:
            archive.close()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in [pool.submit(run, shard) for shard in shards]:
            future.result()
    return [journal.records[row['path']] for row in rows], counter['uploaded']

