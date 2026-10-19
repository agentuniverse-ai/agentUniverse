#!/usr/bin/env python3

# @Time    : 2026/10/19
# @FileName: datetime_tool.py

"""
Date Time Tool — datetime parsing, formatting, conversion and arithmetic.

A dependency-free datetime utility for agent workflows, built exclusively
on the Python standard library (``datetime`` / ``zoneinfo``; Python 3.9+,
no third-party packages, no network access). Agents frequently need to
answer "what time is it in Tokyo", reformat a scraped timestamp, convert
between timezones, measure the distance between two events or compute a
deadline. This tool concentrates those operations behind a single
``mode``-style ``execute`` method:

- ``now``: current datetime in a timezone (IANA name, ``UTC``, ``local``
  or a fixed offset like ``+08:00``);
- ``format``: parse a datetime string with a given or auto-detected
  format and reformat it with a ``strftime`` pattern;
- ``convert``: convert a datetime between timezones (DST-aware through
  the IANA timezone database);
- ``diff``: difference between two datetimes in a chosen unit — calendar
  ``months`` / ``years`` use dateutil ``relativedelta``-style month
  arithmetic implemented manually (no dependency), while
  seconds/minutes/hours/days/weeks are exact durations;
- ``add``: date arithmetic — add or subtract years, months, weeks, days,
  hours, minutes and seconds, with end-of-month day clamping
  (2026-01-31 + 1 month = 2026-02-28).

All results are structured dicts carrying a ``status`` field
(``success`` / ``error``); errors are returned, never raised, so agents
can branch on the response instead of catching exceptions. Validation is
strict: unknown modes, malformed formats and unparseable datetimes are
rejected with informative payloads — an unknown timezone comes back with
suggestions, an unparseable datetime comes back with the exact formats
that were tried.

Deterministic testing is supported through the ``frozen_now`` attribute:
when set to a datetime, every internal "current time" read
(``now`` mode and ``diff`` without ``end_datetime``) uses it instead of
the wall clock.

Addresses #252 (common utility tools).
"""

import difflib
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation exceptions into structured tool
# responses instead of raising.
# ruff: noqa: TRY003

# Output format used by every mode when no explicit `fmt` is given.
_DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"

# Formats tried, in order, when parsing without an explicit input_fmt.
# Deliberately unambiguous-first: year-first forms, then month-first
# slash forms and English textual dates. Day-first forms such as
# 31/12/2026 are ambiguous and require an explicit input_fmt.
_PARSE_FORMATS: tuple[str, ...] = (
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y",
    "%d %B %Y",
    "%B %d, %Y",
    "%d %b %Y",
    "%b %d, %Y",
)

# Human-readable rendering of the auto-detection list for error payloads.
_FORMATS_TRIED = ", ".join(_PARSE_FORMATS) + ", ISO 8601 (fromisoformat)"

# diff units expressible as an exact number of seconds.
_DIFF_TIMEDUNITS: dict[str, float] = {
    "seconds": 1.0,
    "minutes": 60.0,
    "hours": 3600.0,
    "days": 86400.0,
    "weeks": 604800.0,
}
_DIFF_UNIT_ALIASES: dict[str, str] = {
    "s": "seconds", "sec": "seconds", "second": "seconds", "secs": "seconds",
    "m": "minutes", "min": "minutes", "minute": "minutes", "mins": "minutes",
    "h": "hours", "hour": "hours", "hrs": "hours", "hr": "hours",
    "d": "days", "day": "days",
    "w": "weeks", "week": "weeks", "wk": "weeks", "wks": "weeks",
    "mo": "months", "month": "months", "mos": "months",
    "y": "years", "yr": "years", "yrs": "years", "year": "years",
}

# add() unit kwargs and the ceiling on their magnitude. datetime years
# span 1..9999, so offsets beyond this always overflow anyway; the cap
# keeps mistakes loud and bounded.
_ADD_UNIT_KEYS: tuple[str, ...] = (
    "years", "months", "weeks", "days", "hours", "minutes", "seconds")
_MAX_UNIT_VALUE = 100_000

