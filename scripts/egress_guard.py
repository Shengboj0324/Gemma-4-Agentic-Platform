"""Install, remove or check the loopback-only egress guard (root, Linux).

For hosts that refuse network namespaces. `install` compiles
zenithsync/egress_guard.c into --dir, adds it to /etc/ld.so.preload and points
/etc/resolv.conf at a dead loopback resolver, saving what it replaced to
--state; `remove` restores exactly that; `check` runs the same verification the
evaluation scripts require (`netns.require_guard`) and prints the evidence.
Every process started after `install` is guarded, including this machine's
later downloads — remove the guard before fetching or uploading anything.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zenithsync import netns

STATE = Path('/root/.zenithsync-egress-guard.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'remove', 'check'))
    parser.add_argument('--dir', type=Path, default=Path('/root/egress-guard'))
    parser.add_argument('--state', type=Path, default=STATE)
    args = parser.parse_args()
    if args.action == 'install':
        library = netns.build_guard(args.dir)
        print(json.dumps({'installed': netns.install_guard(library, args.state)}))
    elif args.action == 'remove':
        print(json.dumps({'removed': netns.remove_guard(args.state)}))
    else:
        print(json.dumps(netns.require_guard()))


if __name__ == '__main__':
    main()
