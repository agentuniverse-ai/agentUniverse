#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @FileName: network_diagnose_tool.py

"""A standard-library network diagnostic tool for agentUniverse agents.

The tool answers the three questions an agent usually needs when a host
looks unreachable:

* ``dns``:     which addresses and aliases a host name resolves to;
* ``reverse``: which PTR record an IP address resolves to;
* ``tls``:     which certificate a host serves and when it expires.

It deliberately avoids port scanning and arbitrary HTTP probing: ``tls``
always performs a normal TLS handshake against the given port, so the
work it does is the same as opening a browser connection.
"""

import ipaddress
import socket
import ssl
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.tool.tool import Tool

DEFAULT_TIMEOUT: float = 5.0
MAX_TIMEOUT: float = 30.0

MODE_DNS: str = "dns"
MODE_REVERSE: str = "reverse"
MODE_TLS: str = "tls"

VALID_MODES: Tuple[str, ...] = (MODE_DNS, MODE_REVERSE, MODE_TLS)


def _resolve_addresses(target: str) -> Tuple[List[str], List[str], List[str]]:
    """Resolve a host name into IPv4/IPv6 addresses and aliases.

    Args:
        target: The host name to resolve.

    Returns:
        A tuple of (ipv4 addresses, ipv6 addresses, aliases). Duplicated
        addresses are removed and the input name itself is not reported
        as an alias.
    """
    ipv4: List[str] = []
    ipv6: List[str] = []
    seen = set()
    for family, _, _, _, sockaddr in socket.getaddrinfo(target, None, proto=socket.IPPROTO_TCP):
        address = sockaddr[0]
        if address in seen:
            continue
        seen.add(address)
        if family == socket.AF_INET:
            ipv4.append(address)
        elif family == socket.AF_INET6:
            ipv6.append(address)

    aliases: List[str] = []
    try:
        _, alias_list, _ = socket.gethostbyname_ex(target)
        aliases = [alias for alias in alias_list if alias and alias.lower() != target.lower()]
    except socket.gaierror:
        # getaddrinfo already succeeded, so aliases are optional information.
        aliases = []
    return ipv4, ipv6, aliases


def _open_tls_socket(target: str, port: int, timeout: float) -> ssl.SSLSocket:
    """Open a verified TLS connection to ``target:port``.

    Args:
        target: The host name or IP address to connect to.
        port: The TCP port to connect to.
        timeout: The handshake timeout in seconds.

    Returns:
        The connected TLS socket.
    """
    context = ssl.create_default_context()
    return context.wrap_socket(
        socket.create_connection((target, port), timeout=timeout),
        server_hostname=target,
    )


def _format_cert_time(value: Optional[str]) -> Optional[str]:
    """Convert a certificate timestamp into an ISO 8601 UTC string."""
    if not value:
        return None
    seconds = ssl.cert_time_to_seconds(value)
    return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()


def _describe_certificate(cert: Dict[str, Any], sock: ssl.SSLSocket) -> Dict[str, Any]:
    """Build the TLS part of the answer from a peer certificate.

    Args:
        cert: The dictionary returned by ``SSLSocket.getpeercert()``.
        sock: The connected TLS socket, used for protocol and cipher details.

    Returns:
        A dictionary with the certificate subject, issuer, validity window
        and the number of days left before it expires.
    """
    not_after_seconds = ssl.cert_time_to_seconds(cert["notAfter"]) if cert.get("notAfter") else None
    remaining_days = None
    if not_after_seconds is not None:
        remaining_days = round((not_after_seconds - datetime.now(tz=timezone.utc).timestamp()) / 86400, 1)

    subject = {name: value for part in cert.get("subject", ()) for name, value in part}
    issuer = {name: value for part in cert.get("issuer", ()) for name, value in part}
    return {
        "subject": subject.get("commonName"),
        "issuer": issuer.get("commonName") or issuer.get("organizationName"),
        "not_before": _format_cert_time(cert.get("notBefore")),
        "not_after": _format_cert_time(cert.get("notAfter")),
        "days_remaining": remaining_days,
        "expired": remaining_days is not None and remaining_days < 0,
        "protocol": sock.version(),
        "cipher": sock.cipher()[0] if sock.cipher() else None,
        "subject_alt_names": [value for key, value in cert.get("subjectAltName", ()) if key == "DNS"],
    }


