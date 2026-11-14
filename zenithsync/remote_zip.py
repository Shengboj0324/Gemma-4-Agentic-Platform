"""Read members of a remote zip through HTTP range requests, one at a time.

Kaggle's per-file API throttled this project after a few hundred requests
(HTTP 429 on every endpoint). Its bulk endpoint costs one API call and returns
a signed storage URL for a single archive of every file — 22 GB here, larger
than the free disk of the machine doing the ingest. With range requests the
archive never has to exist locally: Python's `zipfile` reads the central
directory from the end, then each member's bytes, through a seekable reader
that fetches only the ranges it is asked for.
"""
import io


class HTTPRangeReader(io.RawIOBase):
    """Seekable, read-only view of a URL that honours `Range: bytes=a-b`."""

    def __init__(self, url, *, session=None, block=8 * 1024 * 1024, timeout=120):
        if session is None:
            import requests
            session = requests.Session()
        self.url = url
        self.session = session
        self.block = block
        self.timeout = timeout
        self.position = 0
        self._buffer_start = 0
        self._buffer = b''
        head = self._get(0, 0)
        content_range = head.headers.get('Content-Range', '')
        if head.status_code != 206 or '/' not in content_range:
            raise ValueError(f'Server does not honour range requests (status {head.status_code})')
        self.size = int(content_range.rsplit('/', 1)[1])

    def _get(self, start, end):
        response = self.session.get(self.url, headers={'Range': f'bytes={start}-{end}'},
                                    timeout=self.timeout)
        if response.status_code not in (200, 206):
            response.raise_for_status()
        return response

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            target = offset
        elif whence == io.SEEK_CUR:
            target = self.position + offset
        elif whence == io.SEEK_END:
            target = self.size + offset
        else:
            raise ValueError('Invalid whence')
        if target < 0:
            raise ValueError('Negative seek position')
        self.position = target
        return self.position

    def read(self, size=-1):
        if size is None or size < 0:
            size = self.size - self.position
        size = min(size, max(0, self.size - self.position))
        if size == 0:
            return b''
        end = self.position + size
        in_buffer = self._buffer_start <= self.position and end <= self._buffer_start + len(self._buffer)
        if not in_buffer:
            fetch_end = min(self.size, self.position + max(size, self.block)) - 1
            response = self._get(self.position, fetch_end)
            data = response.content
            if response.status_code == 200:  # server ignored Range; never trust it
                raise ValueError('Server returned the whole object to a range request')
            expected = fetch_end - self.position + 1
            if len(data) != expected:
                raise IOError(f'Short range read: {len(data)} of {expected} bytes')
            self._buffer_start, self._buffer = self.position, data
        offset = self.position - self._buffer_start
        chunk = self._buffer[offset:offset + size]
        self.position += len(chunk)
        return chunk

    def readinto(self, target):
        data = self.read(len(target))
        target[:len(data)] = data
        return len(data)


def extract_member(archive, info, destination, *, chunk=4 * 1024 * 1024):
    """Stream one member to `destination`; zipfile checks the member's CRC-32."""
    with archive.open(info) as source, destination.open('xb') as sink:
        while block := source.read(chunk):
            sink.write(block)
    return destination
