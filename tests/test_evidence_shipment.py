"""Shipment must group every file, refuse unsafe packages whole, and index them."""

from pathlib import Path
import tempfile
import unittest

from zenithsync.artifacts import canonical_json
from zenithsync.evidence_shipment import (ShipmentLockError, classify_package,
                                          discover_packages, forbidden, ship_tree,
                                          shipment_index, shipment_lock,
                                          verify_local_coverage)
from zenithsync.object_store import ArtifactStore


class ForbiddenPathTests(unittest.TestCase):
    def test_credential_paths_are_recognised(self):
        for name in ('.env', '.env.local', 'a/.env', '.ssh/id',
                     'x/.aws/credentials', '.kaggle/kaggle.json'):
            self.assertTrue(forbidden(name), name)
        for name in ('a.env', 'environment.json', 'gitignore', 'a/b/c.json',
                     'env/settings.py'):
            self.assertFalse(forbidden(name), name)

    def test_vcs_metadata_is_skipped_rather_than_refused(self):
        # A checkout's working tree is the retained evidence; its .git directory
        # is reproducible from the pinned commit and could carry a remote URL
        # with a credential, so it is never shipped and never blocks the package.
        self.assertFalse(forbidden('a/.git/config'))
        from zenithsync.evidence_shipment import SKIPPED_DIRECTORIES
        self.assertIn('.git', SKIPPED_DIRECTORIES)
        self.assertNotIn('.git', __import__(
            'zenithsync.evidence_shipment', fromlist=['x']).FORBIDDEN_PARTS)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tree = Path(self.temp.name) / 'evidence'
        for relative in ('p1/alpha/receipt.json', 'p1/alpha/sub/deep.json',
                         'p1/beta/report.json', 'p1/loose.json', 'top.json'):
            path = self.tree / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(canonical_json({'relative': relative}))

    def test_every_file_lands_in_exactly_one_package(self):
        packages = discover_packages(self.tree, package_depth=2)
        names = {root.relative_to(self.tree.resolve()).as_posix() or '.': sorted(
            path.name for path in rows) for root, rows in packages.items()}
        self.assertEqual(set(names), {'.', 'p1', 'p1/alpha', 'p1/beta'})
        self.assertEqual(names['p1/alpha'], ['deep.json', 'receipt.json'])
        self.assertEqual(names['p1'], ['loose.json'])
        self.assertEqual(names['.'], ['top.json'])
        total = sum(len(rows) for rows in packages.values())
        self.assertEqual(total, 5)

    def test_shallower_depth_groups_more_coarsely_without_losing_files(self):
        packages = discover_packages(self.tree, package_depth=1)
        self.assertEqual(sum(len(rows) for rows in packages.values()), 5)
        names = {root.relative_to(self.tree.resolve()).as_posix() or '.'
                 for root in packages}
        self.assertEqual(names, {'.', 'p1'})

    def test_reconstructable_caches_and_vcs_metadata_are_not_shipped(self):
        cache = self.tree / 'p1' / 'alpha' / '__pycache__'
        cache.mkdir()
        (cache / 'x.pyc').write_bytes(b'\x00')
        (self.tree / 'p1' / 'alpha' / 'venv').mkdir()
        (self.tree / 'p1' / 'alpha' / 'venv' / 'pyvenv.cfg').write_bytes(b'x')
        git = self.tree / 'p1' / 'alpha' / '.git'
        git.mkdir()
        (git / 'config').write_text('[remote "origin"]\n\turl = https://x/y\n')
        packages = discover_packages(self.tree, package_depth=2)
        shipped = {path.name for rows in packages.values() for path in rows}
        self.assertNotIn('x.pyc', shipped)
        self.assertNotIn('pyvenv.cfg', shipped)
        self.assertNotIn('config', shipped)
        # The working tree of the same package still ships.
        self.assertIn('receipt.json', shipped)

    def test_a_symlinked_or_missing_tree_is_refused(self):
        link = Path(self.temp.name) / 'link'
        link.symlink_to(self.tree, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'ordinary directory'):
            discover_packages(link)
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            discover_packages(self.tree, package_depth=0)


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        self.root.mkdir()
        (self.root / 'receipt.json').write_bytes(canonical_json({'ok': True}))

    def files(self):
        return sorted(path for path in self.root.rglob('*') if not path.is_dir())

    def test_a_clean_package_is_publishable_with_its_declared_bytes(self):
        verdict = classify_package(self.root, self.files(),
                                   max_package_bytes=10**6)
        self.assertTrue(verdict['publishable'])
        self.assertEqual(verdict['files'], 1)
        self.assertEqual(verdict['declared_bytes'],
                         (self.root / 'receipt.json').stat().st_size)
        self.assertEqual(verdict['problems'], [])

    def test_a_credential_path_refuses_the_whole_package(self):
        (self.root / '.env').write_text('R2_SECRET_ACCESS_KEY=planted\n')
        verdict = classify_package(self.root, self.files(),
                                   max_package_bytes=10**6)
        self.assertFalse(verdict['publishable'])
        self.assertIn('credential_or_workspace_metadata:.env', verdict['problems'])

    def test_a_symlink_refuses_the_whole_package(self):
        target = Path(self.temp.name) / 'outside.json'
        target.write_bytes(canonical_json({'outside': True}))
        (self.root / 'link.json').symlink_to(target)
        verdict = classify_package(self.root, self.files(),
                                   max_package_bytes=10**6)
        self.assertFalse(verdict['publishable'])
        self.assertIn('symlink:link.json', verdict['problems'])

    def test_an_oversized_package_is_refused(self):
        verdict = classify_package(self.root, self.files(), max_package_bytes=1)
        self.assertFalse(verdict['publishable'])
        self.assertTrue(any(problem.startswith('exceeds_package_ceiling')
                            for problem in verdict['problems']))

    def test_an_empty_package_is_refused_rather_than_published(self):
        verdict = classify_package(self.root, [], max_package_bytes=10**6)
        self.assertFalse(verdict['publishable'])
        self.assertEqual(verdict['problems'], ['no_regular_files'])


class ShipmentLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def lock(self, bucket='bucket', prefix='artifacts/v1'):
        return shipment_lock(bucket, prefix, directory=self.directory)

    def test_a_second_shipment_on_the_same_prefix_is_refused(self):
        with self.lock() as held:
            self.assertTrue(held.path.is_file())
            with self.assertRaises(ShipmentLockError) as caught:
                with self.lock():
                    pass
            message = str(caught.exception)
            self.assertIn('another publisher', message)
            self.assertIn('artifacts/v1', message)
            self.assertIn('integrity guard', message)
        self.assertFalse(held.path.exists())

    def test_a_different_prefix_or_bucket_is_a_different_lock(self):
        with self.lock(prefix='artifacts/v1'):
            with self.lock(prefix='quarantine/v1'):
                pass
            with self.lock(bucket='other'):
                pass

    def test_a_stale_lock_from_a_dead_process_is_reclaimed(self):
        import json as json_module
        # A killed shipment leaves nothing to clean up, so its lock is safe to
        # take over. PID 2**31-1 is not a live process.
        probe = self.lock()
        probe.path.write_text(json_module.dumps(
            {'pid': 2**31 - 1, 'bucket': 'bucket', 'prefix': 'artifacts/v1',
             'started_utc': '2026-01-01T00:00:00+00:00'}))
        with self.lock() as held:
            self.assertTrue(held.path.is_file())
        self.assertFalse(probe.path.exists())

    def test_an_unreadable_lock_is_reclaimed_rather_than_blocking_forever(self):
        probe = self.lock()
        probe.path.write_text('not json')
        with self.lock():
            pass

    def test_the_lock_is_released_even_when_the_body_raises(self):
        held = self.lock()
        with self.assertRaises(ZeroDivisionError):
            with held:
                1 / 0
        self.assertFalse(held.path.exists())

    def test_the_holder_label_names_what_is_publishing(self):
        import json as json_module
        with self.lock() as held:
            holder = json_module.loads(held.path.read_text())
            self.assertEqual(holder['label'], 'shipment')
            self.assertEqual(holder['bucket'], 'bucket')
            self.assertEqual(holder['prefix'], 'artifacts/v1')
        labelled = shipment_lock('bucket', 'artifacts/v1', label='publish_corpus_to_r2',
                                 directory=self.directory)
        with labelled:
            with self.assertRaises(ShipmentLockError) as caught:
                with self.lock():
                    pass
            self.assertIn('publish_corpus_to_r2', str(caught.exception))

    def test_every_publisher_cli_takes_the_lock(self):
        # The hazard is two writers of one content-addressed key, whichever
        # command they are, so a new publisher must not forget this.
        root = Path(__file__).resolve().parents[1]
        for name in ('scripts/ship_evidence_to_r2.py',
                     'scripts/publish_corpus_to_r2.py'):
            source = (root / name).read_text(encoding='utf-8')
            self.assertIn('shipment_lock(', source, name)

    def test_a_blank_bucket_or_prefix_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'Bucket is required'):
            shipment_lock('  ', 'artifacts/v1', directory=self.directory)
        with self.assertRaisesRegex(ValueError, 'Prefix is required'):
            shipment_lock('bucket', '', directory=self.directory)


