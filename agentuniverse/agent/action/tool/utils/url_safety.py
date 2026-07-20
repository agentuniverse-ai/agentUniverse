#!/usr/bin/env python3
"""Network destination validation for server-side HTTP requests."""

# Validation errors intentionally describe the rejected destination.
# ruff: noqa: TRY003

import ipaddress
import socket
from urllib.parse import urlparse


def validate_public_http_url(url: str) -> str:
    """Reject non-HTTP and non-public destinations after DNS resolution."""
    if not isinstance(url, str) or not url:
        raise ValueError("URL must be a non-empty string")
    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL must use http or https and include a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URL credentials are not allowed")
    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(
                parsed.hostname,
                parsed.port or (443 if parsed.scheme.lower() == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        }
    except socket.gaierror as exc:
        raise ValueError(f"URL hostname could not be resolved: {parsed.hostname}") from exc
    if not addresses:
        raise ValueError(f"URL hostname could not be resolved: {parsed.hostname}")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ValueError(f"URL resolves to a non-public address: {address}")
    return url
