"""Export one hash-bound training checkpoint as a PEFT adapter directory.

Refuses an existing --output, verifies the checkpoint by SHA-256 and size before
deserialising it, checks the adapter against the base model's projection layout,
and writes a receipt binding output files to their source.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.quantized_layout import expected_projections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--checkpoint-sha256', required=True)
    parser.add_argument('--checkpoint-size', type=int, required=True)
    parser.add_argument('--model-config', type=Path, required=True)
    parser.add_argument('--max-bytes', type=int, default=536870912)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    from zenithsync.adapter_export import export_adapter
    from zenithsync.checkpoint_storage import load_checkpoint
    shapes = expected_projections(load_json(args.model_config))
    identity = {'sha256': args.checkpoint_sha256, 'size_bytes': args.checkpoint_size}
    payload = load_checkpoint(args.checkpoint, expected_identity=identity, max_bytes=args.max_bytes)
    counts = export_adapter(payload, shapes, args.output / 'adapter')
    receipt = {'schema_version': 1, 'status': 'adapter_exported', 'checkpoint': identity,
               'bindings': payload['bindings'], 'cursor': payload['cursor'],
               'model_config': file_record(args.model_config), 'projections': len(shapes), **counts,
               'files': {name: file_record(args.output / 'adapter' / name)
                         for name in ('adapter_config.json', 'adapter_model.safetensors')},
               'scope': 'Format conversion of trained weights; no quality or serving claim'}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'status': receipt['status'], 'tensors': counts['tensors'], 'parameters': counts['parameters']})


if __name__ == '__main__':
    main()
