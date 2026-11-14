"""Air-gap a process tree the way the official runtime is air-gapped.

The competition runs every sandbox with networking disabled. The subprocess
sandbox used on a GPU pod (no Docker daemon) cannot do that itself, and it
strips proxy variables from commands, so an environment-variable block would be
silently ignored. Instead the whole evaluation — inference server included —
runs in a fresh network namespace holding only loopback: `unshare -rn` gives an
unprivileged user namespace with its own network namespace, and loopback is
brought up with one ioctl. Nothing in that tree can reach the internet,
including the upstream repository that holds each task's fix.

Some hosts refuse unshare outright (a container under a seccomp profile without
CAP_SYS_ADMIN, as on Runpod). There the `egress-guard` mode is used instead: a
small library in /etc/ld.so.preload — read by the dynamic loader for every
process, whatever its environment — refuses any non-loopback peer, and the
resolver is pointed at a dead loopback address. It is installed by root before
the run (scripts/egress_guard.py) and checked, never installed, here: the
current process must have it mapped, and a fresh `env -i` process — Python and,
when present, curl — must fail to reach the internet. It is weaker than a
namespace (static binaries and raw syscalls pass); receipts say which mode ran.
"""
import errno
import fcntl
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys

MARKER = 'ZENITHSYNC_NETNS'
MODES = ('netns', 'egress-guard')
GUARD_SOURCE = Path(__file__).with_name('egress_guard.c')
GUARD_NAME = 'libzenithsync_egress_guard.so'
PRELOAD = Path('/etc/ld.so.preload')
RESOLV = Path('/etc/resolv.conf')
DEAD_RESOLVER = 'nameserver 127.0.0.9\noptions timeout:1 attempts:1\n'
SIOCGIFFLAGS = 0x8913
SIOCSIFFLAGS = 0x8914
IFF_UP = 0x1


def reexec_isolated(argv=None):
    """Replace this process with itself inside a new user+network namespace."""
    if os.environ.get(MARKER) == '1':
        return
    unshare = shutil.which('unshare')
    if unshare is None:
        raise RuntimeError('unshare(1) unavailable; cannot air-gap the evaluation')
    os.environ[MARKER] = '1'
    os.execv(unshare, [unshare, '--user', '--map-root-user', '--net', sys.executable,
                       *(sys.argv if argv is None else argv)])


def bring_loopback_up():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        request = struct.pack('16sH14s', b'lo', 0, b'\0' * 14)
        flags = struct.unpack('16sH14s', fcntl.ioctl(sock.fileno(), SIOCGIFFLAGS, request))[1]
        fcntl.ioctl(sock.fileno(), SIOCSIFFLAGS, struct.pack('16sH14s', b'lo', flags | IFF_UP, b'\0' * 14))


def probe_isolation(external=('1.1.1.1', 443), timeout=3.0):
    """Return evidence that loopback works and an external address does not."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        with socket.create_connection(server.getsockname(), timeout=timeout):
            pass
    try:
        with socket.create_connection(external, timeout=timeout):
            reachable = True
            error = None
    except OSError as exc:
        reachable = False
        error = errno.errorcode.get(exc.errno, type(exc).__name__) if exc.errno else type(exc).__name__
    try:
        socket.getaddrinfo('github.com', 443)
        dns = True
    except OSError:
        dns = False
    return {'loopback': True, 'external_reachable': reachable, 'external_error': error,
            'dns_resolves': dns, 'probe': f'{external[0]}:{external[1]}'}


def require_isolation():
    evidence = probe_isolation()
    if evidence['external_reachable'] or evidence['dns_resolves']:
        raise RuntimeError(f'Network is not isolated: {evidence}')
    return evidence


def build_guard(directory, cc='cc'):
    """Compile the guard library into `directory`; return its path."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    library = directory / GUARD_NAME
    subprocess.run([cc, '-shared', '-fPIC', '-O2', '-Wall', '-Werror', '-o', str(library),
                    str(GUARD_SOURCE), '-ldl'], check=True)
    return library


def install_guard(library, state, *, preload=PRELOAD, resolv=RESOLV):
    """Preload `library` system-wide and blackhole DNS; save what it replaced to `state`."""
    library, state, preload, resolv = (Path(p) for p in (library, state, preload, resolv))
    if state.exists():
        raise FileExistsError(f'{state}: guard already installed')
    saved = {'library': str(library.resolve()),
             'preload': preload.read_text() if preload.exists() else None,
             'resolv': resolv.read_text() if resolv.exists() else None}
    state.write_text(json.dumps(saved))
    preload.write_text((saved['preload'] or '') + saved['library'] + '\n')
    resolv.write_text(DEAD_RESOLVER)
    return saved


def remove_guard(state, *, preload=PRELOAD, resolv=RESOLV):
    """Restore exactly what install_guard replaced."""
    state, preload, resolv = Path(state), Path(preload), Path(resolv)
    saved = json.loads(state.read_text())
    for path, text in ((preload, saved['preload']), (resolv, saved['resolv'])):
        if text is None:
            path.unlink(missing_ok=True)
        else:
            path.write_text(text)
    state.unlink()
    return saved


def guard_loaded(maps=Path('/proc/self/maps')):
    try:
        return GUARD_NAME in Path(maps).read_text()
    except OSError:
        return False


PROBE = ('import json, sys; sys.path.insert(0, sys.argv[1]); '
         'from zenithsync.netns import probe_isolation, guard_loaded; '
         'print(json.dumps({**probe_isolation(), "guard_loaded": guard_loaded()}))')


def probe_fresh_process(run=subprocess.run):
    """Probe from new processes with an empty environment: Python, then curl if present."""
    root = str(Path(__file__).resolve().parents[1])
    python = run(['env', '-i', sys.executable, '-I', '-c', PROBE, root],
                 capture_output=True, text=True, timeout=60, check=True)
    evidence = {'python': json.loads(python.stdout)}
    curl = shutil.which('curl')
    if curl:
        result = run(['env', '-i', curl, '-sS', '--max-time', '5', '-o', '/dev/null', 'https://1.1.1.1'],
                     capture_output=True, text=True, timeout=60)
        evidence['curl'] = {'exit_code': result.returncode, 'stderr': result.stderr.strip()[:200]}
    return evidence


def require_guard():
    """Fail unless the egress guard is active here and in a fresh, environment-free process."""
    if not guard_loaded():
        raise RuntimeError('Egress guard is not loaded in this process; install it first')
    evidence = require_isolation()
    fresh = probe_fresh_process()
    python = fresh['python']
    if not python['guard_loaded'] or python['external_reachable'] or python['dns_resolves']:
        raise RuntimeError(f'Fresh process is not isolated: {fresh}')
    if 'curl' in fresh and fresh['curl']['exit_code'] == 0:
        raise RuntimeError(f'curl reached the internet: {fresh}')
    return {**evidence, 'fresh_process': fresh}


def isolate(mode):
    """Enter (netns) or verify (egress-guard) the air gap; return evidence naming the mode."""
    if mode == 'netns':
        reexec_isolated()
        bring_loopback_up()
        return {'mode': mode, **require_isolation()}
    if mode == 'egress-guard':
        return {'mode': mode, **require_guard()}
    raise ValueError(f'Unknown isolation mode {mode!r}; expected one of {MODES}')
