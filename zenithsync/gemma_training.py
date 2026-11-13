"""Exact-shape LoRA attachment for the full Gemma corpus worker.

Targets may be dense ``nn.Linear`` or ``PackedW4Linear`` (never a mix); the
adapter shapes, names and parameter count are identical either way.
"""
import re


def attach_training_adapter(base, target_shapes):
    from peft import LoraConfig, get_peft_model
    from .packed_base import require_projection_targets
    if not target_shapes:
        raise ValueError('Nonempty exact target shapes required')
    require_projection_targets(base, target_shapes)
    model = get_peft_model(base, LoraConfig(
        r=4, lora_alpha=8, lora_dropout=0.0, bias='none',
        target_modules='(?:' + '|'.join(re.escape(name) for name in sorted(target_shapes)) + ')'))
    parameters = [(name, value) for name, value in model.named_parameters() if value.requires_grad]
    expected = {f'base_model.model.{name}.lora_{side}.default.weight'
                for name in target_shapes for side in ('A', 'B')}
    if {name for name, _ in parameters} != expected:
        raise ValueError('Unexpected trainable adapter coverage')
    if sum(value.numel() for _, value in parameters) != 4 * sum(a+b for a, b in target_shapes.values()):
        raise ValueError('Adapter parameter count differs from projection accounting')
    if len({value.device for value in model.parameters()}) != 1:
        raise ValueError('Adapter and base parameters must share one device')
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    model.train()
    return model
