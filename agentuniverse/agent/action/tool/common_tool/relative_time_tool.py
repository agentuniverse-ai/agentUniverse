#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: relative_time_tool.py

"""Relative time tool — humanized "3 hours ago" / "in 2 days" timestamps.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency utility that converts
between absolute datetimes and the humanized relative expressions
agents keep meeting in scraped text, chat history and log lines: "3
hours ago", "in 2 days", "3小时前", "2天后", "刚刚".

Built purely on the Python standard library (``datetime`` / ``re`` /
``math``) and deliberately distinct from the sibling common tools:
``DateTimeTool`` performs absolute datetime operations (parsing,
formatting, timezone conversion, calendar arithmetic), ``DurationTool``
converts duration *amounts* between units ("PT3H" ↔ 180 minutes), and
this tool handles the *humanized relative* layer between the two — a
timestamp rendered as speech, and speech parsed back into a timestamp.

Two modes
---------

``to_relative``
    Given a datetime (ISO 8601 string) and a reference "now", produce
    the humanized relative expression in English or Chinese. ``week``
    never appears in the output (the ladder below skips it), but it is
    a first-class unit for parsing.

``from_relative``
    Given a relative expression — English ("3 hours ago", "in 2 days",
    "2 days from now", "a minute ago", case-insensitive, common
    abbreviations such as "30s ago" / "2 hrs ago") or Chinese ("3小时前",
    "2天后", "刚刚", "刚才") — produce the absolute datetime at the same
    offset from the reference "now". Parsing auto-detects the language
    regardless of the ``language`` option (which only styles
    ``to_relative`` output).

``both_dirs`` — the bidirectional guarantee
-------------------------------------------

The two modes are documented inverses of each other: every string
``to_relative`` emits parses back under ``from_relative`` to the
reference offset by exactly ``N`` units ("a minute ago" → 60 seconds
earlier, "2 months ago" → 60 days earlier), and feeding that datetime
through ``to_relative`` again reproduces the original string. Agents
can therefore chain the modes — parse a scraped "2 days ago" into a
datetime, re-render it in the other language — without drift.

Threshold ladder (moment.js-style)
----------------------------------

``to_relative`` buckets the absolute delta with the classic moment.js
``humanize`` ladder (the hard-coded boundaries of moment.js ≤ 2.17's
``fromNow`` / ``humanize`` implementation). Months count 30 days and
years count 365 days; bucket values round half away from zero
(moment's ``Math.round``), not banker's rounding:

==================  ============================  ==============
Delta (absolute)    English                      Chinese
==================  ============================  ==============
< 45 s              N second(s) ago / in N s     N秒前 / N秒后
45 s - 90 s         a minute ago / in a minute   1分钟前 / 1分钟后
90 s - 45 min       N minute(s) ago / in N min   N分钟前 / N分钟后
45 min - 90 min     an hour ago / in an hour     1小时前 / 1小时后
90 min - 22 h       N hour(s) ago / in N hours   N小时前 / N小时后
22 h - 36 h         a day ago / in a day         1天前 / 1天后
36 h - 25 d         N day(s) ago / in N days     N天前 / N天后
25 d - 45 d         a month ago / in a month     1个月前 / 1个月后
45 d - 345 d        N month(s) ago / in N month  N个月前 / N个月后
345 d - 548 d       a year ago / in a year       1年前 / 1年后
>= 548 d            N year(s) ago / in N years   N年前 / N年后
==================  ============================  ==============

Reference "now" injection
-------------------------

Determinism: the reference ``now`` is the ``reference_datetime``
argument when given, otherwise the injectable class attribute
``_now`` (set it in tests: ``RelativeTimeTool._now = fixed_now``),
and only when that is ``None`` the real wall clock (UTC) is read.
Tests never depend on the real clock unless they explicitly choose to.

Errors
------

Parameter-level problems — unknown mode or language, wrong types,
missing ``datetime`` (``to_relative``) or ``text`` (``from_relative``),
oversized text — raise ``ValueError`` before any computation,
mirroring the other common tools. Content-level problems — an
unparseable datetime string, mixing naive and timezone-aware values,
an unknown unit, a malformed expression, or an offset that overflows
the datetime range — come back as a structured ``error`` payload
(``{"type": ..., "message": ..., "position": ...}``) with ``position``
being the 0-based character index into the whitespace-collapsed input
where the problem was detected, so an agent can react without
catching exceptions.
"""

