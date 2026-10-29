"""Group an evidence tree into packages and publish each one, with an index.

The object store moves one curated bundle at a time. A tree of thousands of
retained evidence directories needs the same guarantees applied package by
package, plus an index that says which packages were shipped and under which
manifest, so a later reader can restore any one of them without guessing.

Three refusals are deliberate and are reported rather than worked around:

* A package containing a credential or workspace-metadata path is refused
  whole. Silently skipping the file would publish a bundle whose manifest
  disagrees with the directory it was built from.
* A package containing a symlink or any non-regular file is refused whole,
  because the inventory contract covers regular files only and a symlink's
  target is not part of the bundle.
* A package whose declared bytes exceed its ceiling is refused, so one
  unexpectedly large directory cannot consume an entire transfer budget.

Nothing here deletes, overwrites or rewrites a local file. Publication is
content-addressed, so re-running it re-verifies what is already present instead
of uploading it again.
"""

import os
from pathlib import Path
import stat

from .artifacts import canonical_json, file_record, inventory, relative_path

# Credential-bearing paths. A package containing one is refused whole rather than
# shipped with the file removed, because a manifest that disagrees with the
# directory it was built from is worse than a refusal. `object_store._snapshot`
# refuses these too; checking here reports the problem against its package
# instead of aborting the whole run.
FORBIDDEN_PARTS = frozenset({'.ssh', '.aws', '.kaggle'})
# Reconstructable metadata, caches and environments: never evidence, and skipped
# rather than refused. `.git` belongs here, not above — a repository checkout's
# working tree *is* the retained evidence, while its VCS metadata is both
# reproducible from the pinned commit and a place a remote URL could carry a
# credential. Skipping it is what makes those checkouts shippable at all.
SKIPPED_DIRECTORIES = frozenset({'.git', '__pycache__', '.venv', 'venv',
                                 'node_modules', '.pytest_cache', '.mypy_cache',
                                 '.ruff_cache', '.hg', '.svn'})


def forbidden(relative: str) -> bool:
    parts = relative.split('/')
    return any(part in FORBIDDEN_PARTS or part == '.env' or part.startswith('.env.')
               for part in parts)


def discover_packages(tree: Path, *, package_depth=1):
    """Group a tree's files into packages at a fixed depth below its root.

    Files lying directly above the grouping depth are collected into one package
    named for the directory that holds them, so nothing in the tree is silently
    left out of the grouping.
    """
    if type(package_depth) is not int or package_depth < 1:
        raise ValueError('Package depth must be a positive integer')
    tree = Path(tree)
    if tree.is_symlink() or not tree.is_dir():
        raise ValueError('Evidence tree must be an ordinary directory')
    tree = tree.resolve(strict=True)
    packages = {}
    for directory, dirs, names in os.walk(tree, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in SKIPPED_DIRECTORIES)
        current = Path(directory)
        relative = current.relative_to(tree)
        depth = len(relative.parts)
        root = current if depth <= package_depth else tree / Path(*relative.parts[:package_depth])
        for name in sorted(names):
            path = current / name
            packages.setdefault(root, []).append(path)
    return {root: rows for root, rows in sorted(packages.items()) if rows}


def classify_package(root: Path, files, *, max_package_bytes):
    """Decide whether a package can be published, and why not when it cannot."""
    root = Path(root)
    problems, total, regular = [], 0, 0
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
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            problems.append('symlink:' + name)
            continue
        if not stat.S_ISREG(mode):
            problems.append('non_regular_file:' + name)
            continue
        total += path.lstat().st_size
        regular += 1
    if not regular and not problems:
        problems.append('no_regular_files')
    if total > max_package_bytes:
        problems.append(f'exceeds_package_ceiling:{total}>{max_package_bytes}')
    return {'root': str(root), 'files': regular, 'declared_bytes': total,
            'problems': problems, 'publishable': not problems}


def _publish_one(store, root: Path, label, *, source_prefix, revision, verdict, log):
    manifest = inventory(root, kind='candidate',
                        source=source_prefix + ':' + label, revision=revision)
    if log is not None:
        log(f'publishing {label}: {len(manifest["files"])} files, '
            f'{verdict["declared_bytes"]} bytes')
    result = store.publish(root, manifest)
    return {**verdict, 'published': True,
            'manifest_sha256': result['manifest_sha256'],
            'manifest_key': result['manifest_key'],
            'uploaded_files': result['uploaded_files'],
            'reused_files': result['reused_files'],
            'verified_bytes': result['verified_bytes'],
            'manifest_files': len(manifest['files'])}


