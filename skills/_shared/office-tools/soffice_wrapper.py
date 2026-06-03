#!/usr/bin/env python3
"""LibreOffice (soffice) wrapper for sandboxed environments.

Detects when AF_UNIX sockets are blocked (common in containers/VMs)
and applies an LD_PRELOAD shim that redirects AF_UNIX to socketpair().

Usage:
    python soffice_wrapper.py --headless --convert-to pdf document.docx
    python soffice_wrapper.py --headless --convert-to pdf presentation.pptx

Programmatic:
    from soffice_wrapper import run_soffice, get_soffice_env
    result = run_soffice(["--headless", "--convert-to", "pdf", "doc.docx"])
"""

import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

_SHIM_SO = Path(tempfile.gettempdir()) / "lo_socket_shim.so"

_SHIM_C = r"""
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>

static int (*real_socket)(int, int, int);
static int (*real_socketpair)(int, int, int, int[2]);
static int (*real_listen)(int, int);
static int (*real_accept)(int, struct sockaddr *, socklen_t *);
static int (*real_close)(int);
static int (*real_read)(int, void *, size_t);

static int is_shimmed[1024];
static int peer_of[1024];
static int wake_r[1024];
static int wake_w[1024];
static int listener_fd = -1;

__attribute__((constructor))
static void init(void) {
    real_socket     = dlsym(RTLD_NEXT, "socket");
    real_socketpair = dlsym(RTLD_NEXT, "socketpair");
    real_listen     = dlsym(RTLD_NEXT, "listen");
    real_accept     = dlsym(RTLD_NEXT, "accept");
    real_close      = dlsym(RTLD_NEXT, "close");
    real_read       = dlsym(RTLD_NEXT, "read");
    for (int i = 0; i < 1024; i++) {
        peer_of[i] = -1;
        wake_r[i]  = -1;
        wake_w[i]  = -1;
    }
}

int socket(int domain, int type, int protocol) {
    if (domain == AF_UNIX) {
        int fd = real_socket(domain, type, protocol);
        if (fd >= 0) return fd;
        int sv[2];
        if (real_socketpair(domain, type, protocol, sv) == 0) {
            if (sv[0] >= 0 && sv[0] < 1024) {
                is_shimmed[sv[0]] = 1;
                peer_of[sv[0]]    = sv[1];
                int wp[2];
                if (pipe(wp) == 0) {
                    wake_r[sv[0]] = wp[0];
                    wake_w[sv[0]] = wp[1];
                }
            }
            return sv[0];
        }
        errno = EPERM;
        return -1;
    }
    return real_socket(domain, type, protocol);
}

int listen(int sockfd, int backlog) {
    if (sockfd >= 0 && sockfd < 1024 && is_shimmed[sockfd]) {
        listener_fd = sockfd;
        return 0;
    }
    return real_listen(sockfd, backlog);
}

int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen) {
    if (sockfd >= 0 && sockfd < 1024 && is_shimmed[sockfd]) {
        if (wake_r[sockfd] >= 0) {
            char buf;
            real_read(wake_r[sockfd], &buf, 1);
        }
        errno = ECONNABORTED;
        return -1;
    }
    return real_accept(sockfd, addr, addrlen);
}

int close(int fd) {
    if (fd >= 0 && fd < 1024 && is_shimmed[fd]) {
        int was_listener = (fd == listener_fd);
        is_shimmed[fd] = 0;
        if (wake_w[fd] >= 0) { char c = 0; write(wake_w[fd], &c, 1); real_close(wake_w[fd]); wake_w[fd] = -1; }
        if (wake_r[fd] >= 0) { real_close(wake_r[fd]); wake_r[fd] = -1; }
        if (peer_of[fd] >= 0) { real_close(peer_of[fd]); peer_of[fd] = -1; }
        if (was_listener) _exit(0);
    }
    return real_close(fd);
}
"""


def _needs_shim() -> bool:
    """Check if AF_UNIX sockets are blocked."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.close()
        return False
    except OSError:
        return True


def _ensure_shim() -> Path:
    """Compile the LD_PRELOAD shim if needed."""
    if _SHIM_SO.exists():
        return _SHIM_SO
    src = Path(tempfile.gettempdir()) / "lo_socket_shim.c"
    src.write_text(_SHIM_C)
    subprocess.run(
        ["gcc", "-shared", "-fPIC", "-o", str(_SHIM_SO), str(src), "-ldl"],
        check=True, capture_output=True,
    )
    src.unlink()
    return _SHIM_SO


def get_soffice_env() -> dict:
    """Return env dict configured for LibreOffice in current environment."""
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "svp"
    if _needs_shim():
        env["LD_PRELOAD"] = str(_ensure_shim())
    return env


def run_soffice(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run soffice with proper environment setup."""
    return subprocess.run(["soffice"] + args, env=get_soffice_env(), **kwargs)


if __name__ == "__main__":
    result = run_soffice(sys.argv[1:])
    sys.exit(result.returncode)
