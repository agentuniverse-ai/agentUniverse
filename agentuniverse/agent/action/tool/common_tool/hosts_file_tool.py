#!/usr/bin/env python3
# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: hosts_file_tool.py
# ruff: noqa: TRY003

"""Hosts file (``/etc/hosts``) parsing, validation and lookup analysis tool.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, pure-stdlib analyzer for hosts(5)
style files. The tool never touches DNS or any other network resource:
every answer is derived from the text it is handed, so results are
fully deterministic.

Five modes are supported:

* ``parse`` — full structural lint of a hosts text. Returns one entry
  per data line (normalized IP via ``ipaddress`` semantics, address
  family, canonical hostname, aliases, source line, raw snippet,
  attached comment), the comment lines, blank/total line counts and a
  findings list. Checks include: malformed IPv4/IPv6 addresses
  (mirroring ``ipaddress`` accept/reject — leading-zero octets are
  rejected, embedded IPv4 tails and ``::`` compression are accepted),
  IPv6 zone IDs (``fe80::1%eth0`` — **rejected** because hosts files
  have no interface scope concept, even though ``ipaddress`` itself
  accepts them), missing hostname after the IP, invalid hostname
  characters (letters, digits, hyphen and dot only; underscores are
  tolerated with an informational finding), raw unicode hostnames
  (rejected with punycode guidance — ``xn--`` forms are valid ASCII),
  hostnames with leading/trailing dots, hyphens at label edges, labels
  longer than 63 characters and names longer than 253 characters,
  aliases equal to the canonical name, duplicate hostname+IP pairs,
  conflicting entries (same hostname in the same address family mapped
  to different IPs — the **first** match wins per resolver order, both
  spellings and the winner are reported; IPv4+IPv6 coexistence for one
  hostname is legitimate), localhost conventions (``127.0.0.1``/``::1``
  lines, ``localhost`` as the canonical name), non-POSIX ``;`` comment
  starts (informational), tab-separated fields (informational) and
  uppercase hostnames (informational — hosts names are case-insensitive;
  the tool lowercases for comparison and preserves the raw spelling).
* ``lookup`` — resolve one hostname against a hosts text with
  first-match-wins semantics, exactly as the POSIX resolver contract
  prescribes for ``/etc/hosts`` (the contract ``getent hosts`` /
  ``gethostbyname`` implement): lines are scanned top to bottom, a line
  matches when the query equals its canonical hostname or any alias
  case-insensitively, and per address family the first matching line
  wins. The optional ``family`` filter (``v4``/``v6``) restricts the
  scan to one family, mirroring ``gethostbyname2``. Later same-family
  matches are shadowed and reported in ``overridden_by_earlier``.
* ``analyze`` — whole-file statistics: unique hostnames, a per-host
  summary (addresses, families, lines, same-family conflicts),
  localhost coverage for both families with recommendations, neutral
  reporting of sinkhole/blocking entries (hostnames mapped to the
  all-zeros address or ``127.0.0.1`` — the common ad/tracker pattern
  of Pi-hole-style blocklists; informational, not a verdict), IPv6
  readiness numbers and file stats.
* ``diff`` — compare two hosts texts with a hostname-keyed merge:
  added, removed and changed mappings (winner per family on each
  side), plus counts. Intended for reviewing hosts-file changes;
  comment-only edits are out of scope.
* ``generate`` — the inverse of ``parse``: build a well-formed hosts
  text from a ``{hostname: ip}`` mapping. Entries are emitted in
  mapping order, one single-space separated ``ip hostname`` pair per
  line under a single header comment; IPs are written in their
  normalized (``ipaddress`` compressed) form and hostname spelling is
  preserved verbatim. Only strictly valid hostnames are emitted
  (underscores — tolerated by ``parse`` with an informational flag —
  are rejected here with a clear message), so
  ``parse(generate(mapping))`` recovers the mapping exactly.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types, missing required
arguments, a bad ``family`` value, oversized inputs) raise a
``ValueError``, mirroring the other common tools. Errors that depend
on the *content being processed* are findings (``parse`` / ``analyze``
/ ``diff`` / ``lookup`` never fail on file content — a hosts file full
of garbage is a lint result, not an exception) except for ``generate``,
which must produce well-formed output and therefore returns a
structured ``error`` payload for an invalid IP or hostname token.

All listed outputs are capped (entries, comments, findings, per-host
summaries, diff lists, blocking samples, generate mappings) with
explicit ``truncated`` flags; counts and statistics are always exact.
"""

