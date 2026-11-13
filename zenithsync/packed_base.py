"""Train LoRA over the W4A16 checkpoint without decompressing it.

The competition ships Gemma 4 31B as compressed-tensors ``pack-quantized``:
symmetric int4, group size 32, eight values per int32. Loading it with
``run_compressed=False`` reconstructs every projection as dense bf16 and keeps
it resident — 60.88 GiB of weights on an 80 GiB card before one activation,
which is what the first GPU session measured.

Here the 410 quantized projections stay packed on the device. Each use rebuilds
one projection's bf16 weight, runs the matmul and drops it again; backward
rebuilds it once more instead of keeping it. The dense weight is never stored,
never trained, and never outlives the call that needed it.

Numerics are the decompressed path's numerics, not an approximation of them.
``dequantize_packed`` reproduces compressed-tensors' own
``unpack_from_int32`` + ``dequantize`` bit for bit (tested against the library),
and the matmul is the same ``F.linear`` the dense module would run. Only memory
residency changes.

PEFT compatibility. PEFT's LoRA dispatch accepts ``torch.nn.Linear`` and reads
``in_features``/``out_features``, so ``PackedW4Linear`` subclasses it without
running ``nn.Linear.__init__`` (that would allocate the dense weight this module
exists to avoid). ``weight`` is ``None``; ``qweight`` names the packed tensor,
which is the attribute PEFT already consults for packed-integer layers to place
new adapters on the base layer's device.
"""

GROUP_SIZE = 32
NUM_BITS = 4
PACK_FACTOR = 32 // NUM_BITS
_OFFSET = 1 << (NUM_BITS - 1)
_MASK = (1 << NUM_BITS) - 1


