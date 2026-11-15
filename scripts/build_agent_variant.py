"""Build an agent variant that differs from a base submission only in declared ways.

Each variant changes some of: `eval_config.yaml` budget keys (`--eval KEY=VALUE`,
KEY in evaluation.*), sampling keys (`--sampling KEY=VALUE`, dotted for nested
keys such as thinking_config.thinking_budget), the system prompt replaced
(`--prompt-file FILE`) and/or an instruction addendum appended to it
(`--prompt-addendum FILE`), and harness tools removed from the root
agent's tool list (`--drop-tool NAME`; agent.yaml uses `!include` tags, so
the edit is on the exact `  - NAME` line, which must occur once). Everything else is
copied byte for byte. Then the output is compared with the base, and the build
is refused unless the differing paths are exactly the declared ones. The
variant's declaration is written to `variant.json` beside, not inside, the
submission. Values are parsed as YAML scalars, so 20 is an int and 0.2 a float.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record

EVAL_KEYS = {'max_time_minutes', 'max_tool_calls', 'max_turns', 'timeout_seconds'}
SAMPLING_TOP = {'temperature', 'top_p', 'top_k', 'max_output_tokens', 'thinking_config'}


def parse_assignments(items):
    import yaml
    pairs = {}
    for item in items:
        key, _, raw = item.partition('=')
        if not key or not _:
            raise ValueError(f'Expected KEY=VALUE, got {item!r}')
        pairs[key] = yaml.safe_load(raw)
    return pairs


def set_dotted(mapping, dotted, value):
    keys = dotted.split('.')
    node = mapping
    for key in keys[:-1]:
        node = node.setdefault(key, {})
        if not isinstance(node, dict):
            raise ValueError(f'{dotted}: {key} is not a mapping')
    node[keys[-1]] = value


def tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}


def build(base, output, *, eval_changes, sampling_changes, addendum, prompt_file=None, drop_tools=()):
    import yaml
    if output.exists():
        raise FileExistsError(output)
    unknown = set(eval_changes) - EVAL_KEYS
    if unknown:
        raise ValueError(f'Unsupported eval_config keys: {sorted(unknown)}')
    unknown = {k.split('.')[0] for k in sampling_changes} - SAMPLING_TOP
    if unknown:
        raise ValueError(f'Unsupported sampling keys: {sorted(unknown)}')
    shutil.copytree(base, output)
    declared = set()
    if eval_changes:
        config = yaml.safe_load((output / 'eval_config.yaml').read_text())
        for key, value in eval_changes.items():
            config['evaluation'][key] = value
        (output / 'eval_config.yaml').write_text(yaml.safe_dump(config, sort_keys=False))
        declared.add('eval_config.yaml')
    if sampling_changes:
        path = output / 'configs' / 'sampling.yaml'
        sampling = yaml.safe_load(path.read_text())
        for key, value in sampling_changes.items():
            set_dotted(sampling, key, value)
        path.write_text(yaml.safe_dump(sampling, sort_keys=False))
        declared.add('configs/sampling.yaml')
    if prompt_file is not None:
        text = prompt_file.read_text().strip()
        if not text:
            raise ValueError('Empty prompt file')
        (output / 'prompts' / 'system.md').write_text(text + '\n')
        declared.add('prompts/system.md')
    if addendum is not None:
        text = addendum.read_text().strip()
        if not text:
            raise ValueError('Empty prompt addendum')
        prompt = output / 'prompts' / 'system.md'
        prompt.write_text(prompt.read_text().rstrip('\n') + '\n\n' + text + '\n')
        declared.add('prompts/system.md')
    if drop_tools:
        agent = output / 'agent.yaml'
        lines = agent.read_text().split('\n')
        for tool in drop_tools:
            hits = [i for i, line in enumerate(lines) if line.strip() == f'- {tool}']
            if len(hits) != 1:
                raise ValueError(f'Tool {tool!r} must appear exactly once in agent.yaml, found {len(hits)}')
            del lines[hits[0]]
        agent.write_text('\n'.join(lines))
        declared.add('agent.yaml')
    before, after = tree(base), tree(output)
    if set(before) != set(after):
        raise ValueError('Variant added or removed files')
    differing = {p for p in before if before[p] != after[p]}
    if differing != declared:
        raise ValueError(f'Differing paths {sorted(differing)} != declared {sorted(declared)}')
    return sorted(differing)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--eval', action='append', default=[], help='evaluation KEY=VALUE')
    parser.add_argument('--sampling', action='append', default=[], help='sampling KEY=VALUE (dotted)')
    parser.add_argument('--prompt-file', type=Path, help='replaces prompts/system.md')
    parser.add_argument('--prompt-addendum', type=Path)
    parser.add_argument('--drop-tool', action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    eval_changes = parse_assignments(args.eval)
    sampling_changes = parse_assignments(args.sampling)
    differing = build(args.base, args.output, eval_changes=eval_changes, sampling_changes=sampling_changes,
                      addendum=args.prompt_addendum, prompt_file=args.prompt_file, drop_tools=args.drop_tool)
    record = {'schema_version': 1, 'name': args.name, 'base': str(args.base), 'eval': eval_changes,
              'sampling': sampling_changes, 'differing_paths': differing,
              'prompt_addendum': file_record(args.prompt_addendum) if args.prompt_addendum else None,
              'prompt_file': file_record(args.prompt_file) if args.prompt_file else None,
              'dropped_tools': args.drop_tool,
              'files': {p: file_record(args.output / p) for p in differing}}
    (args.output.parent / f'{args.output.name}.variant.json').write_bytes(canonical_json(record))
    print(json.dumps({'name': args.name, 'differing_paths': differing}))


if __name__ == '__main__':
    main()