import ipaddress
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class HostsFileTool(Tool):
    """Parse, validate, look up, diff and generate hosts(5) files.

    Attributes:
        max_text_chars (int): Upper bound on one hosts text argument.
        max_lines (int): Upper bound on the number of physical lines.
        max_generate_mappings (int): Upper bound on generate mappings.
        max_entries_listed (int): Cap on the ``parse`` entries list.
        max_comments_listed (int): Cap on the ``parse`` comments list.
        max_findings (int): Cap on the findings list.
        max_per_host (int): Cap on the ``analyze`` per-host table.
        max_diff_items (int): Cap on each ``diff`` output list.
        max_blocking_sample (int): Cap on blocking-entry samples.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "hosts_file_tool"
    description: str = (
        "Hosts file (/etc/hosts) analysis tool — pure Python stdlib, "
        "no DNS or network access. Structural lint of a hosts text "
        "(mode='parse': per-line entries with normalized IPs, aliases "
        "and attached comments, plus findings for malformed IPs "
        "(IPv6 zone IDs rejected), invalid hostnames, duplicate and "
        "conflicting mappings — first match wins per resolver order — "
        "and localhost conventions), first-match-wins hostname lookup "
        "with optional v4/v6 family filter (mode='lookup'), whole-file "
        "statistics with localhost coverage and sinkhole-entry "
        "reporting (mode='analyze'), hostname-keyed diff of two hosts "
        "texts (mode='diff'), and deterministic hosts-text generation "
        "from a hostname-to-IP mapping (mode='generate')."
    )

    MODES: ClassVar[tuple] = ("parse", "lookup", "analyze", "diff", "generate")

    max_text_chars: ClassVar[int] = 8_000_000
    max_lines: ClassVar[int] = 200_000
    max_generate_mappings: ClassVar[int] = 1000
    max_entries_listed: ClassVar[int] = 2000
    max_comments_listed: ClassVar[int] = 2000
    max_findings: ClassVar[int] = 200
    max_per_host: ClassVar[int] = 512
    max_diff_items: ClassVar[int] = 512
    max_blocking_sample: ClassVar[int] = 64

    _raw_snippet_chars: ClassVar[int] = 80
    _comment_snippet_chars: ClassVar[int] = 120
    _max_hostname_len: ClassVar[int] = 253
    _max_label_len: ClassVar[int] = 63
    _loopback_ips: ClassVar[frozenset] = frozenset({"127.0.0.1", "::1"})
    # The all-zeros address here is the sinkhole constant used to detect
    # Pi-hole-style blocklist entries, not a socket bind target.
    _blocking_ips: ClassVar[frozenset] = frozenset({"0.0.0.0", "127.0.0.1"})  # noqa: S104

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        hosts_text: Any = None,
        hostname: Any = None,
        family: Any = None,
        hosts_text_a: Any = None,
        hosts_text_b: Any = None,
        mapping: Any = None,
    ) -> dict[str, Any]:
        """Run one hosts file analysis.

        Args:
            mode (str): One of ``parse`` / ``lookup`` / ``analyze`` /
                ``diff`` / ``generate``.
            hosts_text (str): The hosts file content for the ``parse``,
                ``lookup`` and ``analyze`` modes.
            hostname (str): The hostname to resolve, for ``lookup``.
            family (str): Optional ``"v4"`` or ``"v6"`` filter for
                ``lookup``; ``None`` scans both families.
            hosts_text_a (str): The first (old) hosts text for ``diff``.
            hosts_text_b (str): The second (new) hosts text for ``diff``.
            mapping (Dict[str, str]): ``{hostname: ip}`` mapping for
                ``generate``; insertion order is preserved in the
                generated text.

        Returns:
            Dict[str, Any]: The analysis result (always carrying the
                call context). Content problems in the hosts text are
                reported as findings, never as exceptions; the
                ``generate`` mode returns a structured ``error``
                payload for an invalid IP or hostname token.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        if mode == "generate":
            return self._run_generate(mapping)

        family_clean = self._validate_family(family)
        if mode == "lookup":
            return self._run_lookup(hosts_text, hostname, family_clean)
        if mode == "diff":
            text_a = self._validate_hosts_text(hosts_text_a, "hosts_text_a")
            text_b = self._validate_hosts_text(hosts_text_b, "hosts_text_b")
            return self._run_diff(text_a, text_b)

        text = self._validate_hosts_text(hosts_text, "hosts_text")
        scan = self._scan(text)
        if mode == "parse":
            return self._parse_result(scan)
        return self._analyze_result(scan)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"hosts_file_tool: {message}")

    @classmethod
    def _validate_family(cls, value: Any) -> str | None:
        """Validate the optional lookup family filter."""
        if value is None:
            return None
        if value not in ("v4", "v6"):
            cls._invalid(f"family must be 'v4', 'v6' or None (got {value!r})")
        return value

    @classmethod
    def _validate_hosts_text(cls, value: Any, label: str) -> str:
        """Validate a required hosts text argument (non-empty, bounded)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a non-empty string (got {value!r})")
        if not value.strip():
            cls._invalid(f"{label} must be a non-empty string (got blank text)")
        if len(value) > cls.max_text_chars:
            cls._invalid(
                f"{label} exceeds the {cls.max_text_chars}-character limit "
                f"(got {len(value)} characters)"
            )
        if value.count("\n") + 1 > cls.max_lines:
            cls._invalid(f"{label} exceeds the {cls.max_lines}-line limit")
        return value

    @classmethod
    def _validate_hostname_query(cls, value: Any) -> str:
        """Validate the lookup hostname parameter."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"hostname must be a non-empty string (got {value!r})")
        token = value.strip()
        if not token:
            cls._invalid(f"hostname must be a non-empty string (got {value!r})")
        return token

    @classmethod
    def _snippet(cls, text: str, limit: int) -> str:
        """Truncate a snippet deterministically for bounded output."""
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."

    # ------------------------------------------------------------------ #
    # Core scanner (shared by parse / lookup / analyze / diff)
    # ------------------------------------------------------------------ #

    def _new_state(self) -> dict[str, Any]:
        """Create the mutable accumulator shared by the scan helpers."""
        return {
            "findings": [],
            "totals": {"error": 0, "warning": 0, "info": 0, "all": 0},
            "entries": [],
            "comments": [],
            "registry": {},
            "line_meta": {},
            "pair_first_line": {},
            "blank_lines": 0,
            "comment_lines": 0,
            "crlf_lines": 0,
            "tab_lines": 0,
            "first_tab_line": None,
            "uppercase_lines": 0,
            "first_uppercase_line": None,
            "semicolon_lines": 0,
            "valid_entries": 0,
            "invalid_entries": 0,
            "ipv4_entries": 0,
            "ipv6_entries": 0,
            "duplicate_pairs": 0,
            "conflicting_hostnames": set(),
        }

    @classmethod
    def _add_finding(
        cls, state: dict[str, Any], line: int | None, severity: str, code: str, message: str
    ) -> None:
        """Record one finding (exact totals, capped listing)."""
        totals: dict[str, int] = state["totals"]
        totals[severity] += 1
        totals["all"] += 1
        if len(state["findings"]) < cls.max_findings:
            state["findings"].append(
                {
                    "line": line,
                    "severity": severity,
                    "code": code,
                    "message": str(message)[:500],
                }
            )

    def _record_comment(self, state: dict[str, Any], line: int, text: str) -> None:
        """Record one comment line (capped listing)."""
        state["comment_lines"] += 1
        if len(state["comments"]) < self.max_comments_listed:
            state["comments"].append(
                {"line": line, "text": self._snippet(text, self._comment_snippet_chars)}
            )

    def _scan(self, text: str) -> dict[str, Any]:
        """Scan a hosts text once and build every shared structure.

        Returns a dict with the capped entries / comments / findings
        lists (plus exact totals), exact aggregates, the hostname
        registry (lowercase hostname -> occurrence list, file order)
        and per-line name metadata used by ``lookup``.
        """
        lines = text.split("\n")
        if len(lines) > 1 and lines[-1] == "":
            # A terminating newline does not create an extra blank line.
            lines.pop()

        state = self._new_state()
        for index, raw_line in enumerate(lines, start=1):
            line = raw_line
            if line.endswith("\r"):
                state["crlf_lines"] += 1
                line = line[:-1]
            stripped = line.strip()
            if not stripped:
                state["blank_lines"] += 1
            elif stripped.startswith("#"):
                self._record_comment(state, index, stripped[1:].strip())
            else:
                data_part, _, comment_part = line.partition("#")
                if not data_part.strip():
                    self._record_comment(state, index, comment_part.strip())
                else:
                    self._process_data_line(state, index, line, data_part, comment_part)

        if state["tab_lines"]:
            self._add_finding(
                state,
                None,
                "info",
                "tab_separator",
                f"{state['tab_lines']} data line(s) use tab separators (first on "
                f"line {state['first_tab_line']}) — tabs are valid separators in "
                "hosts files; listed for awareness only",
            )
        if state["uppercase_lines"]:
            self._add_finding(
                state,
                None,
                "info",
                "uppercase_hostname",
                f"{state['uppercase_lines']} line(s) contain uppercase hostnames "
                f"(first on line {state['first_uppercase_line']}) — hosts names "
                "are case-insensitive; the tool lowercases for comparison and "
                "preserves the raw spelling",
            )
        return self._state_to_scan(state, lines)

    def _state_to_scan(
        self, state: dict[str, Any], lines: list[str]
    ) -> dict[str, Any]:
        """Freeze the mutable scan state into the shared scan result."""
        registry: dict[str, list[dict[str, Any]]] = state["registry"]
        unique_ips: set[str] = set()
        for occurrences in registry.values():
            for occ in occurrences:
                unique_ips.add(occ["ip"])
        totals: dict[str, int] = state["totals"]
        data_lines = len(lines) - state["blank_lines"] - state["comment_lines"]
        findings: list[dict[str, Any]] = state["findings"]
        return {
            "total_lines": len(lines),
            "blank_lines": state["blank_lines"],
            "comment_lines": state["comment_lines"],
            "data_lines": data_lines,
            "crlf_lines": state["crlf_lines"],
            "entries": state["entries"],
            "entries_total": data_lines,
            "entries_truncated": data_lines > len(state["entries"]),
            "comments": state["comments"],
            "comments_truncated": state["comment_lines"] > len(state["comments"]),
            "findings": findings,
            "findings_total": totals["all"],
            "findings_truncated": totals["all"] > len(findings),
            "severity_totals": {
                "error": totals["error"],
                "warning": totals["warning"],
                "info": totals["info"],
            },
            "registry": registry,
            "line_meta": state["line_meta"],
            "stats": {
                "total_entries": data_lines,
                "valid_entries": state["valid_entries"],
                "invalid_entries": state["invalid_entries"],
                "ipv4_entries": state["ipv4_entries"],
                "ipv6_entries": state["ipv6_entries"],
                "unique_hostnames": len(registry),
                "unique_ips": len(unique_ips),
                "duplicate_pairs": state["duplicate_pairs"],
                "conflicting_hostnames": len(state["conflicting_hostnames"]),
                "comment_lines": state["comment_lines"],
                "blank_lines": state["blank_lines"],
                "crlf_lines": state["crlf_lines"],
                "tab_lines": state["tab_lines"],
                "uppercase_hostname_lines": state["uppercase_lines"],
                "semicolon_comment_lines": state["semicolon_lines"],
            },
        }

    # ------------------------------------------------------------------ #
    # Per-data-line processing
    # ------------------------------------------------------------------ #

    def _process_data_line(
        self,
        state: dict[str, Any],
        index: int,
        line: str,
        data_part: str,
        comment_part: str,
    ) -> None:
        """Parse and register one data (non-comment, non-blank) line."""
        data_stripped = data_part.strip()
        if data_stripped.startswith(";"):
            state["semicolon_lines"] += 1
            self._add_finding(
                state,
                index,
                "info",
                "semicolon_comment",
                "line starts with ';' — POSIX hosts files treat only '#' as a "
                "comment start, so this line is parsed as data (some parsers "
                "accept ';' comments; that is non-portable)",
            )

        if "\t" in data_part:
            state["tab_lines"] += 1
            if state["first_tab_line"] is None:
                state["first_tab_line"] = index

        tokens = data_part.split()
        ip_raw = tokens[0]
        hostname_tokens = tokens[1:]
        comment_text = comment_part.strip()
        entry: dict[str, Any] = {
            "line": index,
            "raw": self._snippet(line, self._raw_snippet_chars),
            "ip": None,
            "ip_raw": ip_raw,
            "ip_version": None,
            "canonical_hostname": None,
            "aliases": [],
            "invalid_hostnames": [],
            "comment_attached": (
                self._snippet(comment_text, self._comment_snippet_chars)
                if comment_text
                else None
            ),
            "valid": False,
        }

        ip_norm, ip_version, ip_code, ip_reason = self._parse_ip_token(ip_raw)
        if ip_norm is None:
            self._add_finding(state, index, "error", ip_code, ip_reason)
        else:
            entry["ip"] = ip_norm
            entry["ip_version"] = ip_version
            state["ipv4_entries" if ip_version == 4 else "ipv6_entries"] += 1

        if hostname_tokens:
            valid_names = self._process_hostnames(state, entry, hostname_tokens, index)
            state["line_meta"][index] = {
                "canonical_lower": hostname_tokens[0].lower(),
                "aliases": list(entry["aliases"]),
            }
            if ip_norm is not None:
                self._register_names(state, ip_norm, ip_raw, ip_version, valid_names, index)
                self._localhost_findings(state, ip_norm, valid_names, index)
        else:
            self._add_finding(
                state,
                index,
                "error",
                "missing_hostname",
                f"line {index} has an address but no hostname "
                f"(got {self._snippet(ip_raw, 64)!r} only)",
            )

        if entry["ip"] is not None and entry["canonical_hostname"]:
            if entry["invalid_hostnames"]:
                state["invalid_entries"] += 1
            else:
                entry["valid"] = True
                state["valid_entries"] += 1
        else:
            state["invalid_entries"] += 1
        if len(state["entries"]) < self.max_entries_listed:
            state["entries"].append(entry)

    def _process_hostnames(
        self,
        state: dict[str, Any],
        entry: dict[str, Any],
        hostname_tokens: list[str],
        index: int,
    ) -> list[str]:
        """Validate the hostname tokens of one line.

        Fills ``canonical_hostname`` / ``aliases`` / ``invalid_hostnames``
        on the entry and returns the valid names in token order.
        """
        if any("A" <= ch <= "Z" for tok in hostname_tokens for ch in tok):
            state["uppercase_lines"] += 1
            if state["first_uppercase_line"] is None:
                state["first_uppercase_line"] = index

        seen_on_line: set[str] = set()
        valid_names: list[str] = []
        for position, token in enumerate(hostname_tokens):
            verdict, code, reason = self._check_hostname(token)
            if verdict == "invalid":
                entry["invalid_hostnames"].append({"token": token, "code": code})
                label = "canonical hostname" if position == 0 else f"alias #{position}"
                self._add_finding(
                    state,
                    index,
                    "error",
                    "invalid_hostname",
                    f"{label} {self._snippet(token, 64)!r} on line {index} is "
                    f"invalid: {reason}",
                )
                continue
            if verdict == "underscore":
                self._add_finding(
                    state,
                    index,
                    "info",
                    "underscore_hostname",
                    f"hostname {self._snippet(token, 64)!r} contains '_' — not "
                    "valid in hosts(5)/DNS names, but tolerated by some stacks "
                    "(informational)",
                )
            lower = token.lower()
            if lower in seen_on_line:
                self._add_finding(
                    state,
                    index,
                    "warning",
                    "alias_equals_canonical",
                    f"hostname {self._snippet(token, 64)!r} appears more than "
                    f"once on line {index} (duplicates are ignored)",
                )
                continue
            seen_on_line.add(lower)
            if position == 0:
                entry["canonical_hostname"] = token
            else:
                entry["aliases"].append(token)
            valid_names.append(token)
        return valid_names

    def _register_names(
        self,
        state: dict[str, Any],
        ip_norm: str,
        ip_raw: str,
        ip_version: int,
        valid_names: list[str],
        index: int,
    ) -> None:
        """Register every valid hostname token against the line's address.

        The first occurrence per hostname and family wins per the POSIX
        resolver contract; later same-family mappings are flagged as
        duplicates (identical address) or conflicts (different address).
        """
        registry: dict[str, list[dict[str, Any]]] = state["registry"]
        pair_first_line: dict[tuple[str, str], int] = state["pair_first_line"]
        for token in valid_names:
            lower = token.lower()
            occurrences = registry.setdefault(lower, [])
            same_family = [occ for occ in occurrences if occ["family"] == ip_version]
            if same_family:
                winner = same_family[0]
                if winner["ip"] == ip_norm:
                    pair_key = (lower, ip_norm)
                    if pair_key not in pair_first_line:
                        pair_first_line[pair_key] = winner["line"]
                    state["duplicate_pairs"] += 1
                    self._add_finding(
                        state,
                        index,
                        "warning",
                        "duplicate_hostname_ip",
                        f"hostname {lower!r} is mapped to {ip_norm} again on "
                        f"line {index} — identical to line "
                        f"{pair_first_line[pair_key]}; the first entry wins and "
                        "this one is redundant",
                    )
                else:
                    state["conflicting_hostnames"].add(lower)
                    self._add_finding(
                        state,
                        index,
                        "warning",
                        "conflicting_entry",
                        f"hostname {lower!r} (IPv{ip_version}) is mapped to "
                        f"{winner['ip']} on line {winner['line']} and to "
                        f"{ip_norm} on line {index} — the FIRST match wins per "
                        "resolver order, so this line's address is shadowed",
                    )
            occurrences.append(
                {
                    "ip": ip_norm,
                    "ip_raw": ip_raw,
                    "line": index,
                    "family": ip_version,
                }
            )

    def _localhost_findings(
        self,
        state: dict[str, Any],
        ip_norm: str,
        valid_names: list[str],
        index: int,
    ) -> None:
        """Check the 127.0.0.1 / ::1 / localhost conventions for a line."""
        lower_names = [t.lower() for t in valid_names]
        if ip_norm in self._loopback_ips:
            if "localhost" not in lower_names:
                self._add_finding(
                    state,
                    index,
                    "info",
                    "loopback_without_localhost",
                    f"line {index} maps {ip_norm} without 'localhost' — "
                    "conventional hosts files map the loopback address to "
                    "localhost first (intentional in blocking configs)",
                )
            elif lower_names[0] != "localhost":
                self._add_finding(
                    state,
                    index,
                    "info",
                    "localhost_not_canonical",
                    f"'localhost' appears as an alias on line {index} — the "
                    "convention is to list it as the canonical (first) name",
                )
        for lower in lower_names:
            if lower == "localhost" and ip_norm not in self._loopback_ips:
                self._add_finding(
                    state,
                    index,
                    "warning",
                    "localhost_non_loopback",
                    f"'localhost' is mapped to {ip_norm} on line {index} — "
                    "conventionally it maps to 127.0.0.1 or ::1",
                )

    # ------------------------------------------------------------------ #
    # Token-level checks
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_ip_token(
        cls, token: str
    ) -> tuple[str | None, int | None, str | None, str | None]:
        """Parse one address token.

        Returns ``(normalized_ip, version, code, reason)`` where the
        first two are ``None`` on failure with an error ``code`` and a
        human-readable ``reason``. Zone IDs are rejected explicitly:
        ``ipaddress`` accepts them (they are meaningful for connected
        sockets), but hosts files have no interface scope concept.
        """
        malformed = (
            f"{cls._snippet(token, 64)!r} does not appear to be a valid "
            "IPv4 or IPv6 address (check octet ranges, hexadecimal "
            "groups and stray characters; IPv4 octets may not have "
            "leading zeros)"
        )
        if "%" in token:
            base = token.split("%", 1)[0]
            try:
                ipaddress.ip_address(base)
            except ValueError:
                return None, None, "malformed_ip", malformed
            return (
                None,
                None,
                "ip_zone_id",
                f"{cls._snippet(token, 64)!r} carries a zone ID ('%zone') — "
                "zone IDs identify a network interface on connected sockets "
                "and are not allowed in hosts file addresses; drop the "
                "'%...' part",
            )
        try:
            addr = ipaddress.ip_address(token)
        except ValueError:
            return None, None, "malformed_ip", malformed
        return str(addr), addr.version, None, None

    @classmethod
    def _hostname_char_scan(cls, token: str) -> tuple[bool, str | None]:
        """Scan the character set of a hostname token.

        Returns ``(has_underscore, bad_char)`` — ``bad_char`` is the
        first character outside letters / digits / hyphen / dot /
        (tolerated) underscore, or ``None`` when the set is clean.
        """
        has_underscore = False
        for char in token:
            if char == "_":
                has_underscore = True
            elif char in ".-":
                continue
            elif not ("a" <= char <= "z" or "A" <= char <= "Z" or "0" <= char <= "9"):
                return has_underscore, char
        return has_underscore, None

    @classmethod
    def _check_hostname(cls, token: str) -> tuple[str, str | None, str | None]:
        """Check one hostname token against the hosts(5) name grammar.

        Returns ``(verdict, code, reason)`` where verdict is one of
        ``valid`` / ``underscore`` (valid with an informational flag) /
        ``invalid``. Allowed characters are ASCII letters, digits,
        hyphen and dot (plus the tolerated underscore); labels must be
        1-63 characters without hyphens at the edges, total length is
        capped at 253, and leading/trailing dots are rejected. Names
        are matched case-insensitively by callers (raw spelling is
        preserved in entries).
        """
        if any(ord(c) > 127 for c in token):
            return (
                "invalid",
                "non_ascii",
                "non-ASCII characters are not valid in hosts file names — "
                "convert the internationalized name to its ASCII punycode "
                "('xn--...') form",
            )
        if len(token) > cls._max_hostname_len:
            return (
                "invalid",
                "hostname_too_long",
                f"length {len(token)} exceeds the {cls._max_hostname_len}"
                "-character limit for hostnames",
            )
        if token.startswith("."):
            return "invalid", "leading_dot", "hostnames must not start with a dot"
        if token.endswith("."):
            return (
                "invalid",
                "trailing_dot",
                "hostnames in hosts files are written without the DNS root "
                "dot (a trailing '.' marks the fully-qualified root form)",
            )
        has_underscore, bad_char = cls._hostname_char_scan(token)
        if bad_char is not None:
            return (
                "invalid",
                "invalid_chars",
                f"character {bad_char!r} is not allowed — hosts file names "
                "may only contain letters, digits, hyphens and dots",
            )
        label_problem = cls._label_problem(token)
        if label_problem is not None:
            return "invalid", label_problem[0], label_problem[1]
        if has_underscore:
            return "underscore", None, None
        return "valid", None, None

    @classmethod
    def _label_problem(cls, token: str) -> tuple[str, str] | None:
        """Find the first label-level grammar problem, if any."""
        for label in token.split("."):
            if not label:
                return (
                    "empty_label",
                    "empty label (from consecutive dots) is not allowed",
                )
            if len(label) > cls._max_label_len:
                return (
                    "label_too_long",
                    f"label {cls._snippet(label, 40)!r} exceeds the "
                    f"{cls._max_label_len}-character limit",
                )
            if label.startswith("-") or label.endswith("-"):
                return (
                    "label_hyphen_edge",
                    f"label {cls._snippet(label, 40)!r} starts or ends with "
                    "a hyphen — hyphens are only allowed inside labels",
                )
        return None

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _parse_result(self, scan: dict[str, Any]) -> dict[str, Any]:
        """Build the parse-mode response from a scan."""
        return {
            "mode": "parse",
            "total_lines": scan["total_lines"],
            "blank_lines": scan["blank_lines"],
            "comment_lines": scan["comment_lines"],
            "crlf_lines": scan["crlf_lines"],
            "entries": scan["entries"],
            "entries_total": scan["entries_total"],
            "entries_truncated": scan["entries_truncated"],
            "comments": scan["comments"],
            "comments_total": scan["comment_lines"],
            "comments_truncated": scan["comments_truncated"],
            "findings": scan["findings"],
            "findings_total": scan["findings_total"],
            "findings_truncated": scan["findings_truncated"],
            "summary": {
                **scan["severity_totals"],
                "valid_entries": scan["stats"]["valid_entries"],
                "invalid_entries": scan["stats"]["invalid_entries"],
                "unique_hostnames": scan["stats"]["unique_hostnames"],
                "unique_ips": scan["stats"]["unique_ips"],
            },
            "stats": scan["stats"],
        }

    # ------------------------------------------------------------------ #
    # lookup mode
    # ------------------------------------------------------------------ #

    def _run_lookup(
        self, hosts_text: Any, hostname: Any, family: str | None
    ) -> dict[str, Any]:
        """Resolve one hostname with first-match-wins semantics."""
        text = self._validate_hosts_text(hosts_text, "hosts_text")
        query = self._validate_hostname_query(hostname)
        scan = self._scan(text)

        key = query.lower()
        family_id = int(family[1]) if family else None
        occurrences = scan["registry"].get(key, [])

        winners: dict[int, dict[str, Any]] = {}
        overridden: list[dict[str, Any]] = []
        for occ in occurrences:
            fam = occ["family"]
            if family_id is not None and fam != family_id:
                continue
            if fam not in winners:
                winners[fam] = occ
            else:
                overridden.append(
                    {"ip": occ["ip"], "line": occ["line"], "family": f"v{fam}"}
                )

        ordered = sorted(winners.values(), key=lambda occ: occ["line"])
        result: dict[str, Any] = {
            "mode": "lookup",
            "hostname": query,
            "hostname_key": key,
            "family": family,
            "addresses": [occ["ip"] for occ in ordered],
            "from_line": ordered[0]["line"] if ordered else None,
            "canonical": None,
            "aliases": [],
            "overridden_by_earlier": overridden,
            "not_found": not ordered,
        }
        if ordered:
            winner = ordered[0]
            meta = scan["line_meta"].get(winner["line"], {})
            result["canonical"] = meta.get("canonical_lower") == key
            result["aliases"] = list(meta.get("aliases", []))
        return result

    # ------------------------------------------------------------------ #
    # analyze mode
    # ------------------------------------------------------------------ #

    def _per_host_entry(self, occurrences: list[dict[str, Any]]) -> dict[str, Any]:
        """Summarize one hostname's occurrences (ips/families/lines/conflicts)."""
        ips: list[str] = []
        for occ in occurrences:
            if occ["ip"] not in ips:
                ips.append(occ["ip"])
        conflicts: list[dict[str, Any]] = []
        for fam in (4, 6):
            distinct: list[dict[str, Any]] = []
            for occ in occurrences:
                if occ["family"] == fam and occ["ip"] not in [d["ip"] for d in distinct]:
                    distinct.append(occ)
            if len(distinct) > 1:
                conflicts.append(
                    {
                        "family": f"v{fam}",
                        "winner": {"ip": distinct[0]["ip"], "line": distinct[0]["line"]},
                        "losers": [
                            {"ip": occ["ip"], "line": occ["line"]} for occ in distinct[1:]
                        ],
                    }
                )
        return {
            "ips": ips,
            "families": sorted({f"v{occ['family']}" for occ in occurrences}),
            "lines": sorted({occ["line"] for occ in occurrences}),
            "conflicts": conflicts,
        }

    def _localhost_coverage(
        self, registry: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Coverage of the conventional localhost entries, plus advice."""
        localhost = registry.get("localhost", [])
        has_v4 = any(o["family"] == 4 and o["ip"] == "127.0.0.1" for o in localhost)
        has_v6 = any(o["family"] == 6 and o["ip"] == "::1" for o in localhost)
        recommendations: list[str] = []
        if not has_v4:
            recommendations.append(
                "no '127.0.0.1 localhost' entry found — conventional hosts "
                "files include one for IPv4 loopback resolution"
            )
        if not has_v6:
            recommendations.append(
                "no '::1 localhost' entry found — adding one covers IPv6 "
                "loopback resolution"
            )
        return {"ipv4": has_v4, "ipv6": has_v6, "recommendations": recommendations}

    def _blocking_report(
        self, registry: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Neutral report of sinkhole-mapped hostnames (Pi-hole pattern)."""
        count = 0
        sample: list[dict[str, Any]] = []
        for name in registry:
            if name == "localhost":
                continue
            for occ in registry[name]:
                if occ["ip"] in self._blocking_ips:
                    count += 1
                    if len(sample) < self.max_blocking_sample:
                        sample.append(
                            {"hostname": name, "ip": occ["ip"], "line": occ["line"]}
                        )
        return {
            "count": count,
            "sample": sample,
            "note": "neutral observation: hostnames mapped to the all-zeros "
            "address or 127.0.0.1 follow the common ad/tracker sinkhole "
            "pattern (Pi-hole-style blocklists); listed for information, "
            "not a verdict",
        }

    def _analyze_result(self, scan: dict[str, Any]) -> dict[str, Any]:
        """Build the analyze-mode response from a scan."""
        registry: dict[str, list[dict[str, Any]]] = scan["registry"]
        per_host: dict[str, Any] = {}
        per_host_truncated = False
        for name in sorted(registry):
            if len(per_host) >= self.max_per_host:
                per_host_truncated = True
                break
            per_host[name] = self._per_host_entry(registry[name])

        coverage = self._localhost_coverage(registry)
        ipv6_hosts = {
            name
            for name in registry
            if any(occ["family"] == 6 for occ in registry[name])
        }
        return {
            "mode": "analyze",
            "unique_hosts": len(registry),
            "per_host": per_host,
            "per_host_total": len(registry),
            "per_host_truncated": per_host_truncated,
            "localhost_coverage": coverage,
            "blocking_entries": self._blocking_report(registry),
            "ipv6_readiness": {
                "ipv6_entries": scan["stats"]["ipv6_entries"],
                "has_ipv6_localhost": coverage["ipv6"],
                "distinct_ipv6_hosts": len(ipv6_hosts),
                "ipv4_only_hosts": sum(
                    1
                    for name in registry
                    if all(occ["family"] == 4 for occ in registry[name])
                ),
            },
            "stats": scan["stats"],
            "findings": scan["findings"],
            "findings_total": scan["findings_total"],
            "findings_truncated": scan["findings_truncated"],
        }

    # ------------------------------------------------------------------ #
    # diff mode
    # ------------------------------------------------------------------ #

    def _run_diff(self, text_a: str, text_b: str) -> dict[str, Any]:
        """Compare two hosts texts with a hostname-keyed merge."""
        map_a = self._winner_map(self._scan(text_a))
        map_b = self._winner_map(self._scan(text_b))

        added: list[dict[str, Any]] = []
        removed: list[dict[str, Any]] = []
        changed: list[dict[str, Any]] = []
        added_truncated = removed_truncated = changed_truncated = False
        unchanged = 0
        changed_total = 0

        def as_item(name: str, winners: dict[str, dict[str, Any]]) -> dict[str, Any]:
            return {"hostname": name, "v4": winners.get("v4"), "v6": winners.get("v6")}

        for name in sorted(set(map_a) | set(map_b)):
            in_a, in_b = name in map_a, name in map_b
            if in_a and not in_b:
                if len(removed) < self.max_diff_items:
                    removed.append(as_item(name, map_a[name]))
                else:
                    removed_truncated = True
            elif in_b and not in_a:
                if len(added) < self.max_diff_items:
                    added.append(as_item(name, map_b[name]))
                else:
                    added_truncated = True
            elif map_a[name] == map_b[name]:
                unchanged += 1
            else:
                changed_total += 1
                if len(changed) < self.max_diff_items:
                    changed.append(
                        {
                            "hostname": name,
                            "a": as_item(name, map_a[name]),
                            "b": as_item(name, map_b[name]),
                        }
                    )
                else:
                    changed_truncated = True

        return {
            "mode": "diff",
            "added": added,
            "removed": removed,
            "changed": changed,
            "counts": {
                "added": len(set(map_b) - set(map_a)),
                "removed": len(set(map_a) - set(map_b)),
                "changed": changed_total,
                "unchanged": unchanged,
            },
            "added_truncated": added_truncated,
            "removed_truncated": removed_truncated,
            "changed_truncated": changed_truncated,
        }

    def _winner_map(
        self, scan: dict[str, Any]
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """First-match-winner per hostname and family from a scan."""
        winners: dict[str, dict[str, dict[str, Any]]] = {}
        for name, occurrences in scan["registry"].items():
            per_family: dict[str, dict[str, Any]] = {}
            for fam in (4, 6):
                first = next((occ for occ in occurrences if occ["family"] == fam), None)
                if first is not None:
                    per_family[f"v{fam}"] = {"ip": first["ip"], "line": first["line"]}
            if per_family:
                winners[name] = per_family
        return winners

    # ------------------------------------------------------------------ #
    # generate mode
    # ------------------------------------------------------------------ #

    def _validate_mapping_shape(self, mapping: Any) -> None:
        """Parameter-level validation of the generate mapping."""
        if not isinstance(mapping, dict):
            self._invalid(
                f"mapping must be a non-empty dict of {{hostname: ip}} (got {mapping!r})"
            )
        if not mapping:
            self._invalid("mapping must be a non-empty dict of {hostname: ip} (got {})")
        if len(mapping) > self.max_generate_mappings:
            self._invalid(
                f"mapping exceeds the {self.max_generate_mappings}-entry limit "
                f"(got {len(mapping)} entries)"
            )
        seen_keys: dict[str, str] = {}
        for key, value in mapping.items():
            if key is None or isinstance(key, bool) or not isinstance(key, str):
                self._invalid(f"every mapping key must be a non-empty string (got {key!r})")
            clean_key = key.strip()
            if not clean_key:
                self._invalid(f"every mapping key must be a non-empty string (got {key!r})")
            lower_key = clean_key.lower()
            if lower_key in seen_keys and seen_keys[lower_key] != clean_key:
                self._invalid(
                    f"mapping keys collide case-insensitively: "
                    f"{seen_keys[lower_key]!r} and {clean_key!r}"
                )
            seen_keys[lower_key] = clean_key
            if value is None or isinstance(value, bool) or not isinstance(value, str):
                self._invalid(
                    f"the IP for {clean_key!r} must be a non-empty string (got {value!r})"
                )
            if not value.strip():
                self._invalid(
                    f"the IP for {clean_key!r} must be a non-empty string (got blank)"
                )

    def _run_generate(self, mapping: Any) -> dict[str, Any]:
        """Generate a well-formed hosts text from a hostname->ip mapping."""
        self._validate_mapping_shape(mapping)

        lines = ["# generated by hosts_file_tool"]
        hostnames: list[str] = []
        for key, value in mapping.items():
            clean_key = key.strip()
            clean_value = value.strip()
            ip_norm, _, ip_code, ip_reason = self._parse_ip_token(clean_value)
            if ip_norm is None:
                return self._error_result(
                    "generate",
                    "invalid_ip",
                    f"the IP for hostname {clean_key!r} is invalid: {ip_reason}",
                    extra={
                        "hostname": self._snippet(clean_key, 64),
                        "input": self._snippet(clean_value, 64),
                        "code": ip_code,
                    },
                )
            verdict, code, reason = self._check_hostname(clean_key)
            if verdict == "underscore":
                return self._error_result(
                    "generate",
                    "invalid_hostname",
                    f"hostname {clean_key!r} contains '_' — generate only emits "
                    "strictly valid hosts(5) names (parse tolerates underscores "
                    "with an informational flag, generate does not emit them)",
                    extra={"hostname": self._snippet(clean_key, 64), "code": "underscore"},
                )
            if verdict == "invalid":
                return self._error_result(
                    "generate",
                    "invalid_hostname",
                    f"hostname {clean_key!r} is invalid: {reason}",
                    extra={"hostname": self._snippet(clean_key, 64), "code": code},
                )
            lines.append(f"{ip_norm} {clean_key}")
            hostnames.append(clean_key)

        return {
            "mode": "generate",
            "hosts_text": "\n".join(lines) + "\n",
            "entry_count": len(hostnames),
            "hostnames": hostnames,
            "notes": [
                "entries are emitted in mapping order, one single-space "
                "separated 'ip hostname' pair per line",
                "IPs are written in their normalized (ipaddress compressed) form",
                "hostname spelling is preserved verbatim; a single header "
                "comment marks the file as generated",
            ],
        }

    @classmethod
    def _error_result(
        cls,
        mode: str,
        error_type: str,
        message: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        error: dict[str, Any] = {"type": error_type, "message": str(message)[:500]}
        if extra:
            error.update(extra)
        return {"mode": mode, "error": error}
