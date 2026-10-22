#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: duration_tool.py

"""Duration parsing / formatting / arithmetic tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency duration utility agents
can call for time-span plumbing: normalizing service uptimes, computing
gaps between timestamps, or doing arithmetic on offsets. It complements
``DateTimeTool`` (calendar date arithmetic) by working on *durations*
only.

The tool supports four modes:

* ``parse`` — accept an ISO-8601 duration (``PT1H30M``, ``P1DT2H``,
  ``P1Y2M3W4DT5H6M7S``, weeks ``P2W``, fractional components such as
  ``PT1.5H`` with ``.`` or ``,`` as the decimal separator, optional
  leading ``+``/``-`` sign) *or* a shorthand expression (``1d 2h 3m``,
  ``90m``, ``1.5h``, ``2 hours 15 minutes``, ``500ms``, ``1500us``) and
  return the total seconds, exact microseconds, a canonical
  days/hours/minutes/seconds/milliseconds/microseconds breakdown, the
  normalized ISO-8601 form and a humanized string. Chinese (CJK) units
  are also accepted: ``天`` (day), ``时`` / ``小时`` (hour), ``分`` /
  ``分钟`` (minute), ``秒`` / ``秒钟`` (second), plus ``毫秒`` and
  ``微秒``.
* ``humanize`` — render a number of seconds as text in one of three
  formats: ``compact`` (``26h 30m`` — hours are never folded into days),
  ``long`` (``1 day, 2:30:00`` — days in words plus an ``H:MM:SS``
  remainder clock, or spelled-out units below a day) or ``clock``
  (``26:30:00``).
* ``between`` — duration between two ISO datetimes or dates. Naive
  values are treated as being in the same (unspecified) zone; mixing
  an offset-aware value with a naive one is an error; aware values are
  compared by instant.
* ``add`` — add or subtract two duration strings (either style) and
  return the same normalized payload as ``parse``.

Conversions are fixed and documented (deterministic): 1 year = 365
days, 1 month = 30 days, 1 week = 7 days. All arithmetic is exact
``decimal.Decimal`` math quantized once, half-to-even, to whole
microseconds; sub-microsecond input precision is rounded the same way.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / format / operation,
missing required arguments, non-bool ``allow_negative``, non-finite or
non-numeric ``seconds``, oversized strings) raise a ``ValueError``,
mirroring the other common tools. Errors that depend on the *content
being processed* — unparseable durations (including unknown units and
the 0-based position where parsing failed), negative durations or
results when ``allow_negative`` is not set, magnitude above the
10**12-second cap, invalid datetimes and mixed timezone awareness —
are returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import datetime as datetime_module
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Canonical unit -> exact multiplier in microseconds (int).
_UNIT_MICROSECONDS: Dict[str, int] = {
    "y": 31_536_000_000_000,        # 365 days
    "mo": 2_592_000_000_000,        # 30 days
    "w": 604_800_000_000,           # 7 days
    "d": 86_400_000_000,
    "h": 3_600_000_000,
    "m": 60_000_000,
    "s": 1_000_000,
    "ms": 1_000,
    "us": 1,
}

# ISO-8601 letters -> canonical units, in the order the standard
# prescribes (date section: Y M W D; time section: H M S).
_ISO_DATE_UNITS: Dict[str, str] = {"Y": "y", "M": "mo", "W": "w", "D": "d"}
_ISO_TIME_UNITS: Dict[str, str] = {"H": "h", "M": "m", "S": "s"}

# Shorthand / long / CJK unit tokens -> canonical units. Both the micro
# sign "µ" (U+00B5) and the Greek mu "μ" spell microseconds: str.lower()
# does not fold one into the other, so both are listed explicitly.
_SHORTHAND_TOKENS: Dict[str, str] = {}
for _canon, _tokens in {
    "y": ("y", "yr", "yrs", "year", "years"),
    "mo": ("mo", "mon", "mons", "month", "months"),
    "w": ("w", "wk", "wks", "week", "weeks"),
    "d": ("d", "day", "days", "天"),
    "h": ("h", "hr", "hrs", "hour", "hours", "时", "小时"),
    "m": ("m", "min", "mins", "minute", "minutes", "分", "分钟"),
    "s": ("s", "sec", "secs", "second", "seconds", "秒", "秒钟"),
    "ms": ("ms", "millis", "millisecond", "milliseconds", "毫秒"),
    "us": ("us", "µs", "μs", "microsec", "microsecond", "microseconds", "微秒"),
}.items():
    for _token in _tokens:
        _SHORTHAND_TOKENS[_token] = _canon
del _canon, _tokens, _token

_MAX_INPUT_CHARS = 1_000
_MAX_PART_VALUE = Decimal(10) ** 12          # per-component literal cap
_MAX_TOTAL_SECONDS = 10 ** 12                # ~31,688 years
_MICROSECOND = Decimal(1_000_000)


def _is_ascii_digit(char: str) -> bool:
    """True only for the ASCII digits 0-9 (str.isdigit() is wider)."""
    return "0" <= char <= "9"


def _is_ascii_alpha(char: str) -> bool:
    """True for ASCII letters only (str.isalpha() is wider)."""
    return ("a" <= char <= "z") or ("A" <= char <= "Z")


def _is_cjk(char: str) -> bool:
    """True for characters in the CJK unified ideograph blocks."""
    return 0x2E80 <= ord(char) <= 0x9FFF


def _is_unit_letter(char: str) -> bool:
    """True for characters that may appear inside a shorthand unit."""
    return (
        _is_ascii_alpha(char)
        or char in ("µ", "μ")
        or _is_cjk(char)
    )


class _DurationContentError(Exception):
    """Internal: content-level failure reported as a structured payload."""

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class DurationTool(Tool):
    """Duration parsing / formatting / arithmetic tool, pure stdlib.

    Attributes:
        max_total_seconds (int): Upper bound on the magnitude of any
            duration handled, in seconds (~31,688 years); larger values
            are rejected with a structured error.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "duration_tool"
    description: str = (
        "Duration tool — pure Python stdlib, no network required. Parse "
        "ISO-8601 durations (PT1H30M, P1DT2H) and shorthand expressions "
        "('1d 2h 3m', '90m', '1.5h', CJK 天/时/分/秒) into total seconds, "
        "microseconds and canonical parts (mode='parse'); humanize a "
        "number of seconds as compact ('26h 30m'), long ('1 day, "
        "2:30:00') or clock ('26:30:00') text (mode='humanize'); measure "
        "the duration between two ISO datetimes or dates (mode='between'); "
        "and add or subtract two duration strings (mode='add'). Fixed "
        "conversions: 1y=365d, 1mo=30d, 1w=7d; microsecond precision."
    )

    MODES: ClassVar[tuple] = ("parse", "humanize", "between", "add")
    FORMATS: ClassVar[tuple] = ("compact", "long", "clock")
    OPERATIONS: ClassVar[tuple] = ("add", "subtract")

    max_total_seconds: int = 10 ** 12

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        duration: Any = None,
        seconds: Any = None,
        start: Any = None,
        end: Any = None,
        other: Any = None,
        operation: Any = None,
        format: Any = None,
        allow_negative: Any = None,
    ) -> Dict[str, Any]:
        """Run one duration operation.

        Args:
            mode (str): One of ``parse`` / ``humanize`` / ``between`` /
                ``add``.
            duration (str): The duration string to parse (``parse``) or
                the left operand (``add``). ISO-8601 or shorthand.
            seconds (int | float | str): The number of seconds to
                humanize (``humanize``). Numeric strings are accepted.
            start (str): ISO datetime or date (``between``).
            end (str): ISO datetime or date (``between``).
            other (str): The right operand duration string (``add``).
            operation (str): ``add`` (default) or ``subtract``
                (``add`` mode only).
            format (str): Humanized output style — ``compact``
                (default), ``long`` or ``clock``; used by ``humanize``,
                ``between`` and ``add``.
            allow_negative (bool): Explicitly permit negative durations
                and results. Defaults to False, in which case any
                negative duration, operand or result is a structured
                ``negative_duration`` error.

        Returns:
            Dict[str, Any]: The operation result (``result`` plus
                ``total_seconds``, ``total_microseconds``, canonical
                ``parts``, ``iso8601`` and ``humanized`` where
                applicable) or a structured ``error`` payload for
                content-level failures (invalid duration, invalid
                datetime, mixed timezone awareness, negative values
                without ``allow_negative``, magnitude above the cap).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_negative = self._validate_allow_negative(allow_negative)
        clean_format = self._validate_format(format)
        clean_operation = self._validate_operation(operation)

        try:
            if mode == "parse":
                return self._run_parse(duration, clean_negative, clean_format)
            if mode == "humanize":
                return self._run_humanize(
                    seconds, clean_negative, clean_format
                )
            if mode == "between":
                return self._run_between(
                    start, end, clean_negative, clean_format
                )
            return self._run_add(
                duration, other, clean_operation, clean_negative, clean_format
            )
        except _DurationContentError as exc:
            return self._error_result(
                {"mode": mode}, exc.error_type, exc.message
            )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"duration_tool: {message}")

    @classmethod
    def _validate_allow_negative(cls, allow_negative: Any) -> bool:
        """Validate the ``allow_negative`` flag."""
        if allow_negative is None:
            return False
        if isinstance(allow_negative, bool):
            return allow_negative
        cls._invalid(
            f"allow_negative must be a boolean (got {allow_negative!r})"
        )

    @classmethod
    def _validate_format(cls, format: Any) -> str:
        """Validate the humanized ``format`` selector."""
        if format is None:
            return "compact"
        if format not in cls.FORMATS:
            cls._invalid(
                "format must be one of: "
                f"{', '.join(cls.FORMATS)} (got {format!r})"
            )
        return format

    @classmethod
    def _validate_operation(cls, operation: Any) -> str:
        """Validate the arithmetic ``operation`` selector."""
        if operation is None:
            return "add"
        if operation not in cls.OPERATIONS:
            cls._invalid(
                "operation must be one of: "
                f"{', '.join(cls.OPERATIONS)} (got {operation!r})"
            )
        return operation

    @classmethod
    def _validate_duration_string(cls, value: Any, label: str) -> str:
        """Validate a duration string parameter (type / emptiness / size)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(
                f"{label} must be a non-empty duration string (got {value!r})"
            )
        stripped = value.strip()
        if not stripped:
            cls._invalid(
                f"{label} must be a non-empty duration string (got {value!r})"
            )
        if len(value) > _MAX_INPUT_CHARS:
            cls._invalid(
                f"{label} exceeds the {_MAX_INPUT_CHARS:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return stripped

    @classmethod
    def _validate_datetime_string(cls, value: Any, label: str) -> str:
        """Validate a datetime string parameter (type / emptiness / size)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(
                f"{label} must be a non-empty ISO datetime or date string "
                f"(got {value!r})"
            )
        stripped = value.strip()
        if not stripped:
            cls._invalid(
                f"{label} must be a non-empty ISO datetime or date string "
                f"(got {value!r})"
            )
        if len(value) > 64:
            cls._invalid(
                f"{label} exceeds the 64-character limit for datetimes "
                f"(got {len(value):,} characters)"
            )
        return stripped

    @classmethod
    def _validate_seconds(cls, seconds: Any) -> Decimal:
        """Validate the ``seconds`` parameter into an exact Decimal.

        Accepts ints, finite floats and numeric strings; rejects bools,
        NaN, infinities and anything else.
        """
        if seconds is None or isinstance(seconds, bool):
            cls._invalid(f"seconds must be a finite number (got {seconds!r})")
        if isinstance(seconds, int):
            return Decimal(seconds)
        if isinstance(seconds, float):
            if seconds != seconds or seconds in (
                float("inf"),
                float("-inf"),
            ):
                cls._invalid(
                    f"seconds must be a finite number (got {seconds!r})"
                )
            return Decimal(str(seconds))
        if isinstance(seconds, str):
            try:
                parsed = Decimal(seconds.strip())
            except Exception:
                cls._invalid(
                    f"seconds must be a finite number (got {seconds!r})"
                )
            if parsed.is_nan() or parsed.is_infinite():
                cls._invalid(
                    f"seconds must be a finite number (got {seconds!r})"
                )
            return parsed
        cls._invalid(f"seconds must be a finite number (got {seconds!r})")

    # ------------------------------------------------------------------ #
    # Core: duration-string parsing (ISO-8601 and shorthand)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_duration_string(
        cls, text: str, allow_negative: bool
    ) -> Tuple[int, str]:
        """Parse one duration string into (signed microseconds, style).

        Raises ``_DurationContentError`` for content-level problems:
        unknown units (with the 0-based position), malformed numbers,
        duplicate / out-of-order components, negative durations without
        ``allow_negative``, and magnitude above the caps.
        """
        body = text.strip()
        negative = False
        if body[:1] in ("+", "-"):
            negative = body[0] == "-"
            body = body[1:].strip()
        if not body:
            raise _DurationContentError(
                "invalid_duration",
                "duration string is empty or only contains a sign",
            )
        with localcontext() as ctx:
            ctx.prec = 60
            if body[0] in ("p", "P"):
                total_us, style = cls._parse_iso8601(body)
            else:
                total_us, style = cls._parse_shorthand(body)
        cls._check_magnitude(total_us)
        if negative:
            if not allow_negative:
                raise _DurationContentError(
                    "negative_duration",
                    "duration is negative; pass allow_negative=true to "
                    "accept it",
                )
            total_us = -total_us
        return total_us, style

    # ---------------------------- ISO-8601 --------------------------- #

    @classmethod
    def _scan_number(
        cls, body: str, index: int, decimal_separators: Tuple[str, ...]
    ) -> Tuple[Decimal, int]:
        """Scan an ASCII number starting at ``index``.

        Accepts ``digits`` or ``digits<sep>digits`` with no sign and no
        exponent; ``decimal_separators`` is ``('.', ',')`` for ISO-8601
        (the standard allows the comma) and ``('.',)`` for shorthand.
        """
        length = len(body)
        start = index
        while index < length and _is_ascii_digit(body[index]):
            index += 1
        if index == start:
            raise _DurationContentError(
                "invalid_duration",
                f"expected a number at position {start} (0-based) in "
                f"{body[:32]!r}",
            )
        digits = body[start:index]
        if index < length and body[index] in decimal_separators:
            cursor = index + 1
            fraction_start = cursor
            while cursor < length and _is_ascii_digit(body[cursor]):
                cursor += 1
            if cursor == fraction_start:
                raise _DurationContentError(
                    "invalid_duration",
                    f"decimal separator at position {index} (0-based) must "
                    f"be followed by digits in {body[:32]!r}",
                )
            digits = digits + "." + body[fraction_start:cursor]
            index = cursor
        return Decimal(digits), index

    @classmethod
    def _scan_iso_section(
        cls,
        body: str,
        index: int,
        section_units: Dict[str, str],
        section_name: str,
    ) -> Tuple[Decimal, int, int]:
        """Scan one (number unit)* run of an ISO-8601 duration section.

        Returns ``(total, new_index, component_count)``. Enforces the
        prescribed unit order, one occurrence per unit, the per-component
        magnitude cap, and that a unit letter follows every number.
        """
        length = len(body)
        total = Decimal(0)
        last_order = -1
        seen: Dict[str, bool] = {}
        components = 0
        while index < length:
            if body[index] in ("T", "t") and section_name == "date":
                break
            if not _is_ascii_digit(body[index]):
                break
            number, index = cls._scan_number(body, index, (".", ","))
            if index >= length or body[index].upper() not in section_units:
                raise _DurationContentError(
                    "invalid_duration",
                    f"expected one of the ISO-8601 {section_name} units "
                    f"({'/'.join(section_units)}) after the number ending "
                    f"at position {index - 1} (0-based) in {body[:32]!r}",
                )
            letter = body[index].upper()
            unit = section_units[letter]
            order = list(section_units).index(letter)
            if unit in seen:
                raise _DurationContentError(
                    "invalid_duration",
                    f"duplicate {section_name} unit '{letter}' at position "
                    f"{index} (0-based) in {body[:32]!r}",
                )
            if order <= last_order:
                raise _DurationContentError(
                    "invalid_duration",
                    f"unit '{letter}' at position {index} (0-based) is out "
                    f"of the prescribed order "
                    f"({''.join(section_units)}) in {body[:32]!r}",
                )
            seen[unit] = True
            last_order = order
            index += 1
            if number >= _MAX_PART_VALUE:
                raise _DurationContentError(
                    "duration_too_large",
                    f"component value {number} exceeds the per-component "
                    f"cap of {_MAX_PART_VALUE} at position {index} "
                    f"(0-based)",
                )
            total += number * _UNIT_MICROSECONDS[unit]
            components += 1
        return total, index, components

    @classmethod
    def _parse_iso8601(cls, body: str) -> Tuple[int, str]:
        """Parse the body after the leading sign of an ISO-8601 duration."""
        if body[0] not in ("P", "p"):
            raise _DurationContentError(
                "invalid_duration",
                f"ISO-8601 durations must start with 'P' (got {body[:32]!r})",
            )
        length = len(body)
        index = 1
        date_total, index, date_components = cls._scan_iso_section(
            body, index, _ISO_DATE_UNITS, "date"
        )
        time_total = Decimal(0)
        time_components = 0
        if index < length and body[index] in ("T", "t"):
            time_index = index + 1
            time_total, index, time_components = cls._scan_iso_section(
                body, time_index, _ISO_TIME_UNITS, "time"
            )
            if time_components == 0:
                raise _DurationContentError(
                    "invalid_duration",
                    f"'T' at position {time_index - 1} (0-based) must be "
                    f"followed by at least one time component in "
                    f"{body[:32]!r}",
                )
        if date_components == 0 and time_components == 0:
            raise _DurationContentError(
                "invalid_duration",
                f"duration must contain at least one component "
                f"(got {body[:32]!r})",
            )
        if index != length:
            raise _DurationContentError(
                "invalid_duration",
                f"unexpected character {body[index]!r} at position {index} "
                f"(0-based) in {body[:32]!r}",
            )
        return cls._quantize(date_total + time_total), "iso8601"

    # ---------------------------- Shorthand -------------------------- #

    @classmethod
    def _parse_shorthand(cls, body: str) -> Tuple[int, str]:
        """Parse a shorthand duration expression like '1d 2h 3m' or '2小时'."""
        length = len(body)
        index = 0

        def skip_separators(position: int) -> int:
            while position < length and body[position] in (" ", "\t"):
                position += 1
            return position

        index = skip_separators(index)
        total = Decimal(0)
        seen: Dict[str, bool] = {}
        components = 0
        while index < length:
            number, index = cls._scan_number(body, index, (".",))
            index = skip_separators(index)
            token_start = index
            if index >= length or not _is_unit_letter(body[index]):
                raise _DurationContentError(
                    "invalid_duration",
                    f"expected a unit at position {index} (0-based) in "
                    f"{body[:32]!r}",
                )
            while index < length and _is_unit_letter(body[index]):
                index += 1
            token = body[token_start:index].lower()
            unit = _SHORTHAND_TOKENS.get(token)
            if unit is None:
                raise _DurationContentError(
                    "invalid_duration",
                    f"unknown unit {token!r} at position {token_start} "
                    f"(0-based); expected one of: "
                    f"{', '.join(sorted(set(_SHORTHAND_TOKENS)))}",
                )
            if unit in seen:
                raise _DurationContentError(
                    "invalid_duration",
                    f"duplicate unit {token!r} (canonical '{unit}') at "
                    f"position {token_start} (0-based) in {body[:32]!r}",
                )
            seen[unit] = True
            if number >= _MAX_PART_VALUE:
                raise _DurationContentError(
                    "duration_too_large",
                    f"component value {number} exceeds the per-component "
                    f"cap of {_MAX_PART_VALUE} at position {token_start} "
                    f"(0-based)",
                )
            total += number * _UNIT_MICROSECONDS[unit]
            components += 1
            index = skip_separators(index)

        if components == 0:
            raise _DurationContentError(
                "invalid_duration",
                f"duration must contain at least one component "
                f"(got {body[:32]!r})",
            )
        return cls._quantize(total), "shorthand"

    # ------------------------------------------------------------------ #
    # Shared numeric helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _quantize(total: Decimal) -> int:
        """Quantize exact Decimal microseconds to an int, half-to-even."""
        with localcontext() as ctx:
            ctx.prec = 60
            return int(total.quantize(Decimal(1), rounding=ROUND_HALF_EVEN))

    @classmethod
    def _check_magnitude(cls, total_us: int) -> None:
        """Reject durations at or above the configured total cap."""
        if abs(Decimal(total_us)) >= Decimal(_MAX_TOTAL_SECONDS) * _MICROSECOND:
            raise _DurationContentError(
                "duration_too_large",
                "duration magnitude exceeds the cap of "
                f"{_MAX_TOTAL_SECONDS:,} seconds",
            )

    @classmethod
    def _parts_of(cls, total_us: int) -> Dict[str, int]:
        """Canonical breakdown of a magnitude in microseconds."""
        magnitude = abs(total_us)
        days, remainder = divmod(magnitude, 86_400_000_000)
        hours, remainder = divmod(remainder, 3_600_000_000)
        minutes, remainder = divmod(remainder, 60_000_000)
        secs, remainder = divmod(remainder, 1_000_000)
        milliseconds, microseconds = divmod(remainder, 1_000)
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": secs,
            "milliseconds": milliseconds,
            "microseconds": microseconds,
        }

    @classmethod
    def _total_seconds_of(cls, total_us: int) -> Any:
        """Total seconds as int when integral, else a 6-decimal float."""
        negative = total_us < 0
        magnitude = abs(total_us)
        if magnitude % 1_000_000 == 0:
            value: Any = magnitude // 1_000_000
        else:
            value = float(Decimal(magnitude) / _MICROSECOND)
        return -value if negative else value

    @classmethod
    def _to_iso8601(cls, total_us: int) -> str:
        """Normalized canonical ISO-8601 form (e.g. ``-P1DT2H30M0.5S``)."""
        negative = total_us < 0
        parts = cls._parts_of(total_us)
        text = "P"
        if parts["days"]:
            text += f"{parts['days']}D"
        time = ""
        if parts["hours"]:
            time += f"{parts['hours']}H"
        if parts["minutes"]:
            time += f"{parts['minutes']}M"
        fraction = parts["milliseconds"] * 1_000 + parts["microseconds"]
        if parts["seconds"] or fraction:
            if fraction:
                fraction_text = f"{fraction:06d}".rstrip("0")
                time += f"{parts['seconds']}.{fraction_text}S"
            else:
                time += f"{parts['seconds']}S"
        if time:
            text += "T" + time
        if text == "P":
            text = "PT0S"
        return "-" + text if negative else text

    @classmethod
    def _humanize_us(cls, total_us: int, fmt: str) -> str:
        """Render signed microseconds in the requested format."""
        negative = total_us < 0
        magnitude = abs(total_us)
        if fmt == "clock":
            hours, remainder = divmod(magnitude, 3_600_000_000)
            minutes, remainder = divmod(remainder, 60_000_000)
            secs, remainder = divmod(remainder, 1_000_000)
            text = f"{hours}:{minutes:02d}:{secs:02d}"
            if remainder:
                text += "." + f"{remainder:06d}".rstrip("0")
        elif fmt == "long":
            days, remainder = divmod(magnitude, 86_400_000_000)
            if days:
                text = f"{days} day" if days == 1 else f"{days} days"
                if remainder:
                    text += ", " + cls._humanize_us(remainder, "clock")
            else:
                pieces: List[str] = []
                for label, multiplier in (
                    ("hour", 3_600_000_000),
                    ("minute", 60_000_000),
                    ("second", 1_000_000),
                    ("millisecond", 1_000),
                    ("microsecond", 1),
                ):
                    value, remainder = divmod(remainder, multiplier)
                    if value:
                        pieces.append(
                            f"{value} {label}" if value == 1
                            else f"{value} {label}s"
                        )
                text = ", ".join(pieces) if pieces else "0 seconds"
        else:  # compact — from the first nonzero unit down to the last
            values: List[Tuple[str, int]] = []
            for label, multiplier in (
                ("h", 3_600_000_000),
                ("m", 60_000_000),
                ("s", 1_000_000),
                ("ms", 1_000),
                ("us", 1),
            ):
                value, magnitude = divmod(magnitude, multiplier)
                values.append((label, value))
            first = next(
                (i for i, (_, value) in enumerate(values) if value), None
            )
            if first is None:
                text = "0s"
            else:
                last = len(values) - 1
                while values[last][1] == 0:
                    last -= 1
                text = " ".join(
                    f"{value}{label}"
                    for label, value in values[first : last + 1]
                )
        return "-" + text if negative else text

    @classmethod
    def _payload(
        cls,
        context: Dict[str, Any],
        total_us: int,
        fmt: str,
        include_iso: bool = True,
    ) -> Dict[str, Any]:
        """Assemble the normalized result payload shared by all modes."""
        payload: Dict[str, Any] = {
            **context,
            "negative": total_us < 0,
            "total_seconds": cls._total_seconds_of(total_us),
            "total_microseconds": total_us,
            "parts": cls._parts_of(total_us),
        }
        if include_iso:
            payload["iso8601"] = cls._to_iso8601(total_us)
        payload["humanized"] = cls._humanize_us(total_us, fmt)
        payload["result"] = payload["total_seconds"]
        return payload

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(
        self, duration: Any, allow_negative: bool, fmt: str
    ) -> Dict[str, Any]:
        """Parse one duration string into the normalized payload."""
        clean = self._validate_duration_string(duration, "duration")
        total_us, style = self._parse_duration_string(clean, allow_negative)
        return self._payload(
            {"mode": "parse", "input": duration, "style": style},
            total_us,
            fmt,
        )

    # ------------------------------------------------------------------ #
    # humanize mode
    # ------------------------------------------------------------------ #

    def _run_humanize(
        self, seconds: Any, allow_negative: bool, fmt: str
    ) -> Dict[str, Any]:
        """Render a number of seconds as text."""
        clean_seconds = self._validate_seconds(seconds)
        if abs(clean_seconds) >= Decimal(_MAX_TOTAL_SECONDS):
            raise _DurationContentError(
                "duration_too_large",
                "seconds exceeds the cap of "
                f"{_MAX_TOTAL_SECONDS:,} seconds",
            )
        total_us = self._quantize(clean_seconds * _MICROSECOND)
        if total_us < 0 and not allow_negative:
            raise _DurationContentError(
                "negative_duration",
                "seconds is negative; pass allow_negative=true to accept it",
            )
        return self._payload(
            {"mode": "humanize", "seconds": seconds, "format": fmt},
            total_us,
            fmt,
            include_iso=False,
        )

    # ------------------------------------------------------------------ #
    # between mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_iso_datetime(value: str, label: str) -> Any:
        """Parse one ISO datetime/date string ('Z' suffix normalized)."""
        normalized = (
            value[:-1] + "+00:00" if value[-1:] in ("Z", "z") else value
        )
        try:
            return datetime_module.datetime.fromisoformat(normalized)
        except ValueError:
            raise _DurationContentError(
                "invalid_datetime",
                f"{label} must be an ISO datetime ('2026-01-01T10:30:00', "
                f"optional fraction and '+HH:MM' offset) or a date "
                f"'2026-01-01' (got {value[:64]!r})",
            )

    def _run_between(
        self, start: Any, end: Any, allow_negative: bool, fmt: str
    ) -> Dict[str, Any]:
        """Duration between two ISO datetimes or dates."""
        clean_start = self._validate_datetime_string(start, "start")
        clean_end = self._validate_datetime_string(end, "end")
        start_dt = self._parse_iso_datetime(clean_start, "start")
        end_dt = self._parse_iso_datetime(clean_end, "end")
        if (start_dt.tzinfo is None) != (end_dt.tzinfo is None):
            raise _DurationContentError(
                "mixed_timezone",
                "start and end must both be timezone-naive (treated as the "
                "same unspecified zone) or both offset-aware; got one of "
                "each",
            )
        delta = end_dt - start_dt
        total_us = (
            (delta.days * 86_400 + delta.seconds) * 1_000_000
            + delta.microseconds
        )
        self._check_magnitude(total_us)
        if total_us < 0 and not allow_negative:
            raise _DurationContentError(
                "negative_duration",
                "end is before start; pass allow_negative=true to accept "
                "the negative span",
            )
        return self._payload(
            {"mode": "between", "start": start, "end": end, "format": fmt},
            total_us,
            fmt,
        )

    # ------------------------------------------------------------------ #
    # add mode
    # ------------------------------------------------------------------ #

    def _run_add(
        self,
        duration: Any,
        other: Any,
        operation: str,
        allow_negative: bool,
        fmt: str,
    ) -> Dict[str, Any]:
        """Add or subtract two duration strings."""
        clean_left = self._validate_duration_string(duration, "duration")
        clean_right = self._validate_duration_string(other, "other")
        left_us, _ = self._parse_duration_string(clean_left, allow_negative)
        right_us, _ = self._parse_duration_string(clean_right, allow_negative)
        total_us = (
            left_us - right_us if operation == "subtract" else left_us + right_us
        )
        self._check_magnitude(total_us)
        if total_us < 0 and not allow_negative:
            raise _DurationContentError(
                "negative_duration",
                f"result of {operation} is negative; pass "
                "allow_negative=true to accept it",
            )
        return self._payload(
            {
                "mode": "add",
                "operation": operation,
                "duration": duration,
                "other": other,
            },
            total_us,
            fmt,
        )

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