def dequantize_packed(packed, scale, rows, columns):
    """Rebuild one projection's weight exactly as compressed-tensors would.

    ``packed`` is int32 ``[rows, ceil(columns/8)]`` whose column ``g`` holds
    source columns ``8g .. 8g+7`` in ascending nibbles, each stored with a +8
    offset. ``scale`` is ``[rows, columns/32]`` in the compute dtype. Integers
    in [-8, 7] and their products with a bf16 scale are exact in float32, so the
    single final rounding matches the library's however it orders the cast.
    """
    import torch
    if packed.dtype != torch.int32 or packed.ndim != 2:
        raise ValueError('Packed weight must be a 2-D int32 tensor')
    if columns % GROUP_SIZE or packed.shape != (rows, -(-columns // PACK_FACTOR)):
        raise ValueError('Packed weight shape differs from the declared projection')
    if scale.shape != (rows, columns // GROUP_SIZE) or not scale.dtype.is_floating_point:
        raise ValueError('Group scale shape differs from the declared projection')
    shifts = torch.arange(0, 32, NUM_BITS, dtype=torch.int32, device=packed.device)
    values = torch.bitwise_right_shift(packed.unsqueeze(-1), shifts).bitwise_and_(_MASK)
    values = values.reshape(rows, -1)[:, :columns].to(scale.dtype).sub_(_OFFSET)
    return (values.view(rows, -1, GROUP_SIZE) * scale.unsqueeze(-1)).reshape(rows, columns)


def _packed_linear_function():
    import torch

    class PackedLinearFunction(torch.autograd.Function):
        """y = x Wᵀ with W rebuilt from int4 on demand; nothing dense is saved."""

        @staticmethod
        def forward(ctx, inputs, packed, scale, rows, columns):
            weight = dequantize_packed(packed, scale, rows, columns)
            if inputs.dtype != weight.dtype:
                raise ValueError('Activation dtype differs from the base compute dtype')
            ctx.save_for_backward(packed, scale)
            ctx.shape = (rows, columns)
            return torch.nn.functional.linear(inputs, weight)

        @staticmethod
        def backward(ctx, grad_output):
            if not ctx.needs_input_grad[0]:
                return None, None, None, None, None
            packed, scale = ctx.saved_tensors
            weight = dequantize_packed(packed, scale, *ctx.shape)
            return grad_output.matmul(weight), None, None, None, None

    return PackedLinearFunction


def _packed_class():
    import torch

    class PackedW4Linear(torch.nn.Linear):
        """Frozen int4 group-32 projection; dequantized per call, never stored dense."""

        def __init__(self, weight_packed, weight_scale, weight_shape):
            torch.nn.Module.__init__(self)
            shape = [int(value) for value in weight_shape.tolist()]
            if len(shape) != 2 or min(shape) <= 0:
                raise ValueError('Invalid stored weight shape')
            rows, columns = shape
            if weight_packed.dtype != torch.int32 or tuple(weight_packed.shape) != (rows, -(-columns // PACK_FACTOR)):
                raise ValueError('Packed weight shape differs from stored shape')
            if columns % GROUP_SIZE or tuple(weight_scale.shape) != (rows, columns // GROUP_SIZE):
                raise ValueError('Group-32 scale shape differs from stored shape')
            if weight_scale.dtype != torch.bfloat16:
                raise ValueError('bf16 group scales required')
            self.in_features, self.out_features = columns, rows
            self.weight = None
            self.bias = None
            self.compute_dtype = weight_scale.dtype
            for name, value in [('weight_packed', weight_packed), ('weight_scale', weight_scale),
                                ('weight_shape', weight_shape)]:
                parameter = value if isinstance(value, torch.nn.Parameter) else torch.nn.Parameter(value, requires_grad=False)
                parameter.requires_grad_(False)
                self.register_parameter(name, parameter)

        @property
        def qweight(self):
            return self.weight_packed

        def dense_weight(self):
            """Diagnostic only: allocates the full bf16 weight."""
            return dequantize_packed(self.weight_packed, self.weight_scale,
                                     self.out_features, self.in_features)

        def forward(self, inputs):
            return packed_linear_function().apply(inputs, self.weight_packed, self.weight_scale,
                                                  self.out_features, self.in_features)

        def extra_repr(self):
            return f'in_features={self.in_features}, out_features={self.out_features}, bits=4, group_size=32'

    return PackedW4Linear


_CACHE = {}


def packed_linear_function():
    if 'function' not in _CACHE:
        _CACHE['function'] = _packed_linear_function()
    return _CACHE['function']


def packed_linear_class():
    if 'class' not in _CACHE:
        _CACHE['class'] = _packed_class()
    return _CACHE['class']


def pack_quantized_projections(model, target_shapes):
    """Replace exactly the expected compressed projections with packed modules.

    Requires every module that carries ``weight_packed`` to be an expected target
    and every target to carry one, so a partial load or an unexpected quantized
    layer fails here rather than training silently over a mixed base.
    """
    import torch
    packed_class = packed_linear_class()
    modules = dict(model.named_modules())
    carriers = {name for name, module in modules.items()
                if 'weight_packed' in getattr(module, '_parameters', {})}
    if carriers != set(target_shapes):
        missing, extra = sorted(set(target_shapes) - carriers), sorted(carriers - set(target_shapes))
        raise ValueError(f'Packed projection coverage differs: missing={missing[:3]} extra={extra[:3]}')
    for name, shape in sorted(target_shapes.items()):
        module = modules[name]
        if type(module) is not torch.nn.Linear or getattr(module, 'bias', None) is not None:
            raise ValueError('Unexpected compressed module type or bias: ' + name)
        present = {key for key, value in module._parameters.items() if value is not None}
        if present != {'weight_packed', 'weight_scale', 'weight_shape'} or module._buffers:
            raise ValueError('Compressed module carries unexpected state: ' + name)
        replacement = packed_class(module.weight_packed, module.weight_scale, module.weight_shape)
        if [replacement.out_features, replacement.in_features] != list(shape):
            raise ValueError('Packed projection shape differs from configuration: ' + name)
        parent_name, _, child = name.rpartition('.')
        setattr(modules[parent_name] if parent_name else model, child, replacement)
    for name, parameter in model.named_parameters():
        parameter.requires_grad_(False)
    return model


def require_projection_targets(model, target_shapes):
    """Each target must be a dense Linear or a PackedW4Linear of the exact shape."""
    import torch
    packed_class = packed_linear_class()
    modules = dict(model.named_modules())
    kinds = set()
    for name, shape in target_shapes.items():
        module = modules.get(name)
        if isinstance(module, packed_class):
            actual, kind = [module.out_features, module.in_features], 'packed'
        elif type(module) is torch.nn.Linear and module.weight is not None:
            actual, kind = list(module.weight.shape), 'dense'
        else:
            raise ValueError('Target is absent or has unexpected shape: ' + name)
        if actual != list(shape):
            raise ValueError('Target is absent or has unexpected shape: ' + name)
        kinds.add(kind)
    if len(kinds) != 1:
        raise ValueError('Mixed dense and packed projection targets rejected')
    return kinds.pop()


ATTENTION_IMPLEMENTATION = 'sdpa'


def restrict_attention_kernels():
    """Forbid SDPA's math fallback, which materialises [batch, heads, seq, seq].

    With math disabled, an input no fused kernel accepts raises instead of
    quietly allocating the quadratic score tensor the first session OOMed on.
    cuDNN attention is disabled too, so the choice is between the flash and
    memory-efficient kernels only. Returns the flags actually in force.
    """
    import torch
    backends = torch.backends.cuda
    backends.enable_math_sdp(False)
    backends.enable_cudnn_sdp(False)
    backends.enable_flash_sdp(True)
    backends.enable_mem_efficient_sdp(True)
    flags = {'math': backends.math_sdp_enabled(), 'cudnn': backends.cudnn_sdp_enabled(),
             'flash': backends.flash_sdp_enabled(), 'mem_efficient': backends.mem_efficient_sdp_enabled()}
    if flags != {'math': False, 'cudnn': False, 'flash': True, 'mem_efficient': True}:
        raise ValueError('Attention kernel restriction did not take effect')
    return flags


def load_packed_base(model_class, model_dir, target_shapes, *, device):
    """Load the compressed checkpoint packed, swap in PackedW4Linear, verify."""
    import torch
    from transformers import CompressedTensorsConfig
    base = model_class.from_pretrained(model_dir, local_files_only=True, trust_remote_code=False,
        dtype=torch.bfloat16, quantization_config=CompressedTensorsConfig(run_compressed=True),
        attn_implementation=ATTENTION_IMPLEMENTATION, device_map={'': device})
    pack_quantized_projections(base, target_shapes)
    if base.config._attn_implementation != ATTENTION_IMPLEMENTATION:
        raise ValueError('Attention implementation differs from the requested kernel')
    if any(value.device.type != torch.device(device).type for value in base.parameters()):
        raise ValueError('CPU/meta/offloaded model parameter rejected')
    if any(value.requires_grad for value in base.parameters()):
        raise ValueError('Base parameter left trainable')
    packed_class = packed_linear_class()
    for name, module in base.named_modules():
        if type(module) is torch.nn.Linear and module.weight is None:
            raise ValueError('Linear without a weight left after packing: ' + name)
    if sum(isinstance(module, packed_class) for module in base.modules()) != len(target_shapes):
        raise ValueError('Packed module count differs from target coverage')
    return base
