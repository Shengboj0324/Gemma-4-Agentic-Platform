"""Validate declared split isolation; semantic contamination needs a later audit."""

import hashlib

from .artifacts import canonical_json
from .contracts import digest


def validate_splits(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {"schema_version", "status", "tasks"}:
        raise ValueError("invalid split manifest")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("unsupported split schema")
    if value["status"] not in ("draft", "frozen") or not isinstance(value["tasks"], list):
        raise ValueError("invalid split status or tasks")
    if value["status"] == "frozen" and not value["tasks"]:
        raise ValueError("cannot freeze an empty cohort")
    identifiers = set()
    groups = {}
    for task in value["tasks"]:
        required = {"task_id", "repository_group", "leakage_group", "split", "input_sha256"}
        if not isinstance(task, dict) or set(task) != required:
            raise ValueError("invalid task fields")
        for key in required:
            if not isinstance(task[key], str) or not task[key].strip():
                raise ValueError(f"invalid task {key}")
        digest(task["input_sha256"])
        if task["split"] not in ("train", "development", "confirmation"):
            raise ValueError("unknown split")
        if task["task_id"] in identifiers:
            raise ValueError("duplicate task ID")
        identifiers.add(task["task_id"])
        # Content, repository, and known duplicate/fork families cannot cross splits.
        for key in ("repository_group", "leakage_group", "input_sha256"):
            group = (key, task[key])
            if group in groups and groups[group] != task["split"]:
                raise ValueError(f"cross-split leakage in {key}")
            groups[group] = task["split"]
    return {"status": value["status"], "task_count": len(identifiers)}


def merge_leakage_groups(manifest, links, *, max_link_members=1000000):
    """Apply reviewed task links transitively to a draft without moving tasks.

    Existing leakage families remain indivisible. Links are lists of at least
    two known task IDs; their evidential justification belongs to the caller.
    A linked component crossing split assignments fails rather than silently
    moving or dropping records. Frozen manifests cannot be rewritten here.
    """
    validate_splits(manifest)
    if manifest['status'] != 'draft':
        raise ValueError('Leakage merges require a draft split')
    if type(max_link_members) is not int or max_link_members <= 0:
        raise ValueError('Positive link-member budget required')
    if not isinstance(links, list) or len(links) > max_link_members // 2:
        raise ValueError('Bounded link list required')
    tasks = {row['task_id']: row for row in manifest['tasks']}
    parents = {task: task for task in tasks}

    def root(task):
        while parents[task] != task:
            parents[task] = parents[parents[task]]
            task = parents[task]
        return task

    def join(first, second):
        a, b = root(first), root(second)
        if a != b:
            parents[max(a, b)] = min(a, b)

    representatives = {}
    for task in sorted(tasks):
        family = tasks[task]['leakage_group']
        if family in representatives:
            join(task, representatives[family])
        else:
            representatives[family] = task
    members = 0
    for link in links:
        if not isinstance(link, list) or len(link) < 2:
            raise ValueError('Each link needs at least two distinct known task IDs')
        members += len(link)
        if members > max_link_members:
            raise ValueError('Link-member budget exceeded')
        if (any(not isinstance(task, str) or task not in tasks for task in link)
                or len(set(link)) != len(link)):
            raise ValueError('Each link needs at least two distinct known task IDs')
        for task in link[1:]:
            join(link[0], task)
    components = {}
    for task in sorted(tasks):
        components.setdefault(root(task), []).append(task)
    assignments, merged, emitted_labels = {}, [], set()
    for component in components.values():
        families = sorted({tasks[task]['leakage_group'] for task in component})
        if len({tasks[task]['split'] for task in component}) != 1:
            raise ValueError('Linked leakage family crosses splits')
        label = families[0]
        if len(families) > 1:
            label = 'merged-sha256:' + hashlib.sha256(canonical_json(families)).hexdigest()
            if label in representatives and label not in families:
                raise ValueError('Generated leakage label collides with existing family')
            merged.append({'leakage_group': label, 'source_groups': families, 'tasks': component})
        if label in emitted_labels:
            raise ValueError('Generated leakage labels collide across components')
        emitted_labels.add(label)
        for task in component:
            assignments[task] = label
    result = {'schema_version': manifest['schema_version'], 'status': 'draft',
              'tasks': [{**tasks[task], 'leakage_group': assignments[task]}
                        for task in sorted(tasks)]}
    validate_splits(result)
    return {'manifest': result, 'merged_families': merged,
            'training_approved': False, 'split_frozen': False}
