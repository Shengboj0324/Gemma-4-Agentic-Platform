"""Turn a hash-bound training checkpoint into a standard PEFT LoRA adapter.

A corpus-session checkpoint carries the adapter under PEFT's in-memory names
(``base_model.model.<module>.lora_A.default.weight``) beside optimizer, RNG and
cursor state. A deliverable adapter is the directory ``PeftModel.from_pretrained``
reads: ``adapter_config.json`` plus ``adapter_model.safetensors`` with the
adapter name dropped from every key.

The configuration is rebuilt to equal the one ``attach_training_adapter`` used
(r=4, alpha=8, no dropout, no bias, an exact anchored pattern of the trained
projections), and the test suite holds the two equal field by field. Weights
are checked for exact coverage, shape, dtype and finiteness before anything is
written; nothing else from the checkpoint leaves it.
"""
import re

RANK = 4
ALPHA = 8


def lora_config(target_shapes):
    from peft import LoraConfig
    if not target_shapes:
        raise ValueError('Nonempty exact target shapes required')
    return LoraConfig(r=RANK, lora_alpha=ALPHA, lora_dropout=0.0, bias='none',
                      target_modules='(?:' + '|'.join(re.escape(name) for name in sorted(target_shapes)) + ')')


def adapter_tensors(adapter, target_shapes):
    """Validate checkpoint adapter tensors and return them under saved-PEFT keys."""
    import torch
    expected = {}
    for name, (rows, columns) in target_shapes.items():
        expected[f'base_model.model.{name}.lora_A.default.weight'] = (f'base_model.model.{name}.lora_A.weight', (RANK, columns))
        expected[f'base_model.model.{name}.lora_B.default.weight'] = (f'base_model.model.{name}.lora_B.weight', (rows, RANK))
    if not isinstance(adapter, dict) or set(adapter) != set(expected):
        raise ValueError('Checkpoint adapter coverage differs from the target projections')
    result = {}
    for key, (saved, shape) in expected.items():
        value = adapter[key]
        if not isinstance(value, torch.Tensor) or tuple(value.shape) != shape:
            raise ValueError('Adapter tensor shape differs: ' + key)
        if value.dtype != torch.float32:
            raise ValueError('Adapter tensors must be float32 as trained: ' + key)
        if not torch.isfinite(value).all().item():
            raise ValueError('Nonfinite adapter tensor: ' + key)
        result[saved] = value.detach().contiguous().clone()
    return result


def export_adapter(payload, target_shapes, output):
    """Write adapter_config.json and adapter_model.safetensors to a new directory."""
    from safetensors.torch import save_file
    if not isinstance(payload, dict) or payload.get('schema_version') != 1 or 'adapter' not in payload:
        raise ValueError('Schema-1 training checkpoint payload required')
    tensors = adapter_tensors(payload['adapter'], target_shapes)
    output.mkdir(parents=True, exist_ok=False)
    lora_config(target_shapes).save_pretrained(str(output))
    save_file(tensors, str(output / 'adapter_model.safetensors'), metadata={'format': 'pt'})
    return {'tensors': len(tensors), 'parameters': sum(value.numel() for value in tensors.values())}