def ship_tree(store, tree: Path, *, source_prefix, revision, package_depth=1,
              max_package_bytes=512 * 1024**2, max_total_bytes=16 * 1024**3,
              publish=True, workers=1, log=None):
    """Publish every publishable package under a tree and return an index.

    `publish=False` performs the same grouping and classification without any
    transport, which is the honest way to see what a run would do before it
    spends bandwidth. Refused packages are listed with their reasons; they are
    never partially published.

    `workers` above one publishes *different packages* concurrently. Each
    package keeps its full sequential contract — verify the tree, read back or
    upload every blob, verify again, then commit the manifest — so concurrency
    changes throughput and nothing else. Two packages that share a blob may both
    upload it; publication is content-addressed and verified by readback, so
    that is idempotent rather than a race. Which package is admitted first under
    `max_total_bytes` is decided before any transport, in sorted package order,
    so the admitted set does not depend on worker scheduling.
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
    # Admission is decided up front and in deterministic order, so the set of
    # shipped packages is identical whatever `workers` is set to.
    for root, files in discovered.items():
        verdict = classify_package(root, files, max_package_bytes=max_package_bytes)
        label = root.relative_to(tree).as_posix() or '.'
        verdict['package'] = label
        if not verdict['publishable']:
            refused.append(verdict)
            continue
        if planned_bytes + verdict['declared_bytes'] > max_total_bytes:
            verdict['problems'] = ['exceeds_total_ceiling']
            verdict['publishable'] = False
            refused.append(verdict)
            continue
        planned_bytes += verdict['declared_bytes']
        admitted.append((root, label, verdict))

    shipped = []
    if not publish:
        shipped = [{**verdict, 'published': False} for _, _, verdict in admitted]
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

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_publish_one, store, root, label,
                                   source_prefix=source_prefix, revision=revision,
                                   verdict=verdict, log=logged)
                       for root, label, verdict in admitted]
            # Collect in submission order so the result is independent of
            # scheduling; an exception from any package aborts the whole tree.
            shipped = [future.result() for future in futures]

    uploaded = sum(row.get('uploaded_files', 0) for row in shipped)
    reused = sum(row.get('reused_files', 0) for row in shipped)
    verified_bytes = sum(row.get('verified_bytes', 0) for row in shipped)
    return {'schema_version': 1,
            'status': 'tree_shipped' if publish else 'tree_planned',
            'tree': str(tree), 'package_depth': package_depth,
            'source_prefix': source_prefix, 'revision': revision,
            'workers': workers if publish else 1,
            'discovered_packages': len(discovered),
            'shipped_packages': len(shipped), 'refused_packages': len(refused),
            'planned_bytes': planned_bytes, 'verified_bytes': verified_bytes,
            'uploaded_files': uploaded, 'reused_files': reused,
            'packages': shipped, 'refused': refused,
            'scope': 'Content-addressed publication and readback of each package. '
                     'Not a durability, replication or access-control guarantee, '
                     'and not a statement that the evidence is correct.'}


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
            'index_sha256': __import__('hashlib').sha256(
                canonical_json(packages)).hexdigest(),
            'scope': 'Where each shipped package lives in the bucket and under '
                     'which manifest. Restoring one still requires authenticating '
                     'its manifest separately.'}


def verify_local_coverage(trees, remote_digests, *, package_depth=1):
    """Report which local regular files are not present as remote blobs.

    `remote_digests` is the set of SHA-256 hex digests the bucket holds. This is
    a coverage statement about content, not about manifests: a covered digest
    means the bytes exist remotely, not that a manifest references them.
    """
    if not isinstance(remote_digests, (set, frozenset)):
        raise ValueError('remote_digests must be a set of hex digests')
    covered = missing = 0
    covered_bytes = missing_bytes = 0
    gaps = {}
    for tree in trees:
        for root, files in discover_packages(Path(tree), package_depth=package_depth).items():
            for path in files:
                if path.is_symlink() or not path.is_file():
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
            'complete': missing == 0,
            'gaps': dict(sorted(gaps.items(), key=lambda kv: -kv[1][1])),
            'scope': 'Content presence only. A covered digest means the bytes are '
                     'in the bucket, not that any manifest references them.'}
