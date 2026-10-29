"""Translate OpenHands tool calls into the official nine-tool contract.

Scope, stated plainly: this translates **actions only**. It never translates a
tool result. The official tools return structured JSON objects — `run_command`
returns `exit_code`/`status`/`stdout`/`stderr`, `read_file` returns `content`
and a line range, `edit_file` returns a unified diff and an occurrence count —
and an OpenHands observation does not separate those fields. Re-rendering one
into the other would fabricate a runtime result, so results must come from
actually executing the translated action in the official runtime and capturing
what it returns. `zenithsync.replay_history` consumes this module's output for
exactly that purpose.

Every translation is justified by a named rule and records the argument mapping
it applied. Anything without a demonstrated equivalent is refused with a stable
reason code rather than approximated. A refusal is the correct outcome: renaming
a function does not make its semantics match.

The terminal action is deliberately not translated. OpenHands `finish` signals
that the agent considers itself done; the official `submit_patch` captures the
working tree as a diff. They are different acts, so the submission must be
authored by the replay adapter and recorded as adapter-authored.
"""

from .artifacts import canonical_json
from .conversation import normalize_arguments, normalize_history

OPENHANDS_TOOLS = frozenset({'execute_bash', 'str_replace_editor', 'think',
                             'task_tracker', 'finish'})
OFFICIAL_TOOLS = frozenset({'run_command', 'read_file', 'edit_file', 'write_file',
                            'get_status', 'submit_patch', 'get_code_neighbors',
                            'search_similar_code', 'get_code_subgraph'})
# OpenHands exports a thought as a tool exchange; the official template carries
# assistant reasoning in its own channel, so a thought becomes a reasoning field
# on the next assistant action rather than a call with an invented result.
FOLDED_TOOLS = frozenset({'think'})
# Authored by the replay adapter, never carried over from the source trajectory.
ADAPTER_AUTHORED_TERMINAL = 'submit_patch'

DEFAULT_WORKSPACE = '/workspace'
# `execute_bash` documents `command` as accepting control sentinels that are sent
# to a running process rather than executed. The official `run_command` has no
# process to send them to, so they are refused rather than run as programs.
INTERACTIVE_SENTINELS = frozenset({'C-c', 'C-d', 'C-z', 'C-C', 'C-D', 'C-Z'})


class UntranslatableCall(ValueError):
    """A stable reason code; never echoes source code or file content."""

    def __init__(self, reason, *, tool=None):
        super().__init__(reason if tool is None else f'{reason} [{tool}]')
        self.reason = reason
        self.tool = tool


def _text(value, field):
    if not isinstance(value, str):
        raise UntranslatableCall('nontext_' + field)
    return value


def workspace_relative(path, *, workspace=DEFAULT_WORKSPACE, file_paths=None):
    """Map an absolute workspace path to the relative path the official tools take.

    The official schema documents `filepath` as a relative path within the
    workspace. A path outside the declared workspace, a traversal segment, or a
    directory-shaped path is refused rather than guessed at.

    `file_paths`, when supplied, is the set of relative file paths that actually
    exist in the pinned snapshot. It resolves the file-or-directory question
    exactly, which matters because the source's `str_replace_editor` accepts a
    directory for `view` and lists it, while the official `read_file` reads a
    file. Without it, callers that need the distinction must use
    `require_file_target=True` and accept the conservative heuristic below.
    """
    value = _text(path, 'path')
    if not value or value.endswith('/'):
        raise UntranslatableCall('directory_shaped_path')
    prefix = workspace.rstrip('/') + '/'
    if value.startswith(prefix):
        value = value[len(prefix):]
    elif value == workspace.rstrip('/'):
        raise UntranslatableCall('workspace_root_is_not_a_file')
    elif value.startswith('/'):
        raise UntranslatableCall('path_outside_declared_workspace')
    parts = value.split('/')
    if not value or any(part in ('', '.', '..') for part in parts):
        raise UntranslatableCall('noncanonical_relative_path')
    if file_paths is not None:
        if not isinstance(file_paths, (set, frozenset)):
            raise ValueError('file_paths must be a set of relative file paths')
        if value not in file_paths:
            # Either a directory or a path absent from the snapshot. Both would
            # make the official call do something different from the source's.
            raise UntranslatableCall('target_is_not_a_known_snapshot_file')
    return value


def _looks_like_a_file(relative):
    """A declared heuristic, used only when no snapshot is supplied.

    Directories in source repositories overwhelmingly lack a suffix and source
    files overwhelmingly have one. This errs toward refusal: an extensionless
    file such as `Makefile`, `LICENSE` or `Dockerfile` is refused rather than
    translated, which loses data but never changes what the agent did. Pass
    `file_paths` to decide exactly instead.
    """
    final = relative.rsplit('/', 1)[-1]
    return '.' in final.strip('.') and not final.endswith('.')


