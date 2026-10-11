"""Construct explicitly attributed action derivatives; never reuse observations.

This is a provenance primitive, not a command sandbox or replay qualification.
Callers must preflight source actions and execute the derivative in a fresh runtime.
"""

import copy
import hashlib
import re

from .artifacts import canonical_json

MAX_ACTION_BYTES = 2 * 1024**2


def _identity(data):
    return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}


def _check_identity(value):
    if (not isinstance(value, dict) or set(value) != {'sha256', 'size_bytes'}
            or not isinstance(value['sha256'], str)
            or re.fullmatch('[0-9a-f]{64}', value['sha256']) is None
            or type(value['size_bytes']) is not int
            or not 0 < value['size_bytes'] <= MAX_ACTION_BYTES):
        raise ValueError('Bound action-list identity required')


def amend_actions(actions, plan):
    """Return a detached derivative and attribution after checking both identities.

    Amendments replace whole text fields in normalized shell/create actions only.
    No action may be inserted, removed, reordered, or assigned a different path.
    ``action_index`` is the list ordinal, not the original teacher event index.
    Expected identities refer to canonical JSON, including its trailing newline.
    """
    required = {'schema_version', 'author', 'reason', 'source_actions',
                'derived_actions', 'amendments'}
    if (not isinstance(plan, dict) or set(plan) != required
            or type(plan['schema_version']) is not int or plan['schema_version'] != 1
            or plan['author'] != 'assistant'
            or not isinstance(plan['reason'], str) or not plan['reason'].strip()):
        raise ValueError('Explicit assistant action-amendment plan required')
    for name in ('source_actions', 'derived_actions'):
        _check_identity(plan[name])
    if plan['source_actions'] == plan['derived_actions']:
        raise ValueError('Amendment must change action content')
    if not isinstance(actions, list) or not actions:
        raise ValueError('Nonempty normalized source action list required')
    source = canonical_json(actions)
    if len(source) > MAX_ACTION_BYTES or _identity(source) != plan['source_actions']:
        raise ValueError('Source actions differ from amendment plan')
    changes = plan['amendments']
    if not isinstance(changes, list) or not 1 <= len(changes) <= 32:
        raise ValueError('One to 32 ordered action amendments required')
    derived = copy.deepcopy(actions)
    previous = -1
    attribution = []
    for change in changes:
        if (not isinstance(change, dict)
                or set(change) != {'action_index', 'field', 'before', 'after', 'reason'}):
            raise ValueError('Exact amendment fields required')
        index = change['action_index']
        if type(index) is not int or not previous < index < len(actions):
            raise ValueError('Amendment indices must be unique and increasing')
        previous = index
        if (not isinstance(change['reason'], str) or not change['reason'].strip()
                or any(not isinstance(change[key], str) or not change[key].strip()
                       or '\0' in change[key] for key in ('before', 'after'))
                or change['before'] == change['after']):
            raise ValueError('Nonempty, different amendment text and reason required')
        action = derived[index]
        if not isinstance(action, dict) or type(action.get('index')) is not int:
            raise ValueError('Normalized source event index required')
        if action.get('kind') == 'shell' and change['field'] == 'command':
            target, key = action, 'command'
        elif action.get('kind') == 'create' and change['field'] == 'file_text':
            target, key = action.get('arguments'), 'file_text'
        else:
            raise ValueError('Only shell command or created-file text may be amended')
        if not isinstance(target, dict) or target.get(key) != change['before']:
            raise ValueError('Amendment text does not match original action')
        target[key] = change['after']
        attribution.append({'action_index': index, 'source_index': action['index'],
                            'author': 'assistant', 'reason': change['reason'],
                            'before': _identity(change['before'].encode('utf-8')),
                            'after': _identity(change['after'].encode('utf-8'))})
    encoded = canonical_json(derived)
    if len(encoded) > MAX_ACTION_BYTES or _identity(encoded) != plan['derived_actions']:
        raise ValueError('Derived actions differ from amendment plan')
    return {'actions': derived, 'attribution': attribution,
            'source_actions': _identity(source), 'derived_actions': _identity(encoded),
            'training_approved': False, 'fresh_replay_required': True}


def amended_replay_history(events, *, actions, plan, system, problem,
                           allowed_tools, completion_plan=None):
    """Bind changed native calls to the derivative before projecting observations."""
    from .replay_completion import completed_replay_history
    from .replay_history import native_replay_history

    derivative = amend_actions(actions, plan)
    if not isinstance(events, list) or any(not isinstance(e, dict) for e in events):
        raise ValueError('Captured native event list required')
    source_events = [e for e in events if e.get('kind') != 'completion']
    if len(source_events) != len(derivative['actions']):
        raise ValueError('Every derived action requires its own native event')
    changed = {row['action_index']: row for row in derivative['attribution']}
    for ordinal, (action, event) in enumerate(zip(derivative['actions'], source_events)):
        if (type(event.get('source_index')) is not int
                or event['source_index'] != action['index']
                or event.get('kind') != action['kind']):
            raise ValueError('Derived action order or kind differs from captured events')
        if ordinal in changed:
            if action['kind'] == 'shell':
                name, arguments = 'run_command', {'command': action['command']}
            else:
                name, arguments = 'write_file', {'filepath': action['path'],
                                                'content': action['arguments']['file_text']}
            if event.get('native_calls') != [{'name': name, 'arguments': arguments,
                                              'result': event.get('result')}]:
                raise ValueError('Amended native call differs from explicit derivative')
    kwargs = dict(system=system, problem=problem, allowed_tools=allowed_tools)
    if completion_plan is None:
        if any(e.get('kind') == 'completion' or 'adapter_authored' in e for e in events):
            raise ValueError('Completion events require their own bound plan')
        projected = native_replay_history(events, **kwargs)
    else:
        if completion_plan.get('source_actions') != derivative['derived_actions']:
            raise ValueError('Completion plan must bind derived actions')
        projected = completed_replay_history(events, plan=completion_plan, **kwargs)
    by_source = {row['source_index']: row for row in derivative['attribution']}
    for row in projected['mapping']:
        if row['source_index'] in by_source:
            row.update(amendment=copy.deepcopy(by_source[row['source_index']]),
                       author='assistant', adapter_authored=True)
    projected['scope'] += '; explicitly attributed action amendments verified against captured calls'
    return projected
