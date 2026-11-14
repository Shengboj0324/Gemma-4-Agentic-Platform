/* Loopback-only egress guard, loaded into every process via /etc/ld.so.preload.

   For hosts where a network namespace cannot be created (a container whose
   seccomp profile refuses unshare). Wraps the libc calls that name a peer:
   connect, sendto, sendmsg, sendmmsg; and socket, to refuse raw and packet
   sockets. Any IPv4 peer outside 127/8 and any IPv6 peer other than ::1 or a
   v4-mapped 127/8 address fails with ENETUNREACH. Unix and netlink sockets are
   local and pass. glibc's resolver connects through an internal symbol this
   cannot see, so the installer also points resolv.conf at a dead loopback
   address. Not covered: statically linked binaries and raw syscalls. */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <dlfcn.h>
#include <errno.h>
#include <netinet/in.h>
#include <stddef.h>
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
        return (ntohl(in->sin_addr.s_addr) >> 24) == 127;
    }
    case AF_INET6: {
        if (len < (socklen_t)sizeof(struct sockaddr_in6)) return 0;
        const struct sockaddr_in6 *in6 = (const struct sockaddr_in6 *)addr;
        if (IN6_IS_ADDR_LOOPBACK(&in6->sin6_addr)) return 1;
        if (IN6_IS_ADDR_V4MAPPED(&in6->sin6_addr)) return in6->sin6_addr.s6_addr[12] == 127;
        return 0;
    }
    default:
        return 0;
    }
}

#define REAL(name, type) \
    static type real_##name; \
    if (!real_##name) real_##name = (type)dlsym(RTLD_NEXT, #name)

#define REFUSE() do { errno = ENETUNREACH; return -1; } while (0)

int socket(int domain, int type, int protocol) {
    REAL(socket, int (*)(int, int, int));
    int base = type & 0xf;
    if (domain == AF_PACKET || ((domain == AF_INET || domain == AF_INET6) && base == SOCK_RAW)) {
        errno = EACCES;
        return -1;
    }
    return real_socket(domain, type, protocol);
}

int connect(int fd, const struct sockaddr *addr, socklen_t len) {
    REAL(connect, int (*)(int, const struct sockaddr *, socklen_t));
    if (!peer_allowed(addr, len)) REFUSE();
    return real_connect(fd, addr, len);
}

ssize_t sendto(int fd, const void *buf, size_t n, int flags, const struct sockaddr *addr, socklen_t len) {
    REAL(sendto, ssize_t (*)(int, const void *, size_t, int, const struct sockaddr *, socklen_t));
    if (!peer_allowed(addr, len)) REFUSE();
    return real_sendto(fd, buf, n, flags, addr, len);
}

ssize_t sendmsg(int fd, const struct msghdr *msg, int flags) {
    REAL(sendmsg, ssize_t (*)(int, const struct msghdr *, int));
    if (msg && !peer_allowed((const struct sockaddr *)msg->msg_name, msg->msg_namelen)) REFUSE();
    return real_sendmsg(fd, msg, flags);
}

int sendmmsg(int fd, struct mmsghdr *vec, unsigned int count, int flags) {
    REAL(sendmmsg, int (*)(int, struct mmsghdr *, unsigned int, int));
    for (unsigned int i = 0; vec && i < count; i++)
        if (!peer_allowed((const struct sockaddr *)vec[i].msg_hdr.msg_name, vec[i].msg_hdr.msg_namelen))
            REFUSE();
    return real_sendmmsg(fd, vec, count, flags);
}
