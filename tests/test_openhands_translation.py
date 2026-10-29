"""Translation must justify every mapping and refuse everything else."""

import unittest

from zenithsync.openhands_translation import (ADAPTER_AUTHORED_TERMINAL,
                                              UntranslatableCall, audit_translation,
                                              translate_call, translate_trajectory,
                                              workspace_relative)


def call(name, arguments, identifier='c1'):
    return {'role': 'assistant', 'content': '', 'tool_calls': [
        {'id': identifier, 'type': 'function',
         'function': {'name': name, 'arguments': arguments}}]}


def response(identifier='c1', content='observation text'):
    return {'role': 'tool', 'tool_call_id': identifier, 'content': content}


class WorkspacePathTests(unittest.TestCase):
    def test_absolute_workspace_paths_become_relative(self):
        self.assertEqual(workspace_relative('/workspace/pkg/mod.py'), 'pkg/mod.py')
        self.assertEqual(workspace_relative('pkg/mod.py'), 'pkg/mod.py')
        self.assertEqual(workspace_relative('/repo/a.py', workspace='/repo'), 'a.py')

    def test_unmappable_paths_are_refused(self):
        cases = [('/workspace/', 'directory_shaped_path'),
                 ('/workspace', 'workspace_root_is_not_a_file'),
                 ('/etc/passwd', 'path_outside_declared_workspace'),
                 ('/workspace/../escape.py', 'noncanonical_relative_path'),
                 ('pkg//mod.py', 'noncanonical_relative_path'),
                 ('./mod.py', 'noncanonical_relative_path'),
                 ('', 'directory_shaped_path')]
        for path, reason in cases:
            with self.assertRaises(UntranslatableCall) as caught:
                workspace_relative(path)
            self.assertEqual(caught.exception.reason, reason)
        with self.assertRaises(UntranslatableCall) as caught:
            workspace_relative(7)
        self.assertEqual(caught.exception.reason, 'nontext_path')