def _line(value, field):
    if type(value) is not int or value < 1:
        raise UntranslatableCall('invalid_' + field)
    return value


def _required(arguments, field):
    if field not in arguments:
        raise UntranslatableCall('missing_' + field)
    return arguments[field]


def _view(arguments, workspace, file_paths):
    extra = sorted(set(arguments) - {'command', 'path', 'view_range'})
    if extra:
        raise UntranslatableCall('unsupported_view_argument_' + extra[0])
    name = workspace_relative(_required(arguments, 'path'), workspace=workspace,
                              file_paths=file_paths)
    if file_paths is None and not _looks_like_a_file(name):
        # The source tool lists a directory here; the official tool reads a
        # file. Guessing would replace a listing with an error observation and
        # silently change the trajectory.
        raise UntranslatableCall('view_target_may_be_a_directory')
    translated = {'filepath': name}
    mapping = {'path': 'filepath'}
    rule = 'view_whole_file_to_read_file'
    if 'view_range' in arguments:
        window = arguments['view_range']
        if not isinstance(window, list) or len(window) != 2:
            raise UntranslatableCall('invalid_view_range')
        start, end = window
        # OpenHands uses -1 to mean "to end of file"; the official tool has no
        # such sentinel, so an open-ended window becomes a whole-file read.
        start = _line(start, 'view_range_start')
        if end == -1:
            # OpenHands reads from `start` to end of file; the official tool
            # omits `end_line` for the same effect. It is a read from a line,
            # not a whole-file read, unless `start` happens to be 1.
            rule = 'open_ended_view_range_to_read_file_from_line'
            mapping['view_range'] = 'start_line'
            translated['start_line'] = start
        else:
            end = _line(end, 'view_range_end')
            if end < start:
                raise UntranslatableCall('inverted_view_range')
            rule = 'bounded_view_range_to_read_file_line_range'
            mapping['view_range'] = 'start_line,end_line'
            translated.update(start_line=start, end_line=end)
    return 'read_file', translated, rule, mapping


def _create(arguments, workspace, file_paths):
    extra = sorted(set(arguments) - {'command', 'path', 'file_text'})
    if extra:
        raise UntranslatableCall('unsupported_create_argument_' + extra[0])
    if 'file_text' not in arguments:
        raise UntranslatableCall('create_without_file_text')
    # `create` names the file it is about to write, so it cannot be checked
    # against a snapshot of files that already exist.
    return 'write_file', {
        'filepath': workspace_relative(_required(arguments, 'path'),
                                       workspace=workspace),
        'content': _text(arguments['file_text'], 'file_text'),
    }, 'create_to_write_file', {'path': 'filepath', 'file_text': 'content'}


def _str_replace(arguments, workspace, file_paths):
    extra = sorted(set(arguments) - {'command', 'path', 'old_str', 'new_str'})
    if extra:
        raise UntranslatableCall('unsupported_str_replace_argument_' + extra[0])
    if 'old_str' not in arguments:
        raise UntranslatableCall('str_replace_without_old_str')
    old = _text(arguments['old_str'], 'old_str')
    if not old:
        raise UntranslatableCall('empty_old_str')
    if 'new_str' not in arguments or arguments['new_str'] is None:
        # Deleting a block and replacing it with the empty string are different
        # declarations; the official tool requires new_string, so refuse rather
        # than assume the source meant an empty replacement.
        raise UntranslatableCall('str_replace_without_explicit_new_str')
    new = _text(arguments['new_str'], 'new_str')
    if new == old:
        raise UntranslatableCall('no_op_str_replace')
    return 'edit_file', {
        'filepath': workspace_relative(_required(arguments, 'path'),
                                       workspace=workspace, file_paths=file_paths),
        'old_string': old, 'new_string': new,
    }, 'str_replace_to_edit_file', {'path': 'filepath', 'old_str': 'old_string',
                                    'new_str': 'new_string'}


_EDITOR_COMMANDS = {'view': _view, 'create': _create, 'str_replace': _str_replace}


