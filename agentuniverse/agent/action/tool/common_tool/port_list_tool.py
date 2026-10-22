#!/usr/bin/env python3
"""Port specification parsing, canonicalization, and set algebra for agents."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
import socket
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

PORT_MIN = 0
PORT_MAX = 65535


class PortListTool(Tool):
    """Parse, canonicalize, expand, and combine TCP/UDP port specifications.

    A port specification is a comma-separated list of single ports and
    inclusive ranges, for example ``22,80-90,443``.  All modes validate ports
    against the 0-65535 range, return canonical (sorted, deduplicated, merged)
    range strings, and stay deterministic: identical inputs always produce
    identical outputs with no clock, randomness, network, or filesystem use.
    """

    max_spec_chars: int = 4096
    max_ranges: int = 1024
    max_expanded_ports: int = 8192
    max_lookup_ports: int = 1024

    _MODES: ClassVar[frozenset[str]] = frozenset(
        {"parse", "expand", "compress", "lookup", "union", "intersect"}
    )
    _ITEM_RE: ClassVar[re.Pattern[str]] = re.compile(r"^(\d{1,5})(?:\s*-\s*(\d{1,5}))?$")

    # Embedded table of common IANA-registered service names.  It is the
    # tool's primary, platform-independent lookup source.  The optional
    # system_check flag cross-checks rows against socket.getservbyname, whose
    # answers come from the local services database and may differ from IANA:
    # local files lag the registry and IANA assigns some names (http-alt) to
    # more than one port, so a disagreement is reported as information about
    # the platform, never as an error.
    _SERVICES: ClassVar[dict[int, dict[str, Any]]] = {
        20: {"name": "ftp-data", "protocols": ["tcp"], "description": "File Transfer Protocol data channel"},
        21: {"name": "ftp", "protocols": ["tcp"], "description": "File Transfer Protocol control channel"},
        22: {"name": "ssh", "protocols": ["tcp"], "description": "Secure Shell remote login"},
        23: {"name": "telnet", "protocols": ["tcp"], "description": "Telnet remote login"},
        25: {"name": "smtp", "protocols": ["tcp"], "description": "Simple Mail Transfer Protocol"},
        37: {"name": "time", "protocols": ["tcp", "udp"], "description": "Time protocol"},
        42: {"name": "nameserver", "protocols": ["tcp", "udp"], "description": "Host name server"},
        43: {"name": "whois", "protocols": ["tcp"], "description": "WHOIS directory service"},
        49: {"name": "tacacs", "protocols": ["tcp", "udp"], "description": "TACACS remote authentication"},
        53: {"name": "domain", "protocols": ["tcp", "udp"], "description": "Domain Name System (DNS)"},
        67: {"name": "bootps", "protocols": ["udp"], "description": "DHCP server / BOOTP service"},
        68: {"name": "bootpc", "protocols": ["udp"], "description": "DHCP client / BOOTP client"},
        69: {"name": "tftp", "protocols": ["udp"], "description": "Trivial File Transfer Protocol"},
        70: {"name": "gopher", "protocols": ["tcp"], "description": "Gopher document protocol"},
        79: {"name": "finger", "protocols": ["tcp"], "description": "Finger user information"},
        80: {"name": "http", "protocols": ["tcp"], "description": "Hypertext Transfer Protocol"},
        88: {"name": "kerberos-sec", "protocols": ["tcp"], "description": "Kerberos authentication"},
        101: {"name": "hostname", "protocols": ["tcp"], "description": "NIC host name server"},
        107: {"name": "rtelnet", "protocols": ["tcp"], "description": "Remote Telnet service"},
        109: {"name": "pop2", "protocols": ["tcp"], "description": "Post Office Protocol v2"},
        110: {"name": "pop3", "protocols": ["tcp"], "description": "Post Office Protocol v3"},
        111: {"name": "sunrpc", "protocols": ["tcp", "udp"], "description": "ONC RPC / portmapper"},
        113: {"name": "auth", "protocols": ["tcp"], "description": "Identification protocol (ident)"},
        119: {"name": "nntp", "protocols": ["tcp"], "description": "Network News Transfer Protocol"},
        123: {"name": "ntp", "protocols": ["udp"], "description": "Network Time Protocol"},
        135: {"name": "epmap", "protocols": ["tcp"], "description": "Microsoft RPC endpoint mapper"},
        137: {"name": "netbios-ns", "protocols": ["udp"], "description": "NetBIOS name service"},
        138: {"name": "netbios-dgm", "protocols": ["udp"], "description": "NetBIOS datagram service"},
        139: {"name": "netbios-ssn", "protocols": ["tcp"], "description": "NetBIOS session service"},
        143: {"name": "imap", "protocols": ["tcp"], "description": "Internet Message Access Protocol"},
        161: {"name": "snmp", "protocols": ["tcp", "udp"], "description": "Simple Network Management Protocol"},
        162: {"name": "snmptrap", "protocols": ["tcp", "udp"], "description": "SNMP trap"},
        177: {"name": "xdmcp", "protocols": ["udp"], "description": "X Display Manager Control Protocol"},
        179: {"name": "bgp", "protocols": ["tcp"], "description": "Border Gateway Protocol"},
        194: {"name": "irc", "protocols": ["tcp"], "description": "Internet Relay Chat"},
        389: {"name": "ldap", "protocols": ["tcp"], "description": "Lightweight Directory Access Protocol"},
        443: {"name": "https", "protocols": ["tcp"], "description": "HTTP over TLS/SSL"},
        445: {"name": "microsoft-ds", "protocols": ["tcp"], "description": "Microsoft Directory Services (SMB over TCP)"},
        464: {"name": "kpasswd", "protocols": ["tcp", "udp"], "description": "Kerberos password change"},
        465: {"name": "submissions", "protocols": ["tcp"], "description": "Mail submission over TLS (historic smtps)"},
        500: {"name": "isakmp", "protocols": ["udp"], "description": "Internet Security Association and Key Management (IKE)"},
        513: {"name": "who", "protocols": ["tcp"], "description": "Remote login (rlogin)"},
        514: {"name": "syslog", "protocols": ["udp"], "description": "System logging"},
        515: {"name": "printer", "protocols": ["tcp"], "description": "Line Printer Daemon protocol (LPD)"},
        520: {"name": "rip", "protocols": ["udp"], "description": "Routing Information Protocol"},
        543: {"name": "klogin", "protocols": ["tcp"], "description": "Kerberos login"},
        546: {"name": "dhcpv6-client", "protocols": ["udp"], "description": "DHCPv6 client"},
        547: {"name": "dhcpv6-server", "protocols": ["udp"], "description": "DHCPv6 server"},
        554: {"name": "rtsp", "protocols": ["tcp"], "description": "Real Time Streaming Protocol"},
        587: {"name": "submission", "protocols": ["tcp"], "description": "Mail message submission (SMTP with STARTTLS)"},
        631: {"name": "ipp", "protocols": ["tcp"], "description": "Internet Printing Protocol (CUPS)"},
        636: {"name": "ldaps", "protocols": ["tcp"], "description": "LDAP over TLS/SSL"},
        873: {"name": "rsync", "protocols": ["tcp"], "description": "rsync file synchronization"},
        992: {"name": "telnets", "protocols": ["tcp"], "description": "Telnet over TLS/SSL"},
        993: {"name": "imaps", "protocols": ["tcp"], "description": "IMAP over TLS/SSL"},
        995: {"name": "pop3s", "protocols": ["tcp"], "description": "POP3 over TLS/SSL"},
        1080: {"name": "socks", "protocols": ["tcp"], "description": "SOCKS proxy"},
        1194: {"name": "openvpn", "protocols": ["tcp", "udp"], "description": "OpenVPN"},
        1433: {"name": "ms-sql-s", "protocols": ["tcp"], "description": "Microsoft SQL Server"},
        1434: {"name": "ms-sql-m", "protocols": ["udp"], "description": "Microsoft SQL Server browser"},
        1521: {"name": "oracle", "protocols": ["tcp"], "description": "Oracle database listener"},
        1723: {"name": "pptp", "protocols": ["tcp"], "description": "Point-to-Point Tunneling Protocol"},
        1812: {"name": "radius", "protocols": ["udp"], "description": "RADIUS authentication"},
        1813: {"name": "radius-acct", "protocols": ["udp"], "description": "RADIUS accounting"},
        1883: {"name": "mqtt", "protocols": ["tcp"], "description": "MQTT message transport"},
        1900: {"name": "upnp", "protocols": ["tcp", "udp"], "description": "Universal Plug and Play (SSDP)"},
        2049: {"name": "nfs", "protocols": ["tcp"], "description": "Network File System"},
        3128: {"name": "squid", "protocols": ["tcp"], "description": "Squid web proxy"},
        3260: {"name": "iscsi", "protocols": ["tcp"], "description": "Object storage (iSCSI)"},
        3306: {"name": "mysql", "protocols": ["tcp"], "description": "MySQL database"},
        3389: {"name": "ms-wbt-server", "protocols": ["tcp"], "description": "Microsoft Remote Desktop (RDP)"},
        3478: {"name": "stun", "protocols": ["udp", "tcp"], "description": "Session Traversal Utilities for NAT"},
        3690: {"name": "svn", "protocols": ["tcp"], "description": "Subversion version control"},
        4500: {"name": "ipsec-nat-t", "protocols": ["udp"], "description": "IPsec NAT traversal"},
        5060: {"name": "sip", "protocols": ["tcp", "udp"], "description": "Session Initiation Protocol"},
        5061: {"name": "sips", "protocols": ["tcp"], "description": "SIP over TLS"},
        5222: {"name": "xmpp-client", "protocols": ["tcp"], "description": "XMPP client connection"},
        5269: {"name": "xmpp-server", "protocols": ["tcp"], "description": "XMPP server-to-server"},
        5432: {"name": "postgresql", "protocols": ["tcp"], "description": "PostgreSQL database"},
        5672: {"name": "amqp", "protocols": ["tcp"], "description": "Advanced Message Queuing Protocol"},
        5900: {"name": "rfb", "protocols": ["tcp"], "description": "VNC remote framebuffer (display :0)"},
        5985: {"name": "wsman", "protocols": ["tcp"], "description": "Windows Remote Management over HTTP"},
        5986: {"name": "wsmans", "protocols": ["tcp"], "description": "Windows Remote Management over HTTPS"},
        6000: {"name": "x11", "protocols": ["tcp"], "description": "X Window System (display :0)"},
        6379: {"name": "redis", "protocols": ["tcp"], "description": "Redis in-memory data store"},
        8080: {"name": "http-alt", "protocols": ["tcp"], "description": "HTTP alternate; IANA also maps the name to 591"},
        8883: {"name": "secure-mqtt", "protocols": ["tcp"], "description": "MQTT over TLS/SSL"},
        9418: {"name": "git", "protocols": ["tcp"], "description": "Git native protocol"},
        11211: {"name": "memcache", "protocols": ["tcp", "udp"], "description": "Memcached"},
        27017: {"name": "mongodb", "protocols": ["tcp"], "description": "MongoDB database"},
    }

    def execute(
        self,
        mode: str,
        spec: str | None = None,
        other_spec: str | None = None,
        ports: list[int] | None = None,
        system_check: bool = False,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "parse":
                return self._parse(spec)
            if operation == "expand":
                return self._expand(spec)
            if operation == "compress":
                return self._compress(spec, ports)
            if operation == "lookup":
                return self._lookup(spec, ports, system_check)
            return self._algebra(operation, spec, other_spec, ports)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"Port list operation failed: {exc}")

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_config(self) -> None:
        for name in ("max_spec_chars", "max_ranges", "max_expanded_ports", "max_lookup_ports"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in PortListTool._MODES:
            raise ValueError("mode must be parse, expand, compress, lookup, union, or intersect")
        return operation

    def _spec(self, value: Any, label: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{label} must be a string")
        spec = value.strip()
        if not spec:
            raise ValueError(f"{label} must be a non-empty port list such as '22,80-90,443'")
        if len(spec) > self.max_spec_chars:
            raise ValueError(f"{label} exceeds max_spec_chars ({self.max_spec_chars})")
        return spec

    @staticmethod
    def _token_range(token: str, label: str) -> tuple[int, int, str, str | None]:
        """Validate one spec item and return (start, end, start_text, end_text)."""
        match = PortListTool._ITEM_RE.match(token)
        if match is None:
            raise ValueError(f"invalid port list item in {label}: {token!r}")
        start_text, end_text = match.group(1), match.group(2)
        start = int(start_text)
        end = int(end_text) if end_text is not None else start
        for port in (start, end):
            if not PORT_MIN <= port <= PORT_MAX:
                raise ValueError(f"port {port} out of range {PORT_MIN}-{PORT_MAX} in {label}")
        if end_text is not None and start > end:
            raise ValueError(f"descending range {start}-{end} in {label}")
        return start, end, start_text, end_text

    @staticmethod
    def _padded_texts(*pairs: tuple[str | None, int]) -> list[str]:
        """Return the texts of numbers written with leading zeros."""
        return [text for text, number in pairs if text is not None and text != str(number)]

    def _scan_tokens(self, spec: str, label: str) -> tuple[list[tuple[int, int]], list[dict[str, str]]]:
        """Tokenize a spec into raw ranges plus per-item findings."""
        findings: list[dict[str, str]] = []
        raw: list[tuple[int, int]] = []
        zero_padded: list[str] = []
        duplicate_items = 0
        for token in spec.split(","):
            token = token.strip()
            if not token:
                raise ValueError(f"empty item in {label}: {spec!r}")
            start, end, start_text, end_text = self._token_range(token, label)
            if end_text is not None and start == end:
                findings.append({"code": "single_port_range", "message": f"range {start}-{end} covers one port"})
            zero_padded.extend(self._padded_texts((start_text, start), (end_text, end)))
            if (start, end) in raw:
                duplicate_items += 1
            raw.append((start, end))
        if duplicate_items:
            findings.append({"code": "duplicate_items", "message": f"{duplicate_items} duplicate item(s) removed"})
        if zero_padded:
            findings.append({
                "code": "leading_zeros",
                "message": "normalized leading zeros in: " + ", ".join(zero_padded),
            })
        return raw, findings

    def _resolve_spec(self, value: Any, label: str = "spec") -> tuple[list[tuple[int, int]], list[dict[str, str]]]:
        """Parse a port specification into merged canonical ranges plus findings."""
        spec = self._spec(value, label)
        raw, findings = self._scan_tokens(spec, label)
        if len(raw) > self.max_ranges:
            raise ValueError(f"{label} has more than max_ranges ({self.max_ranges}) items")
        if raw != sorted(raw):
            findings.append({"code": "unsorted_input", "message": "input items were not in ascending order"})
        merged = self._merge(raw)
        if len(merged) < len(raw):
            findings.append({
                "code": "merged_ranges",
                "message": f"{len(raw)} item(s) merged into {len(merged)} canonical range(s)",
            })
        if len(merged) > self.max_ranges:
            raise ValueError(f"{label} produces more than max_ranges ({self.max_ranges}) ranges")
        return merged, findings

    @staticmethod
    def _merge(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Sort ranges and merge overlapping or adjacent ones."""
        merged: list[tuple[int, int]] = []
        for start, end in sorted(ranges):
            if merged and start <= merged[-1][1] + 1:
                if end > merged[-1][1]:
                    merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))
        return merged

    @staticmethod
    def _canonical(ranges: list[tuple[int, int]]) -> str:
        return ",".join(
            str(start) if start == end else f"{start}-{end}" for start, end in ranges
        )

    @staticmethod
    def _range_dicts(ranges: list[tuple[int, int]]) -> list[dict[str, int]]:
        return [
            {"start": start, "end": end, "size": end - start + 1} for start, end in ranges
        ]

    @staticmethod
    def _expand_ranges(ranges: list[tuple[int, int]], limit: int) -> list[int]:
        expanded: list[int] = []
        for start, end in ranges:
            for port in range(start, end + 1):
                if len(expanded) >= limit:
                    return expanded
                expanded.append(port)
        return expanded

    def _port_list(self, value: Any, label: str) -> list[int]:
        if not isinstance(value, (list, tuple)):
            raise TypeError(f"{label} must be a list of integers")
        if not value:
            raise ValueError(f"{label} must contain at least one port")
        if len(value) > self.max_expanded_ports:
            raise ValueError(f"{label} exceeds max_expanded_ports ({self.max_expanded_ports})")
        ports: list[int] = []
        for item in value:
            if isinstance(item, bool) or not isinstance(item, int):
                raise TypeError(f"{label} entries must be integers: {item!r}")
            if not PORT_MIN <= item <= PORT_MAX:
                raise ValueError(f"port {item} out of range {PORT_MIN}-{PORT_MAX} in {label}")
            ports.append(item)
        return ports

    def _single_source(
        self, spec: Any, ports: Any
    ) -> tuple[list[tuple[int, int]], list[dict[str, str]], int]:
        """Resolve the one allowed input source (spec or ports) to ranges."""
        if spec is not None and ports is not None:
            raise ValueError("provide either spec or ports, not both")
        if spec is not None:
            ranges, findings = self._resolve_spec(spec)
            return ranges, findings, sum(end - start + 1 for start, end in ranges)
        if ports is None:
            raise ValueError("spec or ports is required")
        values = self._port_list(ports, "ports")
        findings: list[dict[str, str]] = []
        if len(set(values)) < len(values):
            findings.append({
                "code": "duplicate_items",
                "message": f"{len(values) - len(set(values))} duplicate port(s) removed",
            })
        if values != sorted(values):
            findings.append({"code": "unsorted_input", "message": "input ports were not in ascending order"})
        merged = self._merge([(port, port) for port in values])
        return merged, findings, len(set(values))

    def _parse(self, spec: Any) -> dict[str, Any]:
        ranges, findings = self._resolve_spec(spec)
        return {
            "status": "success",
            "mode": "parse",
            "canonical": self._canonical(ranges),
            "ranges": self._range_dicts(ranges),
            "port_count": sum(end - start + 1 for start, end in ranges),
            "findings": findings,
        }

    def _expand(self, spec: Any) -> dict[str, Any]:
        ranges, findings = self._resolve_spec(spec)
        total = sum(end - start + 1 for start, end in ranges)
        if total > self.max_expanded_ports:
            ports = self._expand_ranges(ranges, self.max_expanded_ports)
            truncated = True
        else:
            ports = self._expand_ranges(ranges, total)
            truncated = False
        return {
            "status": "success",
            "mode": "expand",
            "canonical": self._canonical(ranges),
            "ports": ports,
            "returned": len(ports),
            "port_count": total,
            "truncated": truncated,
            "findings": findings,
        }

    def _compress(self, spec: Any, ports: Any) -> dict[str, Any]:
        ranges, findings, port_count = self._single_source(spec, ports)
        return {
            "status": "success",
            "mode": "compress",
            "canonical": self._canonical(ranges),
            "ranges": self._range_dicts(ranges),
            "port_count": port_count,
            "findings": findings,
        }

    def _lookup(self, spec: Any, ports: Any, system_check: Any) -> dict[str, Any]:
        if not isinstance(system_check, bool):
            raise TypeError("system_check must be a boolean")
        ranges, _findings, _count = self._single_source(spec, ports)
        total = sum(end - start + 1 for start, end in ranges)
        if total > self.max_lookup_ports:
            raise ValueError(f"lookup exceeds max_lookup_ports ({self.max_lookup_ports})")
        port_values = self._expand_ranges(ranges, total)
        results: list[dict[str, Any]] = []
        unknown: list[int] = []
        for port in port_values:
            entry = self._SERVICES.get(port)
            if entry is None:
                unknown.append(port)
                results.append({"port": port, "known": False})
                continue
            record: dict[str, Any] = {
                "port": port,
                "known": True,
                "name": entry["name"],
                "protocols": list(entry["protocols"]),
                "description": entry["description"],
            }
            if system_check:
                record["system_check"] = self._system_check(port, entry)
            results.append(record)
        return {
            "status": "success",
            "mode": "lookup",
            "count": len(results),
            "known_count": len(results) - len(unknown),
            "unknown_count": len(unknown),
            "unknown": unknown,
            "results": results,
        }

    @staticmethod
    def _system_check(port: int, entry: dict[str, Any]) -> dict[str, Any]:
        """Cross-check one embedded table row against the local services file.

        socket.getservbyname answers from the platform services database, so a
        missing mapping or a different port is a platform difference, not an
        error: IANA assigns some names (http-alt) to several ports and local
        files lag the registry.  The result is informational only.
        """
        protocol = entry["protocols"][0]
        try:
            mapped = socket.getservbyname(entry["name"], protocol)
        except OSError:
            return {
                "protocol": protocol,
                "status": "missing_local_mapping",
                "mapped_port": None,
                "note": "local services database has no such entry for this protocol",
            }
        if mapped == port:
            return {"protocol": protocol, "status": "agree", "mapped_port": mapped}
        return {
            "protocol": protocol,
            "status": "name_maps_to_other_port",
            "mapped_port": mapped,
            "note": "IANA assigns this service name to more than one port; the platform maps it elsewhere",
        }

    def _algebra(self, operation: str, spec: Any, other_spec: Any, ports: Any) -> dict[str, Any]:
        if other_spec is None:
            raise ValueError("other_spec is required for union and intersect")
        left_ranges, left_findings, _left_count = self._single_source(spec, ports)
        right_ranges, right_findings = self._resolve_spec(other_spec, "other_spec")
        left = self._expand_ranges(left_ranges, PORT_MAX + 1)
        right = self._expand_ranges(right_ranges, PORT_MAX + 1)
        combined = sorted(set(left) | set(right)) if operation == "union" else sorted(set(left) & set(right))
        findings = left_findings + right_findings
        if operation == "intersect" and not combined:
            findings.append({"code": "empty_intersection", "message": "the two port lists share no ports"})
        ranges = self._merge([(port, port) for port in combined])
        result: dict[str, Any] = {
            "status": "success",
            "mode": operation,
            "canonical": self._canonical(ranges),
            "ranges": self._range_dicts(ranges),
            "port_count": len(combined),
            "findings": findings,
        }
        if len(combined) <= self.max_expanded_ports:
            result["ports"] = combined
        else:
            result["ports_omitted"] = True
            result["max_expanded_ports"] = self.max_expanded_ports
        return result
