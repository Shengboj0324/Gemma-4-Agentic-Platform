"""Check all checkpoint tensor names/shapes using meta tensors, without a GPU."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.architecture_layout import validate_architecture
from zenithsync.model_intake import inspect_safetensors
from zenithsync.quantized_layout import expected_projections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest_identity = file_record(args.manifest)
    if manifest_identity['sha256'] != args.manifest_sha256:
        raise ValueError('Unexpected model manifest')
    manifest = load_json(args.manifest)
    config_path = args.model_dir / 'config.json'
    config_identity = file_record(config_path)
    expected_config = next(row for row in manifest['files'] if row['path'] == 'config.json')
    if config_identity != {key: expected_config[key] for key in ('sha256', 'size_bytes')}:
        raise ValueError('Config does not match model manifest')
    config = load_json(config_path)
    projections = expected_projections(config)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', CUDA_VISIBLE_DEVICES='')
    import torch
    import transformers
    if transformers.__version__ != '5.13.1':
        raise ValueError('Requires qualified Transformers 5.13.1')
    from transformers import AutoConfig, AutoModelForMultimodalLM
    loaded_config = AutoConfig.from_pretrained(args.model_dir, local_files_only=True)
    with torch.device('meta'):
        model = AutoModelForMultimodalLM.from_config(loaded_config)
    state = model.state_dict()
    if not all(tensor.is_meta for tensor in state.values()):
        raise ValueError('Model construction allocated non-meta tensors')
    expected = {name: list(tensor.shape) for name, tensor in state.items()}
    checkpoint = args.model_dir / 'model.safetensors'
    structure = inspect_safetensors(checkpoint)
    with checkpoint.open('rb') as stream:
        prefix = stream.read(8)
        size = struct.unpack('<Q', prefix)[0]
        if size != structure['header_size_bytes']:
            raise ValueError('Checkpoint header changed')
        raw = stream.read(size)
        if hashlib.sha256(raw).hexdigest() != structure['header_sha256']:
            raise ValueError('Checkpoint header changed')
        header = json.loads(raw)
        original = {}
        for name in projections:
            descriptor = header[name + '.weight_shape']
            if descriptor['dtype'] != 'I64' or descriptor['shape'] != [2]:
                raise ValueError('Invalid original shape descriptor')
            stream.seek(8 + size + descriptor['data_offsets'][0])
            original[name] = struct.unpack('<qq', stream.read(16))
    counts = validate_architecture(header, expected, projections, original)
    if inspect_safetensors(checkpoint) != structure or file_record(config_path) != config_identity:
        raise ValueError('Structural inputs changed')
    if file_record(args.manifest) != manifest_identity:
        raise ValueError('Manifest changed')
    report = {'schema_version': 1, 'status': 'complete_tensor_layout_passed', **counts,
        'model_manifest': manifest_identity, 'config': config_identity, 'structure': structure,
        'torch_version': torch.__version__, 'transformers_version': transformers.__version__,
        'gpu_used': False, 'numerical_values_checked': False,
        'limitations': ['Metadata and stored shape integers only; no fresh full-weight hash or value scan.',
                        'Meta constructor is a pinned implementation comparison, not independent proof of architecture semantics.',
                        'No inference, training, dequantization or model-quality claim.'],
        'sources': {name: file_record(ROOT/name) for name in ['scripts/verify_architecture_layout.py', 'zenithsync/architecture_layout.py', 'zenithsync/quantized_layout.py', 'zenithsync/model_intake.py']}}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'report.json').write_bytes(canonical_json(report))
    (args.output/'expected-shapes.json').write_bytes(canonical_json(expected))
    print(counts)


if __name__ == '__main__':
    main()