def translate_call(name, arguments, *, workspace=DEFAULT_WORKSPACE, file_paths=None):
    """Return the official call an OpenHands call is demonstrably equivalent to.

    Raises `UntranslatableCall` for every operation without such an equivalent,
    including `insert`, `undo_edit`, interactive stdin writes, interactive
    control sentinels, directory listings and task tracking.

    `file_paths` is the set of relative file paths in the pinned snapshot. Supply
    it to decide file-versus-directory targets exactly; without it a declared,
    conservative suffix heuristic is used and extensionless targets are refused.
    """
    if not isinstance(name, str) or name not in OPENHANDS_TOOLS:
        raise UntranslatableCall('unknown_source_tool', tool=str(name))
    arguments = normalize_arguments(arguments)
    if name == 'think':
        if set(arguments) - {'thought'} or 'thought' not in arguments:
            raise UntranslatableCall('unsupported_think_arguments', tool=name)
        thought = _text(arguments['thought'], 'thought')
        if not thought.strip():
            raise UntranslatableCall('empty_thought', tool=name)
        return {'disposition': 'folded_into_reasoning', 'reasoning': thought,
                'rule': 'think_to_reasoning_channel', 'source_tool': name,
                'argument_mapping': {'thought': 'reasoning'}}
    if name == 'finish':
        extra = sorted(set(arguments) - {'message'})
        if extra:
            raise UntranslatableCall(
                'unsupported_finish_argument_' + extra[0], tool=name)
        if 'message' in arguments:
            _text(arguments['message'], 'message')
        return {'disposition': 'terminal_requires_adapter_submission',
                'rule': 'finish_is_not_submit_patch', 'source_tool': name,
                'adapter_authored_tool': ADAPTER_AUTHORED_TERMINAL,
                # Recorded so a plan says whether the source terminal carried a
                # message, rather than erasing the distinction.
                'source_message_present': 'message' in arguments,
                'argument_mapping': {}}
    if name == 'task_tracker':
        raise UntranslatableCall('no_official_task_tracking_tool', tool=name)
    if name == 'execute_bash':
        # Each untranslatable argument gets its own reason code. A single shared
        # code would hide which of these an exporter actually produces, and the
        # per-reason histogram is the whole point of screening a shard.
        if 'is_input' in arguments:
            value = arguments['is_input']
            if value is not False:
                # Writing to a running process's stdin needs a persistent
                # interactive session, which `run_command` does not have.
                raise UntranslatableCall('interactive_stdin_write', tool=name)
            # An explicitly serialized `is_input: false` is a plain command.
            arguments = {key: item for key, item in arguments.items()
                         if key != 'is_input'}
        if 'timeout' in arguments:
            # A real source field with no official counterpart; dropping it
            # would silently change how long the command is allowed to run.
            raise UntranslatableCall('unsupported_execute_bash_timeout', tool=name)
        extra = sorted(set(arguments) - {'command'})
        if extra:
            raise UntranslatableCall(
                'unsupported_execute_bash_argument_' + extra[0], tool=name)
        if 'command' not in arguments:
            raise UntranslatableCall('execute_bash_without_command', tool=name)
        command = _text(arguments['command'], 'command')
        if not command.strip():
            raise UntranslatableCall('empty_command', tool=name)
        if command.strip() in INTERACTIVE_SENTINELS:
            # `C-c` and friends arrive through `command` but are not commands:
            # the source runtime interprets them as control characters sent to a
            # running process. Translating them literally would run a nonexistent
            # program instead of interrupting one.
            raise UntranslatableCall('interactive_control_sentinel', tool=name)
        return {'disposition': 'translated', 'name': 'run_command',
                'arguments': {'command': command},
                'rule': 'execute_bash_to_run_command', 'source_tool': name,
                'argument_mapping': {'command': 'command'}}
    command = arguments.get('command')
    if not isinstance(command, str):
        raise UntranslatableCall('editor_without_command', tool=name)
    handler = _EDITOR_COMMANDS.get(command)
    if handler is None:
        # `insert` places text at a line number and `undo_edit` reverts the
        # editor's own history; neither has an official counterpart.
        raise UntranslatableCall('unsupported_editor_command_' + command, tool=name)
    official, translated, rule, mapping = handler(arguments, workspace, file_paths)
    if official not in OFFICIAL_TOOLS:
        raise UntranslatableCall('translation_target_not_in_official_contract', tool=name)
    return {'disposition': 'translated', 'name': official, 'arguments': translated,
            'rule': rule, 'source_tool': name, 'argument_mapping': mapping}