class TranslateCallTests(unittest.TestCase):
    def assertRefused(self, name, arguments, reason):
        with self.assertRaises(UntranslatableCall) as caught:
            translate_call(name, arguments)
        self.assertEqual(caught.exception.reason, reason)

    def test_bash_maps_to_run_command(self):
        result = translate_call('execute_bash', {'command': 'pytest -q'})
        self.assertEqual(result['disposition'], 'translated')
        self.assertEqual(result['name'], 'run_command')
        self.assertEqual(result['arguments'], {'command': 'pytest -q'})
        self.assertEqual(result['rule'], 'execute_bash_to_run_command')
        self.assertEqual(result['argument_mapping'], {'command': 'command'})

    def test_interactive_stdin_writes_are_refused(self):
        self.assertRefused('execute_bash', {'command': 'y', 'is_input': True},
                           'interactive_stdin_write')
        self.assertRefused('execute_bash', {'command': 'ls', 'timeout': 30},
                           'unsupported_execute_bash_timeout')
        self.assertRefused('execute_bash', {'command': 'ls', 'shell': 'zsh'},
                           'unsupported_execute_bash_argument_shell')
        self.assertRefused('execute_bash', {}, 'execute_bash_without_command')
        self.assertRefused('execute_bash', {'command': '  '}, 'empty_command')

    def test_interactive_control_sentinels_are_not_run_as_commands(self):
        # `C-c` arrives through `command` but interrupts a running process in
        # the source runtime; run_command has no process to interrupt.
        for sentinel in ('C-c', 'C-d', 'C-z', '  C-c  '):
            self.assertRefused('execute_bash', {'command': sentinel},
                               'interactive_control_sentinel')
        # A command that merely mentions one is still a command.
        self.assertEqual(translate_call('execute_bash',
                                        {'command': 'echo C-c'})['arguments'],
                         {'command': 'echo C-c'})

    def test_an_explicit_is_input_false_is_a_plain_command(self):
        result = translate_call('execute_bash', {'command': 'ls', 'is_input': False})
        self.assertEqual(result['arguments'], {'command': 'ls'})
        self.assertEqual(result['rule'], 'execute_bash_to_run_command')

    def test_a_directory_view_is_not_translated_into_a_file_read(self):
        # The source schema accepts a directory for `view` and lists it; the
        # official read_file reads a file. Guessing would change the trajectory.
        self.assertRefused('str_replace_editor',
                           {'command': 'view', 'path': '/workspace/pkg'},
                           'view_target_may_be_a_directory')
        self.assertRefused('str_replace_editor',
                           {'command': 'view', 'path': '/workspace/src/tests'},
                           'view_target_may_be_a_directory')
        # The heuristic errs toward refusal: extensionless files are refused too.
        self.assertRefused('str_replace_editor',
                           {'command': 'view', 'path': '/workspace/Makefile'},
                           'view_target_may_be_a_directory')

    def test_a_snapshot_file_set_decides_the_question_exactly(self):
        known = {'pkg/a.py', 'Makefile'}
        self.assertEqual(
            translate_call('str_replace_editor',
                           {'command': 'view', 'path': '/workspace/Makefile'},
                           file_paths=known)['arguments'],
            {'filepath': 'Makefile'})
        with self.assertRaises(UntranslatableCall) as caught:
            translate_call('str_replace_editor',
                           {'command': 'view', 'path': '/workspace/pkg'},
                           file_paths=known)
        self.assertEqual(caught.exception.reason,
                         'target_is_not_a_known_snapshot_file')
        with self.assertRaises(UntranslatableCall) as caught:
            translate_call('str_replace_editor',
                           {'command': 'view', 'path': '/workspace/absent.py'},
                           file_paths=known)
        self.assertEqual(caught.exception.reason,
                         'target_is_not_a_known_snapshot_file')
        with self.assertRaisesRegex(ValueError, 'must be a set'):
            workspace_relative('a.py', file_paths=['a.py'])

    def test_a_missing_path_is_a_reason_code_not_a_key_error(self):
        for arguments, reason in [
                ({'command': 'view'}, 'missing_path'),
                ({'command': 'create', 'file_text': 'x'}, 'missing_path'),
                ({'command': 'str_replace', 'old_str': 'a', 'new_str': 'b'},
                 'missing_path')]:
            with self.assertRaises(UntranslatableCall) as caught:
                translate_call('str_replace_editor', arguments)
            self.assertEqual(caught.exception.reason, reason)

    def test_finish_rejects_unknown_arguments(self):
        self.assertRefused('finish', {'anything_at_all': [1, 2, 3]},
                           'unsupported_finish_argument_anything_at_all')
        self.assertTrue(translate_call('finish', {'message': 'done'})
                        ['source_message_present'])
        self.assertFalse(translate_call('finish', {})['source_message_present'])

    def test_view_maps_to_read_file_with_and_without_a_range(self):
        whole = translate_call('str_replace_editor',
                               {'command': 'view', 'path': '/workspace/pkg/a.py'})
        self.assertEqual(whole['name'], 'read_file')
        self.assertEqual(whole['arguments'], {'filepath': 'pkg/a.py'})
        self.assertEqual(whole['rule'], 'view_whole_file_to_read_file')
        bounded = translate_call('str_replace_editor',
                                 {'command': 'view', 'path': '/workspace/pkg/a.py',
                                  'view_range': [10, 40]})
        self.assertEqual(bounded['arguments'],
                         {'filepath': 'pkg/a.py', 'start_line': 10, 'end_line': 40})
        self.assertEqual(bounded['rule'], 'bounded_view_range_to_read_file_line_range')
        open_ended = translate_call('str_replace_editor',
                                    {'command': 'view', 'path': 'pkg/a.py',
                                     'view_range': [5, -1]})
        self.assertEqual(open_ended['arguments'], {'filepath': 'pkg/a.py',
                                                   'start_line': 5})
        # The emitted call reads from a line, not the whole file, so the rule
        # name must not claim otherwise: it is the provenance in the histogram.
        self.assertEqual(open_ended['rule'],
                         'open_ended_view_range_to_read_file_from_line')

    def test_invalid_view_ranges_are_refused(self):
        base = {'command': 'view', 'path': 'a.py'}
        self.assertRefused('str_replace_editor', {**base, 'view_range': [40, 10]},
                           'inverted_view_range')
        self.assertRefused('str_replace_editor', {**base, 'view_range': [0, 10]},
                           'invalid_view_range_start')
        self.assertRefused('str_replace_editor', {**base, 'view_range': [1, 2, 3]},
                           'invalid_view_range')
        self.assertRefused('str_replace_editor', {**base, 'view_range': [1, -2]},
                           'invalid_view_range_end')
        self.assertRefused('str_replace_editor', {**base, 'concise': True},
                           'unsupported_view_argument_concise')

    def test_create_maps_to_write_file(self):
        result = translate_call('str_replace_editor',
                                {'command': 'create', 'path': '/workspace/new.py',
                                 'file_text': 'print(1)\n'})
        self.assertEqual(result['name'], 'write_file')
        self.assertEqual(result['arguments'], {'filepath': 'new.py',
                                               'content': 'print(1)\n'})
        self.assertRefused('str_replace_editor', {'command': 'create', 'path': 'a.py'},
                           'create_without_file_text')
        # `create` names a file that does not exist yet, so a snapshot set must
        # not be applied to it.
        self.assertEqual(
            translate_call('str_replace_editor',
                           {'command': 'create', 'path': '/workspace/new.py',
                            'file_text': 'x'},
                           file_paths={'other.py'})['arguments']['filepath'],
            'new.py')

    def test_str_replace_maps_to_edit_file(self):
        result = translate_call('str_replace_editor',
                                {'command': 'str_replace', 'path': 'pkg/a.py',
                                 'old_str': 'return x', 'new_str': 'return x.T'})
        self.assertEqual(result['name'], 'edit_file')
        self.assertEqual(result['arguments'], {'filepath': 'pkg/a.py',
                                               'old_string': 'return x',
                                               'new_string': 'return x.T'})
        self.assertEqual(result['argument_mapping'],
                         {'path': 'filepath', 'old_str': 'old_string',
                          'new_str': 'new_string'})

    def test_ambiguous_or_degenerate_edits_are_refused(self):
        base = {'command': 'str_replace', 'path': 'a.py'}
        self.assertRefused('str_replace_editor', {**base, 'old_str': 'x'},
                           'str_replace_without_explicit_new_str')
        self.assertRefused('str_replace_editor',
                           {**base, 'old_str': 'x', 'new_str': None},
                           'str_replace_without_explicit_new_str')
        self.assertRefused('str_replace_editor',
                           {**base, 'old_str': '', 'new_str': 'y'}, 'empty_old_str')
        self.assertRefused('str_replace_editor',
                           {**base, 'old_str': 'x', 'new_str': 'x'}, 'no_op_str_replace')
        self.assertRefused('str_replace_editor', {**base, 'new_str': 'y'},
                           'str_replace_without_old_str')

    def test_operations_without_an_official_equivalent_are_refused(self):
        self.assertRefused('str_replace_editor',
                           {'command': 'insert', 'path': 'a.py', 'insert_line': 3,
                            'new_str': 'x'},
                           'unsupported_editor_command_insert')
        self.assertRefused('str_replace_editor', {'command': 'undo_edit', 'path': 'a.py'},
                           'unsupported_editor_command_undo_edit')
        self.assertRefused('str_replace_editor', {'path': 'a.py'},
                           'editor_without_command')
        self.assertRefused('task_tracker', {'command': 'plan'},
                           'no_official_task_tracking_tool')
        self.assertRefused('browse_url', {'url': 'http://x'}, 'unknown_source_tool')

    def test_think_folds_into_the_reasoning_channel(self):
        result = translate_call('think', {'thought': 'Inspect the sampler first.'})
        self.assertEqual(result['disposition'], 'folded_into_reasoning')
        self.assertEqual(result['reasoning'], 'Inspect the sampler first.')
        self.assertEqual(result['rule'], 'think_to_reasoning_channel')
        self.assertRefused('think', {'thought': '  '}, 'empty_thought')
        self.assertRefused('think', {}, 'unsupported_think_arguments')

    def test_finish_is_not_treated_as_a_submission(self):
        result = translate_call('finish', {'message': 'done'})
        self.assertEqual(result['disposition'], 'terminal_requires_adapter_submission')
        self.assertEqual(result['adapter_authored_tool'], ADAPTER_AUTHORED_TERMINAL)
        self.assertNotIn('arguments', result)


