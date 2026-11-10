#!/usr/bin/env python3

"""DNS, reverse-DNS and TLS diagnostics built only on the standard library.

The tool never scans ports and never sends HTTP requests. The ``tls`` mode
performs one ordinary TLS handshake and reads the certificate the server
already serves.
"""

# Invalid arguments are part of the documented execute contract, so a dedicated
# exception subclass would add no information for callers.
# ruff: noqa: TRY003, TRY004

import hashlib
import ipaddress
import math
import socket
import ssl
from datetime import datetime, timezone
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


class NetworkDiagnoseTool(Tool):
    """Resolve hostnames, look up PTR records and inspect served TLS certificates."""

    MODES: ClassVar[frozenset[str]] = frozenset({"dns", "reverse", "tls"})
    MAX_TARGET_CHARS: ClassVar[int] = 253
    MAX_PORT: ClassVar[int] = 65535
    MAX_TIMEOUT_SECONDS: ClassVar[float] = 30.0
    MAX_ERROR_CHARS: ClassVar[int] = 1000
    MAX_ALIASES: ClassVar[int] = 50
    MAX_SUBJECT_ALT_NAMES: ClassVar[int] = 100
    MAX_CERTIFICATE_PEM_CHARS: ClassVar[int] = 8192

    def execute(
        self,
        mode: str,
        target: str,
        port: int = 443,
        timeout: float = 5.0,
    ) -> dict[str, Any]:
        """Run one network diagnostic.

        Args:
            mode: ``dns``, ``reverse`` or ``tls``.
            target: Hostname for ``dns`` and ``tls``, IPv4 or IPv6 address for
                ``reverse``.
            port: TCP port for ``tls``, from 1 to 65535. Defaults to 443.
            timeout: Socket timeout for ``tls`` in seconds, greater than 0 and
                at most 30. Defaults to 5.

        Returns:
            A result dictionary. Resolver, connection and handshake failures
            are described in ``error`` instead of being raised, so an agent can
            report the cause and continue.

        Raises:
            ValueError: If an argument is malformed, for example an unknown
                ``mode``, an empty ``target`` or an out-of-range ``port``.
        """
        normalized_mode = self._normalize_mode(mode)
        normalized_target = self._normalize_target(target)

        if normalized_mode == "dns":
            return self._diagnose_dns(normalized_target)
        if normalized_mode == "reverse":
            return self._diagnose_reverse(normalized_target)
        return self._diagnose_tls(
            normalized_target,
            self._normalize_port(port),
            self._normalize_timeout(timeout),
        )

    def _diagnose_dns(self, target: str) -> dict[str, Any]:
        hostname = self._to_ascii_idna(target)

        try:
            infos = socket.getaddrinfo(
                hostname,
                None,
                type=socket.SOCK_STREAM,
                flags=socket.AI_CANONNAME,
            )
        except socket.gaierror as exc:
            return self._error("dns", target, "resolver_error", exc)
        except OSError as exc:
            return self._error("dns", target, "network_error", exc)

        addresses: list[dict[str, str]] = []
        seen: set[tuple[int, str]] = set()
        canonical_name: str | None = None
        for family, _socktype, _proto, canonname, sockaddr in infos:
            if family not in (socket.AF_INET, socket.AF_INET6):
                continue
            if canonname and canonical_name is None:
                canonical_name = canonname
            address = sockaddr[0]
            if (family, address) in seen:
                continue
            seen.add((family, address))
            addresses.append(
                {
                    "family": "IPv6" if family == socket.AF_INET6 else "IPv4",
                    "address": address,
                }
            )

        if not addresses:
            return self._error(
                "dns",
                target,
                "resolver_error",
                "the resolver returned no IPv4 or IPv6 address",
            )

        addresses.sort(
            key=lambda item: (
                item["family"] != "IPv4",
                ipaddress.ip_address(item["address"]),
            )
        )

        return {
            "mode": "dns",
            "target": target,
            "host": hostname,
            "canonical_name": canonical_name,
            "aliases": self._lookup_aliases(hostname),
            "addresses": addresses,
            "error": None,
        }

    def _diagnose_reverse(self, target: str) -> dict[str, Any]:
        try:
            address = ipaddress.ip_address(target)
        except ValueError as exc:
            raise ValueError("target must be an IPv4 or IPv6 address in reverse mode") from exc

        try:
            hostname, aliases, _addresses = socket.gethostbyaddr(str(address))
        except (socket.herror, socket.gaierror) as exc:
            return self._error("reverse", target, "ptr_not_found", exc)
        except OSError as exc:
            return self._error("reverse", target, "network_error", exc)

        return {
            "mode": "reverse",
            "target": target,
            "address": str(address),
            "family": "IPv6" if address.version == 6 else "IPv4",
            "hostname": hostname,
            "aliases": list(aliases)[: self.MAX_ALIASES],
            "error": None,
        }

    def _diagnose_tls(self, target: str, port: int, timeout: float) -> dict[str, Any]:
        host = target[1:-1] if target.startswith("[") and target.endswith("]") else target
        context = ssl.create_default_context()

        try:
            with (
                socket.create_connection((host, port), timeout=timeout) as raw,
                context.wrap_socket(raw, server_hostname=host) as connection,
            ):
                return {
                    "mode": "tls",
                    "target": target,
                    "host": host,
                    "port": port,
                    "verified": True,
                    "tls_version": connection.version(),
                    "cipher": self._cipher_summary(connection.cipher()),
                    "certificate": self._certificate_summary(connection.getpeercert() or {}),
                    "error": None,
                }
        except ssl.SSLCertVerificationError as exc:
            return self._certificate_verification_failure(target, host, port, timeout, exc)
        except TimeoutError as exc:
            return self._error("tls", target, "timeout", exc, host=host, port=port)
        except ssl.SSLError as exc:
            return self._error("tls", target, "tls_error", exc, host=host, port=port)
        except socket.gaierror as exc:
            return self._error("tls", target, "resolver_error", exc, host=host, port=port)
        except ConnectionRefusedError as exc:
            return self._error("tls", target, "connection_refused", exc, host=host, port=port)
        except OSError as exc:
            return self._error("tls", target, "network_error", exc, host=host, port=port)

    def _certificate_verification_failure(
        self,
        target: str,
        host: str,
        port: int,
        timeout: float,
        exc: ssl.SSLCertVerificationError,
    ) -> dict[str, Any]:
        result = self._error(
            "tls",
            target,
            "certificate_verification_failed",
            exc,
            host=host,
            port=port,
        )
        result["verified"] = False
        result["certificate"] = self._probe_certificate(host, port, timeout)
        return result

    def _probe_certificate(self, host: str, port: int, timeout: float) -> dict[str, Any]:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        try:
            with (
                socket.create_connection((host, port), timeout=timeout) as raw,
                context.wrap_socket(raw, server_hostname=host) as connection,
            ):
                der = connection.getpeercert(binary_form=True)
        except OSError:
            return {}

        if not der:
            return {}

        fingerprint = hashlib.sha256(der).hexdigest()
        pem = ssl.DER_cert_to_PEM_cert(der)
        return {
            "sha256": fingerprint,
            "pem": pem[: self.MAX_CERTIFICATE_PEM_CHARS],
        }

    @staticmethod
    def _lookup_aliases(hostname: str) -> list[str]:
        try:
            _name, aliases, _addresses = socket.gethostbyname_ex(hostname)
        except (socket.gaierror, OSError, UnicodeError):
            return []
        return list(aliases)[: NetworkDiagnoseTool.MAX_ALIASES]

    @classmethod
    def _normalize_mode(cls, mode: Any) -> str:
        if not isinstance(mode, str) or not mode.strip():
            raise ValueError("mode must be one of: dns, reverse, tls")
        normalized = mode.strip().lower()
        if normalized not in cls.MODES:
            raise ValueError("mode must be one of: dns, reverse, tls")
        return normalized

    @classmethod
    def _normalize_target(cls, target: Any) -> str:
        if not isinstance(target, str):
            raise ValueError("target must be a string")
        normalized = target.strip()
        if not normalized:
            raise ValueError("target must not be empty")
        if any(ord(char) < 0x20 or ord(char) == 0x7F for char in normalized):
            raise ValueError("target must not contain control characters")
        if any(char.isspace() for char in normalized):
            raise ValueError("target must not contain whitespace")
        if len(normalized) > cls.MAX_TARGET_CHARS:
            raise ValueError(f"target must be at most {cls.MAX_TARGET_CHARS} characters")
        return normalized

    @classmethod
    def _normalize_port(cls, port: Any) -> int:
        message = f"port must be an integer between 1 and {cls.MAX_PORT}"
        number = cls._to_number(port, message)
        if number is None or not number.is_integer():
            raise ValueError(message)
        value = int(number)
        if not 1 <= value <= cls.MAX_PORT:
            raise ValueError(message)
        return value

    @classmethod
    def _normalize_timeout(cls, timeout: Any) -> float:
        message = f"timeout must be greater than 0 and at most {cls.MAX_TIMEOUT_SECONDS:g} seconds"
        number = cls._to_number(timeout, message)
        if number is None or not math.isfinite(number):
            raise ValueError(message)
        if not 0 < number <= cls.MAX_TIMEOUT_SECONDS:
            raise ValueError(message)
        return float(number)

    @staticmethod
    def _to_number(value: Any, message: str) -> float | None:
        if isinstance(value, bool):
            raise ValueError(message)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                raise ValueError(message)
            try:
                return float(text)
            except ValueError as exc:
                raise ValueError(message) from exc
        raise ValueError(message)

    @staticmethod
    def _to_ascii_idna(target: str) -> str:
        try:
            return target.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError(f"target is not a valid host name: {exc}") from exc

    @classmethod
    def _error(
        cls,
        mode: str,
        target: str,
        error_type: str,
        exc: Exception | str,
        **extra: Any,
    ) -> dict[str, Any]:
        message = str(exc).strip() or exc.__class__.__name__
        if len(message) > cls.MAX_ERROR_CHARS:
            message = f"{message[: cls.MAX_ERROR_CHARS]}..."
        result: dict[str, Any] = {"mode": mode, "target": target, **extra}
        result["error"] = {"type": error_type, "message": message}
        return result

    @classmethod
    def _certificate_summary(cls, certificate: dict[str, Any]) -> dict[str, Any]:
        not_before = cls._parse_certificate_time(certificate.get("notBefore"))
        not_after = cls._parse_certificate_time(certificate.get("notAfter"))
        now = datetime.now(timezone.utc)

        days_remaining = None
        if not_after is not None:
            days_remaining = int((not_after - now).total_seconds() // 86400)

        subject_alt_names = [
            {"type": name_type, "value": value} for name_type, value in certificate.get("subjectAltName", ())
        ]

        return {
            "subject": cls._flatten_name(certificate.get("subject")),
            "issuer": cls._flatten_name(certificate.get("issuer")),
            "serial_number": certificate.get("serialNumber"),
            "version": certificate.get("version"),
            "not_before": cls._isoformat(not_before),
            "not_after": cls._isoformat(not_after),
            "days_remaining": days_remaining,
            "expired": not_after is not None and not_after <= now,
            "subject_alt_names": subject_alt_names[: cls.MAX_SUBJECT_ALT_NAMES],
            "subject_alt_names_omitted": max(0, len(subject_alt_names) - cls.MAX_SUBJECT_ALT_NAMES),
        }

    @classmethod
    def _flatten_name(cls, name: Any) -> dict[str, str]:
        flattened: dict[str, str] = {}
        for relative_distinguished_name in name or ():
            for key, value in relative_distinguished_name:
                if key in flattened:
                    flattened[key] = f"{flattened[key]}, {value}"
                else:
                    flattened[key] = value
        return flattened

    @staticmethod
    def _parse_certificate_time(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            seconds = ssl.cert_time_to_seconds(value)
        except (TypeError, ValueError):
            return None
        return datetime.fromtimestamp(seconds, tz=timezone.utc)

    @staticmethod
    def _isoformat(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _cipher_summary(cipher: Any) -> dict[str, Any] | None:
        if not cipher:
            return None
        name, protocol, bits = cipher
        return {"name": name, "protocol": protocol, "bits": bits}
