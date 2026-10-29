"""Check a training host against the worker's preconditions before GPU cost.

Run this on the pod as the first command, before staging weights or starting the
worker. It performs the same platform, pin, device and capacity checks the worker
enforces internally, and writes a receipt either way. A failing receipt is the
point: discovering a wrong Python or an unpinned Torch here costs nothing, and
discovering it inside the worker costs a billed pod.

It allocates nothing on the device, loads no model and changes no state.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
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


def installed_versions():
    from importlib.metadata import PackageNotFoundError, version
    found = {}
    for name in REQUIRED_PACKAGES:
        try:
            found[name] = version(name)
        except PackageNotFoundError:
            found[name] = None
    return found


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
                        help='Check platform, pins and capacity only; no CUDA read')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sources = {name: file_record(ROOT / name) for name in SOURCES}

    checks = {
        'platform': check_platform(platform.system(), sys.version_info[:2]),
        'packages': check_packages(installed_versions()),
    }
    device = None
    if not args.skip_device:
        device = device_report()
        if device['available']:
            checks['device_memory'] = check_device_memory(
                device['free_bytes'], device['total_bytes'],
                required_free_bytes=args.required_free_bytes)
            if device.get('device_exclusive') is False:
                checks['device_memory']['problems'].append(
                    'another GPU compute process is active: '
                    + ','.join(device['other_compute_processes']))
                checks['device_memory']['satisfied'] = False
        else:
            checks['device'] = {
                'problems': ['no single usable CUDA device: ' + device['reason']],
                'satisfied': False, 'report': device}
    if args.longest_input_tokens is not None:
        if args.worker_config is None:
            parser.error('--longest-input-tokens also requires --worker-config')
        config = load_json(args.worker_config)
        checks['sequence_capacity'] = check_sequence_capacity(
            args.longest_input_tokens, config['max_sequence_tokens'])
    elif args.worker_config is not None:
        parser.error('--worker-config also requires --longest-input-tokens')

    verdict = summarise(checks)
    if sources != {name: file_record(ROOT / name) for name in SOURCES}:
        raise RuntimeError('Implementation changed during verification')
    receipt = {**verdict, 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'sources': sources, 'device_report': device,
               'interpreter': sys.executable,
               'worker_config': (None if args.worker_config is None
                                 else file_record(args.worker_config)),
               'training_started': False}
    (args.output / 'receipt.json').write_bytes(canonical_json(receipt))
    print({'status': verdict['status'], 'satisfied': verdict['satisfied'],
           'failed_checks': verdict['failed_checks'],
           'problems': verdict['problems']})
    raise SystemExit(0 if verdict['satisfied'] else 1)


if __name__ == '__main__':
    main()