def translate_trajectory(messages, *, workspace=DEFAULT_WORKSPACE,
                         file_paths=None, max_messages=100000):
    """Translate one source trajectory into an ordered official action plan.

    The result is a plan for replay, not a training example: every `result` is
    absent because only the official runtime may supply one. Thoughts attach to
    the action that follows them, and a thought with no following action is
    dropped and counted rather than attached to an invented action.

    A trajectory is translatable only if every one of its calls translates. A
    partially translated trajectory would silently change what the agent did,
    so the first refusal fails the whole trajectory with its reason code.
    """
    if type(max_messages) is not int or max_messages <= 0:
        raise ValueError('Positive message ceiling required')
    normalized = normalize_history(messages, allowed_tools=set(OPENHANDS_TOOLS),
                                   allow_pending=True)
    if len(normalized) > max_messages:
        raise UntranslatableCall('trajectory_exceeds_message_ceiling')
    actions, rules, folded = [], {}, 0
    pending_reasoning = []
    terminal = None
    source_calls = 0
    for index, message in enumerate(normalized):
        if message['role'] != 'assistant':
            continue
        for call in message.get('tool_calls', []):
            source_calls += 1
            function = call['function']
            outcome = translate_call(function['name'], function['arguments'],
                                     workspace=workspace, file_paths=file_paths)
            rules[outcome['rule']] = rules.get(outcome['rule'], 0) + 1
            disposition = outcome['disposition']
            if disposition == 'folded_into_reasoning':
                pending_reasoning.append(outcome['reasoning'])
                folded += 1
                continue
            if disposition == 'terminal_requires_adapter_submission':
                if terminal is not None:
                    raise UntranslatableCall('multiple_terminal_calls')
                terminal = {'source_index': index, 'rule': outcome['rule'],
                            'adapter_authored_tool': outcome['adapter_authored_tool']}
                continue
            if terminal is not None:
                raise UntranslatableCall('action_after_terminal_call')
            actions.append({'source_index': index, 'name': outcome['name'],
                            'arguments': outcome['arguments'],
                            'rule': outcome['rule'],
                            'source_tool': outcome['source_tool'],
                            'argument_mapping': outcome['argument_mapping'],
                            'reasoning': '\n\n'.join(pending_reasoning)})
            pending_reasoning = []
    if not actions:
        raise UntranslatableCall('no_translatable_actions')
    if terminal is None:
        raise UntranslatableCall('missing_terminal_finish_call')
    return {
        'schema_version': 1, 'workspace': workspace,
        'snapshot_file_paths_supplied': file_paths is not None,
        'source_messages': len(normalized), 'source_calls': source_calls,
        'actions': actions, 'translated_actions': len(actions),
        'folded_thoughts': folded,
        'dropped_trailing_thoughts': len(pending_reasoning),
        'terminal': terminal, 'rules_applied': dict(sorted(rules.items())),
        'source_history_sha256': _digest(messages),
        'plan_sha256': _digest(actions),
        'results_present': False, 'training_approved': False,
        'scope': 'Action-only translation under named equivalence rules. Results '
                 'are absent by design and must be captured by executing these '
                 'actions in the official runtime. The terminal submission is '
                 'adapter-authored, not carried over from the source.',
    }


def _digest(value):
    import hashlib
    return hashlib.sha256(canonical_json(value)).hexdigest()


def audit_translation(rows, *, workspace=DEFAULT_WORKSPACE, file_paths=None):
    """Count translatable and refused trajectories with per-reason breakdowns.

    Intended for screening a shard before committing replay compute. Refusal
    reasons are retained in full: a high refusal rate for one reason is a signal
    about the source's tool semantics, not noise to be summarised away.
    """
    if not isinstance(rows, list) or not rows:
        raise ValueError('Nonempty trajectory row list required')
    accepted, refused = [], []
    reasons, rules = {}, {}
    for row in rows:
        if not isinstance(row, dict) or 'trajectory_id' not in row or 'messages' not in row:
            raise ValueError('Each row requires trajectory_id and messages')
        identity = row['trajectory_id']
        try:
            plan = translate_trajectory(row['messages'], workspace=workspace,
                                        file_paths=file_paths)
        except UntranslatableCall as error:
            reason = error.reason
        except ValueError:
            reason = 'source_history_validation_failed'
        except (KeyError, TypeError, AttributeError) as error:
            # A malformed row must be one counted refusal, never an aborted
            # shard screen. Any such case is a defect, so it is named loudly.
            reason = 'unexpected_' + type(error).__name__.lower()
        else:
            reason = None
        if reason is not None:
            reasons[reason] = reasons.get(reason, 0) + 1
            refused.append({'trajectory_id': identity, 'reason': reason})
            continue
        for rule, count in plan['rules_applied'].items():
            rules[rule] = rules.get(rule, 0) + count
        accepted.append({'trajectory_id': identity,
                         'translated_actions': plan['translated_actions'],
                         'folded_thoughts': plan['folded_thoughts'],
                         'plan_sha256': plan['plan_sha256'],
                         'source_history_sha256': plan['source_history_sha256']})
    return {'schema_version': 1, 'rows': len(rows), 'accepted': len(accepted),
            'refused': len(refused),
            'acceptance_rate': len(accepted) / len(rows),
            'refusal_reasons': dict(sorted(reasons.items())),
            'rules_applied': dict(sorted(rules.items())),
            'accepted_trajectories': accepted, 'refused_trajectories': refused,
            'replay_verified': False, 'training_approved': False,
            'scope': 'Structural translatability only. It does not establish that '
                     'the translated actions reproduce the source behaviour, that '
                     'the task was solved, or that the data may be trained on.'}