import datetime as datetime_module
import math
import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Fixed-length unit constants (spec: month = 30 days, year = 365 days).
_SECOND = 1.0
_MINUTE = 60.0
_HOUR = 3600.0
_DAY = 86400.0
_WEEK = 604800.0
_MONTH = 30.0 * _DAY
_YEAR = 365.0 * _DAY

# Canonical unit name -> length in seconds.
UNIT_SECONDS: dict[str, float] = {
    "second": _SECOND,
    "minute": _MINUTE,
    "hour": _HOUR,
    "day": _DAY,
    "week": _WEEK,
    "month": _MONTH,
    "year": _YEAR,
}

# English unit spellings accepted by from_relative (case-insensitive).
_EN_UNIT_ALIASES: dict[str, str] = {
    "second": "second",
    "seconds": "second",
    "sec": "second",
    "secs": "second",
    "s": "second",
    "minute": "minute",
    "minutes": "minute",
    "min": "minute",
    "mins": "minute",
    "m": "minute",
    "hour": "hour",
    "hours": "hour",
    "hr": "hour",
    "hrs": "hour",
    "h": "hour",
    "day": "day",
    "days": "day",
    "d": "day",
    "week": "week",
    "weeks": "week",
    "wk": "week",
    "wks": "week",
    "w": "week",
    "month": "month",
    "months": "month",
    "mo": "month",
    "mos": "month",
    "year": "year",
    "years": "year",
    "yr": "year",
    "yrs": "year",
    "y": "year",
}

# Chinese unit spellings accepted by from_relative.
_ZH_UNIT_ALIASES: dict[str, str] = {
    "秒": "second",
    "秒钟": "second",
    "分钟": "minute",
    "分": "minute",
    "小时": "hour",
    "时": "hour",
    "天": "day",
    "日": "day",
    "周": "week",
    "星期": "week",
    "个月": "month",
    "月": "month",
    "年": "year",
}

# Chinese rendering of each canonical unit (to_relative output).
_ZH_UNIT_TEXT: dict[str, str] = {
    "second": "秒",
    "minute": "分钟",
    "hour": "小时",
    "day": "天",
    "week": "周",
    "month": "个月",
    "year": "年",
}

# The classic moment.js humanize ladder: each row is an (exclusive
# upper bound of |delta| in seconds, value divisor or None, canonical
# unit). A None divisor marks the singular "a unit" buckets; otherwise
# the bucket value is round_half_up(|delta| / divisor). Months count
# 30 days, years 365 days.
_LADDER: tuple[tuple[float, float | None, str], ...] = (
    (45.0, _SECOND, "second"),
    (90.0, None, "minute"),
    (45.0 * _MINUTE, _MINUTE, "minute"),
    (90.0 * _MINUTE, None, "hour"),
    (22.0 * _HOUR, _HOUR, "hour"),
    (36.0 * _HOUR, None, "day"),
    (25.0 * _DAY, _DAY, "day"),
    (45.0 * _DAY, None, "month"),
    (345.0 * _DAY, _MONTH, "month"),
    (548.0 * _DAY, None, "year"),
    (math.inf, _YEAR, "year"),
)

# English article form used for the "a minute" / "an hour" buckets.
_EN_ARTICLE: dict[str, str] = {
    "second": "a second",
    "minute": "a minute",
    "hour": "an hour",
    "day": "a day",
    "week": "a week",
    "month": "a month",
    "year": "a year",
}

# Number token: word values ("a" / "an") require a separating space,
# digits may hug the unit ("30s ago", "2hrs from now"). The captured
# value includes its trailing space — strip before converting.
_NUM_PART = r"(?P<value>(?:a|an)\s+|\d+\s*)"
# Longest-first so "seconds" is not matched as "second" + "s".
_EN_UNIT_PART = (
    r"(?:seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d" r"|weeks?|wks?|w|months?|mos?|mo|years?|yrs?|y)"
)
_ZH_UNIT_PART = r"(?:秒钟|秒|分钟|分|小时|时|星期|周|天|日|个月|月|年)"

# Grammar accepted by from_relative. English is case-insensitive; the
# ZH pattern anchors on the trailing 前 (past) / 后 (future). The value
# token carries no sign of its own — the direction comes from the
# surrounding marker (ago / in / from now / 前 / 后).
_RE_ZH = re.compile(rf"^(?P<value>\d+)\s*(?P<unit>{_ZH_UNIT_PART})(?P<dir>前|后)$")
_RE_EN_PAST = re.compile(rf"^{_NUM_PART}(?P<unit>{_EN_UNIT_PART})\s+ago$", re.IGNORECASE)
_RE_EN_IN = re.compile(rf"^in\s+{_NUM_PART}(?P<unit>{_EN_UNIT_PART})$", re.IGNORECASE)
_RE_EN_FROM_NOW = re.compile(rf"^{_NUM_PART}(?P<unit>{_EN_UNIT_PART})\s+from\s+now$", re.IGNORECASE)
# Diagnostic shape used to build positioned error payloads: the leading
# "in <number>" of a well-formed English expression.
_RE_EN_HEAD = re.compile(r"^(?:in\s+)?(?:(?:a|an)\s+|\d+\s*)", re.IGNORECASE)

