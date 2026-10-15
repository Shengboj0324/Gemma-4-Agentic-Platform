"""Derive explicit mini-trace command amendments without reusing observations."""
from .conversation import normalize_history
from .replay_amendment import amend_actions


TERMINALS = frozenset({
    'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && cat patch.txt',
    'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && cat /testbed/patch.txt',
})


def mini_command_actions(messages):
    """Normalize source calls into indexed shell actions, including the terminal."""
    normalized = normalize_history(messages, allowed_tools={'bash'}, allow_pending=True)
    actions = []
    for index, message in enumerate(normalized):
        for call in message.get('tool_calls', []):
            arguments = call['function']['arguments']
            if (set(arguments) != {'command'}
                    or not isinstance(arguments['command'], str)
                    or not arguments['command'].strip() or '\0' in arguments['command']):
                raise ValueError('Exact nonempty source bash command required')
            actions.append({'index': index, 'kind': 'shell', 'command': arguments['command']})
    if not actions or actions[-1]['command'] not in TERMINALS:
        raise ValueError('Reviewed source terminal required')
    return actions


def mini_commands(messages, plan=None):
    """Preserve action order and source indices; never permit terminal amendments."""
    actions = mini_command_actions(messages)
    attribution = []
    if plan is not None:
        result = amend_actions(actions, plan)
        if any(row['action_index'] == len(actions) - 1 for row in result['attribution']):
            raise ValueError('Source terminal cannot be amended')
        actions = result['actions']
        attribution = result['attribution']
    commands = [(row['index'], {'command': row['command']}) for row in actions]
    return commands, {row['action_index']: row for row in attribution}


def verify_mini_amendment_binding(profile, replay, history=None):
    """Reject missing, orphaned or inconsistent amendment provenance claims."""
    documents = [replay] if history is None else [replay, history]
    if 'amendment' not in profile:
        if any('amendment' in document for document in documents):
            raise ValueError('Amendment claims require an explicit profile plan')
        return None
    plan = profile['amendment']
    if not isinstance(plan, dict) or any(document.get('amendment') != plan for document in documents):
        raise ValueError('Mini amendment provenance differs from profile')
    # Complete plan and source/derived identities are checked by mini_commands.
    return plan
