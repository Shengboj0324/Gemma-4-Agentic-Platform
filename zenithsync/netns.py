"""Air-gap a process tree the way the official runtime is air-gapped.

The competition runs every sandbox with networking disabled. The subprocess
sandbox used on a GPU pod (no Docker daemon) cannot do that itself, and it
strips proxy variables from commands, so an environment-variable block would be
silently ignored. Instead the whole evaluation — inference server included —
runs in a fresh network namespace holding only loopback: `unshare -rn` gives an
unprivileged user namespace with its own network namespace, and loopback is
brought up with one ioctl. Nothing in that tree can reach the internet,
including the upstream repository that holds each task's fix.
"""
import errno
import fcntl
import os
import shutil
import socket
import struct
import sys

MARKER = 'ZENITHSYNC_NETNS'
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