_MAX_TEXT_CHARS = 500


class _ContentError(Exception):
    """Internal marker: convert to a structured error payload, not a raise."""

    def __init__(self, error_type: str, message: str, position: int = 0) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.position = position


class RelativeTimeTool(Tool):
    """Convert datetimes to humanized relative time and back, pure stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any computation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "relative_time_tool"
    description: str = (
        "Relative time tool — humanized timestamps ('3 hours ago' / "
        "'in 2 days' / '3小时前' / '2天后' / '刚刚') converted in both "
        "directions, pure Python stdlib, no network required. "
        "mode='to_relative' renders a datetime against a reference "
        "'now' with the standard moment.js-style threshold ladder in "
        "English or Chinese (language='en'|'zh'); mode='from_relative' "
        "parses such expressions back into the datetime at the same "
        "offset from the reference 'now'. Deterministic via the "
        "injectable reference 'now' (reference_datetime argument or "
        "the _now class attribute; the real clock is only read when "
        "both are unset)."
    )

    MODES: ClassVar[tuple] = ("to_relative", "from_relative")
    LANGUAGES: ClassVar[tuple] = ("en", "zh")

    # Injectable reference clock: set on the class (or an instance) for
    # deterministic tests. When None the tool reads the real UTC clock —
    # and only then.
    _now: ClassVar[datetime_module.datetime | None] = None

    max_text_chars: int = _MAX_TEXT_CHARS

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        datetime: Any = None,
        text: Any = None,
        reference_datetime: Any = None,
        language: Any = None,
    ) -> dict[str, Any]:
        """Run one relative-time conversion.

        Args:
            mode (str): ``to_relative`` (datetime → humanized string) or
                ``from_relative`` (humanized string → datetime).
            datetime (str): ISO 8601 datetime string for
                ``to_relative``; not used by ``from_relative``.
            text (str): The relative expression for ``from_relative``
                (e.g. ``"3 hours ago"``, ``"in 2 days"``, ``"3小时前"``,
                ``"刚刚"``); not used by ``to_relative``.
            reference_datetime (str): Optional ISO 8601 reference
                "now"; defaults to the injectable ``_now`` class
                attribute and finally the real UTC clock.
            language (str): Output style for ``to_relative`` — ``en``
                (default) or ``zh``. ``from_relative`` parses English
                and Chinese regardless of this option.

        Returns:
            Dict[str, Any]: The conversion result (a ``result`` string
                plus the call context) or a structured ``error``
                payload for content-level failures (invalid datetime,
                mixed naive/aware values, unknown unit, malformed
                expression, out-of-range offset).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        clean_language = self._validate_language(language)
        if mode == "to_relative":
            return self._run_to_relative(datetime, reference_datetime, clean_language)
        return self._run_from_relative(text, reference_datetime, clean_language)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"relative_time_tool: {message}")

    @classmethod
    def _validate_language(cls, language: Any) -> str:
        """Validate the ``language`` option, defaulting to English."""
        if language is None:
            return "en"
        if isinstance(language, bool) or not isinstance(language, str):
            cls._invalid(f"language must be one of: {', '.join(cls.LANGUAGES)} (got {language!r})")
        normalized = language.strip().lower()
        if normalized not in cls.LANGUAGES:
            cls._invalid("language must be one of: " f"{', '.join(cls.LANGUAGES)} (got {language!r})")
        return normalized

    @classmethod
    def _validate_datetime_param(cls, value: Any, label: str) -> str:
        """Type-check a datetime parameter (content is parsed later)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a non-empty ISO 8601 string (got {value!r})")
        if not value.strip():
            cls._invalid(f"{label} must be a non-empty ISO 8601 string (got '')")
        return value

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` expression for ``from_relative``."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text.strip():
            cls._invalid("text must be a non-empty string (got whitespace only)")
        if len(text) > _MAX_TEXT_CHARS:
            cls._invalid(f"text exceeds the {_MAX_TEXT_CHARS}-character limit " f"(got {len(text)} characters)")
        return " ".join(text.split())

    # ------------------------------------------------------------------ #
    # Reference "now" resolution and datetime parsing
    # ------------------------------------------------------------------ #

    def _resolve_reference(self, reference_datetime: Any) -> datetime_module.datetime:
        """Resolve the reference 'now': argument > _now attribute > clock."""
        if reference_datetime is not None:
            clean = self._validate_datetime_param(reference_datetime, "reference_datetime")
            return self._parse_datetime(clean)
        if self._now is not None:
            return self._now
        return datetime_module.datetime.now(datetime_module.timezone.utc)

    @staticmethod
    def _parse_datetime(value: str) -> datetime_module.datetime:
        """Parse an ISO 8601 datetime string strictly.

        Raises ``_ContentError`` (converted to a payload by the caller)
        when the string is not a valid ISO 8601 datetime.
        """
        try:
            return datetime_module.datetime.fromisoformat(value.strip())
        except ValueError:
            raise _ContentError(
                "invalid_datetime",
                "not a valid ISO 8601 datetime; accepted forms include "
                "'2026-10-19 12:00:00', '2026-10-19T12:00:00+08:00' and "
                "'2026-10-19' "
                f"(got {value.strip()[:64]!r})",
            ) from None

    # ------------------------------------------------------------------ #
    # to_relative: datetime -> humanized string
    # ------------------------------------------------------------------ #

    def _run_to_relative(self, datetime_value: Any, reference_datetime: Any, language: str) -> dict[str, Any]:
        """Render a datetime as a humanized relative expression."""
        context: dict[str, Any] = {"mode": "to_relative", "language": language}
        try:
            target = self._parse_datetime(self._validate_datetime_param(datetime_value, "datetime"))
            now = self._resolve_reference(reference_datetime)
            try:
                delta_seconds = (target - now).total_seconds()
            except TypeError:
                raise _ContentError(
                    "inconsistent_awareness",
                    "datetime and reference_datetime must both be naive or "
                    "both timezone-aware; mix a naive value with an aware "
                    "reference (or vice versa) is ambiguous — pass an "
                    "explicit offset such as '+00:00'",
                ) from None
        except _ContentError as exc:
            return self._error_result(context, exc)

        text, unit, value = self._humanize(delta_seconds, language)
        direction = "future" if delta_seconds > 0 else "past"
        return {
            **context,
            "datetime": target.isoformat(sep=" "),
            "reference_datetime": now.isoformat(sep=" "),
            "delta_seconds": delta_seconds,
            "direction": direction,
            "unit": unit,
            "value": value,
            "result": text,
        }

    @classmethod
    def _humanize(cls, delta_seconds: float, language: str) -> tuple[str, str, int]:
        """Bucket a signed delta (seconds) per the moment.js-style ladder.

        Returns the rendered expression plus the canonical ``unit`` and
        ``value`` it stands for, so callers can echo the quantization.
        """
        future = delta_seconds > 0
        seconds = abs(delta_seconds)

        divisor, unit = next(
            (row_divisor, row_unit) for row_bound, row_divisor, row_unit in _LADDER if seconds < row_bound
        )
        if divisor is None:
            value, article = 1, True
        else:
            value, article = cls._round_half_up(seconds / divisor), False

        if language == "zh":
            text = f"{value}{_ZH_UNIT_TEXT[unit]}{'后' if future else '前'}"
        elif article:
            stem = _EN_ARTICLE[unit]
            text = f"in {stem}" if future else f"{stem} ago"
        else:
            plural = "" if value == 1 else "s"
            stem = f"{value} {unit}{plural}"
            text = f"in {stem}" if future else f"{stem} ago"
        return text, unit, value

    @staticmethod
    def _round_half_up(value: float) -> int:
        """Round half away from zero (moment.js ``Math.round`` semantics)."""
        return math.floor(value + 0.5)

    # ------------------------------------------------------------------ #
    # from_relative: humanized string -> datetime
    # ------------------------------------------------------------------ #

    def _run_from_relative(self, text: Any, reference_datetime: Any, language: str) -> dict[str, Any]:
        """Parse a relative expression into a datetime offset from 'now'."""
        context: dict[str, Any] = {"mode": "from_relative"}
        try:
            clean_text = self._validate_text(text)
            now = self._resolve_reference(reference_datetime)
            value, unit, future = self._parse_expression(clean_text)
            # 刚刚 / 刚才 (unit is None) map to exactly the reference now.
            offset = 0.0 if unit is None else UNIT_SECONDS[unit] * value * (1.0 if future else -1.0)
            try:
                result_dt = now + datetime_module.timedelta(seconds=offset)
            except (OverflowError, OSError):
                raise _ContentError(
                    "out_of_range",
                    "the parsed offset overflows the datetime range "
                    f"(expression {clean_text[:64]!r}, offset {offset} seconds)",
                    position=0,
                ) from None
        except _ContentError as exc:
            return self._error_result(context, exc)

        if offset == 0:
            direction = "now"
        elif offset > 0:
            direction = "future"
        else:
            direction = "past"
        return {
            **context,
            "text": clean_text,
            "reference_datetime": now.isoformat(sep=" "),
            "direction": direction,
            "offset_seconds": offset,
            "value": value,
            "unit": unit,
            "result": result_dt.isoformat(sep=" "),
        }

    @classmethod
    def _parse_expression(cls, text: str) -> tuple[int, str | None, bool]:
        """Parse a whitespace-collapsed expression into (value, unit, future).

        Raises ``_ContentError`` with a 0-based ``position`` into
        ``text`` for unknown units and malformed expressions.
        """
        # Chinese "刚刚" / "刚才" — exactly now.
        if text in ("刚刚", "刚才"):
            return 0, None, False

        match = _RE_ZH.match(text)
        if match:
            unit = _ZH_UNIT_ALIASES[match.group("unit")]
            return int(match.group("value")), unit, match.group("dir") == "后"

        for pattern, future in ((_RE_EN_PAST, False), (_RE_EN_IN, True), (_RE_EN_FROM_NOW, True)):
            match = pattern.match(text)
            if match:
                unit = _EN_UNIT_ALIASES[match.group("unit").lower()]
                raw_value = match.group("value").strip()
                value = 1 if raw_value.lower() in ("a", "an") else int(raw_value)
                return value, unit, future

        raise cls._diagnose_expression(text)

    # ------------------------------------------------------------------ #
    # Error diagnostics for unparseable expressions
    # ------------------------------------------------------------------ #

    @staticmethod
    def _diagnose_expression(text: str) -> _ContentError:
        """Explain why an expression did not parse, with a position."""
        # English-shaped head: "[in] <number> ..." — blame the unit
        # token when it is unknown, otherwise the trailer.
        head = _RE_EN_HEAD.match(text)
        if head:
            rest = text[head.end() :]
            token_match = re.match(r"\S+", rest)
            if token_match is None:
                return _ContentError(
                    "malformed_expression",
                    "missing unit after the number; expected forms like "
                    "'3 hours ago', 'in 2 days', '3 hours from now', "
                    "'3小时前' or '2天后'",
                    position=head.end(),
                )
            token = token_match.group(0)
            if token.lower() not in _EN_UNIT_ALIASES and token not in _ZH_UNIT_ALIASES:
                return _ContentError(
                    "unknown_unit",
                    f"unknown unit {token!r}; expected one of: "
                    "second/minute/hour/day/week/month/year (English, "
                    "with common abbreviations) or "
                    "秒/分钟/小时/天/周/个月/年 (Chinese)",
                    position=head.end(),
                )
            trailer = rest[token_match.end() :].strip()
            if trailer:
                detail = f", got trailing {trailer[:32]!r}"
            else:
                detail = ", the direction marker ('ago' / 'in ...' / '... from now' / '前' / '后') is missing"
            return _ContentError(
                "malformed_expression",
                "unrecognized structure after the unit; expected '... ago' "
                "(past), 'in N unit' or 'N unit from now' (future)" + detail,
                position=head.end() + token_match.end(),
            )

        # Chinese-shaped: digits followed by something and 前/后 —
        # blame the unit in the middle when it is unknown.
        zh = re.match(r"^(?P<value>\d+)\s*(?P<mid>\S*?)(前|后)$", text)
        if zh and zh.group("mid"):
            mid = zh.group("mid")
            return _ContentError(
                "unknown_unit",
                f"unknown unit {mid!r}; expected one of " "秒/分钟/小时/天/周/个月/年 or their English spellings",
                position=zh.start("mid"),
            )

        return _ContentError(
            "malformed_expression",
            "not a recognized relative-time expression; expected forms "
            "like '3 hours ago', 'in 2 days', '2 days from now', "
            "'a minute ago', '3小时前', '2天后', '刚刚' or '刚才'",
            position=0,
        )

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(context: dict[str, Any], exc: _ContentError) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {
                "type": exc.error_type,
                "message": str(exc.message)[:500],
                "position": exc.position,
            },
        }