def _coerce_int(name: str, value: Any, default: int) -> int:
    """Accept an int, or a numeric string as produced by a JSON tool call."""
    if value is None:
        return default
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer, got: {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("+-").isdigit():
        return int(value.strip())
    raise ValueError(f"{name} must be an integer, got: {value!r}")


def _coerce_float(name: str, value: Any, default: float) -> float:
    """Accept a number, or a numeric string as produced by a JSON tool call."""
    if value is None:
        return default
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number, got: {value!r}")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            pass
    raise ValueError(f"{name} must be a number, got: {value!r}")


class NetworkDiagnoseTool(Tool):
    """Diagnose DNS, PTR and TLS problems for a host name or IP address.

    The tool never scans ports and never talks HTTP: every mode either asks
    the local resolver or performs one ordinary TLS handshake.
    """

    def execute(self, mode: str, target: str, port: int = 443,
                timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Run one diagnostic mode.

        Args:
            mode: One of ``dns``, ``reverse``, ``tls``.
            target: The host name to resolve, or the IP address to reverse
                lookup, or the host to inspect a certificate for.
            port: The TCP port used by the ``tls`` mode. Defaults to 443.
            timeout: The handshake timeout in seconds for the ``tls`` mode.
                Defaults to 5 seconds.

        Returns:
            A dictionary describing the result. Failures return an ``error``
            key with a readable message instead of raising, so an agent can
            still explain what happened.

        Raises:
            ValueError: If ``mode`` is unknown, ``target`` is empty, ``port``
                is out of range, ``timeout`` is out of range, or ``reverse``
                is asked for a value that is not an IP address.
        """
        if mode not in VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {list(VALID_MODES)}")
        if not isinstance(target, str) or not target.strip():
            raise ValueError("The target must be a non-empty host name or IP address.")
        target = target.strip()

        if mode == MODE_DNS:
            return self._diagnose_dns(target)
        if mode == MODE_REVERSE:
            return self._diagnose_reverse(target)
        port = _coerce_int("port", port, 443)
        timeout = _coerce_float("timeout", timeout, DEFAULT_TIMEOUT)
        return self._diagnose_tls(target, port, timeout)

    def _diagnose_dns(self, target: str) -> Dict[str, Any]:
        """Resolve a host name and report every distinct address."""
        try:
            ipv4, ipv6, aliases = _resolve_addresses(target)
        except socket.gaierror as e:
            return {
                "mode": MODE_DNS,
                "target": target,
                "error": f"DNS resolution failed for {target}: {e}",
            }
        except socket.timeout as e:
            return {
                "mode": MODE_DNS,
                "target": target,
                "error": f"DNS resolution timed out for {target}: {e}",
            }
        return {
            "mode": MODE_DNS,
            "target": target,
            "ipv4": ipv4,
            "ipv6": ipv6,
            "aliases": aliases,
            "address_count": len(ipv4) + len(ipv6),
        }

    def _diagnose_reverse(self, target: str) -> Dict[str, Any]:
        """Resolve the PTR record of an IP address."""
        try:
            ipaddress.ip_address(target)
        except ValueError as e:
            raise ValueError(f"The target must be an IP address to reverse lookup: {target}") from e

        try:
            name, aliases, _ = socket.gethostbyaddr(target)
        except socket.herror as e:
            return {
                "mode": MODE_REVERSE,
                "target": target,
                "error": f"Reverse lookup failed for {target}: {e}",
            }
        except socket.gaierror as e:
            return {
                "mode": MODE_REVERSE,
                "target": target,
                "error": f"Reverse lookup failed for {target}: {e}",
            }
        return {
            "mode": MODE_REVERSE,
            "target": target,
            "ptr": name,
            "aliases": aliases,
        }

    def _diagnose_tls(self, target: str, port: int, timeout: float) -> Dict[str, Any]:
        """Inspect the certificate served by ``target:port``."""
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
            raise ValueError(f"port must be an integer between 1 and 65535, got: {port!r}")
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < float(timeout) <= MAX_TIMEOUT:
            raise ValueError(f"timeout must be a number between 0 and {MAX_TIMEOUT}, got: {timeout!r}")

        sock = None
        try:
            sock = _open_tls_socket(target, port, float(timeout))
            cert = sock.getpeercert() or {}
            result = {
                "mode": MODE_TLS,
                "target": target,
                "port": port,
            }
            result.update(_describe_certificate(cert, sock))
            return result
        except ssl.SSLCertVerificationError as e:
            return {
                "mode": MODE_TLS,
                "target": target,
                "port": port,
                "error": f"TLS certificate verification failed for {target}:{port}: {e}",
            }
        except ssl.SSLError as e:
            return {
                "mode": MODE_TLS,
                "target": target,
                "port": port,
                "error": f"TLS handshake failed for {target}:{port}: {e}",
            }
        except socket.timeout as e:
            return {
                "mode": MODE_TLS,
                "target": target,
                "port": port,
                "error": f"TLS handshake timed out for {target}:{port}: {e}",
            }
        except OSError as e:
            return {
                "mode": MODE_TLS,
                "target": target,
                "port": port,
                "error": f"Could not connect to {target}:{port}: {e}",
            }
        finally:
            if sock is not None:
                sock.close()
