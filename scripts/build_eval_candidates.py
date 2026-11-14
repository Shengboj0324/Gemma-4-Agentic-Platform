"""Build the two submissions compared on held-out tasks: base and base+adapter.

Both start from candidates/p1-base, verified against its manifest. The adapter
submission differs in exactly two ways: adapters/main_lora/ holds the exported
PEFT adapter (checked against its export receipt), and the root agent declares
`adapter: main_lora`. Everything else — prompt, tools, sampling, budgets — is
byte-identical, so a difference in outcomes is attributable to the adapter.
Writes base/, adapter/, manifests and receipt.json to a new --output.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, inventory, load_json, verify

ADAPTER = 'main_lora'
LIMIT_BYTES = 3 * 1024 ** 3


def add_adapter_line(agent_yaml: str) -> str:
    lines = agent_yaml.splitlines(keepends=True)
    if any(line.startswith('adapter:') for line in lines):
        raise ValueError('Base agent already declares an adapter')
    model = [i for i, line in enumerate(lines) if line.startswith('model:')]
    if len(model) != 1:
        raise ValueError('Expected exactly one root model declaration')
    lines.insert(model[0] + 1, f'adapter: {ADAPTER}\n')
    return ''.join(lines)


def build(base_source: Path, base_manifest: dict, adapter_dir: Path, adapter_receipt: dict, output: Path):
    verify(base_source, base_manifest)
    for name, identity in adapter_receipt['files'].items():
        if file_record(adapter_dir / name) != identity:
            raise ValueError('Adapter file differs from its export receipt: ' + name)
    output.mkdir(parents=True)
    shutil.copytree(base_source, output / 'base')
    shutil.copytree(base_source, output / 'adapter')
    target = output / 'adapter' / 'adapters' / ADAPTER
    target.mkdir(parents=True)
    for name in adapter_receipt['files']:
        shutil.copyfile(adapter_dir / name, target / name)
    agent = output / 'adapter' / 'agent.yaml'
    agent.write_text(add_adapter_line(agent.read_text()))
    manifests = {}
    for name in ('base', 'adapter'):
        manifest = inventory(output / name, kind='candidate', source='zenithsync', revision=name)
        total = sum(row['size_bytes'] for row in manifest['files'])
        if total >= LIMIT_BYTES:
            raise ValueError(f'{name} submission is not strictly under 3 GiB')
        manifests[name] = manifest
    files = {name: {r['path']: (r['sha256'], r['size_bytes']) for r in m['files']}
             for name, m in manifests.items()}
    differing = sorted(path for path in files['base'].keys() | files['adapter'].keys()
                       if files['base'].get(path) != files['adapter'].get(path))
    expected = sorted({'agent.yaml', f'adapters/{ADAPTER}/adapter_config.json',
                       f'adapters/{ADAPTER}/adapter_model.safetensors'})
    if differing != expected:
        raise ValueError(f'Candidates differ in unexpected files: {differing}')
    return manifests, differing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter-dir', type=Path, required=True)
    parser.add_argument('--adapter-receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    receipt = load_json(args.adapter_receipt)
    manifests, differing = build(ROOT / 'candidates/p1-base', load_json(ROOT / 'evidence/p1/base-agent-001/manifest.json'),
                                 args.adapter_dir, receipt, args.output)
    for name, manifest in manifests.items():
        (args.output / f'{name}-manifest.json').write_bytes(canonical_json(manifest))
    record = {'schema_version': 1, 'status': 'eval_candidates_built', 'adapter_name': ADAPTER,
              'differing_paths': differing, 'adapter_export_receipt': file_record(args.adapter_receipt),
              'manifests': {n: file_record(args.output / f'{n}-manifest.json') for n in manifests},
              'script': file_record(Path(__file__))}
    (args.output / 'receipt.json').write_bytes(canonical_json(record))
    print(json.dumps({'differing_paths': differing}))


if __name__ == '__main__':
    main()
