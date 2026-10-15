"""Exact descriptor coverage for the supported dense Gemma4 W4 checkpoint."""
from .quantized_layout import validate_projection


def validate_architecture(header, expected_shapes, projections, original_shapes):
    """Compare all descriptors to a pinned meta-model and independent W4 rules.

    Unquantized tensors are BF16 for this specific package. This does not
    inspect their values or establish model numerical equivalence.
    """
    if not expected_shapes or not projections:
        raise ValueError('Nonempty architecture and quantized projections required')
    if set(original_shapes) != set(projections):
        raise ValueError('Original projection shape coverage mismatch')
    descriptors = [value for key, value in header.items() if key != '__metadata__']
    if any(not isinstance(value, dict) or not {'shape', 'dtype'} <= value.keys() for value in descriptors):
        raise ValueError('Invalid tensor descriptor')
    for shape in [*expected_shapes.values(), *(value['shape'] for value in descriptors)]:
        if not isinstance(shape, list) or any(type(dim) is not int or dim < 0 for dim in shape):
            raise ValueError('Tensor dimensions must be nonnegative integers')
    expected = dict(expected_shapes)
    packed_names = set()
    for name, shape in projections.items():
        if expected.pop(name + '.weight', None) != list(shape):
            raise ValueError('Meta-model and independent projection shape disagree')
        packed_names.update(name + suffix for suffix in ('.weight_shape', '.weight_packed', '.weight_scale'))
    actual = {name: descriptor for name, descriptor in header.items() if name != '__metadata__'}
    if set(actual) != set(expected) | packed_names:
        raise ValueError('Checkpoint tensor name coverage mismatch')
    for name, shape in expected.items():
        if actual[name]['shape'] != shape or actual[name]['dtype'] != 'BF16':
            raise ValueError('Unquantized tensor shape or dtype mismatch: ' + name)
    for name, shape in projections.items():
        descriptor = actual[name + '.weight_shape']
        if descriptor['dtype'] != 'I64' or descriptor['shape'] != [2]:
            raise ValueError('Original shape descriptor mismatch: ' + name)
        validate_projection(name, original_shapes[name], actual[name + '.weight_packed'],
                            actual[name + '.weight_scale'], shape)
    return {'quantized_projections': len(projections), 'unquantized_tensors': len(expected),
            'checkpoint_tensors': len(actual), 'logical_model_tensors': len(expected_shapes)}
