import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.rebench_pack_pipeline import archive, prune_pack, qualified_ids


class PipelineTests(unittest.TestCase):
    def test_qualified_is_gold_minus_empty(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, 'receipt.json')
            p.write_text(json.dumps({'gold': {'resolved': ['a', 'b', 'c']}, 'empty': {'resolved': ['c']}}))
            self.assertEqual(qualified_ids(p), ['a', 'b'])

    def test_prune_keeps_only_qualified_rows_and_snapshots(self):
        with tempfile.TemporaryDirectory() as d:
            pack = Path(d, 'o__r')
            (pack / 'snapshots').mkdir(parents=True)
            (pack / 'tasks.jsonl').write_text(''.join(json.dumps({'instance_id': i}) + '\n' for i in 'abc'))
            for i in 'abc':
                (pack / 'snapshots' / f'{i}.tgz').write_bytes(b'x')
            self.assertEqual(prune_pack(pack, ['b']), (3, 1))
            self.assertEqual([p.name for p in (pack / 'snapshots').iterdir()], ['b.tgz'])
            self.assertEqual(json.loads((pack / 'qualified.json').read_text()), ['b'])
            self.assertEqual((pack / 'tasks.jsonl').read_text().strip(), json.dumps({'instance_id': 'b'}))

    def test_archive_digests_match_the_file(self):
        with tempfile.TemporaryDirectory() as d:
            pack = Path(d, 'o__r')
            pack.mkdir()
            (pack / 'f').write_text('hello')
            out = Path(d, 'o__r.tar')
            sha, md5, size = archive(pack, out)
            data = out.read_bytes()
            self.assertEqual((sha, md5, size), (hashlib.sha256(data).hexdigest(), hashlib.md5(data).hexdigest(), len(data)))


if __name__ == '__main__':
    unittest.main()
