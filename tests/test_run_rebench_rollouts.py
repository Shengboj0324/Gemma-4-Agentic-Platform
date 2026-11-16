import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_rebench_rollouts import packs_with_work


def pack(root, name, ids, qualified):
    p = Path(root) / name
    p.mkdir()
    (p / 'tasks.jsonl').write_text(''.join(json.dumps({'instance_id': i}) + '\n' for i in ids))
    if qualified is not None:
        (p / 'qualified.json').write_text(json.dumps(qualified))
    return p


class PackTests(unittest.TestCase):
    def test_only_qualified_ids_of_packs_with_work(self):
        with tempfile.TemporaryDirectory() as d:
            pack(d, 'a', ['a1', 'a2'], ['a2'])
            pack(d, 'b', ['b1'], [])
            pack(d, 'c', ['c1'], None)
            work = packs_with_work(d)
            self.assertEqual([(p.name, ids) for p, ids in work], [('a', ['a2'])])

    def test_qualified_id_missing_from_tasks_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            pack(d, 'a', ['a1'], ['zz'])
            with self.assertRaises(ValueError):
                packs_with_work(d)


if __name__ == '__main__':
    unittest.main()