class TranslateTrajectoryTests(unittest.TestCase):
    def setUp(self):
        self.messages = [
            {'role': 'system', 'content': 'You are an engineer.'},
            {'role': 'user', 'content': 'Fix the transpose bug.'},
            call('think', {'thought': 'Read the module.'}, 't1'),
            response('t1', 'Your thought has been logged.'),
            call('str_replace_editor', {'command': 'view', 'path': '/workspace/pkg/a.py'}, 'c1'),
            response('c1', '     1\tdef f(): return x'),
            call('str_replace_editor', {'command': 'str_replace', 'path': '/workspace/pkg/a.py',
                                        'old_str': 'return x', 'new_str': 'return x.T'}, 'c2'),
            response('c2', 'The file has been edited.'),
            call('execute_bash', {'command': 'pytest -q'}, 'c3'),
            response('c3', '1 passed'),
            call('finish', {'message': 'done'}, 'c4'),
        ]

    def test_a_full_trajectory_becomes_an_ordered_action_plan(self):
        plan = translate_trajectory(self.messages)
        self.assertEqual(plan['translated_actions'], 3)
        self.assertEqual(plan['folded_thoughts'], 1)
        self.assertEqual(plan['dropped_trailing_thoughts'], 0)
        # Assert the actual absence of results, not just the flag that claims it.
        self.assertFalse(plan['results_present'])
        for action in plan['actions']:
            self.assertEqual(set(action), {'source_index', 'name', 'arguments',
                                           'rule', 'source_tool',
                                           'argument_mapping', 'reasoning'})
        self.assertNotIn('results', plan)
        self.assertFalse(plan['training_approved'])
        self.assertEqual([action['name'] for action in plan['actions']],
                         ['read_file', 'edit_file', 'run_command'])
        self.assertEqual(plan['actions'][0]['reasoning'], 'Read the module.')
        self.assertEqual(plan['actions'][1]['reasoning'], '')
        self.assertEqual(plan['terminal']['adapter_authored_tool'], 'submit_patch')
        self.assertEqual(plan['rules_applied'], {
            'execute_bash_to_run_command': 1,
            'finish_is_not_submit_patch': 1,
            'str_replace_to_edit_file': 1,
            'think_to_reasoning_channel': 1,
            'view_whole_file_to_read_file': 1,
        })
        self.assertFalse(plan['snapshot_file_paths_supplied'])
        self.assertNotIn('result', plan['actions'][0])
        self.assertEqual(len(plan['plan_sha256']), 64)
        self.assertEqual(len(plan['source_history_sha256']), 64)

    def test_consecutive_thoughts_concatenate_onto_the_next_action(self):
        messages = [
            {'role': 'user', 'content': 'go'},
            call('think', {'thought': 'First.'}, 't1'), response('t1'),
            call('think', {'thought': 'Second.'}, 't2'), response('t2'),
            call('execute_bash', {'command': 'ls'}, 'c1'), response('c1'),
            call('finish', {}, 'c2'),
        ]
        plan = translate_trajectory(messages)
        self.assertEqual(plan['actions'][0]['reasoning'], 'First.\n\nSecond.')
        self.assertEqual(plan['folded_thoughts'], 2)

    def test_a_trailing_thought_is_dropped_not_attached_to_an_invented_action(self):
        messages = [
            {'role': 'user', 'content': 'go'},
            call('execute_bash', {'command': 'ls'}, 'c1'), response('c1'),
            call('think', {'thought': 'Unused.'}, 't1'), response('t1'),
            call('finish', {}, 'c2'),
        ]
        plan = translate_trajectory(messages)
        self.assertEqual(plan['translated_actions'], 1)
        self.assertEqual(plan['dropped_trailing_thoughts'], 1)

    def test_one_untranslatable_call_fails_the_whole_trajectory(self):
        messages = list(self.messages)
        messages[8:10] = [call('str_replace_editor',
                               {'command': 'insert', 'path': 'a.py',
                                'insert_line': 1, 'new_str': 'x'}, 'c3'),
                          response('c3')]
        with self.assertRaises(UntranslatableCall) as caught:
            translate_trajectory(messages)
        self.assertEqual(caught.exception.reason, 'unsupported_editor_command_insert')

    def test_a_trajectory_without_a_terminal_call_is_refused(self):
        with self.assertRaises(UntranslatableCall) as caught:
            translate_trajectory(self.messages[:-1])
        self.assertEqual(caught.exception.reason, 'missing_terminal_finish_call')

    def test_a_trajectory_with_no_actions_is_refused(self):
        messages = [{'role': 'user', 'content': 'go'},
                    call('think', {'thought': 'only a thought'}, 't1'), response('t1'),
                    call('finish', {}, 'c1')]
        with self.assertRaises(UntranslatableCall) as caught:
            translate_trajectory(messages)
        self.assertEqual(caught.exception.reason, 'no_translatable_actions')

    def test_an_action_after_the_terminal_call_is_refused(self):
        messages = [{'role': 'user', 'content': 'go'},
                    call('execute_bash', {'command': 'ls'}, 'c1'), response('c1'),
                    call('finish', {}, 'c2'), response('c2'),
                    call('execute_bash', {'command': 'ls'}, 'c3')]
        with self.assertRaises(UntranslatableCall) as caught:
            translate_trajectory(messages)
        self.assertEqual(caught.exception.reason, 'action_after_terminal_call')

    def test_two_terminal_calls_are_refused(self):
        messages = [{'role': 'user', 'content': 'go'},
                    call('execute_bash', {'command': 'ls'}, 'c1'), response('c1'),
                    call('finish', {}, 'c2'), response('c2'),
                    call('finish', {}, 'c3')]
        with self.assertRaises(UntranslatableCall) as caught:
            translate_trajectory(messages)
        self.assertEqual(caught.exception.reason, 'multiple_terminal_calls')

    def test_message_ceiling_is_enforced(self):
        with self.assertRaises(UntranslatableCall) as caught:
            translate_trajectory(self.messages, max_messages=2)
        self.assertEqual(caught.exception.reason, 'trajectory_exceeds_message_ceiling')

    def test_translation_is_deterministic(self):
        first = translate_trajectory(self.messages)
        second = translate_trajectory(self.messages)
        self.assertEqual(first['plan_sha256'], second['plan_sha256'])
        self.assertEqual(first, second)


