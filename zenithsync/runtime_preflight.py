"""Check a training host against the worker's own preconditions, before GPU cost.

`scripts/run_corpus_training_worker.py` enforces an exact runtime: Linux, Python
3.12, four pinned package versions, one visible CUDA device with no other compute
process, and at least a declared quantity of free device memory. It enforces them
*after* a pod is already running and billing. Running the same checks first turns
a billed failure into a free one.

These functions are deliberately pure where they can be: the pin and platform
checks take their inputs as arguments so they are testable without a GPU, a
particular interpreter or a particular operating system. Only `device_report`
touches hardware.

Passing every check means the host satisfies the worker's declared preconditions.
It does not mean the run will fit: peak memory at a long sequence, throughput and
checkpoint durability are separate measurements this module cannot make.
"""

REQUIRED_PLATFORM = 'Linux'
REQUIRED_PYTHON = (3, 12)
# These are the exact pins `run_corpus_training_worker.py` enforces. A mismatch
# here is a mismatch there, so the two lists must not drift apart.
REQUIRED_PACKAGES = {'torch': '2.10.0', 'transformers': '5.13.1',
                     'compressed-tensors': '0.15.0.1', 'peft': '0.21.2'}
# The worker's own floor. Measured on the qualified fixture, not at full length.
REQUIRED_FREE_DEVICE_BYTES = 70 * 1024**3


def check_platform(system, python_version):
    """Compare a reported platform and interpreter version against the pins."""
    if not isinstance(system, str) or not system:
        raise ValueError('Platform system name required')
    version = tuple(python_version)[:2]
    if any(type(part) is not int for part in version) or len(version) != 2:
        raise ValueError('Python version must be a pair of integers')
    problems = []
    if system != REQUIRED_PLATFORM:
        problems.append(f'platform is {system}, worker requires {REQUIRED_PLATFORM}')
    if version != REQUIRED_PYTHON:
        problems.append('python is {}.{}, worker requires {}.{}'.format(
            *version, *REQUIRED_PYTHON))
    return {'system': system, 'python_version': list(version),
            'required_system': REQUIRED_PLATFORM,
            'required_python_version': list(REQUIRED_PYTHON),
            'problems': problems, 'satisfied': not problems}


def check_packages(installed, *, imported=None):
    """Compare installed versions against the pins, ignoring local build tags.

    `installed` maps distribution name to version string, with `None` for an
    absent distribution. A local version segment after `+` is stripped before
    comparison, matching what the worker does.

    `installed` comes from distribution metadata, which is not the same thing as
    the module that will actually import: a stale `*.dist-info` earlier on the
    path wins. `imported` optionally supplies the version a module reports about
    itself, and a disagreement is a problem rather than a silent mismatch. The
    worker reads the same metadata, so this does not create preflight drift — it
    reveals that the pin claim is about metadata, not about the running code.
    """
    if not isinstance(installed, dict):
        raise ValueError('Installed package mapping required')
    if imported is not None and not isinstance(imported, dict):
        raise ValueError('Imported version mapping must be a dict')
    rows, problems = [], []
    for name, pin in sorted(REQUIRED_PACKAGES.items()):
        found = installed.get(name)
        if found is None:
            problems.append(f'{name} is not installed, worker requires {pin}')
            rows.append({'name': name, 'required': pin, 'found': None,
                         'satisfied': False})
            continue
        if not isinstance(found, str) or not found.strip():
            raise ValueError('Package version must be a nonempty string: ' + name)
        base = found.split('+')[0]
        satisfied = base == pin
        if not satisfied:
            problems.append(f'{name} is {found}, worker requires {pin}')
        row = {'name': name, 'required': pin, 'found': found,
               'compared': base, 'satisfied': satisfied}
        if imported is not None and name in imported:
            reported = imported[name]
            row['imported'] = reported
            if reported is not None and str(reported).split('+')[0] != base:
                problems.append(f'{name} metadata says {found} but the imported '
                                f'module reports {reported}')
                row['satisfied'] = False
        rows.append(row)
    extra = sorted(set(installed) - set(REQUIRED_PACKAGES))
    return {'packages': rows, 'unpinned_packages_reported': extra,
            'problems': problems, 'satisfied': not problems}


def check_device_memory(free_bytes, total_bytes, *,
                        required_free_bytes=REQUIRED_FREE_DEVICE_BYTES):
    """Compare reported device memory against the worker's floor."""
    for name, value in (('free_bytes', free_bytes), ('total_bytes', total_bytes),
                        ('required_free_bytes', required_free_bytes)):
        if type(value) is not int or value < 0:
            raise ValueError(name + ' must be a nonnegative integer')
    if free_bytes > total_bytes:
        raise ValueError('Free device memory exceeds total device memory')
    problems = []
    if free_bytes < required_free_bytes:
        problems.append(
            f'{free_bytes} free bytes ({free_bytes / 1024**3:.2f} GiB), worker '
            f'requires {required_free_bytes} ({required_free_bytes / 1024**3:.2f} GiB)')
    return {'free_bytes': free_bytes, 'total_bytes': total_bytes,
            'free_gib': free_bytes / 1024**3, 'total_gib': total_bytes / 1024**3,
            'required_free_bytes': required_free_bytes,
            'headroom_bytes': free_bytes - required_free_bytes,
            'problems': problems, 'satisfied': not problems,
            'limitation': 'The floor was derived from a short-sequence fixture. It '
                          'does not establish that peak memory at the longest '
                          'corpus example fits this device.'}


