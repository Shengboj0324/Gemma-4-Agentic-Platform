"""Exercise both task readers with real Parquet and mutations between reads."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_rebench_replay_history as history
from scripts import extract_rebench_evaluator_input as evaluator
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.source_bytes import verified_source_bytes


class RebenchSourceSnapshotTests(unittest.TestCase):
    def setUp(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest('PyArrow is required for real task-reader integration')
        self.pa, self.pq = pa, pq
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / 'task.parquet'
        self.task = {'instance_id': 'sample__repo-1', 'repo': 'sample/repo',
                     'base_commit': 'a' * 40, 'environment_setup_commit': 'b' * 40}
        row = dict(self.task, problem_statement='Repair the reported defect.',
                   patch='production patch', test_patch='test patch',
                   meta={'score': 1}, install_config={'python': '3.9'},
                   FAIL_TO_PASS=['test_a'], PASS_TO_PASS=['test_b'],
                   FAIL_TO_FAIL=[], PASS_TO_FAIL=[])
        pq.write_table(pa.Table.from_pylist([row]), self.source)
        self.original = self.source.read_bytes()
        identity = file_record(self.source)
        self.task['source_task_shard_sha256'] = identity['sha256']
        self.write('intake.json', {'dataset': 'nebius/SWE-rebench',
                   'revision': '89cdfbab4ab1bd8f5a658bb212d1b63624f4f881',
                   'downloaded': {'task.parquet': identity}})
        self.write('evidence/data/swe-rebench-task-join-full-001/report.json',
                   {'task_shards': [{'identity': identity, 'path': 'task.parquet',
                     'intake_path': 'intake.json', 'intake': file_record(self.root / 'intake.json')}]})
        self.write('evidence/p1/task-index-001/receipt.json', {'repo_counts': {}})
        self.write('resolution.json', {'task': self.task})
        self.write('task-receipt.json', {'task': self.task, 'source': identity})
        helper = self.root / 'zenithsync/source_bytes.py'
        helper.parent.mkdir()
        helper.write_bytes(Path('zenithsync/source_bytes.py').read_bytes())
        attempt = self.root / 'attempt'
        attempt.mkdir()
        (attempt / 'submitted.patch').write_text('production patch')
        self.write('attempt/receipt.json', {'status': 'replayed_not_graded',
                   'cleanup': {'removed': True}, 'patch': file_record(attempt / 'submitted.patch'),
                   'instance_id': self.task['instance_id'], 'profile': self.task,
                   'available_tools': ['submit_patch']})
        result = {'status': 'ok'}
        self.write('attempt/events.json', [{'source_index': 1, 'kind': 'finish', 'result': result,
                   'native_calls': [{'name': 'submit_patch', 'arguments': {}, 'result': result}]}])
        self.write('evidence/data/source-http-client-001/success/http-fixture/exchanges.json',
                   [{'request': {'messages': [{'role': 'system', 'content': 'Fix the issue.'}],
                     'tools': [{'type': 'function', 'function': {'name': 'submit_patch'}}]}}])

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json(value))

    def invoke(self, module, suffix):
        output = self.root / suffix
        common = ['--output', str(output)]
        arguments = (['--resolution', str(self.root / 'resolution.json')] if module is evaluator
                     else ['--attempt', str(self.root / 'attempt'),
                           '--task-receipt', str(self.root / 'task-receipt.json')])
        with patch.object(module, 'ROOT', self.root), patch('sys.argv', ['test'] + arguments + common):
            with contextlib.redirect_stdout(io.StringIO()):
                module.main()
        return output

    def test_amended_history_binds_original_derived_and_native_call(self):
        import hashlib

        def identity(value):
            data = canonical_json(value)
            return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}

        actions = [{'index': 0, 'kind': 'shell', 'command': 'old diagnostic'},
                   {'index': 1, 'kind': 'finish'}]
        derived = [{'index': 0, 'kind': 'shell', 'command': 'scoped diagnostic'}, actions[1]]
        plan = {'schema_version': 1, 'author': 'assistant', 'reason': 'Scope claims',
                'source_actions': identity(actions), 'derived_actions': identity(derived),
                'amendments': [{'action_index': 0, 'field': 'command',
                    'before': 'old diagnostic', 'after': 'scoped diagnostic', 'reason': 'Correct claim'}]}
        self.write('attempt/original-actions.json', actions)
        self.write('attempt/actions.json', derived)
        module = self.root / 'zenithsync/replay_amendment.py'
        module.write_bytes(Path('zenithsync/replay_amendment.py').read_bytes())
        receipt = load_json(self.root / 'attempt/receipt.json')
        receipt.update(amendment_plan=plan, original_actions=identity(actions),
                       derived_actions=identity(derived), amendment_module=file_record(module),
                       available_tools=['run_command', 'submit_patch'])
        self.write('attempt/receipt.json', receipt)
        protocol_path = 'evidence/data/source-http-client-001/success/http-fixture/exchanges.json'
        protocol = load_json(self.root / protocol_path)
        protocol[0]['request']['tools'].append({'type': 'function', 'function': {'name': 'run_command'}})
        self.write(protocol_path, protocol)
        events = load_json(self.root / 'attempt/events.json')
        result = {'status': 'ok', 'exit_code': 0, 'stdout': 'actual captured output'}
        events.insert(0, {'source_index': 0, 'kind': 'shell', 'result': result,
            'native_calls': [{'name': 'run_command', 'arguments': {'command': 'scoped diagnostic'},
                              'result': result}]})
        self.write('attempt/events.json', events)
        output = self.invoke(history, 'amended-success')
        self.assertEqual(load_json(output / 'mapping.json')[0]['author'], 'assistant')
        self.assertEqual(load_json(output / 'receipt.json')['amendment_plan'], plan)
        events[0]['native_calls'][0]['arguments']['command'] = 'old diagnostic'
        self.write('attempt/events.json', events)
        with self.assertRaisesRegex(ValueError, 'Amended native call'):
            self.invoke(history, 'amended-rejected')
        self.assertFalse((self.root / 'amended-rejected').exists())

    def test_both_reads_use_same_verified_snapshot_despite_transient_path_replacement(self):
        for module in (evaluator, history):
            with self.subTest(module=module.__name__):
                calls = []
                original_reader = self.pq.read_table

                def read(source, **kwargs):
                    self.assertIsInstance(source, self.pa.BufferReader)
                    result = original_reader(source, **kwargs)
                    calls.append(kwargs['columns'])
                    self.source.write_bytes(b'invalid parquet' if len(calls) == 1 else self.original)
                    return result

                with patch.object(self.pq, 'read_table', side_effect=read):
                    output = self.invoke(module, module.__name__)
                self.assertEqual(len(calls), 2)
                receipt = load_json(output / 'receipt.json')
                self.assertEqual(receipt['parser_input']['kind'], 'verified_immutable_bytes')
                self.assertFalse(receipt['training_approved'])

    def test_corruption_after_metadata_check_rejected_before_parser(self):
        for module in (evaluator, history):
            with self.subTest(module=module.__name__):
                self.source.write_bytes(self.original)

                def corrupt(path, identity, *, max_bytes):
                    path.write_bytes(b'corruption')
                    return verified_source_bytes(path, identity, max_bytes=max_bytes)

                with patch.object(module, 'verified_source_bytes', side_effect=corrupt):
                    with patch.object(self.pq, 'read_table') as reader:
                        with self.assertRaisesRegex(ValueError, 'differ from pinned identity'):
                            self.invoke(module, 'corrupt-' + module.__name__)
                        reader.assert_not_called()

    def test_persistent_mutation_after_parsing_is_rejected(self):
        for module in (evaluator, history):
            with self.subTest(module=module.__name__):
                self.source.write_bytes(self.original)
                original_reader = self.pq.read_table

                def mutate(source, **kwargs):
                    result = original_reader(source, **kwargs)
                    self.source.write_bytes(b'changed permanently')
                    return result

                with patch.object(self.pq, 'read_table', side_effect=mutate):
                    with self.assertRaisesRegex(ValueError, 'changed during'):
                        self.invoke(module, 'drift-' + module.__name__)
                self.assertFalse((self.root / ('drift-' + module.__name__)).exists())

    def test_reserved_repository_is_rejected_before_snapshot_or_parser(self):
        self.write('evidence/p1/task-index-001/receipt.json', {'repo_counts': {'SAMPLE/REPO': 1}})
        for module in (evaluator, history):
            with self.subTest(module=module.__name__):
                with patch.object(module, 'verified_source_bytes') as snapshot:
                    with patch.object(self.pq, 'read_table') as reader:
                        with self.assertRaisesRegex(ValueError, 'Reserved repository'):
                            self.invoke(module, 'reserved-' + module.__name__)
                        snapshot.assert_not_called()
                        reader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
