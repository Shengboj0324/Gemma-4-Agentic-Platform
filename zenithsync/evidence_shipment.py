"""Group an evidence tree into packages and publish each one, with an index.

The object store moves one curated bundle at a time. A tree of thousands of
retained evidence directories needs the same guarantees applied package by
package, plus an index that says which packages were shipped and under which
manifest, so a later reader can restore any one of them without guessing.

**Classification is authoritative.** Each package is staged into a fresh
directory holding exactly the files classification admitted, and published from
there. An earlier version instead handed the live directory to
`artifacts.inventory`, which walks recursively and knows nothing about grouping
or exclusions — so a package at or above the grouping depth published its whole
subtree, files deeper than the grouping depth were published twice under two
manifests, byte ceilings were checked against a fraction of what shipped, and
skipped directories such as `__pycache__` shipped anyway. Staging is what makes
the refusals below mean what they say.

Three things are refused rather than worked around, and a refusal names its
package:

* A package whose root path, or whose contents, include a **credential path**
  (`.env`, `.ssh`, `.aws`, `.kaggle`) is refused whole. Shipping it with the
  file removed would publish a bundle whose manifest disagrees with the
  directory it was built from. The package root's own components are checked as
  well as the paths beneath it, because a root named `.ssh` contributes nothing
  to the relative paths inside it — and so escaped every guard, including the
  object store's, which inspects those same relative paths.
* A package containing a **symlink or non-regular file** is refused whole, since
  the inventory contract covers regular files and a symlink's target is not part
  of the bundle. Directory symlinks are refused too, rather than being invisible
  to classification and then aborting the whole run inside `inventory`.
* A package **over its byte ceiling** is refused, so one unexpectedly large
  directory cannot consume the whole transfer budget.

Reconstructable metadata, caches and environments are *skipped*, not refused:
`.git`, `__pycache__`, virtual environments and the like. `.git` belongs there
rather than with the credential paths — a repository checkout's working tree is
the retained evidence, while its VCS metadata is reproducible from the pinned
commit and is a place a remote URL could carry a credential.

Nothing here deletes, overwrites or rewrites a file in the source tree.
Publication is content-addressed, so re-running re-verifies what is already
present instead of uploading it again.

An interrupted run is safe to resume. Each package commits its manifest only
after every blob it names has been read back and verified, so a killed process
leaves complete published packages plus, at worst, uploaded blobs that no
manifest references yet. Those are content-addressed and are reused by the next
run, so resuming costs a presence check per file and no re-upload. There is no
partially published package and nothing to clean up.

Two publishers must not run against one bucket prefix at the same time. Both
would upload the same content-addressed keys, and a readback that races an
in-flight overwrite of the same key can return a length or digest that matches
neither writer — which the object store correctly reports as an integrity
failure and which aborts the run. The bytes are identical either way, so this is
a false alarm rather than corruption, but it is indistinguishable from a real one
at the point it is raised, so it must be prevented. `shipment_lock` provides that
mutual exclusion.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from .artifacts import canonical_json, file_record, inventory, relative_path

# Credential-bearing path components. A package containing one is refused whole.
# `object_store._snapshot` refuses these too; checking here reports the problem
# against its package instead of aborting the whole run.
FORBIDDEN_PARTS = frozenset({'.ssh', '.aws', '.kaggle'})
# Reconstructable metadata, caches and environments: never evidence, and skipped
# rather than refused.
SKIPPED_DIRECTORIES = frozenset({'.git', '__pycache__', '.venv', 'venv',
                                 'node_modules', '.pytest_cache', '.mypy_cache',
                                 '.ruff_cache', '.hg', '.svn'})


def forbidden(relative: str) -> bool:
    """True when any component of a path is credential-bearing."""
    parts = relative.split('/')
    return any(part in FORBIDDEN_PARTS or part == '.env' or part.startswith('.env.')
               for part in parts)


class ShipmentLockError(RuntimeError):
    """Another publisher holds the lock for this bucket prefix."""


def _process_started(pid):
    """Return a process's start time as the OS reports it, or None.

    A PID alone cannot identify a process: PIDs are recycled, so a lock naming a
    dead publisher's PID could name an unrelated live process and block a prefix
    forever. Pairing the PID with its start time makes the identity usable.
    """
    import subprocess
    try:
        result = subprocess.run(['ps', '-o', 'lstart=', '-p', str(pid)],
                                check=True, capture_output=True, text=True,
                                timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


class shipment_lock:
    """Exclude a second *publisher* against the same bucket prefix.

    A context manager holding a lock file keyed by bucket and prefix. The file is
    written complete and then linked into place atomically, so a second
    publisher never observes a half-written lock. An earlier version created the
    file with `O_EXCL` and wrote the payload afterwards, leaving a window in
    which another publisher saw an empty file, concluded the lock was stale and
    reclaimed a *live* publisher's lock — after which release-by-path could
    delete a third publisher's lock in turn.

    Every command that writes to a prefix takes this, not only the bulk
    shipment: the hazard is two writers of the same content-addressed key, and
    which command they are does not matter. `label` records what is holding it.

    A lock is reclaimed only when its recorded process is genuinely gone, judged
    by PID *and* the process start time the OS reports, since PIDs are recycled
    and a recycled PID would otherwise block a prefix with no path to recovery.
    Release unlinks the lock only if it is still the one this object wrote.
    """

    def __init__(self, bucket, prefix, *, label='shipment', directory=None):
        if not isinstance(bucket, str) or not bucket.strip():
            raise ValueError('Bucket is required for the shipment lock')
        if not isinstance(prefix, str) or not prefix.strip():
            raise ValueError('Prefix is required for the shipment lock')
        key = hashlib.sha256(canonical_json([bucket, prefix])).hexdigest()[:32]
        base = Path(directory) if directory is not None else Path(tempfile.gettempdir())
        self.path = base / ('zenithsync-shipment-' + key + '.lock')
        self.bucket = bucket
        self.prefix = prefix
        self.label = label if isinstance(label, str) and label.strip() else 'publisher'
        self._payload = None

    def _holder(self):
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @staticmethod
    def _alive(holder):
        """True when the recorded process is still the one that took the lock."""
        if not isinstance(holder, dict):
            return False
        pid = holder.get('pid')
        if type(pid) is not int or pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            # A live process this user cannot signal. That says the PID is in
            # use, not that it is still the holder, so fall through to the
            # start-time comparison rather than short-circuiting here — PID 1 is
            # exactly this case and would otherwise block a prefix forever.
            pass
        recorded = holder.get('process_started')
        if recorded is None:
            # No start time to compare against. Treat the PID as the holder
            # rather than risk reclaiming a live publisher's lock.
            return True
        current = _process_started(pid)
        if current is None:
            return True
        # A different start time means this PID was recycled; the holder is gone.
        return current == recorded

    def _link(self, payload):
        """Write the payload complete, then link it into place atomically."""
        descriptor, staged = tempfile.mkstemp(
            prefix='.shipment-lock-', dir=self.path.parent)
        staged = Path(staged)
        try:
            with os.fdopen(descriptor, 'w') as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(staged, 0o600)
            os.link(staged, self.path)
        finally:
            staged.unlink(missing_ok=True)

    def __enter__(self):
        from datetime import datetime, timezone
        payload = json.dumps({
            'pid': os.getpid(), 'bucket': self.bucket, 'prefix': self.prefix,
            'label': self.label,
            'process_started': _process_started(os.getpid()),
            'started_utc': datetime.now(timezone.utc).isoformat()})
        for attempt in range(2):
            try:
                self._link(payload)
            except FileExistsError:
                holder = self._holder()
                if self._alive(holder):
                    raise ShipmentLockError(
                        f'another publisher ({(holder or {}).get("label", "unknown")},'
                        f' pid {(holder or {}).get("pid")}, started '
                        f'{(holder or {}).get("started_utc")}) is writing to '
                        f'{self.bucket}/{self.prefix}; concurrent writers can trip '
                        'the integrity guard on a shared content-addressed key')
                if attempt:
                    raise ShipmentLockError('shipment lock could not be reclaimed: '
                                            + str(self.path))
                # The recorded process is gone; a killed publisher leaves nothing
                # to clean up, so the lock is safe to reclaim.
                self.path.unlink(missing_ok=True)
                continue
            self._payload = payload
            return self
        raise ShipmentLockError('shipment lock could not be acquired')

    def __exit__(self, *exception):
        # Release only the lock this object wrote. Unlinking by path alone could
        # delete a lock another publisher had meanwhile acquired.
        if self._payload is not None:
            try:
                current = self.path.read_text(encoding='utf-8')
            except OSError:
                current = None
            if current == self._payload:
                self.path.unlink(missing_ok=True)
        self._payload = None
        return False


def discover_packages(tree: Path, *, package_depth=1):
    """Group a tree's files into packages at a fixed depth below its root.

    Files lying above the grouping depth are collected into the package named for
    the directory that holds them, so nothing in the tree is left out of the
    grouping and no file is assigned to two packages. Directory symlinks are
    collected as entries so classification can refuse them, rather than being
    invisible here and aborting the run later inside `inventory`.
    """
    if type(package_depth) is not int or package_depth < 1:
        raise ValueError('Package depth must be a positive integer')
    tree = Path(tree)
    if tree.is_symlink() or not tree.is_dir():
        raise ValueError('Evidence tree must be an ordinary directory')
    tree = tree.resolve(strict=True)
    packages = {}
    for directory, dirs, names in os.walk(tree, followlinks=False):
        kept = sorted(name for name in dirs if name not in SKIPPED_DIRECTORIES)
        links = [name for name in kept if (Path(directory) / name).is_symlink()]
        dirs[:] = kept
        current = Path(directory)
        relative = current.relative_to(tree)
        depth = len(relative.parts)
        root = current if depth <= package_depth else tree / Path(*relative.parts[:package_depth])
        for name in sorted(names + links):
            packages.setdefault(root, []).append(current / name)
    return {root: rows for root, rows in sorted(packages.items()) if rows}


def classify_package(root: Path, files, *, max_package_bytes, tree=None):
    """Decide whether a package can be published, and why not when it cannot.

    `tree` supplies the package root's own relative path for the credential
    check: a root named `.ssh` contributes nothing to the paths relative to
    itself, so without this a credential directory that *is* a package root
    escapes every guard, including the object store's.

    `admitted_paths` is the exact file set a publish will cover. Staging from it
    is what keeps classification and publication in agreement.
    """
    root = Path(root)
    problems, admitted, total = [], [], 0
    if tree is not None:
        label = root.relative_to(Path(tree).resolve()).as_posix()
        if label and label != '.' and forbidden(label):
            problems.append('credential_or_workspace_metadata_root:' + label)
    for path in files:
        name = path.relative_to(root).as_posix()
        try:
            relative_path(name)
        except ValueError:
            problems.append('non_canonical_path:' + name)
            continue
        if forbidden(name):
            problems.append('credential_or_workspace_metadata:' + name)
            continue
        if set(name.split('/')) & SKIPPED_DIRECTORIES:
            # Skipped rather than refused, and excluded from the publish set.
            continue
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            problems.append('symlink:' + name)
            continue
        if not stat.S_ISREG(mode):
            problems.append('non_regular_file:' + name)
            continue
        total += path.lstat().st_size
        admitted.append(name)
    if not admitted and not problems:
        problems.append('no_regular_files')
    if total > max_package_bytes:
        problems.append(f'exceeds_package_ceiling:{total}>{max_package_bytes}')
    return {'root': str(root), 'files': len(admitted), 'declared_bytes': total,
            'admitted_paths': sorted(admitted),
            'problems': problems, 'publishable': not problems}


def _without_paths(verdict, **extra):
    return {**{key: value for key, value in verdict.items()
               if key != 'admitted_paths'}, **extra}


def _stage(root: Path, admitted, staging: Path):
    """Copy exactly the admitted files into a fresh directory, verifying each."""
    for name in admitted:
        source = root / name
        identity = file_record(source)
        target = staging / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            raise ValueError('Staged paths must not alias: ' + name)
        shutil.copyfile(source, target)
        if file_record(target) != identity:
            raise ValueError('Staged copy identity differs: ' + name)


def _publish_one(store, root: Path, label, *, source_prefix, revision, verdict, log):
    """Stage the admitted files, publish from the staging tree, then discard it.

    Publishing from staging is what makes classification authoritative: the
    manifest covers exactly the files classification admitted, with no
    re-walking of the live directory and so no subtree, cache or duplicate.
    """
    with tempfile.TemporaryDirectory(prefix='.ship-') as temporary:
        staging = Path(temporary) / 'package'
        staging.mkdir(mode=0o700)
        _stage(root, verdict['admitted_paths'], staging)
        manifest = inventory(staging, kind='candidate',
                             source=source_prefix + ':' + label, revision=revision)
        if len(manifest['files']) != verdict['files']:
            raise ValueError('Staged manifest covers a different file set: ' + label)
        if sum(row['size_bytes'] for row in manifest['files']) != verdict['declared_bytes']:
            raise ValueError('Staged manifest bytes differ from classification: ' + label)
        result = store.publish(staging, manifest)
    if log is not None:
        log(f'published {label}: {len(manifest["files"])} files, '
            f'{result["verified_bytes"]} bytes, {result["uploaded_files"]} uploaded')
    return _without_paths(verdict, published=True,
                          manifest_sha256=result['manifest_sha256'],
                          manifest_key=result['manifest_key'],
                          uploaded_files=result['uploaded_files'],
                          reused_files=result['reused_files'],
                          verified_bytes=result['verified_bytes'],
                          manifest_files=len(manifest['files']))


def ship_tree(store, tree: Path, *, source_prefix, revision, package_depth=1,
              max_package_bytes=512 * 1024**2, max_total_bytes=16 * 1024**3,
              publish=True, workers=1, log=None):
    """Publish every publishable package under a tree and return an index.

    `publish=False` performs the same grouping and classification without any
    transport, which is the honest way to see what a run would do before it
    spends bandwidth. Refused packages are listed with their reasons; they are
    never partially published.

    `workers` above one publishes *different packages* concurrently. Each package
    keeps its full sequential contract — stage, verify, read back or upload every
    blob, verify again, commit the manifest — so concurrency changes throughput
    and nothing else. Admission against `max_total_bytes` is decided before any
    transport, in sorted package order, so the admitted set does not depend on
    worker scheduling. A failing package cancels the queued ones, rather than
    letting them commit manifests behind an error nobody has seen yet.
    """
    if not isinstance(source_prefix, str) or not source_prefix.strip():
        raise ValueError('Source label prefix is required')
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError('Revision label is required')
    for name, value in (('max_package_bytes', max_package_bytes),
                        ('max_total_bytes', max_total_bytes),
                        ('workers', workers)):
        if type(value) is not int or value <= 0:
            raise ValueError(name + ' must be a positive integer')
    tree = Path(tree).resolve(strict=True)
    discovered = discover_packages(tree, package_depth=package_depth)
    admitted, refused = [], []
    planned_bytes = 0
    for root, files in discovered.items():
        verdict = classify_package(root, files, max_package_bytes=max_package_bytes,
                                   tree=tree)
        label = root.relative_to(tree).as_posix() or '.'
        verdict['package'] = label
        if not verdict['publishable']:
            refused.append(_without_paths(verdict))
            continue
        if planned_bytes + verdict['declared_bytes'] > max_total_bytes:
            refused.append(_without_paths(
                verdict, publishable=False,
                problems=[f'exceeds_total_ceiling:'
                          f'{planned_bytes + verdict["declared_bytes"]}'
                          f'>{max_total_bytes}']))
            continue
        planned_bytes += verdict['declared_bytes']
        admitted.append((root, label, verdict))

    shipped = []
    if not publish:
        shipped = [_without_paths(verdict, published=False)
                   for _, _, verdict in admitted]
    elif workers == 1:
        for root, label, verdict in admitted:
            shipped.append(_publish_one(store, root, label, source_prefix=source_prefix,
                                        revision=revision, verdict=verdict, log=log))
    else:
        from concurrent.futures import ThreadPoolExecutor
        import threading

        guard = threading.Lock()

        def logged(message):
            if log is not None:
                with guard:
                    log(message)

        pool = ThreadPoolExecutor(max_workers=workers)
        try:
            futures = [pool.submit(_publish_one, store, root, label,
                                   source_prefix=source_prefix, revision=revision,
                                   verdict=verdict, log=logged)
                       for root, label, verdict in admitted]
            try:
                # Collected in submission order, so the result is independent of
                # scheduling. On a failure the queued packages are cancelled: an
                # earlier version let them all publish behind an error nobody had
                # seen, committing manifests no index would locate.
                shipped = [future.result() for future in futures]
            except BaseException:
                for future in futures:
                    future.cancel()
                raise
        finally:
            pool.shutdown(wait=True, cancel_futures=True)

    uploaded = sum(row.get('uploaded_files', 0) for row in shipped)
    reused = sum(row.get('reused_files', 0) for row in shipped)
    verified_bytes = sum(row.get('verified_bytes', 0) for row in shipped)
    return {'schema_version': 1,
            'status': 'tree_shipped' if publish else 'tree_planned',
            'tree': str(tree), 'package_depth': package_depth,
            'source_prefix': source_prefix, 'revision': revision,
            'workers': workers if publish else 1,
            'max_package_bytes': max_package_bytes,
            'max_total_bytes': max_total_bytes,
            'discovered_packages': len(discovered),
            'shipped_packages': len(shipped), 'refused_packages': len(refused),
            'planned_bytes': planned_bytes, 'verified_bytes': verified_bytes,
            'uploaded_files': uploaded, 'reused_files': reused,
            'packages': shipped, 'refused': refused,
            'scope': 'Content-addressed publication and readback of each package, '
                     'covering exactly the files classification admitted. Not a '
                     'durability, replication or access-control guarantee, and not '
                     'a statement that the evidence is correct.'}


def shipment_index(results):
    """Combine per-tree results into one index a reader can restore from."""
    if not isinstance(results, list) or not results:
        raise ValueError('Nonempty shipment result list required')
    packages = []
    seen = set()
    for result in results:
        for row in result['packages']:
            if not row.get('published'):
                continue
            key = (result['tree'], row['package'])
            if key in seen:
                raise ValueError('Duplicate package in shipment index: ' + row['package'])
            seen.add(key)
            packages.append({'tree': result['tree'], 'package': row['package'],
                             'manifest_sha256': row['manifest_sha256'],
                             'manifest_key': row['manifest_key'],
                             'files': row['manifest_files'],
                             'bytes': row['verified_bytes']})
    return {'schema_version': 1, 'status': 'shipment_index',
            'trees': [result['tree'] for result in results],
            'packages': len(packages),
            'files': sum(row['files'] for row in packages),
            'bytes': sum(row['bytes'] for row in packages),
            'uploaded_files': sum(r['uploaded_files'] for r in results),
            'reused_files': sum(r['reused_files'] for r in results),
            'refused_packages': sum(r['refused_packages'] for r in results),
            'index': packages,
            'index_sha256': hashlib.sha256(canonical_json(packages)).hexdigest(),
            'scope': 'Where each shipped package lives in the bucket and under '
                     'which manifest. Restoring one still requires authenticating '
                     'its manifest separately.'}


def verify_local_coverage(trees, remote_digests, *, package_depth=1,
                          max_package_bytes=512 * 1024**2):
    """Report which *shippable* local files are not present as remote blobs.

    Files a package refuses or skips by design are counted as exclusions, not as
    gaps: reporting a deliberately refused credential file as a missing upload
    would make `complete` unreachable and give a reader nothing to act on.

    A file reachable from two overlapping trees is counted once.

    This is a coverage statement about content, not about manifests: a covered
    digest means the bytes exist remotely, not that a manifest references them.
    """
    if not isinstance(remote_digests, (set, frozenset)):
        raise ValueError('remote_digests must be a set of hex digests')
    covered = missing = excluded = 0
    covered_bytes = missing_bytes = excluded_bytes = 0
    gaps, exclusions = {}, {}
    seen = set()
    for tree in trees:
        resolved = Path(tree).resolve(strict=True)
        for root, files in discover_packages(resolved,
                                             package_depth=package_depth).items():
            verdict = classify_package(root, files,
                                       max_package_bytes=max_package_bytes,
                                       tree=resolved)
            admitted = set(verdict['admitted_paths'])
            publishable = verdict['publishable']
            for path in files:
                name = path.relative_to(root).as_posix()
                key = str(path)
                if key in seen:
                    continue
                seen.add(key)
                if name not in admitted or not publishable:
                    size = 0 if path.is_symlink() or not path.is_file() \
                        else path.lstat().st_size
                    excluded += 1
                    excluded_bytes += size
                    row = exclusions.setdefault(str(root), [0, 0])
                    row[0] += 1
                    row[1] += size
                    continue
                record = file_record(path)
                if record['sha256'] in remote_digests:
                    covered += 1
                    covered_bytes += record['size_bytes']
                else:
                    missing += 1
                    missing_bytes += record['size_bytes']
                    row = gaps.setdefault(str(root), [0, 0])
                    row[0] += 1
                    row[1] += record['size_bytes']
    return {'schema_version': 1, 'covered_files': covered, 'missing_files': missing,
            'covered_bytes': covered_bytes, 'missing_bytes': missing_bytes,
            'excluded_files': excluded, 'excluded_bytes': excluded_bytes,
            'complete': missing == 0,
            'gaps': dict(sorted(gaps.items(), key=lambda kv: -kv[1][1])),
            'exclusions': dict(sorted(exclusions.items(), key=lambda kv: -kv[1][1])),
            'scope': 'Content presence for the files a shipment would publish. '
                     'Files refused or skipped by design are reported separately '
                     'as exclusions, not as gaps. A covered digest means the bytes '
                     'are in the bucket, not that any manifest references them.'}