class AuditTests(unittest.TestCase):
    def test_audit_separates_accepted_and_refused_with_reasons(self):
        good = [{'role': 'user', 'content': 'go'},
                call('execute_bash', {'command': 'ls'}, 'c1'), response('c1'),
                call('finish', {}, 'c2')]
        bad = [{'role': 'user', 'content': 'go'},
               call('task_tracker', {'command': 'plan'}, 'c1'), response('c1'),
               call('finish', {}, 'c2')]
        broken = [{'role': 'user', 'content': 'go'}, response('ghost')]
        malformed = [{'role': 'user', 'content': 'go'},
                     call('str_replace_editor', {'command': 'view'}, 'c1'),
                     response('c1'), call('finish', {}, 'c2')]
        report = audit_translation([
            {'trajectory_id': 'a', 'messages': good},
            {'trajectory_id': 'b', 'messages': bad},
            {'trajectory_id': 'c', 'messages': broken},
            {'trajectory_id': 'd', 'messages': malformed}])
        self.assertEqual(report['rows'], 4)
        self.assertEqual(report['accepted'], 1)
        self.assertEqual(report['refused'], 3)
        self.assertAlmostEqual(report['acceptance_rate'], 1 / 4)
        # A malformed row is one counted refusal, never an aborted screen.
        self.assertEqual(report['refusal_reasons'],
                         {'missing_path': 1,
                          'no_official_task_tracking_tool': 1,
                          'source_history_validation_failed': 1})
        self.assertEqual(report['rules_applied'],
                         {'execute_bash_to_run_command': 1,
                          'finish_is_not_submit_patch': 1})
        self.assertFalse(report['replay_verified'])
        self.assertFalse(report['training_approved'])
        self.assertEqual(report['accepted_trajectories'][0]['translated_actions'], 1)

    def test_audit_requires_identified_rows(self):
        with self.assertRaisesRegex(ValueError, 'Nonempty trajectory row list'):
            audit_translation([])
        with self.assertRaisesRegex(ValueError, 'trajectory_id and messages'):
            audit_translation([{'messages': []}])


if __name__ == '__main__':
    unittest.main()