class ShipTreeTests(unittest.TestCase):
    def setUp(self):
        from tests.test_object_store import MemoryClient
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tree = Path(self.temp.name) / 'evidence'
        for relative in ('alpha/receipt.json', 'alpha/report.json',
                         'beta/receipt.json'):
            path = self.tree / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(canonical_json({'relative': relative}))
        self.client = MemoryClient()
        self.store = ArtifactStore(self.client, 'test-bucket', prefix='artifacts/v1')

    def ship(self, **kwargs):
        arguments = {'source_prefix': 'unit-test', 'revision': '001'}
        arguments.update(kwargs)
        return ship_tree(self.store, self.tree, **arguments)

    def test_each_package_is_published_under_its_own_manifest(self):
        result = self.ship()
        self.assertEqual(result['status'], 'tree_shipped')
        self.assertEqual(result['shipped_packages'], 2)
        self.assertEqual(result['refused_packages'], 0)
        self.assertEqual(result['uploaded_files'], 3)
        self.assertEqual(result['reused_files'], 0)
        digests = {row['manifest_sha256'] for row in result['packages']}
        self.assertEqual(len(digests), 2)
        for row in result['packages']:
            self.assertTrue(row['published'])
            self.assertIn(row['manifest_key'], self.client.objects)

    def test_reshipping_reuses_every_verified_object(self):
        self.ship()
        uploads = self.client.uploads
        again = self.ship()
        self.assertEqual(again['uploaded_files'], 0)
        self.assertEqual(again['reused_files'], 3)
        self.assertEqual(self.client.uploads, uploads)

    def test_a_planning_run_publishes_nothing(self):
        result = self.ship(publish=False)
        self.assertEqual(result['status'], 'tree_planned')
        self.assertEqual(result['shipped_packages'], 2)
        self.assertEqual(result['uploaded_files'], 0)
        self.assertFalse(self.client.objects)
        self.assertTrue(all(not row['published'] for row in result['packages']))

    def test_an_unsafe_package_is_refused_and_the_rest_still_ship(self):
        (self.tree / 'alpha' / '.env').write_text('R2_SECRET_ACCESS_KEY=planted\n')
        result = self.ship()
        self.assertEqual(result['shipped_packages'], 1)
        self.assertEqual(result['refused_packages'], 1)
        self.assertEqual(result['refused'][0]['package'], 'alpha')
        self.assertEqual(result['packages'][0]['package'], 'beta')
        # Nothing from the refused package reached the bucket.
        planted = (self.tree / 'alpha' / '.env').read_bytes()
        self.assertNotIn(planted, set(self.client.objects.values()))
        self.assertEqual(result['uploaded_files'], 1)

    def test_a_total_ceiling_stops_shipping_and_says_so(self):
        result = self.ship(max_total_bytes=40)
        self.assertEqual(result['shipped_packages'], 1)
        self.assertEqual(result['refused_packages'], 1)
        self.assertEqual(result['refused'][0]['problems'], ['exceeds_total_ceiling'])

    def test_malformed_labels_and_ceilings_are_refused(self):
        for override, message in [({'source_prefix': ' '}, 'Source label'),
                                  ({'revision': ''}, 'Revision label'),
                                  ({'max_package_bytes': 0}, 'max_package_bytes'),
                                  ({'max_total_bytes': -1}, 'max_total_bytes')]:
            with self.assertRaisesRegex(ValueError, message):
                self.ship(**override)

    def test_concurrent_shipping_gives_the_identical_result(self):
        from tests.test_object_store import MemoryClient
        sequential = self.ship(workers=1)
        self.client = MemoryClient()
        self.store = ArtifactStore(self.client, 'test-bucket', prefix='artifacts/v1')
        concurrent = self.ship(workers=4)
        for result in (sequential, concurrent):
            result.pop('workers')
        self.assertEqual(sequential, concurrent)
        self.assertEqual([row['package'] for row in concurrent['packages']],
                         ['alpha', 'beta'])

    def test_a_concurrent_failure_aborts_the_tree(self):
        self.client.corrupt_upload = True
        with self.assertRaises(Exception):
            self.ship(workers=4)

    def test_worker_count_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, 'workers'):
            self.ship(workers=0)

    def test_the_index_locates_every_shipped_package(self):
        result = self.ship()
        index = shipment_index([result])
        self.assertEqual(index['packages'], 2)
        self.assertEqual(index['files'], 3)
        self.assertEqual(index['uploaded_files'], 3)
        self.assertEqual(len(index['index_sha256']), 64)
        for row in index['index']:
            self.assertIn(row['manifest_key'], self.client.objects)
        with self.assertRaisesRegex(ValueError, 'Nonempty shipment result list'):
            shipment_index([])
        with self.assertRaisesRegex(ValueError, 'Duplicate package'):
            shipment_index([result, result])

    def test_coverage_reports_exactly_what_is_absent(self):
        before = verify_local_coverage([self.tree], set())
        self.assertFalse(before['complete'])
        self.assertEqual(before['missing_files'], 3)
        self.assertEqual(before['covered_files'], 0)
        self.ship()
        digests = {key.rsplit('/', 1)[-1] for key in self.client.objects
                   if '/blobs/sha256/' in key}
        after = verify_local_coverage([self.tree], digests)
        self.assertTrue(after['complete'])
        self.assertEqual(after['missing_files'], 0)
        self.assertEqual(after['covered_files'], 3)
        self.assertEqual(after['gaps'], {})
        with self.assertRaisesRegex(ValueError, 'must be a set'):
            verify_local_coverage([self.tree], ['a' * 64])


if __name__ == '__main__':
    unittest.main()