# Fixed-offset timezone form: +08:00, -0530, +08, ...
_FIXED_OFFSET_RE = re.compile(r"^([+-])(\d{2}):?(\d{2})?$")

# Example zones offered when a timezone name is not recognised.
_TZ_EXAMPLES = "UTC, local, +08:00, America/New_York, Europe/London, Asia/Shanghai"

# Maximum accepted length of a strftime pattern.
_MAX_FMT_LENGTH = 200

_SUPPORTED_MODES = ("now", "format", "convert", "diff", "add")


def _offset_string(offset: timedelta | None) -> str | None:
    """Render a UTC offset as ``+HH:MM`` (``+HH:MM:SS`` when needed)."""
    if offset is None:
        return None
    total = int(offset.total_seconds())
    sign = "-" if total < 0 else "+"
    total = abs(total)
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    text = f"{sign}{hours:02d}:{minutes:02d}"
    if seconds:
        text += f":{seconds:02d}"
    return text


def _days_in_month(year: int, month: int) -> int:
    """Number of days in a month, computed with plain datetime math."""
    following = datetime(year + 1, 1, 1) if month == 12 \
        else datetime(year, month + 1, 1)
    return (following - datetime(year, month, 1)).days


def _shift_months(moment: datetime, months: int) -> datetime:
    """Shift a datetime by whole calendar months, clamping the day.

    Mirrors dateutil's ``relativedelta`` month behaviour without the
    dependency: 2026-01-31 + 1 month = 2026-02-28. The time of day and
    tzinfo are preserved. Raises ValueError when the result leaves the
    supported year range 1..9999.
    """
    total = moment.month - 1 + months
    year = moment.year + total // 12
    month = total % 12 + 1
    day = min(moment.day, _days_in_month(year, month))
    return moment.replace(year=year, month=month, day=day)


def _full_months_between(start: datetime, end: datetime) -> int:
    """Whole calendar months from ``start`` to ``end`` (end - start).

    relativedelta-style: the month count is backed off when ``end`` has
    not yet reached the same day-of-month/time in a later month, so
    2025-01-31 -> 2025-02-27 is 0 months while -> 2025-02-28 is 1.
    """
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if _shift_months(start, months) > end:
        months -= 1
    elif months >= 0 and _shift_months(start, months + 1) <= end:
        months += 1
    return months


