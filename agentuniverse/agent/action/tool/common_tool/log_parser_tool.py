#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: log_parser_tool.py

"""Common log-format parsing tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency log parsing utility
for ops agents: no such parser exists among the common tools, and ops
workflows constantly need to eyeball an unknown log file, structure it,
and slice it by severity or status.

The tool is a thin, strictly-validated façade over the ``re`` module
and supports three modes:

* ``detect`` — sample lines and guess the dominant format by per-line
  voting: every sampled line is tested against each format pattern and
  votes for the first one that matches; the format with the most votes
  wins (ties are broken by the fixed detection priority order), the
  confidence is reported as ``winner votes / total votes``, and lines
  that voted for another format or matched nothing are counted under
  ``mixed_lines``. Recognized formats: ``combined`` (Apache/Nginx
  combined: ``IP - user [time] "REQ" status bytes "ref" "ua"``),
  ``common`` (Apache common access log, no referrer/agent), ``syslog``
  (RFC 3164 style ``Mon DD HH:MM:SS host proc[pid]: msg``), ``leveled``
  (ISO-timestamp + level, e.g. ``2026-10-19T10:30:00Z LEVEL name msg``
  with optional ``[LEVEL]`` brackets, plus bare ``[LEVEL] msg`` lines)
  and ``keyvalue`` (space-separated ``k=v`` pairs, values optionally
  quoted).
* ``parse`` — turn every line into a structured record using an
  explicitly given format (whitelisted) or the auto-detected dominant
  format. Combined records carry ``ip / ident / user / time / method /
  path / protocol / status / bytes / referrer / agent`` (quoted fields
  follow the Apache escaping convention: ``\"`` inside the referrer or
  agent is accepted and the record carries the unescaped value); syslog
  records carry ``timestamp / host / proc / pid / message``; leveled
  records carry ``timestamp / level / logger / message``; keyvalue
  records are the flat ``key=value`` dictionary itself. Lines that do
  not match the chosen format come back as ``{"raw": ..., "error":
  ...}`` entries and are tallied in ``failed_count`` — parsing never
  raises on bad lines.
* ``filter`` — parse first (explicit or detected format), then keep the
  records whose fields satisfy every given predicate: ``level_min``
  (inclusive severity threshold; ordering TRACE < DEBUG < INFO < WARN <
  ERROR < FATAL with the WARNING / CRITICAL aliases), ``status_min``
  (inclusive HTTP status threshold), ``method`` (exact match) and
  ``ip`` (exact match). The result carries both the matching raw lines
  and their parsed records.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown mode / format /
level, out-of-range ``status_min`` / ``sample_size``, oversized text,
too many lines, an over-long single line, predicates passed outside
``filter`` mode or no predicate at all in ``filter`` mode) raise a
``ValueError``, mirroring the other common tools. Content-level
failures — no non-blank line at all, or auto-detection finding zero
parsable lines — are returned as a structured ``error`` payload so an
agent can react without catching exceptions.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
_ISO_TS = (
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
    r"(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
)
_LEVEL_TOKEN = r"(?:TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)"

# Apache/Nginx combined access log: ... "REQ" status bytes "ref" "ua".
# The referrer/agent strings follow the Apache escaping convention:
# a literal quote is logged as \" and a backslash as \\, so the field
# body accepts backslash-escaped quotes and the parsed record carries
# the unescaped value (other backslashes pass through untouched).
_QUOTED_FIELD = r'(?:[^"]|\\")*'
_APACHE_UNESCAPE_RE = re.compile(r'\\(["\\])')
COMBINED_RE = re.compile(
    r"^(?P<ip>\S+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+"
    r"\[(?P<time>[^\]]+)\]\s+"
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+(?P<protocol>[^"\s]+)"\s+'
    r"(?P<status>\d{3})\s+(?P<bytes>\d+|-)\s+"
    rf'"(?P<referrer>{_QUOTED_FIELD})"\s+"(?P<agent>{_QUOTED_FIELD})"\s*$'
)
# Apache common access log: same as combined minus the referrer/agent tail.
COMMON_RE = re.compile(
    r"^(?P<ip>\S+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+"
    r"\[(?P<time>[^\]]+)\]\s+"
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+(?P<protocol>[^"\s]+)"\s+'
    r"(?P<status>\d{3})\s+(?P<bytes>\d+|-)\s*$"
)
# RFC 3164 syslog: "Oct  9 10:30:00 host proc[pid]: message".
SYSLOG_RE = re.compile(
    rf"^(?P<timestamp>(?:{_MONTHS})\s+\d{{1,2}}\s+\d{{2}}:\d{{2}}:\d{{2}})\s+"
    r"(?P<host>\S+)\s+(?P<proc>[^\s:\[\]]+)(?:\[(?P<pid>\d+)\])?:\s*"
    r"(?P<message>.*)$"
)
# ISO timestamp + level (+ optional brackets) + logger + message.
LEVELED_ISO_RE = re.compile(
    rf"^(?P<timestamp>{_ISO_TS})\s+\[?(?P<level>{_LEVEL_TOKEN})\]?\s+"
    r"(?P<logger>[\w.\-/]+)(?:\s+(?P<message>.*))?$",
    re.IGNORECASE,
)
# Bare bracketed prefix: "[LEVEL] message" (no timestamp, no logger).
LEVELED_BRACKET_RE = re.compile(
    rf"^\[(?P<level>{_LEVEL_TOKEN})\]\s*(?P<message>.*)$", re.IGNORECASE
)
# One key=value pair; values are double-quoted, single-quoted or bare.
_KV_PAIR = (
    r"[A-Za-z_][\w.\-]*=(?:\"[^\"]*\"|'[^']*'|[^\s]+)"
)
KEYVALUE_RE = re.compile(rf"^(?:{_KV_PAIR})(?:\s+{_KV_PAIR})*\s*$")
KV_PAIR_RE = re.compile(
    r"(?P<key>[A-Za-z_][\w.\-]*)=(?P<value>\"[^\"]*\"|'[^']*'|[^\s]+)"
)

# Detection priority: the first matching format wins a line's vote.
_DETECTORS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("combined", COMBINED_RE),
    ("common", COMMON_RE),
    ("syslog", SYSLOG_RE),
    ("leveled", LEVELED_ISO_RE),
    ("leveled", LEVELED_BRACKET_RE),
    ("keyvalue", KEYVALUE_RE),
)


class LogParserTool(Tool):
    """Common log-format parsing tool built purely on the stdlib.

    Attributes:
        max_input_chars (int): Upper bound on the ``text`` input length.
        max_lines (int): Upper bound on the number of non-blank lines
            processed; longer inputs are rejected before any work.
        max_line_chars (int): Upper bound on the length of a single
            line; one over-long line rejects the whole input.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "log_parser_tool"
    description: str = (
        "Log parser tool — pure Python stdlib regex, no network "
        "required. Detect the dominant format of sample lines "
        "(mode='detect': apache/nginx combined, apache common, syslog, "
        "ISO-timestamp leveled, key=value; per-line votes, majority "
        "wins, mixed lines reported), parse lines into structured "
        "records per detected or explicit format (mode='parse'; "
        "unparseable lines returned as {raw, error} entries), and "
        "filter parsed records by predicates (mode='filter': "
        "level_min with DEBUG<INFO<WARN<ERROR<FATAL ordering, "
        "status_min, method, ip) getting back the matching raw lines "
        "and their parsed records."
    )

    MODES: ClassVar[tuple] = ("detect", "parse", "filter")
    FORMATS: ClassVar[tuple] = ("combined", "common", "syslog", "leveled", "keyvalue")
    # Severity ranking for level predicates (WARNING/CRITICAL alias
    # WARN/FATAL); unknown levels cannot be ordered.
    LEVEL_RANKS: ClassVar[dict[str, int]] = {
        "TRACE": 0,
        "DEBUG": 10,
        "INFO": 20,
        "WARN": 30,
        "WARNING": 30,
        "ERROR": 40,
        "FATAL": 50,
        "CRITICAL": 50,
    }

    # Size caps are class constants (not pydantic fields) so the
    # validating classmethods below can read them off ``cls``.
    max_input_chars: ClassVar[int] = 1_000_000
    max_lines: ClassVar[int] = 10_000
    max_line_chars: ClassVar[int] = 10_000
    max_sample_size: ClassVar[int] = 10_000
    default_sample_size: ClassVar[int] = 200

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        format: Any = None,
        sample_size: Any = None,
        level_min: Any = None,
        status_min: Any = None,
        method: Any = None,
        ip: Any = None,
    ) -> dict[str, Any]:
        """Run one log parsing operation.

        Args:
            mode (str): One of ``detect`` / ``parse`` / ``filter``.
            text (str): The log text; lines are split on universal
                newlines, blank lines are skipped and counted.
            format (str): Optional explicit format — one of
                ``combined`` / ``common`` / ``syslog`` / ``leveled`` /
                ``keyvalue``. Required for nothing: ``parse`` and
                ``filter`` auto-detect when omitted; ignored by
                ``detect`` (which always votes).
            sample_size (int): Detect mode only — maximum number of
                non-blank lines sampled (evenly spaced, deterministic);
                1..10000, default 200. Ignored by the other modes.
            level_min (str): Filter predicate — keep records whose
                level ranks at or above this threshold (case-insensitive
                TRACE/DEBUG/INFO/WARN/WARNING/ERROR/FATAL/CRITICAL).
            status_min (int): Filter predicate — keep records with
                ``status`` >= this HTTP status code (100..599).
            method (str): Filter predicate — keep records whose request
                method equals this string exactly.
            ip (str): Filter predicate — keep records whose ``ip``
                equals this string exactly.

        Returns:
            Dict[str, Any]: The operation result (format guess + votes
            for ``detect``, records + counts for ``parse``, matching
            lines + records for ``filter``) or a structured ``error``
            payload for content-level failures (no non-blank lines,
            auto-detection with zero parsable lines).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        lines, blank_count = self._validate_text(text)
        if mode == "detect":
            self._reject_predicates(level_min, status_min, method, ip)
            clean_sample_size = self._validate_sample_size(sample_size)
            return self._run_detect(lines, blank_count, clean_sample_size)
        clean_format = self._validate_format(format)
        if mode == "parse":
            self._reject_predicates(level_min, status_min, method, ip)
            return self._run_parse(lines, blank_count, clean_format)
        predicates = self._validate_predicates(
            level_min, status_min, method, ip
        )
        return self._run_filter(lines, blank_count, clean_format, predicates)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"log_parser_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> tuple[list[tuple[int, str]], int]:
        """Split ``text`` into (line_no, line) pairs, blank lines out.

        Returns the non-blank lines with their 1-based line numbers in
        the original ``str.splitlines()`` order plus the blank count.
        """
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > cls.max_input_chars:
            cls._invalid(
                f"text exceeds the {cls.max_input_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        lines: list[tuple[int, str]] = []
        blank_count = 0
        for number, raw_line in enumerate(text.splitlines(), start=1):
            if len(raw_line) > cls.max_line_chars:
                cls._invalid(
                    f"line {number} exceeds the {cls.max_line_chars:,}-"
                    f"character limit (got {len(raw_line):,} characters)"
                )
            line = raw_line.strip()
            if not line:
                blank_count += 1
                continue
            lines.append((number, line))
        if not lines:
            cls._invalid("text contains no non-blank lines to process")
        if len(lines) > cls.max_lines:
            cls._invalid(
                f"text exceeds the {cls.max_lines:,}-line limit "
                f"(got {len(lines):,} non-blank lines)"
            )
        return lines, blank_count

    @classmethod
    def _validate_format(cls, format: Any) -> str | None:
        """Validate the optional explicit ``format`` selector."""
        if format is None:
            return None
        if isinstance(format, bool) or not isinstance(format, str):
            cls._invalid(
                f"format must be one of: {', '.join(cls.FORMATS)} or None "
                f"for auto-detection (got {format!r})"
            )
        if format not in cls.FORMATS:
            cls._invalid(
                "format must be one of: "
                f"{', '.join(cls.FORMATS)} or None for auto-detection "
                f"(got {format!r})"
            )
        return format

    @classmethod
    def _validate_sample_size(cls, sample_size: Any) -> int:
        """Validate the detect-mode ``sample_size`` bound."""
        if sample_size is None:
            return cls.default_sample_size
        if (
            isinstance(sample_size, bool)
            or not isinstance(sample_size, int)
            or sample_size < 1
            or sample_size > cls.max_sample_size
        ):
            cls._invalid(
                f"sample_size must be an integer between 1 and "
                f"{cls.max_sample_size} (got {sample_size!r})"
            )
        return sample_size

    @classmethod
    def _reject_predicates(
        cls, level_min: Any, status_min: Any, method: Any, ip: Any
    ) -> None:
        """Reject filter predicates outside filter mode."""
        given = [
            (name, value)
            for name, value in (
                ("level_min", level_min),
                ("status_min", status_min),
                ("method", method),
                ("ip", ip),
            )
            if value is not None
        ]
        if given:
            names = ", ".join(name for name, _ in given)
            cls._invalid(
                f"filter predicates ({names}) are only accepted in "
                "filter mode"
            )

    @classmethod
    def _validate_predicates(
        cls, level_min: Any, status_min: Any, method: Any, ip: Any
    ) -> dict[str, Any]:
        """Validate the filter-mode predicates (at least one required)."""
        if level_min is not None:
            if (
                isinstance(level_min, bool)
                or not isinstance(level_min, str)
                or level_min.strip().upper() not in cls.LEVEL_RANKS
            ):
                cls._invalid(
                    "level_min must be one of: "
                    f"{', '.join(cls.LEVEL_RANKS)} (case-insensitive) "
                    f"(got {level_min!r})"
                )
            level_min = level_min.strip().upper()
        if status_min is not None:
            if (
                isinstance(status_min, bool)
                or not isinstance(status_min, int)
                or not 100 <= status_min <= 599
            ):
                cls._invalid(
                    f"status_min must be an integer HTTP status code "
                    f"between 100 and 599 (got {status_min!r})"
                )
        if method is not None:
            if isinstance(method, bool) or not isinstance(method, str) or not method:
                cls._invalid(
                    f"method must be a non-empty string (got {method!r})"
                )
        if ip is not None:
            if isinstance(ip, bool) or not isinstance(ip, str) or not ip:
                cls._invalid(f"ip must be a non-empty string (got {ip!r})")
        predicates = {
            "level_min": level_min,
            "status_min": status_min,
            "method": method,
            "ip": ip,
        }
        if all(value is None for value in predicates.values()):
            cls._invalid(
                "filter mode requires at least one predicate: level_min, "
                "status_min, method or ip"
            )
        return predicates

    # ------------------------------------------------------------------ #
    # detect mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _classify_line(cls, line: str) -> str | None:
        """Return the format name a line votes for, or None."""
        for name, pattern in _DETECTORS:
            if pattern.match(line):
                return name
        return None

    def _run_detect(
        self, lines: list[tuple[int, str]], blank_count: int, sample_size: int
    ) -> dict[str, Any]:
        """Vote per sampled line; majority format wins."""
        total = len(lines)
        if total > sample_size:
            # Deterministic even sampling over the line list.
            if sample_size == 1:
                indices = [0]
            else:
                indices = sorted(
                    {
                        round(i * (total - 1) / (sample_size - 1))
                        for i in range(sample_size)
                    }
                )
            sampled = [lines[i] for i in indices]
        else:
            sampled = lines
        votes = {name: 0 for name in self.FORMATS}
        unparseable = 0
        for _, line in sampled:
            name = self._classify_line(line)
            if name is None:
                unparseable += 1
            else:
                votes[name] += 1
        winner = max(self.FORMATS, key=lambda name: (votes[name], -self.FORMATS.index(name)))
        winner_votes = votes[winner]
        sampled_total = len(sampled)
        if winner_votes == 0:
            return {
                "mode": "detect",
                "total_lines": total,
                "blank_lines": blank_count,
                "sampled_lines": sampled_total,
                "format_guess": None,
                "confidence": 0.0,
                "majority": False,
                "votes": {**votes, "unparseable": unparseable},
                "mixed_lines": sampled_total,
            }
        return {
            "mode": "detect",
            "total_lines": total,
            "blank_lines": blank_count,
            "sampled_lines": sampled_total,
            "format_guess": winner,
            "confidence": round(winner_votes / sampled_total, 4),
            "majority": winner_votes * 2 > sampled_total,
            "votes": {**votes, "unparseable": unparseable},
            "mixed_lines": sampled_total - winner_votes,
        }

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(
        self,
        lines: list[tuple[int, str]],
        blank_count: int,
        format: str | None,
    ) -> dict[str, Any]:
        """Parse every line with the explicit or detected format."""
        context = {"mode": "parse", "blank_lines": blank_count, "line_count": len(lines)}
        chosen = format
        detected = False
        if chosen is None:
            chosen = self._majority_format(lines)
            detected = True
            if chosen is None:
                return self._error_result(
                    context,
                    error_type="unrecognized_format",
                    message=(
                        "auto-detection found no line matching any known "
                        "format (combined, common, syslog, leveled, "
                        "keyvalue); pass format= explicitly or check the "
                        "input"
                    ),
                )
        records: list[dict[str, Any]] = []
        parsed_count = 0
        failed_count = 0
        for number, line in lines:
            record = self._parse_line(chosen, line)
            if record is None:
                records.append(
                    {
                        "line_no": number,
                        "raw": line,
                        "error": f"line does not match the {chosen} format",
                    }
                )
                failed_count += 1
            else:
                records.append({"line_no": number, **record})
                parsed_count += 1
        return {
            **context,
            "format": chosen,
            "detected": detected,
            "parsed_count": parsed_count,
            "failed_count": failed_count,
            "records": records,
        }

    def _majority_format(self, lines: list[tuple[int, str]]) -> str | None:
        """Vote over every line; the top format wins (None if zero)."""
        votes = {name: 0 for name in self.FORMATS}
        for _, line in lines:
            name = self._classify_line(line)
            if name is not None:
                votes[name] += 1
        winner = max(self.FORMATS, key=lambda name: (votes[name], -self.FORMATS.index(name)))
        return winner if votes[winner] > 0 else None

    # ------------------------------------------------------------------ #
    # filter mode
    # ------------------------------------------------------------------ #

    def _run_filter(
        self,
        lines: list[tuple[int, str]],
        blank_count: int,
        format: str | None,
        predicates: dict[str, Any],
    ) -> dict[str, Any]:
        """Parse, then keep records matching every given predicate."""
        parsed = self._run_parse(lines, blank_count, format)
        if "error" in parsed:
            return {**parsed, "mode": "filter"}
        matched_lines: list[str] = []
        matched_records: list[dict[str, Any]] = []
        for (number, line), record in zip(lines, parsed["records"]):
            if "error" in record:
                continue
            if not self._matches(record, predicates):
                continue
            matched_lines.append(line)
            matched_records.append(record)
        return {
            "mode": "filter",
            "format": parsed["format"],
            "detected": parsed["detected"],
            "predicates": predicates,
            "parsed_count": parsed["parsed_count"],
            "failed_count": parsed["failed_count"],
            "matched_count": len(matched_lines),
            "matched_lines": matched_lines,
            "records": matched_records,
        }

    @classmethod
    def _matches(cls, record: dict[str, Any], predicates: dict[str, Any]) -> bool:
        """Evaluate the AND of every given predicate over one record."""
        if predicates["level_min"] is not None:
            level = record.get("level")
            rank = cls.LEVEL_RANKS.get(str(level).upper()) if level is not None else None
            if rank is None or rank < cls.LEVEL_RANKS[predicates["level_min"]]:
                return False
        if predicates["status_min"] is not None:
            status = record.get("status")
            if not isinstance(status, int) or status < predicates["status_min"]:
                return False
        if predicates["method"] is not None and record.get("method") != predicates["method"]:
            return False
        if predicates["ip"] is not None and record.get("ip") != predicates["ip"]:
            return False
        return True

    # ------------------------------------------------------------------ #
    # Per-format line parsing (None when the line does not match)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_line(format: str, line: str) -> dict[str, Any] | None:
        """Parse one line as ``format``; None means no match."""
        if format in ("combined", "common"):
            pattern = COMBINED_RE if format == "combined" else COMMON_RE
            match = pattern.match(line)
            if match is None:
                return None
            record = {
                "ip": match.group("ip"),
                "ident": match.group("ident"),
                "user": match.group("user"),
                "time": match.group("time"),
                "method": match.group("method"),
                "path": match.group("path"),
                "protocol": match.group("protocol"),
                "status": int(match.group("status")),
                "bytes": match.group("bytes"),
            }
            # Apache convention: "-" marks an absent optional field.
            if record["ident"] == "-":
                record["ident"] = None
            if record["user"] == "-":
                record["user"] = None
            if record["bytes"] == "-":
                record["bytes"] = None
            else:
                record["bytes"] = int(record["bytes"])
            if format == "combined":
                # The quoted tail fields carry Apache escapes (\" for a
                # literal quote, \\ for a backslash); records expose the
                # true value.
                record["referrer"] = _APACHE_UNESCAPE_RE.sub(r"\1", match.group("referrer"))
                record["agent"] = _APACHE_UNESCAPE_RE.sub(r"\1", match.group("agent"))
            return record
        if format == "syslog":
            match = SYSLOG_RE.match(line)
            if match is None:
                return None
            pid = match.group("pid")
            return {
                "timestamp": match.group("timestamp"),
                "host": match.group("host"),
                "proc": match.group("proc"),
                "pid": int(pid) if pid is not None else None,
                "message": match.group("message"),
            }
        if format == "leveled":
            match = LEVELED_ISO_RE.match(line)
            if match is not None:
                return {
                    "timestamp": match.group("timestamp"),
                    "level": match.group("level").upper(),
                    "logger": match.group("logger"),
                    "message": match.group("message") or "",
                }
            match = LEVELED_BRACKET_RE.match(line)
            if match is not None:
                return {
                    "timestamp": None,
                    "level": match.group("level").upper(),
                    "logger": None,
                    "message": match.group("message"),
                }
            return None
        # keyvalue: the whole line already matched KEYVALUE_RE via the
        # detectors; re-extract the individual pairs here.
        if not KEYVALUE_RE.match(line):
            return None
        record: dict[str, Any] = {}
        for pair in KV_PAIR_RE.finditer(line):
            value = pair.group("value")
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            record[pair.group("key")] = value
        return record

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