def check_sequence_capacity(longest_input_tokens, max_sequence_tokens):
    """Reject a configuration that would need truncation to run the corpus."""
    for name, value in (('longest_input_tokens', longest_input_tokens),
                        ('max_sequence_tokens', max_sequence_tokens)):
        if type(value) is not int or value <= 0:
            raise ValueError(name + ' must be a positive integer')
    problems = []
    if longest_input_tokens > max_sequence_tokens:
        problems.append(f'longest example is {longest_input_tokens} tokens, configured '
                        f'capacity is {max_sequence_tokens}; truncation is forbidden')
    return {'longest_input_tokens': longest_input_tokens,
            'max_sequence_tokens': max_sequence_tokens,
            'slack_tokens': max_sequence_tokens - longest_input_tokens,
            'problems': problems, 'satisfied': not problems,
            'limitation': 'Capacity is a token-count check. Memory at that length '
                          'is a separate measurement.'}


def device_report():
    """Read the actual device state, returning a finding rather than raising.

    Every read here can fail on a real host — a driver mismatch, an ECC-disabled
    card, `CUDA error: unknown error` — and a check that raises produces no
    receipt at all, which is worse than a failing one. So all of them are
    guarded and reported.
    """
    import os
    import subprocess
    try:
        import torch
    except ImportError as error:
        return {'available': False, 'reason': 'torch_import_failed',
                'detail': str(error)}
    try:
        if not torch.cuda.is_available():
            return {'available': False, 'reason': 'cuda_unavailable'}
        count = torch.cuda.device_count()
        if count != 1:
            return {'available': False, 'reason': 'device_count_is_not_one',
                    'device_count': count}
        free, total = torch.cuda.mem_get_info()
        report = {'available': True, 'device_count': count,
                  'device_name': torch.cuda.get_device_name(0),
                  'capability': list(torch.cuda.get_device_capability(0)),
                  'free_bytes': int(free), 'total_bytes': int(total),
                  'torch_version': str(torch.__version__),
                  'torch_file': getattr(torch, '__file__', None)}
    except Exception as error:
        return {'available': False, 'reason': 'cuda_query_failed',
                'detail': f'{type(error).__name__}: {error}'}
    # The worker refuses to share a device, and it makes the same nvidia-smi
    # query with check=True. A query that cannot run is therefore a failure
    # here: the worker would die on it after the pod is already billing.
    report.update(exclusivity_query='nvidia-smi --query-compute-apps=pid')
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader,nounits'],
            check=True, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as error:
        report['other_compute_processes'] = None
        report['device_exclusive'] = False
        report['exclusivity_query_failed'] = type(error).__name__
        return report
    pids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    # Reading free memory above initialises CUDA and creates a context, so this
    # process appears in its own query. The worker excludes its own PID the same
    # way; counting it would fail a healthy exclusive host.
    own = str(os.getpid())
    foreign = [pid for pid in pids if pid != own]
    report['compute_processes'] = pids
    report['own_pid'] = own
    report['other_compute_processes'] = foreign
    report['device_exclusive'] = not foreign
    return report


def summarise(checks, *, device_checked=True):
    """Collapse named check results into one verdict with every problem kept.

    A check's own `satisfied` flag is honoured as well as its problem list, so a
    future check cannot pass by forgetting to describe why it failed.

    `device_checked=False` records that the device was not examined and gives the
    run its own status, so a host check that skipped the GPU can never be read
    as a full pass.
    """
    if not isinstance(checks, dict) or not checks:
        raise ValueError('Nonempty named check results required')
    if type(device_checked) is not bool:
        raise ValueError('device_checked must be boolean')
    problems = {}
    for name, result in checks.items():
        if not isinstance(result, dict) or 'problems' not in result:
            raise ValueError('Each check must report a problems list: ' + str(name))
        if result.get('satisfied') is False and not result['problems']:
            problems[name] = ['check reported unsatisfied without a stated problem']
        elif result['problems']:
            problems[name] = result['problems']
    if problems:
        status = 'runtime_preflight_failed'
    elif device_checked:
        status = 'runtime_preflight_passed'
    else:
        status = 'runtime_preflight_passed_without_device_checks'
    return {'schema_version': 1, 'status': status,
            'checks': checks, 'failed_checks': sorted(problems),
            'problems': problems, 'satisfied': not problems,
            'device_checked': device_checked,
            'required_free_device_bytes': REQUIRED_FREE_DEVICE_BYTES,
            'scope': "The worker's declared preconditions only. Not peak memory at "
                     'full sequence length, not throughput, not checkpoint '
                     'durability, and not a cost or duration estimate.'
                     + ('' if device_checked else
                        ' The device was not examined in this run.')}
