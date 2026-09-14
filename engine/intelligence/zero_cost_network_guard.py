"""Process-local network isolation for Phase 18 $0-local execution.

The guard is deliberately stdlib-only so it can be installed from ``sitecustomize``
before third-party model libraries import. It denies outbound IPv4/IPv6 sockets
except loopback while preserving AF_UNIX/local IPC. This complements, rather than
replaces, Hugging Face/Transformers offline flags.
"""
from __future__ import annotations

import ipaddress
import os
import socket
from typing import Any

_ACTIVE_ENV = "PUL7SAR_PHASE18_NETWORK_GUARD_ACTIVE"
_REQUIRED_COST_MODE = "$0-local"
_INSTALLED = False
_ORIGINAL_CONNECT = socket.socket.connect
_ORIGINAL_CONNECT_EX = socket.socket.connect_ex
_ORIGINAL_CREATE_CONNECTION = socket.create_connection
_ORIGINAL_GETADDRINFO = socket.getaddrinfo


def contract_requests_guard(env: dict[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return (
        values.get("PUL7SAR_PHASE18_COST_MODE") == _REQUIRED_COST_MODE
        and values.get("HF_HUB_OFFLINE") == "1"
        and values.get("TRANSFORMERS_OFFLINE") == "1"
    )


def _host_is_loopback(host: object) -> bool:
    if host is None:
        return True
    if isinstance(host, bytes):
        try:
            host = host.decode("ascii")
        except UnicodeDecodeError:
            return False
    if not isinstance(host, str):
        return False
    normalized = host.strip().strip("[]")
    if normalized.lower() in {"localhost", "localhost.localdomain"}:
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def _address_is_local(address: object, family: int | None = None) -> bool:
    if family == socket.AF_UNIX:
        return True
    if isinstance(address, str):
        return family == socket.AF_UNIX
    if isinstance(address, tuple) and address:
        return _host_is_loopback(address[0])
    return False


def _blocked(destination: object) -> PermissionError:
    return PermissionError(
        "PUL7SAR_PHASE18_ZERO_COST_NETWORK_BLOCKED: external network access is forbidden during $0-local execution"
    )


def install_zero_cost_network_guard() -> bool:
    """Install the guard once when the strict Phase 18 offline contract is active."""
    global _INSTALLED
    if _INSTALLED:
        return True
    if not contract_requests_guard():
        return False

    def guarded_connect(sock: socket.socket, address: Any) -> Any:
        if not _address_is_local(address, getattr(sock, "family", None)):
            raise _blocked(address)
        return _ORIGINAL_CONNECT(sock, address)

    def guarded_connect_ex(sock: socket.socket, address: Any) -> int:
        if not _address_is_local(address, getattr(sock, "family", None)):
            raise _blocked(address)
        return _ORIGINAL_CONNECT_EX(sock, address)

    def guarded_create_connection(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        if not _address_is_local(address):
            raise _blocked(address)
        return _ORIGINAL_CREATE_CONNECTION(address, *args, **kwargs)

    def guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
        if not _host_is_loopback(host):
            raise _blocked(host)
        return _ORIGINAL_GETADDRINFO(host, *args, **kwargs)

    socket.socket.connect = guarded_connect  # type: ignore[assignment]
    socket.socket.connect_ex = guarded_connect_ex  # type: ignore[assignment]
    socket.create_connection = guarded_create_connection  # type: ignore[assignment]
    socket.getaddrinfo = guarded_getaddrinfo  # type: ignore[assignment]
    os.environ[_ACTIVE_ENV] = "1"
    _INSTALLED = True
    return True


def guard_active() -> bool:
    return _INSTALLED and os.environ.get(_ACTIVE_ENV) == "1"
