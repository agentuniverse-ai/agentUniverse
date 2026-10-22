#!/usr/bin/env python3
"""Port specification parsing, canonicalization, and set algebra for agents.

PortListTool is the ops-friendly format layer between free-form port specs
(``"22,80-90,443"``) and explicit port sets.  It provides six modes:

* ``parse``      - spec string to ranged form with positional errors/infos
* ``expand``     - spec to an explicit port list (capped, ``include_full`` guard)
* ``compress``   - port list or spec to the minimal canonical spec (adjacency
  merging: ``80,81,82 -> 80-82``, while ``79,81`` stays unmerged because 80 is
  missing)
* ``services``   - map ranges to well-known service names from an embedded,
  IANA-curated table (~120 entries; misses are reported as ``unknown``, never
  guessed)
* ``algebra``    - union / intersection / difference of two specs
* ``check``      - audit a spec against allowed ranges, blocked ports, and a
  maximum port budget (the firewall-review use case)

Conventions (documented behaviour, not guesses):

* Ports are 0-65535 inclusive.  Port 0 is reserved: it parses but every range
  containing it is flagged with a ``reserved_port_zero`` info.
* Reversed ranges (``90-80``) are errors by convention rather than silently
  normalized, so typos surface at the point of entry.
* ``80-80`` collapses to the singleton ``80`` (info ``singleton_collapse``).
* Whitespace around numbers, hyphens, and commas is tolerated; empty segments
  (``80,,443``) are errors with the exact character position.
* Leading zeros (``080``) are rejected: port specs do not zero-pad.  Only ASCII
  digits are accepted; unicode digits are rejected.
* The ``all`` keyword expands to 0-65535 and requires ``allow_all=true``.
* ``expand`` returns at most ``max_expand_ports`` ports by default; the full
  65536-port list is legal but requires the explicit ``include_full=true``
  guard.

The implementation is stdlib-only and deterministic: identical inputs always
produce identical outputs, iteration order is explicitly sorted, and every
returned collection is bounded by a configurable cap.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

from __future__ import annotations

import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

MIN_PORT = 0
MAX_PORT = 65535
FULL_SPEC = f"{MIN_PORT}-{MAX_PORT}"

# ASCII-only tokenizer: whitespace runs, one number, or one hyphen at a time.
_TOKEN_RE = re.compile(r"[ \t\r\n]*([0-9]+|-)[ \t\r\n]*")
_NUMBER_RE = re.compile(r"[0-9]+")

# (port, service, protocol, note).  protocol: tcp | udp | both.
# Curated subset of IANA assignments plus widely-used de-facto registrations
# (marked "not IANA-assigned" in the note).  A missing port is reported as
# unknown rather than guessed.
_SERVICE_ROWS: ClassVar[tuple[tuple[int, str, str, str], ...]] = (
    (7, "echo", "both", "IANA assigned"),
    (9, "discard", "both", "IANA assigned"),
    (13, "daytime", "both", "IANA assigned"),
    (17, "qotd", "both", "IANA assigned"),
    (19, "chargen", "both", "IANA assigned"),
    (20, "ftp-data", "tcp", "IANA assigned"),
    (21, "ftp", "tcp", "IANA assigned; control channel"),
    (22, "ssh", "both", "IANA assigned"),
    (23, "telnet", "tcp", "IANA assigned"),
    (25, "smtp", "tcp", "IANA assigned"),
    (26, "rsftp", "tcp", "IANA assigned (RSFTP)"),
    (37, "time", "both", "IANA assigned"),
    (42, "nameserver", "both", "IANA assigned (WINS host name server)"),
    (43, "whois", "tcp", "IANA assigned"),
    (49, "tacacs", "both", "IANA assigned"),
    (53, "dns", "both", "IANA assigned (domain)"),
    (67, "dhcp-server", "udp", "IANA assigned (bootps)"),
    (68, "dhcp-client", "udp", "IANA assigned (bootpc)"),
    (69, "tftp", "udp", "IANA assigned"),
    (70, "gopher", "tcp", "IANA assigned"),
    (79, "finger", "tcp", "IANA assigned"),
    (80, "http", "both", "IANA assigned (www-http)"),
    (88, "kerberos", "both", "IANA assigned"),
    (102, "iso-tsap", "tcp", "IANA assigned"),
    (107, "rtelnet", "tcp", "IANA assigned"),
    (109, "pop2", "tcp", "IANA assigned"),
    (110, "pop3", "tcp", "IANA assigned"),
    (111, "rpcbind", "both", "IANA assigned (sunrpc)"),
    (113, "ident", "tcp", "IANA assigned (auth)"),
    (119, "nntp", "tcp", "IANA assigned"),
    (123, "ntp", "udp", "IANA assigned"),
    (135, "msrpc", "tcp", "IANA assigned (epmapper)"),
    (137, "netbios-ns", "udp", "IANA assigned"),
    (138, "netbios-dgm", "udp", "IANA assigned"),
    (139, "netbios-ssn", "tcp", "IANA assigned"),
    (143, "imap", "tcp", "IANA assigned"),
    (161, "snmp", "udp", "IANA assigned"),
    (162, "snmptrap", "udp", "IANA assigned"),
    (177, "xdmcp", "udp", "IANA assigned"),
    (179, "bgp", "tcp", "IANA assigned"),
    (194, "irc", "tcp", "IANA assigned"),
    (201, "apple-talk", "udp", "IANA assigned"),
    (389, "ldap", "tcp", "IANA assigned"),
    (427, "svrloc", "udp", "IANA assigned (Service Location)"),
    (443, "https", "tcp", "IANA assigned"),
    (444, "snpp", "tcp", "IANA assigned"),
    (445, "smb", "tcp", "IANA assigned (microsoft-ds)"),
    (464, "kpasswd", "both", "IANA assigned"),
    (465, "smtps", "tcp", "IANA historically urd/submissions; SMTP over TLS convention"),
    (500, "isakmp", "udp", "IANA assigned (IKE)"),
    (502, "modbus", "tcp", "IANA assigned"),
    (506, "ohmserver", "tcp", "IANA assigned"),
    (514, "shell", "tcp", "IANA assigned (cmd); UDP 514 is syslog"),
    (514, "syslog", "udp", "IANA assigned; TCP 514 is shell/cmd"),
    (515, "printer", "tcp", "IANA assigned (lpd)"),
    (520, "rip", "udp", "IANA assigned"),
    (521, "ripng", "udp", "IANA assigned"),
    (526, "tempo", "tcp", "IANA assigned"),
    (530, "rpc", "tcp", "IANA assigned (courier)"),
    (540, "uucp", "tcp", "IANA assigned"),
    (543, "klogin", "tcp", "IANA assigned"),
    (544, "kshell", "tcp", "IANA assigned"),
    (546, "dhcpv6-client", "udp", "IANA assigned"),
    (547, "dhcpv6-server", "udp", "IANA assigned"),
    (548, "afp", "tcp", "IANA assigned"),
    (554, "rtsp", "both", "IANA assigned"),
    (555, "dsf", "tcp", "IANA assigned"),
    (563, "nntp-over-tls", "tcp", "IANA assigned (nntps)"),
    (587, "submission", "tcp", "IANA assigned; modern SMTP client port"),
    (591, "http-mgmt", "tcp", "IANA assigned"),
    (631, "ipp", "both", "IANA assigned (printing)"),
    (636, "ldaps", "tcp", "IANA assigned (ldap over TLS)"),
    (646, "ldp", "tcp", "IANA assigned"),
    (647, "dhcp-failover", "tcp", "IANA assigned"),
    (873, "rsync", "tcp", "IANA assigned"),
    (990, "ftps", "tcp", "IANA assigned (ftp over TLS)"),
    (992, "telnets", "tcp", "IANA assigned"),
    (993, "imaps", "tcp", "IANA assigned (imap over TLS)"),
    (994, "ircs", "tcp", "IANA assigned"),
    (995, "pop3s", "tcp", "IANA assigned (pop3 over TLS)"),
    (1080, "socks", "tcp", "IANA assigned; UDP used for associate relay"),
    (1099, "jms", "tcp", "de-facto Java RMI/JNDI registry"),
    (1433, "mssql", "tcp", "IANA assigned (ms-sql-s)"),
    (1434, "mssql-monitor", "udp", "IANA assigned (ms-sql-m)"),
    (1521, "oracle-db", "tcp", "de-facto Oracle TNS listener"),
    (1701, "l2tp", "udp", "IANA assigned"),
    (1723, "pptp", "tcp", "IANA assigned"),
    (1725, "ibm-db2", "tcp", "de-facto IBM DB2"),
    (1812, "radius", "udp", "IANA assigned (authentication)"),
    (1813, "radius-accounting", "udp", "IANA assigned"),
    (1883, "mqtt", "tcp", "IANA assigned"),
    (1900, "ssdp", "udp", "IANA assigned (UPnP discovery)"),
    (1935, "rtmp", "tcp", "IANA assigned (Adobe Flash media)"),
    (2049, "nfs", "both", "IANA assigned"),
    (2082, "infowave", "tcp", "IANA assigned"),
    (2181, "zookeeper", "tcp", "de-facto Apache ZooKeeper"),
    (2375, "docker-api", "tcp", "not IANA-assigned; unencrypted de-facto Docker"),
    (2376, "docker-api-tls", "tcp", "not IANA-assigned; TLS de-facto Docker"),
    (2379, "etcd-client", "tcp", "not IANA-assigned; de-facto etcd"),
    (2380, "etcd-peer", "tcp", "not IANA-assigned; de-facto etcd"),
    (2404, "iec-104", "tcp", "IANA assigned (IEC 60870-5-104)"),
    (3128, "web-proxy", "tcp", "IANA assigned (squid http)"),
    (3260, "iscsi", "tcp", "IANA assigned"),
    (3306, "mysql", "tcp", "IANA assigned"),
    (3389, "rdp", "tcp", "IANA assigned (ms-wbt-server)"),
    (3478, "stun", "udp", "IANA assigned; TCP variant also used"),
    (3690, "svn", "tcp", "IANA assigned (subversion)"),
    (4190, "sieve", "tcp", "IANA assigned"),
    (4500, "ipsec-nat-t", "udp", "IANA assigned"),
    (4840, "opc-ua", "tcp", "IANA assigned"),
    (5060, "sip", "both", "IANA assigned"),
    (5061, "sip-tls", "tcp", "IANA assigned"),
    (5222, "xmpp-client", "tcp", "IANA assigned"),
    (5269, "xmpp-server", "tcp", "IANA assigned"),
    (5353, "mdns", "udp", "IANA assigned (multicast DNS)"),
    (5355, "llmnr", "udp", "IANA assigned"),
    (5432, "postgresql", "tcp", "IANA assigned"),
    (5672, "amqp", "tcp", "IANA assigned (AMQP 0-9-1)"),
    (5683, "coap", "udp", "IANA assigned"),
    (5684, "coaps", "udp", "IANA assigned (DTLS)"),
    (5800, "vnc-http", "tcp", "IANA assigned (VNC web console)"),
    (5900, "vnc", "tcp", "IANA assigned"),
    (5985, "winrm", "tcp", "not IANA-assigned; de-facto WinRM HTTP"),
    (5986, "winrm-tls", "tcp", "not IANA-assigned; de-facto WinRM HTTPS"),
    (6000, "x11", "tcp", "IANA assigned (6000-6063 family)"),
    (6379, "redis", "tcp", "IANA assigned"),
    (6443, "kubernetes-api", "tcp", "not IANA-assigned; de-facto Kubernetes"),
    (6667, "irc-alt", "tcp", "IANA assigned"),
    (7000, "cassandra", "tcp", "de-facto Apache Cassandra storage"),
    (7001, "weblogic-admin", "tcp", "de-facto Oracle WebLogic"),
    (8000, "http-alt", "tcp", "IANA assigned (irdmi); common alternate HTTP"),
    (8080, "http-proxy", "tcp", "IANA assigned (http-alt); common app port"),
    (8443, "https-alt", "tcp", "not IANA-assigned; common alternate HTTPS"),
    (8500, "consul", "tcp", "de-facto HashiCorp Consul HTTP API"),
    (8883, "mqtt-tls", "tcp", "IANA assigned"),
    (9001, "etcd-alt", "tcp", "de-facto alternate etcd"),
    (9090, "prometheus", "tcp", "not IANA-assigned; de-facto Prometheus"),
    (9100, "node-exporter", "tcp", "not IANA-assigned; de-facto Prometheus node exporter"),
    (9200, "elasticsearch", "tcp", "de-facto Elasticsearch REST API"),
    (9300, "elasticsearch-transport", "tcp", "de-facto Elasticsearch node transport"),
    (10000, "ndmp", "both", "IANA assigned (network data management)"),
    (10250, "kubelet", "tcp", "not IANA-assigned; de-facto Kubernetes kubelet API"),
    (11211, "memcached", "both", "IANA assigned; UDP used for gets"),
    (15672, "rabbitmq-mgmt", "tcp", "not IANA-assigned; de-facto RabbitMQ management"),
    (27017, "mongodb", "tcp", "IANA assigned"),
    (27018, "mongodb-shard", "tcp", "IANA assigned"),
    (27019, "mongodb-config", "tcp", "IANA assigned"),
    (50000, "db2", "tcp", "de-facto IBM DB2 LUW"),
    (61613, "stomp", "tcp", "de-facto STOMP messaging"),
    (61616, "activemq", "tcp", "de-facto Apache ActiveMQ OpenWire"),
)

_SERVICE_TABLE: ClassVar[dict[int, list[dict[str, str]]]] = {}
for _port, _name, _proto, _note in _SERVICE_ROWS:
    _SERVICE_TABLE.setdefault(_port, []).append(
        {"service": _name, "protocol": _proto, "note": _note}
    )
_SERVICE_TABLE = {port: _SERVICE_TABLE[port] for port in sorted(_SERVICE_TABLE)}

_SERVICE_COVERAGE_NOTE = (
    "Curated subset of IANA and common de-facto assignments; a port reported "
    "as unknown means 'not in this table', not 'unassigned'."
)

_MODES = ("parse", "expand", "compress", "services", "algebra", "check")
_ALGEBRA_OPS = ("union", "intersection", "difference")


class PortListTool(Tool):
    """Parse, canonicalize, annotate, and combine network port specifications."""

    max_spec_length: int = 500_000
    max_spec_segments: int = 20_000
    max_errors: int = 100
    max_infos: int = 50
    max_expand_ports: int = 4_096
    max_input_ports: int = 65_536
    max_service_results: int = 1_000
    max_violation_ranges: int = 20
    max_overlap_reports: int = 50

    def execute(
        self,
        mode: str,
        spec: str | None = None,
        ports: list[int] | None = None,
        spec_a: str | None = None,
        spec_b: str | None = None,
        op: str = "union",
        include_full: bool = False,
        allow_all: bool = False,
        allowed_ranges: str | None = None,
        blocked_ports: str | None = None,
        max_ports: int | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "parse":
                return self._run_parse(spec, allow_all)
            if operation == "expand":
                return self._run_expand(spec, allow_all, include_full)
            if operation == "compress":
                return self._run_compress(spec, ports, allow_all)
            if operation == "services":
                return self._run_services(spec, allow_all)
            if operation == "algebra":
                return self._run_algebra(spec_a, spec_b, op, allow_all)
            return self._run_check(spec, allow_all, allowed_ranges, blocked_ports, max_ports)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"Port list operation failed: {exc}")

    # ------------------------------------------------------------------ util

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_config(self) -> None:
        for name in ("max_spec_length", "max_spec_segments", "max_errors", "max_infos", "max_input_ports", "max_service_results", "max_violation_ranges", "max_overlap_reports"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name in ("max_expand_ports",):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= MAX_PORT + 1:
                raise ValueError(f"{name} must be an integer between 1 and 65536")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in _MODES:
            raise ValueError("mode must be parse, expand, compress, services, algebra, or check")
        return operation

    @staticmethod
    def _string(value: Any, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
        return value

    # ----------------------------------------------------------------- parse

    def _parse_spec(self, spec: Any, allow_all: bool) -> dict[str, Any]:
        """Parse a spec string into ordered ranges, errors, and infos."""
        raw = self._string(spec, "spec")
        if len(raw) > self.max_spec_length:
            raise ValueError(f"spec exceeds max_spec_length={self.max_spec_length}")
        errors: list[dict[str, Any]] = []
        infos: list[dict[str, Any]] = []
        ranges: list[dict[str, int]] = []
        stripped_all = raw.strip().lower()
        if stripped_all == "all":
            if allow_all:
                ranges.append({"start": MIN_PORT, "end": MAX_PORT})
                infos.append({
                    "code": "all_keyword",
                    "position": 0,
                    "message": f"'all' keyword expanded to {FULL_SPEC}",
                })
            else:
                errors.append({
                    "code": "all_keyword_disabled",
                    "position": 0,
                    "segment": "all",
                    "message": "'all' keyword requires allow_all=true",
                })
            return {"ranges": ranges, "errors": errors, "infos": infos, "segment_count": 1}

        segment_count = 0
        start = 0
        for index, char in enumerate(raw):
            if char == ",":
                if segment_count >= self.max_spec_segments:
                    raise ValueError(f"spec exceeds max_spec_segments={self.max_spec_segments}")
                self._parse_segment(raw[start:index], start, ranges, errors, infos)
                segment_count += 1
                start = index + 1
        if segment_count >= self.max_spec_segments:
            raise ValueError(f"spec exceeds max_spec_segments={self.max_spec_segments}")
        self._parse_segment(raw[start:], start, ranges, errors, infos)
        segment_count += 1

        if not errors:
            infos.extend(self._overlap_infos(ranges))
        return {"ranges": ranges, "errors": errors, "infos": infos, "segment_count": segment_count}

    def _fail(
        self,
        errors: list[dict[str, Any]],
        position: int,
        segment: str,
        code: str,
        offset: int,
        message: str,
    ) -> None:
        if len(errors) < self.max_errors:
            errors.append({
                "code": code,
                "position": position + offset,
                "segment": segment,
                "message": message,
            })

    @staticmethod
    def _segment_shape_error(tokens: list[tuple[str, str, int]]) -> tuple[str, int, str] | None:
        """Return (code, offset, message) when a token sequence is not 'port' or 'a-b'."""
        kinds = tuple(token[0] for token in tokens)
        if kinds in (("number",), ("number", "dash", "number")):
            return None
        if kinds[0] == "dash":
            return ("missing_start", tokens[0][2], "range is missing its start port")
        if kinds[-1] == "dash":
            return ("missing_end", tokens[-1][2], "range is missing its end port")
        if kinds.count("dash") > 1:
            second_dash = tokens[kinds.index("dash", kinds.index("dash") + 1)]
            return ("non_numeric", second_dash[2], "segment contains more than one hyphen")
        if kinds.count("number") >= 2:
            second_number = tokens[kinds.index("number", kinds.index("number") + 1)]
            return ("non_numeric", second_number[2], "unexpected second number; separate ports with ',' not whitespace")
        return ("non_numeric", tokens[0][2], "segment is not a port or 'a-b' range")

    def _tokenize_segment(
        self,
        segment: str,
        position: int,
        errors: list[dict[str, Any]],
    ) -> list[tuple[str, str, int]] | None:
        """Split a segment into (kind, text, offset) tokens, or None on failure."""
        tokens: list[tuple[str, str, int]] = []
        cursor = 0
        while cursor < len(segment):
            match = _TOKEN_RE.match(segment, cursor)
            if match is None:
                self._fail(errors, position, segment, "non_numeric", cursor, f"unexpected character {segment[cursor]!r}")
                return None
            text = match.group(1)
            tokens.append(("number" if text != "-" else "dash", text, match.start(1)))
            cursor = match.end()
        return tokens

    def _number_token(
        self,
        token: tuple[str, str, int],
        position: int,
        segment: str,
        errors: list[dict[str, Any]],
    ) -> int | None:
        """Convert a number token to a validated port, or None on failure."""
        _, text, offset = token
        if len(text) > 1 and text.startswith("0"):
            self._fail(errors, position, segment, "leading_zero", offset, f"'{text}' is zero-padded; port specs do not zero-pad")
            return None
        value = int(text)
        if value > MAX_PORT:
            self._fail(errors, position, segment, "out_of_range", offset, f"{value} exceeds the maximum port {MAX_PORT}")
            return None
        return value

    @staticmethod
    def _non_ascii(segment: str) -> tuple[int, str] | None:
        """Return (offset, char) of the first non-ASCII character, or None."""
        for offset, char in enumerate(segment):
            if ord(char) > 0x7F:
                return offset, char
        return None

    def _parse_segment(
        self,
        segment: str,
        position: int,
        ranges: list[dict[str, int]],
        errors: list[dict[str, Any]],
        infos: list[dict[str, Any]],
    ) -> None:
        if not segment.strip():
            self._fail(errors, position, segment, "empty_segment", 0, "empty segment between commas or at spec edge")
            return
        exotic = self._non_ascii(segment)
        if exotic is not None:
            offset, char = exotic
            self._fail(errors, position, segment, "non_numeric", offset, f"non-ASCII character {char!r}; only ASCII digits, hyphen, and whitespace are accepted")
            return
        tokens = self._tokenize_segment(segment, position, errors)
        if tokens is None:
            return
        problem = self._segment_shape_error(tokens)
        if problem is not None:
            self._fail(errors, position, segment, *problem)
            return
        start = self._number_token(tokens[0], position, segment, errors)
        if start is None:
            return
        if len(tokens) == 1:
            ranges.append({"start": start, "end": start})
            return
        end = self._number_token(tokens[2], position, segment, errors)
        if end is None:
            return
        if end < start:
            self._fail(errors, position, segment, "reversed_range", tokens[2][2], f"range end {end} is lower than start {start}; write '{end}-{start}' instead")
            return
        if end == start:
            infos.append({
                "code": "singleton_collapse",
                "position": position + tokens[0][2],
                "segment": segment,
                "message": f"'{start}-{end}' collapses to the singleton {start}",
            })
        ranges.append({"start": start, "end": end})

    def _overlap_infos(self, ranges: list[dict[str, int]]) -> list[dict[str, Any]]:
        """Report duplicate and overlapping ranges with overlap arithmetic."""
        infos: list[dict[str, Any]] = []
        order = sorted(range(len(ranges)), key=lambda i: (ranges[i]["start"], ranges[i]["end"]))
        reported = 0
        for position in range(len(order) - 1):
            left = ranges[order[position]]
            right = ranges[order[position + 1]]
            if right["start"] > left["end"]:
                continue
            overlap = min(left["end"], right["end"]) - right["start"] + 1
            if reported >= self.max_overlap_reports:
                infos.append({
                    "code": "overlap_report_truncated",
                    "message": f"more than {self.max_overlap_reports} overlapping pairs; further pairs are counted only in ports_total",
                })
                break
            code = "duplicate_range" if (left["start"] == right["start"] and left["end"] == right["end"]) else "overlap"
            infos.append({
                "code": code,
                "message": f"ranges {left['start']}-{left['end']} and {right['start']}-{right['end']} overlap by {overlap} port(s)",
            })
            reported += 1
        if any(entry["start"] == MIN_PORT for entry in ranges):
            infos.append({
                "code": "reserved_port_zero",
                "message": "port 0 is reserved (RFC 1700); it parses but is not a usable destination port",
            })
        return infos

    @staticmethod
    def _ranges_to_set(ranges: list[dict[str, int]]) -> set[int]:
        ports: set[int] = set()
        for entry in ranges:
            ports.update(range(entry["start"], entry["end"] + 1))
        return ports

    def _run_parse(self, spec: Any, allow_all: bool) -> dict[str, Any]:
        parsed = self._parse_spec(spec, allow_all)
        base: dict[str, Any] = {"status": "success" if not parsed["errors"] else "error", "spec": spec}
        if parsed["errors"]:
            base.update({"ranges": [], "ports_total": 0, "errors": parsed["errors"], "infos": []})
            return base
        view = [{"start": r["start"], "end": r["end"], "size": r["end"] - r["start"] + 1} for r in parsed["ranges"]]
        base.update({
            "ranges": view,
            "ports_total": len(self._ranges_to_set(parsed["ranges"])),
            "errors": [],
            "infos": parsed["infos"][: self.max_infos],
        })
        return base

    # ---------------------------------------------------------------- expand

    def _run_expand(self, spec: Any, allow_all: bool, include_full: bool) -> dict[str, Any]:
        parsed = self._parse_spec(spec, allow_all)
        if parsed["errors"]:
            return {"status": "error", "spec": spec, "errors": parsed["errors"]}
        total = sum(r["end"] - r["start"] + 1 for r in parsed["ranges"])
        cap = MAX_PORT + 1 if include_full else self.max_expand_ports
        if total > cap:
            return {
                "status": "error",
                "spec": spec,
                "errors": [{
                    "code": "expand_cap_exceeded",
                    "position": None,
                    "segment": None,
                    "message": (
                        f"expansion yields {total} ports which exceeds the cap {cap}; "
                        + ("the full universe is 65536 ports" if include_full else "pass include_full=true to request the full list")
                    ),
                }],
                "ports_total": total,
            }
        ports = sorted(self._ranges_to_set(parsed["ranges"]))
        return {"status": "success", "spec": spec, "ports": ports, "total": total, "truncated": False}

    # -------------------------------------------------------------- compress

    @staticmethod
    def _merge(ports: set[int]) -> list[tuple[int, int]]:
        """Minimal inclusive ranges: overlapping AND adjacent runs are merged."""
        merged: list[tuple[int, int]] = []
        for value in sorted(ports):
            if merged and value <= merged[-1][1] + 1:
                merged[-1] = (merged[-1][0], max(merged[-1][1], value))
            else:
                merged.append((value, value))
        return merged

    @classmethod
    def _canonical(cls, merged: list[tuple[int, int]]) -> str:
        return ",".join(f"{a}" if a == b else f"{a}-{b}" for a, b in merged)

    def _run_compress(self, spec: Any, ports: Any, allow_all: bool) -> dict[str, Any]:
        if spec is not None and ports is not None:
            raise ValueError("pass either spec or ports to compress, not both")
        infos: list[dict[str, Any]] = []
        if ports is not None:
            if not isinstance(ports, (list, tuple, set)):
                raise TypeError("ports must be a list of integers")
            if len(ports) > self.max_input_ports:
                raise ValueError(f"ports exceeds max_input_ports={self.max_input_ports}")
            values: set[int] = set()
            for item in ports:
                if isinstance(item, bool) or not isinstance(item, int):
                    raise TypeError("ports must contain only integers")
                if not MIN_PORT <= item <= MAX_PORT:
                    raise ValueError(f"port {item} is outside {MIN_PORT}-{MAX_PORT}")
                values.add(item)
            if len(values) != len(ports):
                infos.append({"code": "deduplicated", "message": f"removed {len(ports) - len(values)} duplicate port(s)"})
            source = "ports"
        else:
            parsed = self._parse_spec(spec, allow_all)
            if parsed["errors"]:
                return {"status": "error", "spec": spec, "errors": parsed["errors"]}
            values = self._ranges_to_set(parsed["ranges"])
            source = "spec"
        merged = self._merge(values)
        return {
            "status": "success",
            "input": source,
            "spec": self._canonical(merged),
            "ranges": [{"start": a, "end": b, "size": b - a + 1} for a, b in merged],
            "count": len(values),
            "infos": infos,
        }

    # -------------------------------------------------------------- services

    def _run_services(self, spec: Any, allow_all: bool) -> dict[str, Any]:
        parsed = self._parse_spec(spec, allow_all)
        if parsed["errors"]:
            return {"status": "error", "spec": spec, "errors": parsed["errors"]}
        results: list[dict[str, Any]] = []
        for entry in parsed["ranges"]:
            names: list[dict[str, Any]] = []
            for port in range(entry["start"], entry["end"] + 1):
                for row in _SERVICE_TABLE.get(port, ()):
                    names.append({"port": port, "service": row["service"], "protocol": row["protocol"], "note": row["note"]})
            results.append({
                "range": f"{entry['start']}" if entry["start"] == entry["end"] else f"{entry['start']}-{entry['end']}",
                "size": entry["end"] - entry["start"] + 1,
                "names": names,
                "unknown": not names,
            })
            if len(results) >= self.max_service_results:
                break
        return {
            "status": "success",
            "spec": spec,
            "results": results,
            "coverage_note": _SERVICE_COVERAGE_NOTE if len(results) < self.max_service_results else (
                _SERVICE_COVERAGE_NOTE + f" Results truncated at max_service_results={self.max_service_results}."
            ),
        }

    # --------------------------------------------------------------- algebra

    def _run_algebra(self, spec_a: Any, spec_b: Any, op: Any, allow_all: bool) -> dict[str, Any]:
        if not isinstance(op, str):
            raise TypeError("op must be a string")
        operation = op.strip().lower()
        if operation not in _ALGEBRA_OPS:
            raise ValueError("op must be union, intersection, or difference")
        left = self._parse_spec(spec_a, allow_all)
        if left["errors"]:
            return {"status": "error", "spec": spec_a, "errors": left["errors"]}
        right = self._parse_spec(spec_b, allow_all)
        if right["errors"]:
            return {"status": "error", "spec": spec_b, "errors": right["errors"]}
        set_a = self._ranges_to_set(left["ranges"])
        set_b = self._ranges_to_set(right["ranges"])
        if operation == "union":
            outcome = set_a | set_b
        elif operation == "intersection":
            outcome = set_a & set_b
        else:
            outcome = set_a - set_b
        merged = self._merge(outcome)
        return {
            "status": "success",
            "op": operation,
            "spec_a": spec_a,
            "spec_b": spec_b,
            "result_spec": self._canonical(merged),
            "count": len(outcome),
            "ranges": [{"start": a, "end": b, "size": b - a + 1} for a, b in merged],
        }

    # ----------------------------------------------------------------- check

    def _policy_set(self, value: Any, field: str, spec: Any) -> set[int] | None | dict[str, Any]:
        """Parse a policy spec ('blocked'/'allowed'); None when absent, dict on error."""
        if value is None:
            return None
        parsed = self._parse_spec(value, allow_all=True)
        if parsed["errors"]:
            return {"status": "error", "spec": spec, "policy_field": field, "errors": parsed["errors"]}
        return self._ranges_to_set(parsed["ranges"])

    def _check_violations(
        self,
        merged: list[tuple[int, int]],
        blocked: set[int],
        allowed: set[int] | None,
    ) -> list[dict[str, Any]]:
        violations: list[dict[str, Any]] = []
        for a, b in merged:
            label = f"{a}" if a == b else f"{a}-{b}"
            here = set(range(a, b + 1))
            hits = here & blocked
            if hits:
                violations.append({
                    "range": label,
                    "rule": "blocked",
                    "detail": f"contains blocked {self._canonical(self._merge(hits))}",
                })
            stray = here - allowed if allowed is not None else set()
            if stray:
                violations.append({
                    "range": label,
                    "rule": "not_in_allowed_ranges",
                    "detail": self._stray_detail(self._merge(stray)),
                })
            if len(violations) >= self.max_violation_ranges * 2:
                violations.append({
                    "range": "*",
                    "rule": "violations_truncated",
                    "detail": f"more than {self.max_violation_ranges * 2} violations",
                })
                break
        return violations

    def _stray_detail(self, stray_merged: list[tuple[int, int]]) -> str:
        if len(stray_merged) > self.max_violation_ranges:
            head = self._canonical(stray_merged[: self.max_violation_ranges])
            return f"{len(stray_merged)} ranges outside allowed (first {self.max_violation_ranges}: {head})"
        return f"outside allowed: {self._canonical(stray_merged)}"

    def _run_check(
        self,
        spec: Any,
        allow_all: bool,
        allowed_ranges: Any,
        blocked_ports: Any,
        max_ports: Any,
    ) -> dict[str, Any]:
        if max_ports is not None and (
            isinstance(max_ports, bool) or not isinstance(max_ports, int) or max_ports < 0
        ):
            raise ValueError("max_ports must be a non-negative integer")
        parsed = self._parse_spec(spec, allow_all)
        if parsed["errors"]:
            return {"status": "error", "spec": spec, "errors": parsed["errors"]}
        blocked = self._policy_set(blocked_ports, "blocked_ports", spec)
        if isinstance(blocked, dict):
            return blocked
        allowed = self._policy_set(allowed_ranges, "allowed_ranges", spec)
        if isinstance(allowed, dict):
            return allowed
        merged = self._merge(self._ranges_to_set(parsed["ranges"]))
        total = sum(b - a + 1 for a, b in merged)
        violations = self._check_violations(merged, blocked or set(), allowed)

        if max_ports is not None and total > max_ports:
            violations.append({
                "range": f"total:{total}",
                "rule": "max_ports_exceeded",
                "detail": f"{total} ports exceed max_ports={max_ports}",
            })

        return {
            "status": "success",
            "spec": spec,
            "policy": {
                "allowed_ranges": allowed_ranges,
                "blocked_ports": blocked_ports,
                "max_ports": max_ports,
            },
            "ports_total": total,
            "violations": violations,
            "compliant": not violations,
        }
