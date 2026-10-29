"""Check a training host against the worker's preconditions before GPU cost.

Run this on the pod as the first command, before staging weights or starting the
worker. It performs the same platform, pin, device and capacity checks the worker
enforces internally, and writes a receipt either way. A failing receipt is the
point: discovering a wrong Python or an unpinned Torch here costs nothing, and
discovering it inside the worker costs a billed pod.

Exit codes are distinguishable, so a calling script can tell what happened:
0 every check satisfied; 1 a check failed and a receipt was written; 2 bad
arguments; 3 the run itself failed and no receipt exists.

It allocates nothing on the device, loads no model and changes no state.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.runtime_preflight import (REQUIRED_FREE_DEVICE_BYTES,
                                          REQUIRED_PACKAGES, check_device_memory,
                                          check_packages, check_platform,
                                          check_sequence_capacity, device_report,
                                          summarise)

SOURCES = ['scripts/verify_training_runtime.py', 'zenithsync/runtime_preflight.py',
           'zenithsync/artifacts.py', 'zenithsync/contracts.py']

EXIT_SATISFIED = 0
EXIT_CHECKS_FAILED = 1
EXIT_BAD_ARGUMENTS = 2
EXIT_RUN_FAILED = 3


def installed_versions():
    """Report the version distribution metadata declares for each pinned name."""
    from importlib.metadata import PackageNotFoundError, version
    found = {}
    for name in REQUIRED_PACKAGES:
        try:
            found[name] = version(name)
        except PackageNotFoundError:
            found[name] = None
    return found


def imported_versions():
    """Report what each module says about itself, which metadata may contradict."""
    modules = {'torch': 'torch', 'transformers': 'transformers', 'peft': 'peft',
               'compressed-tensors': 'compressed_tensors'}
    reported = {}
    for name, module_name in modules.items():
        try:
            module = __import__(module_name)
        except Exception:
            reported[name] = None
            continue
        reported[name] = getattr(module, '__version__', None)
    return reported


def build_checks(args):
    """Run every requested check. Argument validation happens before this."""
    checks = {
        'platform': check_platform(platform.system(), sys.version_info[:2]),
        'packages': check_packages(installed_versions(),
                                   imported=imported_versions()),
    }
    device = None
    if not args.skip_device:
        device = device_report()
        if device['available']:
            memory = check_device_memory(
                device['free_bytes'], device['total_bytes'],
                required_free_bytes=args.required_free_bytes)
            if device.get('device_exclusive') is not True:
                if device.get('exclusivity_query_failed'):
                    memory['problems'].append(
                        'the exclusivity query the worker runs with check=True '
                        'failed here (' + device['exclusivity_query_failed']
                        + '), so the worker would abort on it')
                else:
                    memory['problems'].append(
                        'another GPU compute process is active: '
                        + ','.join(device.get('other_compute_processes') or ['unknown']))
                memory['satisfied'] = False
            checks['device_memory'] = memory
        else:
            checks['device'] = {
                'problems': ['no single usable CUDA device: ' + device['reason']
                             + (': ' + device['detail'] if device.get('detail') else '')],
                'satisfied': False, 'report': device}
    if args.longest_input_tokens is not None:
        config = load_json(args.worker_config)
        if 'max_sequence_tokens' not in config:
            raise ValueError('Worker config has no max_sequence_tokens')
        checks['sequence_capacity'] = check_sequence_capacity(
            args.longest_input_tokens, config['max_sequence_tokens'])
    return checks, device


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker-config', type=Path,
                        help='Worker config whose max_sequence_tokens to check')
    parser.add_argument('--longest-input-tokens', type=int,
                        help='Longest example in the corpus, from the corpus audit')
    parser.add_argument('--required-free-bytes', type=int,
                        default=REQUIRED_FREE_DEVICE_BYTES)
    parser.add_argument('--skip-device', action='store_true',
                        help='Check platform, pins and capacity only; no CUDA read. '
                             'The receipt records that the device was not examined '
                             'and the status says so.')
    args = parser.parse_args()
    # Validate every argument before creating the output directory, so a bad
    # invocation does not leave a directory that blocks the corrected retry.
    if (args.longest_input_tokens is None) != (args.worker_config is None):
        parser.error('--longest-input-tokens and --worker-config must be given together')
    if args.longest_input_tokens is not None and args.longest_input_tokens <= 0:
        parser.error('--longest-input-tokens must be a positive integer')
    if args.required_free_bytes < 0:
        parser.error('--required-free-bytes must be a nonnegative integer')
    if args.worker_config is not None and not args.worker_config.is_file():
        parser.error('--worker-config is not a readable file')
    if args.output.exists() or args.output.is_symlink():
        parser.error('--output already exists')

    sources = {name: file_record(ROOT / name) for name in SOURCES}
    config_identity = (None if args.worker_config is None
                       else file_record(args.worker_config))
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        checks, device = build_checks(args)
        verdict = summarise(checks, device_checked=not args.skip_device)
        if sources != {name: file_record(ROOT / name) for name in SOURCES}:
            raise RuntimeError('Implementation changed during verification')
        receipt = {**verdict,
                   'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                   'sources': sources, 'device_report': device,
                   'device_skipped': bool(args.skip_device),
                   'required_free_bytes_requested': args.required_free_bytes,
                   'interpreter': sys.executable,
                   'python_version': list(sys.version_info[:3]),
                   'worker_config': config_identity,
                   'longest_input_tokens': args.longest_input_tokens,
                   'training_started': False}
        (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    except BaseException:
        # No partial receipt, and no directory left to block the retry.
        shutil.rmtree(args.output, ignore_errors=True)
        raise
    print({'status': verdict['status'], 'satisfied': verdict['satisfied'],
           'device_checked': verdict['device_checked'],
           'failed_checks': verdict['failed_checks'],
           'problems': verdict['problems']})
    raise SystemExit(EXIT_SATISFIED if verdict['satisfied'] else EXIT_CHECKS_FAILED)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f'Runtime verification failed ({type(error).__name__}: {error}); '
              'no receipt written.', file=sys.stderr)
        raise SystemExit(EXIT_RUN_FAILED)
