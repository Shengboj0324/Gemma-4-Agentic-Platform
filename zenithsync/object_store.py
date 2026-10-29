"""Content-addressed artifact transport using an injected S3-compatible client.

Only explicit, curated, quiescent bundles belong here, never a workspace root.
Remote bytes are streamed and hashed; ETags are never treated as SHA-256.
Local destination parents must be owned and free of concurrent writers.
"""

import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading

from .artifacts import canonical_json, relative_path, validate_manifest, verify
from .contracts import digest, natural


class IntegrityError(ValueError):
    """An object does not match its declared content identity."""


def _missing(exc: Exception) -> bool:
    response = getattr(exc, "response", {})
    return response.get("Error", {}).get("Code") in {"NoSuchKey", "404", "NotFound"}


def _snapshot(manifest: object) -> dict:
    result = json.loads(canonical_json(validate_manifest(manifest)))
    paths = {row["path"] for row in result["files"]}
    for path in paths:
        parts = path.split("/")
        if any(part in {".git", ".ssh", ".aws", ".kaggle"} or
               part == ".env" or part.startswith(".env.") for part in parts):
            raise ValueError("credential or workspace metadata path excluded")
        if any("/".join(parts[:i]) in paths for i in range(1, len(parts))):
            raise ValueError("file/directory path collision")
    return result


class ArtifactStore:
    """Content-addressed publish and restore over an S3-compatible client.

    `verify_once_per_run` narrows what a publish establishes, so it is off by
    default and the caller must ask for it. With it off, every file of every
    bundle is read back from the bucket, so each bundle's result rests on its
    own reads. With it on, a key already read back and verified in this store's
    lifetime is not read again, and a later bundle's result rests on an earlier
    read in the same run instead.

    That is sound only because the keys are content-addressed and immutable and
    the caller holds an exclusive lock on the prefix, and it exists because the
    alternative is worse: evidence trees share files heavily, so concurrent
    workers issue simultaneous GETs on one hot object and R2 answers
    `503 ServiceUnavailable: Reduce your rate of simultaneous reads on the same
    object`. A caller that turns this on should record that it did.
    """

    def __init__(self, client, bucket: str, prefix: str = "artifacts/v1", *,
                 verify_once_per_run: bool = False):
        if not isinstance(bucket, str) or not bucket.strip():
            raise ValueError("bucket is required")
        self.client = client
        self.bucket = bucket
        self.prefix = relative_path(prefix)
        self.verify_once_per_run = bool(verify_once_per_run)
        # Shared by every worker thread using this store, so the set needs a
        # lock of its own.
        self._verified = set()
        self._verified_lock = threading.Lock()

    def _already_verified(self, key, record):
        """True when this exact key, size and digest passed readback already."""
        if not self.verify_once_per_run:
            return False
        with self._verified_lock:
            return (key, record["sha256"], record["size_bytes"]) in self._verified

    def _record_verified(self, key, record):
        if not self.verify_once_per_run:
            return
        with self._verified_lock:
            self._verified.add((key, record["sha256"], record["size_bytes"]))

    def blob_key(self, sha256: str) -> str:
        digest(sha256)
        return f"{self.prefix}/blobs/sha256/{sha256}"

    def _read_verified(self, key: str, record: dict, target=None) -> None:
        # Only a verification-only read may be skipped. A read with a target
        # must transfer the bytes, so it always goes to the network.
        if target is None and self._already_verified(key, record):
            return
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body = response["Body"]
        hasher, size = hashlib.sha256(), 0
        try:
            if response.get("ContentLength") != record["size_bytes"]:
                raise IntegrityError("remote content length differs")
            while chunk := body.read(1024 * 1024):
                size += len(chunk)
                if size > record["size_bytes"]:
                    raise IntegrityError("remote stream exceeds declared size")
                hasher.update(chunk)
                if target is not None:
                    target.write(chunk)
            if size != record["size_bytes"] or hasher.hexdigest() != record["sha256"]:
                raise IntegrityError("remote content digest or size differs")
        finally:
            body.close()
        # Recorded only after the digest matched, and only for a
        # verification-only read, so a partial transfer never marks a key clean.
        if target is None:
            self._record_verified(key, record)

    def publish(self, root: Path, manifest: object) -> dict:
        """Commit a manifest only after all referenced bytes pass readback.

        Retrying reuses verified whole objects. Multipart retries/cleanup are
        delegated to the SDK; a killed process may leave incomplete uploads.
        """
        frozen = _snapshot(manifest)
        verify(root, frozen)
        uploaded, reused = 0, 0
        for record in frozen["files"]:
            key = self.blob_key(record["sha256"])
            try:
                self._read_verified(key, record)
            except Exception as exc:
                if not _missing(exc):
                    raise
                self.client.upload_file(str(root / record["path"]), self.bucket, key)
                self._read_verified(key, record)
                uploaded += 1
            else:
                reused += 1
        # Detect source drift before publishing the bundle's commit marker.
        verify(root, frozen)
        payload = canonical_json(frozen)
        identity = hashlib.sha256(payload).hexdigest()
        key = f"{self.prefix}/manifests/sha256/{identity}.json"
        record = {"sha256": identity, "size_bytes": len(payload)}
        try:
            self._read_verified(key, record)
        except Exception as exc:
            if not _missing(exc):
                raise
            self.client.put_object(Bucket=self.bucket, Key=key, Body=payload,
                                   ContentType="application/json")
            self._read_verified(key, record)
        return {"manifest_sha256": identity, "manifest_key": key,
                "uploaded_files": uploaded, "reused_files": reused,
                "verified_bytes": sum(r["size_bytes"] for r in frozen["files"])}

    def restore(self, manifest: object, destination: Path, *, max_bytes: int) -> dict:
        """Restore a trusted manifest into a new directory, atomically on success.

        No partially validated output is exposed at the destination. The caller
        must authenticate the manifest separately and provide a disk-size cap.
        """
        frozen = _snapshot(manifest)
        natural(max_bytes, "max_bytes")
        total = sum(row["size_bytes"] for row in frozen["files"])
        if total > max_bytes:
            raise ValueError("artifact exceeds restore byte budget")
        if os.path.lexists(destination):
            raise FileExistsError("restore destination already exists")
        parent = destination.parent.resolve(strict=True)
        # Bind relative destinations once, before any transport callbacks run.
        destination = parent / destination.name
        # Reject an already-impossible transfer before spending network bandwidth.
        # Available space can change concurrently; write/fsync failures below
        # still abort staging without exposing an incomplete destination.
        if shutil.disk_usage(parent).free < total:
            raise OSError(errno.ENOSPC, "insufficient free space for artifact restore", str(parent))
        with tempfile.TemporaryDirectory(prefix=".restore-", dir=parent) as temporary:
            staging = Path(temporary) / "bundle"
            staging.mkdir(mode=0o700)
            for row in frozen["files"]:
                path = staging / row["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as stream:
                    self._read_verified(self.blob_key(row["sha256"]), row, stream)
                    stream.flush()
                    os.fsync(stream.fileno())
            verify(staging, frozen)
            if os.path.lexists(destination):
                raise FileExistsError("restore destination appeared during transfer")
            staging.rename(destination)
        # Verify the public destination after promotion and temporary cleanup.
        # This is a point-in-time check, not protection from later external edits.
        verify(destination, frozen)
        return {"restored_files": len(frozen["files"]), "verified_bytes": total,
                "destination": str(destination), "destination_verified": True}
