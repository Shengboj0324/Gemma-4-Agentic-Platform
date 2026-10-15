"""Interpret a deliberately small, auditable pytest version-condition language.

This is not Python execution. It supports direct django.VERSION comparisons
against integer tuples in top-level pytest.mark.skipif decorators. Callers must
bind the source bytes, module path and actual runtime version independently.
"""
import ast


def _version(value):
    if (not isinstance(value, tuple) or not 2 <= len(value) <= 3
            or any(type(x) is not int or x < 0 for x in value)):
        raise ValueError('Two or three nonnegative integer version components required')
    return value


def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _name(node.value) + '.' + node.attr
    return ''


def _condition(node, version):
    if (not isinstance(node, ast.Compare) or len(node.ops) != 1
            or len(node.comparators) != 1 or _name(node.left) != 'django.VERSION'
            or not isinstance(node.comparators[0], ast.Tuple)):
        raise ValueError('Only direct Django version tuple comparisons are supported')
    elements = node.comparators[0].elts
    if any(not isinstance(n, ast.Constant) for n in elements):
        raise ValueError('Literal version tuple required')
    bound = _version(tuple(n.value for n in elements))
    operations = {ast.Lt: lambda: version < bound, ast.LtE: lambda: version <= bound,
                  ast.Gt: lambda: version > bound, ast.GtE: lambda: version >= bound,
                  ast.Eq: lambda: version == bound, ast.NotEq: lambda: version != bound}
    if type(node.ops[0]) not in operations:
        raise ValueError('Unsupported comparison operator')
    return operations[type(node.ops[0])]()


def applicable_nodes(source, *, module_path, collected, version):
    """Return active nodes after interpreting every decorator in one test module.

    Reject aliases, assignments and extra top-level statements so source cannot
    silently redefine pytest or django.VERSION. Only direct imports and plain
    test functions are accepted. Test bodies are never executed by this parser;
    runtime phase verification must still reject dynamic skips or setup errors.
    Other modules' applicability is outside this function's scope.
    """
    if (not isinstance(version, tuple) or len(version) != 5
            or any(type(x) is not int or x < 0 for x in (*version[:3], version[4]))
            or version[3] not in ('alpha', 'beta', 'rc', 'final')):
        raise ValueError('Exact five-component Django VERSION required')
    if (not isinstance(source, str) or len(source.encode('utf-8')) > 1024 * 1024
            or not isinstance(module_path, str) or not module_path.endswith('.py')
            or module_path.startswith('/') or any(p in ('', '.', '..') for p in module_path.split('/'))
            or '::' in module_path or '\x00' in module_path
            or not isinstance(collected, list) or not collected
            or any(not isinstance(n, str) or not n for n in collected)
            or len(collected) != len(set(collected))):
        raise ValueError('Bound source path and unique collected nodes required')
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError('Invalid test module syntax') from error
    imported = set()
    tests = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname or alias.name not in ('django', 'pytest', 'rest_framework_api_key'):
                    raise ValueError('Only reviewed direct imports are supported')
                if alias.name in imported:
                    raise ValueError('Duplicate import')
                imported.add(alias.name)
        elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            if node.name in tests:
                raise ValueError('Duplicate test name')
            if (node.args.defaults or node.args.kw_defaults or node.returns
                    or node.args.vararg or node.args.kwarg or getattr(node, 'type_params', [])):
                raise ValueError('Executable defaults or annotations unsupported')
            if any(a.annotation for a in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)):
                raise ValueError('Argument annotations unsupported')
            if len(node.decorator_list) > 1:
                raise ValueError('Multiple decorators unsupported')
            excluded = False
            if node.decorator_list:
                marker = node.decorator_list[0]
                if (not isinstance(marker, ast.Call) or _name(marker.func) != 'pytest.mark.skipif'
                        or len(marker.args) != 1 or len(marker.keywords) != 1
                        or marker.keywords[0].arg != 'reason'
                        or not isinstance(marker.keywords[0].value, ast.Constant)
                        or not isinstance(marker.keywords[0].value.value, str)
                        or not {'django', 'pytest'} <= imported):
                    raise ValueError('Direct skipif with a literal reason required')
                excluded = _condition(marker.args[0], version)
            tests[module_path + '::' + node.name] = excluded
        else:
            raise ValueError('Unsupported top-level test-module statement')
    observed = {n for n in collected if n.startswith(module_path + '::')}
    if not tests or observed != set(tests):
        raise ValueError('Source tests and collected module nodes differ')
    return [n for n in collected if not tests.get(n, False)]
