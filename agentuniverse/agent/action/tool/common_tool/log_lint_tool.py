#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: log_lint_tool.py

"""Whole-file log consistency linting tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency log auditing
utility for ops agents: ``LogParserTool`` (#3731) structures
individual lines, but no common tool answers the follow-up question
"is this log file internally consistent?". This tool is that QA
layer — it looks across lines and reports anomalies as findings.

Shared detection convention (co-designed with ``LogParserTool``,
PR #3731): the five format patterns below and the per-line voting
rule — every line is tested against each pattern in the fixed
priority order and votes for the first one that matches — are the
same detection language as #3731, duplicated deliberately so each
tool stays standalone with no cross-import; any change to the
accepted format language must be mirrored in both tools. The
recognized formats are ``combined`` (Apache/Nginx combined access
log), ``common`` (Apache common access log), ``syslog`` (RFC 3164
style), ``leveled`` (ISO timestamp + level, with optional
``[LEVEL]`` brackets and bare ``[LEVEL] msg`` lines) and
``keyvalue`` (space-separated ``k=v`` pairs).

The tool supports three modes:

* ``audit`` — auto-detect the dominant format via the shared votes,
  then lint the whole file and return findings as
  ``{code, severity, line, message}`` records. Rules:
  ``format_drift`` (lines failing the dominant format — count plus
  first offenders), ``timestamp_gaps`` (consecutive parsed
  timestamps jumping more than ``threshold_hours`` apart, default
  24h — info), ``timestamp_regression`` (out-of-order timestamps —
  error, naming the offending pair), ``level_sequence_anomaly``
  (an ERROR-family line whose next leveled line is INFO with no WARN
  and no stack-trace context in between — info heuristic),
  ``mixed_line_endings``, ``encoding_replacement_chars`` (U+FFFD
  present — info), ``very_long_line`` (over 10,000 characters; more
  than 5 consecutive over-long lines are collapsed into a single
  "likely stack trace" info finding), ``duplicate_line_burst`` (one
  line repeated more than 5 times consecutively — warning),
  ``empty_lines``, and ``missing_timestamp_mode`` (under 80% of
  lines parse with timestamps — the gap and regression rules are
  skipped with a note). Lines starting with ``Traceback`` /
  ``Exception`` / ``Caused by`` that do not match the dominant
  format are expected stack-trace context: they are tallied under
  ``stacktrace_context`` and never reported as errors.
* ``timeline`` — summarize the parsed timestamps: min / max / total
  span, the gaps over ``threshold_hours`` (largest first), the
  maximal monotonic (non-decreasing) run lengths with their line
  ranges, and the regression count. Skipped cleanly (a structured
  ``skipped`` payload, never an exception) when no line carries a
  parseable timestamp.
* ``level_summary`` — the level histogram (``WARNING``/``CRITICAL``
  are folded into ``WARN``/``FATAL``, the same aliasing as #3731)
  plus, with ``per_hour=True``, per-hour buckets keyed by the ISO
  ``YYYY-MM-DDTHH`` hour convention used across the family's
  datetime tools.

Timestamp semantics: Apache ``combined``/``common`` times carry an
offset and are converted to UTC; ``leveled`` ISO timestamps are
converted to UTC when an offset is present and otherwise used
as-is; ``syslog`` timestamps carry no year and no zone — the
current year is assumed (the RFC 3164 convention) and arithmetic is
wall-clock; ``keyvalue`` lines contribute no timestamp (there is no
canonical timestamp key), so gap/regression rules fall to the
coverage rule. All arithmetic is done on naive datetimes after
normalization, so a span between two tz-less timestamps is pure
wall-clock subtraction (documented limitation: naive timestamps
recorded under different UTC offsets are compared as-is).

Log content is treated as sensitive per the family rule: line
previews embedded in findings are capped at 60 characters and
values whose key looks like a secret (password / passwd / secret /
token / api key / authorization / credential) are masked before the
preview is built.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown mode,
out-of-place or out-of-range ``threshold_hours`` / ``per_hour``,
oversized text, more than 100,000 non-blank lines, a single line
over 1,000,000 characters) raise a ``ValueError``, mirroring the
other common tools. The one content-level failure — audit finding
no line that matches any known format — returns a structured
``error`` payload so an agent can react without catching
exceptions.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Shared detection language (mirrors LogParserTool, PR #3731; keep in sync).
# ---------------------------------------------------------------------------
_MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
_ISO_TS = (
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
    r"(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
)
_LEVEL_TOKEN = r"(?:TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)"

_QUOTED_FIELD = r'(?:[^"]|\\")*'
COMBINED_RE = re.compile(
    r"^(?P<ip>\S+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+"
    r"\[(?P<time>[^\]]+)\]\s+"
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+(?P<protocol>[^"\s]+)"\s+'
    r"(?P<status>\d{3})\s+(?P<bytes>\d+|-)\s+"
    rf'"(?P<referrer>{_QUOTED_FIELD})"\s+"(?P<agent>{_QUOTED_FIELD})"\s*$'
)
COMMON_RE = re.compile(
    r"^(?P<ip>\S+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+"
    r"\[(?P<time>[^\]]+)\]\s+"
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+(?P<protocol>[^"\s]+)"\s+'
    r"(?P<status>\d{3})\s+(?P<bytes>\d+|-)\s*$"
)
SYSLOG_RE = re.compile(
    rf"^(?P<timestamp>(?:{_MONTHS})\s+\d{{1,2}}\s+\d{{2}}:\d{{2}}:\d{{2}})\s+"
    r"(?P<host>\S+)\s+(?P<proc>[^\s:\[\]]+)(?:\[(?P<pid>\d+)\])?:\s*"
    r"(?P<message>.*)$"
)
LEVELED_ISO_RE = re.compile(
    rf"^(?P<timestamp>{_ISO_TS})\s+\[?(?P<level>{_LEVEL_TOKEN})\]?\s+"
    r"(?P<logger>[\w.\-/]+)(?:\s+(?P<message>.*))?$",
    re.IGNORECASE,
)
LEVELED_BRACKET_RE = re.compile(
    rf"^\[(?P<level>{_LEVEL_TOKEN})\]\s*(?P<message>.*)$", re.IGNORECASE
)
_KV_PAIR = r"[A-Za-z_][\w.\-]*=(?:\"[^\"]*\"|'[^']*'|[^\s]+)"
KEYVALUE_RE = re.compile(rf"^(?:{_KV_PAIR})(?:\s+{_KV_PAIR})*\s*$")

# Detection priority: the first matching format wins a line's vote.
_DETECTORS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("combined", COMBINED_RE),
    ("common", COMMON_RE),
    ("syslog", SYSLOG_RE),
    ("leveled", LEVELED_ISO_RE),
    ("leveled", LEVELED_BRACKET_RE),
    ("keyvalue", KEYVALUE_RE),
)

# Severity ranking and level aliasing (identical to #3731).
LEVEL_RANKS: dict[str, int] = {
    "TRACE": 0,
    "DEBUG": 10,
    "INFO": 20,
    "WARN": 30,
    "WARNING": 30,
    "ERROR": 40,
    "FATAL": 50,
    "CRITICAL": 50,
}
_LEVEL_ALIASES = {"WARNING": "WARN", "CRITICAL": "FATAL"}
_CANONICAL_LEVELS = ("TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL")
_ERROR_FAMILY = ("ERROR", "FATAL")

# Stack-trace context markers: counted, never errors.
_EXCEPTION_PREFIXES = ("Traceback", "Exception", "Caused by")

# Locale-independent month numbers (strptime %b is locale-dependent).
_MONTH_NUMBERS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_APACHE_TIME_RE = re.compile(
    r"^(\d{1,2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})"
    r"\s+([+-])(\d{2})(\d{2})$"
)
_SYSLOG_TIME_RE = re.compile(
    r"^([A-Za-z]{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})$"
)
_ISO_OFFSET_NO_COLON_RE = re.compile(r"([+-]\d{2})(\d{2})$")
_ISO_COMMA_FRACTION_RE = re.compile(r"(\d),(\d)")

# Preview hygiene: cap length, then mask secret-looking values.
_SECRET_KEY_RE = re.compile(
    r"(?i)((?:password|passwd|secret|token|api[_-]?key|"
    r"authorization|auth|credential)s?\s*[=:]\s*)\S+"
)
_BEARER_RE = re.compile(r"(?i)(bearer\s+)\S+")


class LogLintTool(Tool):
    """Whole-file log consistency linter built purely on the stdlib.

    Attributes:
        max_input_chars (int): Upper bound on the ``text`` input length.
        max_lines (int): Upper bound on non-blank lines processed.
        max_line_chars (int): Sanity upper bound for a single raw line
            (two orders of magnitude above the 10,000-character
            ``very_long_line`` lint threshold, which reports rather
            than rejects).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "log_lint_tool"
    description: str = (
        "Log lint tool — whole-file log consistency auditing with pure "
        "Python stdlib, no network required. Auto-detects the dominant "
        "format (shared per-line voting convention with LogParserTool: "
        "combined, common, syslog, leveled, key=value), then audits "
        "across lines for consistency anomalies (mode='audit': format "
        "drift, timestamp gaps over a configurable threshold (default "
        "24h), timestamp regressions, ERROR-to-INFO level sequence "
        "anomalies, mixed line endings, U+FFFD encoding replacement "
        "chars, over-long lines with a stack-trace heuristic, duplicate "
        "line bursts, empty lines; stack-trace context lines are "
        "tallied, not flagged), summarizes the timestamp timeline "
        "(mode='timeline': min/max/span, largest gaps, monotonic run "
        "lengths, skipped cleanly without timestamps) and the level "
        "distribution (mode='level_summary': histogram with "
        "WARNING/CRITICAL aliasing plus optional ISO-hour buckets). "
        "Findings carry {code, severity, line, message}; line previews "
        "are capped at 60 chars with secret-looking values masked."
    )

    MODES: ClassVar[tuple] = ("audit", "timeline", "level_summary")
    FORMATS: ClassVar[tuple] = (
        "combined",
        "common",
        "syslog",
        "leveled",
        "keyvalue",
    )

    # Size caps are class constants so validating classmethods can read
    # them off ``cls``.
    max_input_chars: ClassVar[int] = 10_000_000
    max_lines: ClassVar[int] = 100_000
    max_line_chars: ClassVar[int] = 1_000_000

    # Audit constants (documented, not options).
    long_line_threshold: ClassVar[int] = 10_000
    stacktrace_run_length: ClassVar[int] = 5
    duplicate_burst_length: ClassVar[int] = 5
    timestamp_coverage_floor: ClassVar[float] = 0.8
    max_offenders: ClassVar[int] = 5
    max_monotonic_runs: ClassVar[int] = 50
    default_threshold_hours: ClassVar[float] = 24.0
    max_threshold_hours: ClassVar[float] = 87_600.0
    preview_chars: ClassVar[int] = 60

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        text: Any = None,
        threshold_hours: Any = None,
        per_hour: Any = None,
    ) -> dict[str, Any]:
        """Run one log linting operation.

        Args:
            mode (str): One of ``audit`` / ``timeline`` /
                ``level_summary``.
            text (str): The log text; lines are split on universal
                newlines.
            threshold_hours (float): Audit and timeline modes — the
                gap threshold in hours (a jump strictly greater than
                this many hours is a gap); a positive number up to
                87600, default 24. Rejected in ``level_summary`` mode.
            per_hour (bool): Level_summary mode only — add per-hour
                buckets keyed ``YYYY-MM-DDTHH`` for the lines that
                carry both a level and a timestamp. Default False;
                rejected in the other modes.

        Returns:
            Dict[str, Any]: Findings plus context for ``audit``, the
            timestamp timeline summary for ``timeline``, the level
            histogram (and optional hour buckets) for
            ``level_summary``. Timeline and level_summary skip
            cleanly (a ``skipped`` payload) when the log carries no
            parseable timestamps / no levels.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        raw_lines, lines, blank_count, endings = self._validate_text(text)
        if mode == "audit":
            clean_threshold = self._validate_threshold_hours(threshold_hours)
            self._reject_option(
                "per_hour", per_hour, allowed_modes=("level_summary",)
            )
            return self._run_audit(
                raw_lines, lines, blank_count, endings, clean_threshold
            )
        if mode == "timeline":
            clean_threshold = self._validate_threshold_hours(threshold_hours)
            self._reject_option(
                "per_hour", per_hour, allowed_modes=("level_summary",)
            )
            return self._run_timeline(lines, blank_count, clean_threshold)
        self._reject_option(
            "threshold_hours",
            threshold_hours,
            allowed_modes=("audit", "timeline"),
        )
        clean_per_hour = self._validate_per_hour(per_hour)
        return self._run_level_summary(lines, blank_count, clean_per_hour)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"log_lint_tool: {message}")

    @classmethod
    def _validate_text(
        cls, text: Any
    ) -> tuple[
        list[tuple[int, str]], list[tuple[int, str]], int, dict[str, int]
    ]:
        """Split ``text``; return (raw, non-blank, blank_count, endings).

        Raw entries keep the line verbatim (before stripping) with its
        1-based ``str.splitlines()`` number; non-blank entries carry
        the stripped line and drop blanks. Line-ending kinds (LF /
        CRLF / lone CR) are counted on the original text because
        ``splitlines()`` consumes the separators.
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
        raw_lines: list[tuple[int, str]] = []
        lines: list[tuple[int, str]] = []
        blank_count = 0
        for number, raw_line in enumerate(text.splitlines(), start=1):
            if len(raw_line) > cls.max_line_chars:
                cls._invalid(
                    f"line {number} exceeds the {cls.max_line_chars:,}-"
                    f"character limit (got {len(raw_line):,} characters)"
                )
            raw_lines.append((number, raw_line))
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
        crlf = text.count("\r\n")
        total_cr = text.count("\r")
        total_lf = text.count("\n")
        endings = {
            "crlf": crlf,
            "lf": total_lf - crlf,
            "cr": total_cr - crlf,
        }
        return raw_lines, lines, blank_count, endings

    @classmethod
    def _validate_threshold_hours(cls, threshold_hours: Any) -> float:
        """Validate the gap threshold (audit / timeline modes)."""
        if threshold_hours is None:
            return cls.default_threshold_hours
        if (
            isinstance(threshold_hours, bool)
            or not isinstance(threshold_hours, (int, float))
            or threshold_hours <= 0
            or threshold_hours > cls.max_threshold_hours
        ):
            cls._invalid(
                f"threshold_hours must be a positive number up to "
                f"{cls.max_threshold_hours:g} (got {threshold_hours!r})"
            )
        return float(threshold_hours)

    @classmethod
    def _validate_per_hour(cls, per_hour: Any) -> bool:
        """Validate the per-hour bucketing flag (level_summary mode)."""
        if per_hour is None:
            return False
        if not isinstance(per_hour, bool):
            cls._invalid(f"per_hour must be a boolean (got {per_hour!r})")
        return per_hour

    @classmethod
    def _reject_option(
        cls, name: str, value: Any, allowed_modes: tuple[str, ...]
    ) -> None:
        """Reject an option passed outside its allowed modes."""
        if value is not None:
            cls._invalid(
                f"{name} is only accepted in "
                f"{', '.join(allowed_modes)} mode"
            )

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _classify_line(line: str) -> str | None:
        """Return the format name a line votes for, or None."""
        for name, pattern in _DETECTORS:
            if pattern.match(line):
                return name
        return None

    @classmethod
    def _majority_format(cls, lines: list[tuple[int, str]]) -> str | None:
        """Vote over every line; the top format wins (None if zero).

        Same tally rule as LogParserTool: first match in the fixed
        detector priority order wins a line's vote, most votes wins,
        ties break by the priority order.
        """
        votes = {name: 0 for name in cls.FORMATS}
        for _, line in lines:
            name = cls._classify_line(line)
            if name is not None:
                votes[name] += 1
        winner = max(
            cls.FORMATS,
            key=lambda name: (votes[name], -cls.FORMATS.index(name)),
        )
        return winner if votes[winner] > 0 else None

    @classmethod
    def _parse_line(cls, fmt: str, line: str) -> dict[str, Any] | None:
        """Parse one line as ``fmt`` (shared language with #3731).

        Only the fields this linter needs are extracted: the raw
        timestamp text (``ts_raw``) for the timestamp-bearing formats
        and the level token where the format carries one. None means
        the line does not match the format.
        """
        if fmt in ("combined", "common"):
            match = (
                COMBINED_RE.match(line)
                if fmt == "combined"
                else COMMON_RE.match(line)
            )
            if match is None:
                return None
            return {"ts_raw": match.group("time")}
        if fmt == "syslog":
            match = SYSLOG_RE.match(line)
            if match is None:
                return None
            return {"ts_raw": match.group("timestamp")}
        if fmt == "leveled":
            match = LEVELED_ISO_RE.match(line)
            if match is not None:
                return {
                    "ts_raw": match.group("timestamp"),
                    "level": match.group("level").upper(),
                }
            match = LEVELED_BRACKET_RE.match(line)
            if match is not None:
                return {"ts_raw": None, "level": match.group("level").upper()}
            return None
        if fmt == "keyvalue":
            if not KEYVALUE_RE.match(line):
                return None
            return {"ts_raw": None, "level": None}
        return None

    @staticmethod
    def _to_datetime(ts_raw: str, fmt: str) -> datetime | None:
        """Normalize a raw timestamp text to a naive datetime.

        Combined/common carry ``DD/Mon/YYYY:HH:MM:SS +ZZZZ`` (parsed
        month names locale-independently, converted to UTC then made
        naive); leveled ISO timestamps accept ``Z``, an offset (with
        or without a colon), a comma fractional separator or none
        (aware values are converted to UTC then made naive, naive
        values are used as-is); syslog carries no year — the current
        year is assumed and the value stays naive wall-clock.
        """
        if fmt in ("combined", "common"):
            match = _APACHE_TIME_RE.match(ts_raw.strip())
            if match is None:
                return None
            day, mon, year, hh, mi, ss, sign, off_h, off_m = match.groups()
            month = _MONTH_NUMBERS.get(mon.lower())
            if month is None:
                return None
            try:
                local = datetime(
                    int(year), month, int(day), int(hh), int(mi), int(ss)
                )
            except ValueError:
                return None
            offset = timedelta(hours=int(off_h), minutes=int(off_m))
            return local - offset if sign == "+" else local + offset
        if fmt == "syslog":
            # RFC 3164 carries no year: assume the current year.
            match = _SYSLOG_TIME_RE.match(ts_raw.strip())
            if match is None:
                return None
            mon, day, hh, mi, ss = match.groups()
            month = _MONTH_NUMBERS.get(mon.lower())
            if month is None:
                return None
            try:
                return datetime(
                    datetime.now().year,
                    month,
                    int(day),
                    int(hh),
                    int(mi),
                    int(ss),
                )
            except ValueError:
                return None
        # leveled ISO: normalize the Z suffix and colon-less offsets
        # for portability, then let fromisoformat do the strict work.
        normalized = ts_raw.strip()
        if normalized.endswith(("Z", "z")):
            normalized = normalized[:-1] + "+00:00"
        normalized = _ISO_OFFSET_NO_COLON_RE.sub(r"\1:\2", normalized)
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            try:
                parsed = datetime.fromisoformat(
                    _ISO_COMMA_FRACTION_RE.sub(r"\1.\2", normalized)
                )
            except ValueError:
                return None
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed

    @staticmethod
    def _canonical_level(level: Any) -> str | None:
        """Normalize a level token to its canonical name, or None."""
        if not isinstance(level, str):
            return None
        upper = level.strip().upper()
        if upper not in LEVEL_RANKS:
            return None
        return _LEVEL_ALIASES.get(upper, upper)

    @classmethod
    def _extract_level(
        cls, fmt: str, record: dict[str, Any], line: str
    ) -> str | None:
        """Canonical level for a parsed line, or None.

        The leveled format carries its own token; keyvalue lines are
        probed for a ``level=`` pair (the only level convention that
        format has).
        """
        level = cls._canonical_level(record.get("level"))
        if level is not None:
            return level
        if fmt == "keyvalue":
            return cls._canonical_level(cls._keyvalue_level(line))
        return None

    @staticmethod
    def _keyvalue_level(line: str) -> str | None:
        """Extract a ``level=`` value from a keyvalue line, if any."""
        match = re.search(r"(?:^|\s)level=(\"[^\"]*\"|'[^']*'|[^\s]+)", line)
        if match is None:
            return None
        value = match.group(1)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        return value

    @classmethod
    def _preview(cls, line: str) -> str:
        """Build a leak-proof preview of a line for finding messages.

        Secret-looking key=value / key: value assignments and Bearer
        tokens are masked first, then the result is capped at 60
        characters (an ellipsis marks truncation).
        """
        masked = _SECRET_KEY_RE.sub(r"\1***", line)
        masked = _BEARER_RE.sub(r"\1***", masked)
        if len(masked) > cls.preview_chars:
            return masked[: cls.preview_chars] + "..."
        return masked

    # ------------------------------------------------------------------ #
    # audit mode
    # ------------------------------------------------------------------ #

    def _run_audit(
        self,
        raw_lines: list[tuple[int, str]],
        lines: list[tuple[int, str]],
        blank_count: int,
        endings: dict[str, int],
        threshold_hours: float,
    ) -> dict[str, Any]:
        """Detect the dominant format and lint the whole file."""
        context = {
            "mode": "audit",
            "total_lines": len(lines),
            "blank_lines": blank_count,
            "line_endings": endings,
            "threshold_hours": threshold_hours,
        }
        dominant = self._majority_format(lines)
        if dominant is None:
            return self._error_result(
                context,
                error_type="unrecognized_format",
                message=(
                    "auto-detection found no line matching any known "
                    "format (combined, common, syslog, leveled, "
                    "keyvalue); nothing to audit against"
                ),
            )
        total = len(lines)
        findings: list[dict[str, Any]] = []

        # Whole-text hygiene rules.
        self._audit_blank_lines(raw_lines, findings)
        self._audit_replacement_chars(raw_lines, findings)
        self._audit_line_endings(endings, findings)
        self._audit_long_lines(raw_lines, findings)
        findings.extend(self._audit_duplicate_bursts(lines))

        # Per-line classification against the dominant format.
        drift_lines: list[tuple[int, str]] = []
        stack_lines: list[int] = []
        parsed: list[dict[str, Any]] = []
        for number, line in lines:
            record = self._parse_line(dominant, line)
            if record is not None:
                ts = (
                    self._to_datetime(record["ts_raw"], dominant)
                    if record.get("ts_raw")
                    else None
                )
                parsed.append(
                    {
                        "line": number,
                        "ts": ts,
                        "level": self._extract_level(dominant, record, line),
                    }
                )
                continue
            if line.startswith(_EXCEPTION_PREFIXES):
                stack_lines.append(number)
                continue
            drift_lines.append((number, line))

        self._audit_format_drift(dominant, total, drift_lines, findings)
        self._audit_timestamp_rules(total, parsed, threshold_hours, findings)
        self._audit_level_sequence(parsed, stack_lines, findings)

        # Deterministic output order: by line number, then code.
        findings.sort(key=lambda f: (f["line"], f["code"]))
        counts = {"error": 0, "warning": 0, "info": 0}
        for finding in findings:
            counts[finding["severity"]] += 1
        return {
            **context,
            "format": dominant,
            "detected": True,
            "timestamp_coverage": self._coverage(
                [entry for entry in parsed if entry["ts"] is not None], total
            ),
            "stacktrace_context": {
                "count": len(stack_lines),
                "first_lines": stack_lines[: self.max_offenders],
            },
            "findings": findings,
            "finding_counts": {**counts, "total": len(findings)},
        }

    @staticmethod
    def _audit_blank_lines(
        raw_lines: list[tuple[int, str]], findings: list[dict[str, Any]]
    ) -> None:
        """Flag blank lines as one info finding."""
        blank_numbers = [n for n, raw in raw_lines if not raw.strip()]
        if not blank_numbers:
            return
        findings.append(
            {
                "code": "empty_lines",
                "severity": "info",
                "line": blank_numbers[0],
                "message": (
                    f"{len(blank_numbers)} blank line(s) present "
                    f"(first at line {blank_numbers[0]})"
                ),
            }
        )

    def _audit_replacement_chars(
        self, raw_lines: list[tuple[int, str]], findings: list[dict[str, Any]]
    ) -> None:
        """Flag U+FFFD replacement characters as one info finding."""
        affected = [n for n, raw in raw_lines if "\ufffd" in raw]
        if not affected:
            return
        total_chars = sum(raw.count("\ufffd") for _, raw in raw_lines)
        findings.append(
            {
                "code": "encoding_replacement_chars",
                "severity": "info",
                "line": affected[0],
                "message": (
                    f"{total_chars} U+FFFD replacement character(s) on "
                    f"{len(affected)} line(s) (first at line "
                    f"{affected[0]}) — the log was likely decoded with "
                    "the wrong codec somewhere"
                ),
            }
        )

    @staticmethod
    def _audit_line_endings(
        endings: dict[str, int], findings: list[dict[str, Any]]
    ) -> None:
        """Flag a mix of line-ending kinds as one warning finding."""
        kinds = [k for k, v in endings.items() if v > 0]
        if len(kinds) > 1:
            summary = ", ".join(
                f"{k}={endings[k]}" for k in ("crlf", "lf", "cr")
            )
            findings.append(
                {
                    "code": "mixed_line_endings",
                    "severity": "warning",
                    "line": 1,
                    "message": (
                        f"mixed line endings in one file ({summary}) — "
                        "lines may come from different sources or a "
                        "binary concat"
                    ),
                }
            )

    def _audit_long_lines(
        self, raw_lines: list[tuple[int, str]], findings: list[dict[str, Any]]
    ) -> None:
        """Flag over-long lines; collapse runs into a stack-trace info.

        A run of more than ``stacktrace_run_length`` consecutive
        over-long raw lines is reported once as a likely stack trace
        (info); shorter runs report each line individually (warning).
        """
        i = 0
        total = len(raw_lines)
        while i < total:
            if len(raw_lines[i][1]) <= self.long_line_threshold:
                i += 1
                continue
            j = i
            while j < total and len(raw_lines[j][1]) > self.long_line_threshold:
                j += 1
            run_length = j - i
            start_number = raw_lines[i][0]
            if run_length > self.stacktrace_run_length:
                findings.append(
                    {
                        "code": "very_long_line",
                        "severity": "info",
                        "line": start_number,
                        "message": (
                            f"{run_length} consecutive lines over "
                            f"{self.long_line_threshold:,} characters "
                            "starting here — likely a stack trace, "
                            "reported once"
                        ),
                    }
                )
            else:
                for k in range(i, j):
                    number, raw_line = raw_lines[k]
                    findings.append(
                        {
                            "code": "very_long_line",
                            "severity": "warning",
                            "line": number,
                            "message": (
                                f"line is {len(raw_line):,} characters "
                                f"long (over {self.long_line_threshold:,})"
                            ),
                        }
                    )
            i = j

    def _audit_duplicate_bursts(
        self, lines: list[tuple[int, str]]
    ) -> list[dict[str, Any]]:
        """Flag identical lines repeated more than N times in a row.

        Runs are counted over consecutive non-blank lines, so blank
        lines do not break a burst.
        """
        findings: list[dict[str, Any]] = []
        i = 0
        total = len(lines)
        while i < total:
            j = i + 1
            while j < total and lines[j][1] == lines[i][1]:
                j += 1
            run_length = j - i
            if run_length > self.duplicate_burst_length:
                findings.append(
                    {
                        "code": "duplicate_line_burst",
                        "severity": "warning",
                        "line": lines[i][0],
                        "message": (
                            f"identical line repeated {run_length} times "
                            f"consecutively (lines {lines[i][0]}-"
                            f"{lines[j - 1][0]}): "
                            f"{self._preview(lines[i][1])}"
                        ),
                    }
                )
            i = j
        return findings

    def _audit_format_drift(
        self,
        dominant: str,
        total: int,
        drift_lines: list[tuple[int, str]],
        findings: list[dict[str, Any]],
    ) -> None:
        """Flag lines failing the dominant format (count + offenders)."""
        if not drift_lines:
            return
        ratio = len(drift_lines) / total if total else 0.0
        offenders = ", ".join(
            f"line {n}: {self._preview(line)}"
            for n, line in drift_lines[: self.max_offenders]
        )
        findings.append(
            {
                "code": "format_drift",
                "severity": "warning",
                "line": drift_lines[0][0],
                "message": (
                    f"{len(drift_lines)}/{total} lines ({ratio:.1%}) "
                    f"deviate from the dominant '{dominant}' format; "
                    f"first offenders: {offenders}"
                ),
            }
        )

    def _audit_timestamp_rules(
        self,
        total: int,
        parsed: list[dict[str, Any]],
        threshold_hours: float,
        findings: list[dict[str, Any]],
    ) -> None:
        """Run the gap / regression rules under the coverage gate."""
        with_ts = [entry for entry in parsed if entry["ts"] is not None]
        coverage = len(with_ts) / total if total else 0.0
        if coverage < self.timestamp_coverage_floor:
            findings.append(
                {
                    "code": "missing_timestamp_mode",
                    "severity": "info",
                    "line": 1,
                    "message": (
                        f"only {len(with_ts)}/{total} lines "
                        f"({coverage:.1%}) carry parseable timestamps "
                        "(below the 80% floor) — timestamp_gaps and "
                        "timestamp_regression rules skipped"
                    ),
                }
            )
            return
        threshold_seconds = threshold_hours * 3600.0
        for prev, curr in zip(with_ts, with_ts[1:]):
            delta = (curr["ts"] - prev["ts"]).total_seconds()
            if delta > threshold_seconds:
                findings.append(
                    {
                        "code": "timestamp_gaps",
                        "severity": "info",
                        "line": curr["line"],
                        "message": (
                            f"timestamp jumps {delta / 3600.0:.2f}h (> "
                            f"{threshold_hours:g}h threshold) from "
                            f"{prev['ts'].isoformat()} (line "
                            f"{prev['line']}) to {curr['ts'].isoformat()} "
                            f"(line {curr['line']})"
                        ),
                    }
                )
            elif delta < 0:
                findings.append(
                    {
                        "code": "timestamp_regression",
                        "severity": "error",
                        "line": curr["line"],
                        "message": (
                            f"timestamp goes backwards by "
                            f"{abs(delta):g}s from {prev['ts'].isoformat()} "
                            f"(line {prev['line']}) to "
                            f"{curr['ts'].isoformat()} (line {curr['line']})"
                        ),
                    }
                )

    @staticmethod
    def _audit_level_sequence(
        parsed: list[dict[str, Any]],
        stack_lines: list[int],
        findings: list[dict[str, Any]],
    ) -> None:
        """Flag ERROR-family lines that fall straight through to INFO.

        Heuristic: after an ERROR-family line, skip level-less lines;
        if the next line carrying a level is INFO and neither a WARN
        nor any stack-trace context line sits in between, the
        escalation trail is suspicious (info finding). A WARN, another
        ERROR/FATAL, or a stack trace between the two clears the
        suspicion — the stack explains the drop back to INFO.
        """
        i = 0
        total = len(parsed)
        while i < total:
            entry = parsed[i]
            if entry["level"] not in _ERROR_FAMILY:
                i += 1
                continue
            j = i + 1
            while j < total and parsed[j]["level"] is None:
                j += 1
            if (
                j < total
                and parsed[j]["level"] == "INFO"
                and not any(
                    entry["line"] < stack_line < parsed[j]["line"]
                    for stack_line in stack_lines
                )
            ):
                findings.append(
                    {
                        "code": "level_sequence_anomaly",
                        "severity": "info",
                        "line": parsed[j]["line"],
                        "message": (
                            f"{entry['level']} at line {entry['line']} is "
                            f"immediately followed by INFO at line "
                            f"{parsed[j]['line']} with no WARN (or stack "
                            "trace) in between"
                        ),
                    }
                )
                i = j
            else:
                i += 1

    # ------------------------------------------------------------------ #
    # timeline mode
    # ------------------------------------------------------------------ #

    def _run_timeline(
        self,
        lines: list[tuple[int, str]],
        blank_count: int,
        threshold_hours: float,
    ) -> dict[str, Any]:
        """Summarize the parsed timestamps; skip cleanly if none."""
        context = {
            "mode": "timeline",
            "total_lines": len(lines),
            "blank_lines": blank_count,
        }
        dominant = self._majority_format(lines)
        stamped: list[dict[str, Any]] = []
        if dominant is not None:
            for number, line in lines:
                record = self._parse_line(dominant, line)
                if record is None or not record.get("ts_raw"):
                    continue
                ts = self._to_datetime(record["ts_raw"], dominant)
                if ts is not None:
                    stamped.append({"line": number, "ts": ts})
        base = {
            **context,
            "format": dominant,
            "parsed_timestamps": len(stamped),
            "timestamp_coverage": self._coverage(stamped, len(lines)),
        }
        if not stamped:
            reason = (
                f"no line carries a parseable timestamp (dominant "
                f"format: {dominant!r})"
                if dominant is not None
                else "auto-detection found no line matching any known format"
            )
            return {**base, "skipped": True, "reason": reason}
        if len(stamped) == 1:
            only = stamped[0]
            return {
                **base,
                "skipped": False,
                "min": only["ts"].isoformat(),
                "max": only["ts"].isoformat(),
                "span_seconds": 0.0,
                "gaps": {"threshold_hours": threshold_hours, "count": 0, "top": []},
                "monotonic_runs": [
                    {
                        "start_line": only["line"],
                        "end_line": only["line"],
                        "length": 1,
                    }
                ],
                "monotonic_runs_truncated": False,
                "regression_count": 0,
            }
        gaps: list[dict[str, Any]] = []
        regression_count = 0
        threshold_seconds = threshold_hours * 3600.0
        for prev, curr in zip(stamped, stamped[1:]):
            delta = (curr["ts"] - prev["ts"]).total_seconds()
            if delta > threshold_seconds:
                gaps.append(
                    {
                        "from_line": prev["line"],
                        "to_line": curr["line"],
                        "from_ts": prev["ts"].isoformat(),
                        "to_ts": curr["ts"].isoformat(),
                        "gap_hours": round(delta / 3600.0, 4),
                    }
                )
            elif delta < 0:
                regression_count += 1
        top_gaps = sorted(
            gaps, key=lambda g: (-g["gap_hours"], g["from_line"])
        )[: self.max_offenders]
        # Maximal non-decreasing runs over the timestamp sequence (a
        # strict decrease starts a new run; equal timestamps continue).
        runs: list[dict[str, Any]] = []
        run_start = 0
        for idx in range(1, len(stamped)):
            if stamped[idx]["ts"] < stamped[idx - 1]["ts"]:
                runs.append(
                    {
                        "start_line": stamped[run_start]["line"],
                        "end_line": stamped[idx - 1]["line"],
                        "length": idx - run_start,
                    }
                )
                run_start = idx
        runs.append(
            {
                "start_line": stamped[run_start]["line"],
                "end_line": stamped[-1]["line"],
                "length": len(stamped) - run_start,
            }
        )
        truncated = len(runs) > self.max_monotonic_runs
        min_ts = min(entry["ts"] for entry in stamped)
        max_ts = max(entry["ts"] for entry in stamped)
        return {
            **base,
            "skipped": False,
            "min": min_ts.isoformat(),
            "max": max_ts.isoformat(),
            "span_seconds": (max_ts - min_ts).total_seconds(),
            "gaps": {
                "threshold_hours": threshold_hours,
                "count": len(gaps),
                "top": top_gaps,
            },
            "monotonic_runs": runs[: self.max_monotonic_runs],
            "monotonic_runs_truncated": truncated,
            "regression_count": regression_count,
        }

    # ------------------------------------------------------------------ #
    # level_summary mode
    # ------------------------------------------------------------------ #

    def _run_level_summary(
        self,
        lines: list[tuple[int, str]],
        blank_count: int,
        per_hour: bool,
    ) -> dict[str, Any]:
        """Build the level histogram (+ optional ISO-hour buckets)."""
        context = {
            "mode": "level_summary",
            "total_lines": len(lines),
            "blank_lines": blank_count,
        }
        dominant = self._majority_format(lines)
        histogram = {name: 0 for name in _CANONICAL_LEVELS}
        unknown_levels: dict[str, int] = {}
        buckets: dict[str, dict[str, int]] = {}
        if dominant is not None:
            for _, line in lines:
                record = self._parse_line(dominant, line)
                if record is None:
                    continue
                level = self._extract_level(dominant, record, line)
                if level is None:
                    if dominant == "keyvalue":
                        raw = self._keyvalue_level(line)
                        if raw:
                            key = raw.strip().upper()
                            unknown_levels[key] = unknown_levels.get(key, 0) + 1
                    continue
                histogram[level] += 1
                if per_hour and record.get("ts_raw"):
                    ts = self._to_datetime(record["ts_raw"], dominant)
                    if ts is not None:
                        hour_key = ts.strftime("%Y-%m-%dT%H")
                        bucket = buckets.setdefault(hour_key, {})
                        bucket[level] = bucket.get(level, 0) + 1
        leveled_total = sum(histogram.values())
        result: dict[str, Any] = {
            **context,
            "format": dominant,
            "leveled_lines": leveled_total,
        }
        if leveled_total == 0:
            reason = (
                f"no line carries a recognized level (dominant format: "
                f"{dominant!r})"
                if dominant is not None
                else "auto-detection found no line matching any known format"
            )
            result.update({"skipped": True, "reason": reason})
            return result
        if unknown_levels:
            # Non-aliasable level strings (only keyvalue lines can
            # carry them) are reported under UNKNOWN with detail.
            histogram = {
                **histogram,
                "UNKNOWN": sum(unknown_levels.values()),
            }
            result["unknown_levels"] = dict(sorted(unknown_levels.items()))
        result.update({"skipped": False, "level_histogram": histogram})
        if per_hour:
            result["per_hour"] = {
                hour: dict(sorted(levels.items()))
                for hour, levels in sorted(buckets.items())
            }
        return result

    # ------------------------------------------------------------------ #
    # Misc
    # ------------------------------------------------------------------ #

    @staticmethod
    def _coverage(stamped: list[dict[str, Any]], total: int) -> float:
        """Timestamp coverage rounded to 4 decimals (0.0 when empty)."""
        if not total:
            return 0.0
        return round(len(stamped) / total, 4)

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