class DateTimeTool(Tool):
    """Datetime parsing, formatting, timezone conversion and arithmetic.

    Attributes:
        default_timezone: Timezone applied to naive inputs and used by
            ``now`` when none is given. Accepts ``UTC``, ``local``, an
            IANA name (``Asia/Shanghai``) or a fixed offset (``+08:00``).
            Default ``UTC``.
        default_format: strftime pattern used for output when no ``fmt``
            is supplied. Default ``%Y-%m-%d %H:%M:%S``.
        max_unit_value: Largest absolute offset accepted by each ``add``
            unit. Default 100000.
        frozen_now: Optional datetime pinning the internal clock for
            deterministic tests; ``now`` and ``diff`` without
            ``end_datetime`` read it instead of the wall clock.
    """

    name: str = "datetime_tool"
    description: str | None = (
        "Datetime operations: current time in any timezone (now), parse "
        "and reformat datetime strings (format), convert between "
        "timezones (convert), difference between datetimes in chosen "
        "units including calendar months/years (diff), and date "
        "arithmetic with month-end clamping (add). Pure Python, no "
        "dependencies, no network."
    )
    input_keys: list[str] | None = Field(default_factory=lambda: ["mode"])

    default_timezone: str = "UTC"
    default_format: str = _DEFAULT_FORMAT
    max_unit_value: int = _MAX_UNIT_VALUE
    frozen_now: datetime | None = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def execute(
        self,
        mode: str,
        datetime_str: str = "",
        end_datetime: str = "",
        timezone_str: str = "",
        target_timezone: str = "",
        input_fmt: str = "",
        fmt: str = "",
        unit: str = "days",
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        **_: Any,
    ) -> dict:
        """Run one datetime ``mode``.

        Returns a structured dict. On success it carries ``mode`` plus
        mode-specific fields (always including an ISO 8601 rendering);
        on error it carries ``error_type`` and ``error``. Errors are
        returned, never raised.
        """
        try:
            op = self._normalize_mode(mode)
            if op == "now":
                return self._now(timezone_str)
            if op == "format":
                return self._format(datetime_str, timezone_str, input_fmt, fmt)
            if op == "convert":
                return self._convert(
                    datetime_str, timezone_str, target_timezone, input_fmt, fmt)
            if op == "diff":
                return self._diff(
                    datetime_str, end_datetime, timezone_str, input_fmt, unit)
            return self._add(
                datetime_str, timezone_str, input_fmt, fmt,
                years=years, months=months, weeks=weeks, days=days,
                hours=hours, minutes=minutes, seconds=seconds)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc), mode)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error("operation_error", f"Datetime operation failed: {exc}", mode)

    # ------------------------------------------------------------------
    # Argument validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_mode(mode: Any) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        op = mode.strip().lower()
        if op not in _SUPPORTED_MODES:
            raise ValueError(
                f"Unsupported mode {mode!r}. Supported: "
                + ", ".join(_SUPPORTED_MODES)
            )
        return op

    @staticmethod
    def _error(kind: str, message: str, mode: Any) -> dict:
        result = {
            "status": "error",
            "error_type": kind,
            "error": message,
        }
        if mode is not None:
            result["mode"] = mode
        return result

    def _normalize_fmt(self, fmt: str) -> str:
        """Validate a strftime pattern by trial, or return the default."""
        if fmt is None or (isinstance(fmt, str) and not fmt.strip()):
            return self.default_format
        if not isinstance(fmt, str):
            raise TypeError("fmt must be a string")
        if len(fmt) > _MAX_FMT_LENGTH:
            raise ValueError(
                f"fmt must not exceed {_MAX_FMT_LENGTH} characters")
        try:
            datetime(2026, 1, 31, 12, 30, 45).strftime(fmt)
        except (ValueError, OverflowError) as exc:
            raise ValueError(f"Invalid strftime pattern {fmt!r}: {exc}") from exc
        return fmt

    def _get_tz(self, tz_name: Any, *, allow_empty: bool = False):
        """Resolve a timezone spec to a tzinfo.

        Accepts ``UTC``/``Z`` (case-insensitive), ``local``, fixed
        offsets (``+08:00``) and IANA names. Empty input returns None
        (callers substitute the default) unless ``allow_empty`` is set.
        Unknown names raise ValueError with suggestions.
        """
        if tz_name is None:
            tz_name = ""
        if not isinstance(tz_name, str):
            raise TypeError("timezone must be a string")
        spec = tz_name.strip()
        if not spec:
            if allow_empty:
                return None
            raise ValueError("timezone must not be empty")
        if spec.upper() in ("UTC", "Z", "ZULU"):
            return timezone.utc
        if spec.lower() == "local":
            return datetime.now().astimezone().tzinfo
        if _FIXED_OFFSET_RE.match(spec):
            return self._fixed_offset_tz(spec)
        try:
            return ZoneInfo(spec)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(self._tz_suggestion(spec)) from exc

    @staticmethod
    def _fixed_offset_tz(spec: str):
        """Build a tzinfo from a ``+HH:MM`` / ``-HHMM`` fixed offset."""
        match = _FIXED_OFFSET_RE.match(spec)
        sign = -1 if match.group(1) == "-" else 1
        hours = int(match.group(2))
        minutes = int(match.group(3) or 0)
        if hours > 23 or minutes > 59:
            raise ValueError(
                f"Invalid fixed offset {spec!r}: hours must be 00-23 "
                "and minutes 00-59")
        return timezone(sign * timedelta(hours=hours, minutes=minutes))

    @staticmethod
    def _tz_suggestion(spec: str) -> str:
        """Unknown-timezone message with close matches when available."""
        message = (f"Unknown timezone {spec!r}. Use an IANA timezone name "
                   f"or one of: {_TZ_EXAMPLES}.")
        try:
            zones = sorted(available_timezones())
        except Exception:  # pragma: no cover - platforms without tzdata
            zones = []
        matches = difflib.get_close_matches(spec, zones, n=3, cutoff=0.6)
        if matches:
            message += f" Closest matches: {', '.join(matches)}."
        return message

    def _resolve_default_tz(self, tz_name: Any):
        return self._get_tz(tz_name, allow_empty=True) \
            or self._get_tz(self.default_timezone)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def _parse_datetime(
        self, value: Any, tz_name: Any, input_fmt: Any,
    ) -> tuple[datetime, str | None]:
        """Parse a datetime string, returning (aware dt, matched format).

        With ``input_fmt`` only that pattern is tried. Otherwise the
        auto-detection list runs first, then ISO 8601. Naive results are
        localised to ``tz_name`` (or the tool default); aware results
        keep their own offset.
        """
        if input_fmt not in (None, ""):
            if not isinstance(input_fmt, str):
                raise TypeError("input_fmt must be a string")
            text = self._require_datetime_str(value)
            try:
                parsed = datetime.strptime(text, input_fmt)
            except ValueError as exc:
                raise ValueError(
                    f"{text!r} does not match input_fmt {input_fmt!r}") from exc
            matched = input_fmt
        else:
            text = self._require_datetime_str(value)
            parsed, matched = None, None
            for candidate in _PARSE_FORMATS:
                try:
                    parsed = datetime.strptime(text, candidate)
                    matched = candidate
                    break
                except ValueError:
                    continue
            if parsed is None:
                iso_text = text
                if iso_text.endswith(("Z", "z")):
                    iso_text = iso_text[:-1] + "+00:00"
                try:
                    parsed = datetime.fromisoformat(iso_text)
                    matched = "ISO 8601"
                except ValueError as exc:
                    raise ValueError(
                        f"Could not parse {text!r}. Formats tried: "
                        f"{_FORMATS_TRIED}. Day-first dates such as "
                        "31/12/2026 are ambiguous — pass input_fmt "
                        "explicitly.") from exc
        if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
            parsed = parsed.replace(tzinfo=self._resolve_default_tz(tz_name))
        return parsed, matched

    @staticmethod
    def _require_datetime_str(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("datetime_str must be a string")
        text = value.strip()
        if not text:
            raise ValueError("datetime_str is required and must not be empty")
        return text

    def _current_now(self, tz) -> datetime:
        """Current time in ``tz``, honouring the frozen test clock."""
        if self.frozen_now is not None:
            base = self.frozen_now
            if base.tzinfo is None:
                base = base.replace(tzinfo=timezone.utc)
            return base.astimezone(tz)
        return datetime.now(tz)

    # ------------------------------------------------------------------
    # mode: now
    # ------------------------------------------------------------------
    def _now(self, tz_name: Any) -> dict:
        tz = self._resolve_default_tz(tz_name)
        now = self._current_now(tz)
        return {
            "status": "success",
            "mode": "now",
            "datetime": now.strftime(self.default_format),
            "iso": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),
            "timestamp": now.timestamp(),
            "timezone": str(now.tzinfo),
            "utc_offset": _offset_string(now.utcoffset()),
        }

    # ------------------------------------------------------------------
    # mode: format
    # ------------------------------------------------------------------
    def _format(self, value: Any, tz_name: Any, input_fmt: Any,
                fmt: Any) -> dict:
        parsed, matched = self._parse_datetime(value, tz_name, input_fmt)
        output_format = self._normalize_fmt(fmt)
        return {
            "status": "success",
            "mode": "format",
            "formatted": parsed.strftime(output_format),
            "iso": parsed.isoformat(),
            "matched_input_format": matched,
            "timezone": str(parsed.tzinfo),
        }

    # ------------------------------------------------------------------
    # mode: convert
    # ------------------------------------------------------------------
    def _convert(self, value: Any, tz_name: Any, target_name: Any,
                 input_fmt: Any, fmt: Any) -> dict:
        if not isinstance(target_name, str) or not target_name.strip():
            target = timezone.utc
            target_label = "UTC"
        else:
            target = self._get_tz(target_name)
            target_label = str(target)
        parsed, _ = self._parse_datetime(value, tz_name, input_fmt)
        converted = parsed.astimezone(target)
        output_format = self._normalize_fmt(fmt)
        return {
            "status": "success",
            "mode": "convert",
            "original": parsed.strftime(output_format),
            "converted": converted.strftime(output_format),
            "original_iso": parsed.isoformat(),
            "converted_iso": converted.isoformat(),
            "from_timezone": str(parsed.tzinfo),
            "to_timezone": target_label,
            "utc_offset": _offset_string(converted.utcoffset()),
        }

    # ------------------------------------------------------------------
    # mode: diff
    # ------------------------------------------------------------------
    def _diff(self, start_str: Any, end_str: Any, tz_name: Any,
              input_fmt: Any, unit: Any) -> dict:
        if not isinstance(unit, str):
            raise TypeError("unit must be a string")
        unit_key = unit.strip().lower()
        if not unit_key:
            raise ValueError("unit must not be empty")
        unit_key = _DIFF_UNIT_ALIASES.get(unit_key, unit_key)
        if unit_key not in (*_DIFF_TIMEDUNITS, "months", "years"):
            raise ValueError(
                f"Unsupported unit {unit!r}. Supported: seconds, minutes, "
                "hours, days, weeks, months, years.")

        start, _ = self._parse_datetime(start_str, tz_name, input_fmt)
        if end_str not in (None, ""):
            end, _ = self._parse_datetime(end_str, tz_name, input_fmt)
        else:
            end = self._current_now(start.tzinfo)

        full_months = _full_months_between(start, end)
        remainder = end - _shift_months(start, full_months)
        # Sign-consistent decomposition: -14 months renders as
        # -1 year -2 months, never -1 year +10 months.
        years, months = divmod(full_months, 12)
        if full_months < 0 and months != 0:
            years += 1
            months -= 12
        breakdown = {
            "years": years,
            "months": months,
            "days": remainder.days,
            "hours": remainder.seconds // 3600,
            "minutes": remainder.seconds % 3600 // 60,
            "seconds": remainder.seconds % 60,
        }
        if unit_key == "months":
            value: float | int = full_months
        elif unit_key == "years":
            value = years
        else:
            value = round(end.timestamp() - start.timestamp(), 6) \
                / _DIFF_TIMEDUNITS[unit_key]
            value = round(value, 6)
        return {
            "status": "success",
            "mode": "diff",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "unit": unit_key,
            "value": value,
            "breakdown": breakdown,
        }

    # ------------------------------------------------------------------
    # mode: add
    # ------------------------------------------------------------------
    def _add(self, value: Any, tz_name: Any, input_fmt: Any, fmt: Any,
             **offsets: Any) -> dict:
        normalized: dict[str, int] = {}
        for key in _ADD_UNIT_KEYS:
            raw = offsets.get(key, 0)
            if isinstance(raw, bool) or not isinstance(raw, int):
                raise TypeError(f"{key} must be an integer")
            if abs(raw) > self.max_unit_value:
                raise ValueError(
                    f"|{key}| must not exceed max_unit_value "
                    f"({self.max_unit_value})")
            normalized[key] = raw
        if not any(normalized.values()):
            raise ValueError(
                "add requires at least one non-zero offset among: "
                + ", ".join(_ADD_UNIT_KEYS))

        parsed, _ = self._parse_datetime(value, tz_name, input_fmt)
        # Calendar-aware shift first (clamped month ends), then exact
        # durations for the remaining units.
        result = _shift_months(parsed, normalized["months"]
                               + 12 * normalized["years"])
        result = result + timedelta(
            weeks=normalized["weeks"],
            days=normalized["days"],
            hours=normalized["hours"],
            minutes=normalized["minutes"],
            seconds=normalized["seconds"],
        )
        output_format = self._normalize_fmt(fmt)
        return {
            "status": "success",
            "mode": "add",
            "datetime": result.strftime(output_format),
            "iso": result.isoformat(),
            "input_iso": parsed.isoformat(),
            "timezone": str(result.tzinfo),
            "offsets": normalized,
        }
