/* Loopback-only egress guard, loaded into every process via /etc/ld.so.preload.

   For hosts where a network namespace cannot be created (a container whose
   seccomp profile refuses unshare). Wraps the libc calls that name a peer:
   connect, sendto, sendmsg, sendmmsg; and socket, to refuse raw and packet
   sockets. Any peer other than 127.0.0.1, ::1 or ::ffff:127.0.0.1 fails with
   ENETUNREACH — not all of 127/8, because container runtimes put a forwarding
   DNS resolver on loopback (Docker: 127.0.0.11). Unix and netlink sockets are
   local and pass. glibc's resolver connects through an internal symbol this
   cannot see, so the installer also points resolv.conf at a dead loopback
   address. Not covered: statically linked binaries and raw syscalls. */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <dlfcn.h>
#include <errno.h>
#include <netinet/in.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/socket.h>

static int peer_allowed(const struct sockaddr *addr, socklen_t len) {
    if (addr == NULL) return 1;
    if (len < (socklen_t)sizeof(sa_family_t)) return 0;
    switch (addr->sa_family) {
    case AF_UNIX:
    case AF_NETLINK:
    case AF_UNSPEC:
        return 1;
    case AF_INET: {
        if (len < (socklen_t)sizeof(struct sockaddr_in)) return 0;
        const struct sockaddr_in *in = (const struct sockaddr_in *)addr;
        return ntohl(in->sin_addr.s_addr) == INADDR_LOOPBACK;
    }
    case AF_INET6: {
        if (len < (socklen_t)sizeof(struct sockaddr_in6)) return 0;
        const struct sockaddr_in6 *in6 = (const struct sockaddr_in6 *)addr;
        if (IN6_IS_ADDR_LOOPBACK(&in6->sin6_addr)) return 1;
        if (IN6_IS_ADDR_V4MAPPED(&in6->sin6_addr)) {
            const uint8_t *b = in6->sin6_addr.s6_addr;
            return b[12] == 127 && b[13] == 0 && b[14] == 0 && b[15] == 1;
        }
        return 0;
    }
    default:
        return 0;
    }
}

typedef int (*socket_fn)(int, int, int);
typedef int (*connect_fn)(int, const struct sockaddr *, socklen_t);
typedef ssize_t (*sendto_fn)(int, const void *, size_t, int, const struct sockaddr *, socklen_t);
typedef ssize_t (*sendmsg_fn)(int, const struct msghdr *, int);
typedef int (*sendmmsg_fn)(int, struct mmsghdr *, unsigned int, int);

#define REAL(name) \
    static name##_fn real_##name; \
    if (!real_##name) real_##name = (name##_fn)dlsym(RTLD_NEXT, #name)

#define REFUSE() do { errno = ENETUNREACH; return -1; } while (0)

int socket(int domain, int type, int protocol) {
    REAL(socket);
    int base = type & 0xf;
    if (domain == AF_PACKET || ((domain == AF_INET || domain == AF_INET6) && base == SOCK_RAW)) {
        errno = EACCES;
        return -1;
    }
    return real_socket(domain, type, protocol);
}

int connect(int fd, const struct sockaddr *addr, socklen_t len) {
    REAL(connect);
    if (!peer_allowed(addr, len)) REFUSE();
    return real_connect(fd, addr, len);
}

ssize_t sendto(int fd, const void *buf, size_t n, int flags, const struct sockaddr *addr, socklen_t len) {
    REAL(sendto);
    if (!peer_allowed(addr, len)) REFUSE();
    return real_sendto(fd, buf, n, flags, addr, len);
}

ssize_t sendmsg(int fd, const struct msghdr *msg, int flags) {
    REAL(sendmsg);
    if (msg && !peer_allowed((const struct sockaddr *)msg->msg_name, msg->msg_namelen)) REFUSE();
    return real_sendmsg(fd, msg, flags);
}

int sendmmsg(int fd, struct mmsghdr *vec, unsigned int count, int flags) {
    REAL(sendmmsg);
    for (unsigned int i = 0; vec && i < count; i++)
        if (!peer_allowed((const struct sockaddr *)vec[i].msg_hdr.msg_name, vec[i].msg_hdr.msg_namelen))
            REFUSE();
    return real_sendmmsg(fd, vec, count, flags);
}
