#!/usr/bin/env python3

# @Time    : 2026/10/06
# @FileName: number_formatter_tool.py

"""
Number Formatter Tool — human-friendly formatting of numeric values.

A dependency-free formatting utility for agent workflows. Agents frequently
need to present raw numbers — byte counts, durations, ratios, currency
amounts — in a form a human actually reads. This tool concentrates those
presentations behind a single ``mode``-style ``execute`` method:

- ``format``: general formatting with thousands separators, fixed decimal
  places, prefix / suffix and an optional currency symbol;
- ``file_size``: bytes to ``B / KB / MB / GB / TB / PB`` using either the
  binary (1024) or decimal (1000) step;
- ``duration``: seconds to a combination of weeks, days, hours, minutes,
  seconds (and milliseconds), in a compact (``1d 2h 3m``) or verbose
  (``1 day, 2 hours, 3 minutes``) style;
- ``percentage``: a fraction (``0.1234``) to a percentage string
  (``12.3%``);
- ``scientific``: scientific notation (``1.23e+06``) with the mantissa and
  exponent exposed separately.

All results are structured dicts carrying a ``status`` field
(``success`` / ``error``); errors are returned, never raised, so agents can
branch on the response instead of catching exceptions. The ``value``
argument accepts numbers or numeric strings (thousands-separator commas
and surrounding whitespace tolerated) and is bounded by ``max_abs_value``
so a mistaken exponent or unbounded input cannot produce absurd output.

Addresses #252 (common utility tools).
"""

import math
from typing import Any

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation exceptions into structured tool
# responses instead of raising.
# ruff: noqa: TRY003

# Hard ceiling on the magnitude of the input value. Anything larger almost
# certainly indicates a caller mistake (for example passing an exponent or
# a byte count where a count of files was expected).
_MAX_ABS_VALUE = 10**18

# Ceiling for the ``decimals`` argument shared by every mode. Python
# floats carry ~15 significant decimal digits, so more precision than this
# is meaningless decoration.
_MAX_DECIMALS = 15

# file_size units, in increasing order, for both step systems. The binary
# system uses the colloquial KB/MB/... labels (strict ISO spelling would
# be KiB/MiB/...); the chosen ``system`` is reported in the result so the
# caller can relabel.
_FILE_SIZE_UNITS: list[str] = ["B", "KB", "MB", "GB", "TB", "PB"]
_FILE_SIZE_STEPS: dict[str, int] = {"binary": 1024, "decimal": 1000}

# Currency codes accepted by the ``format`` mode, mapped to the symbol
# placed immediately before the (signed) magnitude.
_CURRENCY_SYMBOLS: dict[str, str] = {
    "usd": "$",
    "eur": "€",
    "gbp": "£",
    "cny": "¥",
    "jpy": "¥",
}

# duration decomposition: unit name -> length in milliseconds.
_DURATION_UNITS_MS: dict[str, int] = {
    "week": 7 * 24 * 60 * 60 * 1000,
    "day": 24 * 60 * 60 * 1000,
    "hour": 60 * 60 * 1000,
    "minute": 60 * 1000,
    "second": 1000,
    "millisecond": 1,
}

_SUPPORTED_MODES = ("format", "file_size", "duration", "percentage", "scientific")


def _strip_number_string(raw: str) -> str:
    """Normalise a numeric string: drop spaces and thousands commas."""
    return raw.replace(",", "").replace(" ", "").replace("_", "")


class NumberFormatterTool(Tool):
    """Format numbers for human readers (separators, sizes, durations...).

    Attributes:
        max_abs_value: Largest absolute input magnitude accepted. Inputs
            whose absolute value exceeds this are rejected with a
            ``validation_error``. Default 10**18.
        max_decimals: Largest ``decimals`` value accepted by any mode.
            Default 15.
    """

    name: str = "number_formatter_tool"
    description: str | None = (
        "Format numbers for humans: thousands separators, currency, file "
        "sizes (binary/decimal), durations, percentages and scientific "
        "notation. Pure Python, no dependencies."
    )
    input_keys: list[str] | None = Field(
        default_factory=lambda: ["mode", "value"])

    max_abs_value: int = _MAX_ABS_VALUE
    max_decimals: int = _MAX_DECIMALS

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def execute(
        self,
        mode: str,
        value: Any = None,
        decimals: int | None = None,
        thousands_separator: bool = True,
        prefix: str = "",
        suffix: str = "",
        currency: str | None = None,
        system: str = "binary",
        unit: str | None = None,
        style: str = "compact",
        **_: Any,
    ) -> dict:
        """Run one formatting ``mode`` over ``value``.

        Returns a structured dict. On success it carries ``formatted``
        plus mode-specific fields; on error it carries ``error_type`` and
        ``error``. Errors are returned, never raised.
        """
        try:
            op = self._normalize_mode(mode)
            numeric = self._coerce_value(value)
            self._check_magnitude(numeric)
            if op == "format":
                return self._format_number(
                    numeric, decimals, thousands_separator, prefix, suffix, currency)
            if op == "file_size":
                return self._format_file_size(
                    numeric, decimals, system, unit, thousands_separator)
            if op == "duration":
                return self._format_duration(numeric, style)
            if op == "percentage":
                return self._format_percentage(
                    numeric, decimals, thousands_separator)
            return self._format_scientific(numeric, decimals)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc), mode)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error("operation_error", f"Formatting failed: {exc}", mode)

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

    def _coerce_value(self, value: Any) -> float:
        """Coerce ``value`` to a finite float, rejecting bad inputs."""
        if isinstance(value, bool):
            # bool is a subclass of int but is almost certainly a mistake.
            raise TypeError("value must be a number, not a boolean")
        if value is None:
            raise ValueError("value is required")
        if isinstance(value, str):
            stripped = _strip_number_string(value.strip())
            if not stripped:
                raise ValueError("value must not be an empty string")
            try:
                numeric = float(stripped)
            except ValueError as exc:
                raise ValueError(f"value {value!r} is not a valid number") from exc
        elif isinstance(value, (int, float)):
            numeric = float(value)
        else:
            raise TypeError("value must be a number or numeric string")
        if math.isnan(numeric) or math.isinf(numeric):
            raise ValueError("value must be a finite number")
        return numeric

    def _check_magnitude(self, numeric: float) -> None:
        if abs(numeric) > self.max_abs_value:
            raise ValueError(
                f"|value| must not exceed max_abs_value ({self.max_abs_value})")

    def _normalize_decimals(self, decimals: int | None,
                            default: int) -> int:
        if decimals is None:
            return default
        if isinstance(decimals, bool) or not isinstance(decimals, int):
            raise TypeError("decimals must be an integer")
        if decimals < 0 or decimals > self.max_decimals:
            raise ValueError(
                f"decimals must be within [0, {self.max_decimals}]")
        return decimals

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

    # ------------------------------------------------------------------
    # mode: format
    # ------------------------------------------------------------------
    def _format_number(
        self,
        value: float,
        decimals: int | None,
        thousands_separator: bool,
        prefix: str,
        suffix: str,
        currency: str | None,
    ) -> dict:
        """Thousands separators, fixed decimals, prefix/suffix, currency."""
        if not isinstance(prefix, str) or not isinstance(suffix, str):
            raise TypeError("prefix and suffix must be strings")
        if not isinstance(thousands_separator, bool):
            raise TypeError("thousands_separator must be a boolean")
        symbol = ""
        if currency is not None:
            if not isinstance(currency, str):
                raise TypeError("currency must be a string")
            key = currency.strip().lower()
            if key not in _CURRENCY_SYMBOLS:
                raise ValueError(
                    f"Unsupported currency {currency!r}. Supported: "
                    + ", ".join(sorted(_CURRENCY_SYMBOLS))
                )
            symbol = _CURRENCY_SYMBOLS[key]

        sign = "-" if value < 0 else ""
        magnitude = abs(value)
        places = self._normalize_decimals(decimals, default=-1)
        if places >= 0:
            body = f"{magnitude:,.{places}f}" if thousands_separator \
                else f"{magnitude:.{places}f}"
        else:
            # No fixed precision: keep the value's natural digits.
            body = f"{magnitude:,}" if thousands_separator else str(magnitude)
            if body.endswith(".0"):
                body = body[:-2]
        formatted = f"{prefix}{sign}{symbol}{body}{suffix}"
        return {
            "status": "success",
            "mode": "format",
            "input": value,
            "formatted": formatted,
            "currency": currency.strip().lower() if currency else None,
        }

    # ------------------------------------------------------------------
    # mode: file_size
    # ------------------------------------------------------------------
    def _format_file_size(
        self,
        value: float,
        decimals: int | None,
        system: str,
        unit: str | None,
        thousands_separator: bool = True,
    ) -> dict:
        """Bytes to a human-readable size string."""
        if not isinstance(system, str):
            raise TypeError("system must be a string")
        if not isinstance(thousands_separator, bool):
            raise TypeError("thousands_separator must be a boolean")
        key = system.strip().lower()
        if key not in _FILE_SIZE_STEPS:
            raise ValueError(
                f"Unsupported system {system!r}. Supported: binary, decimal")
        if value < 0:
            raise ValueError("file size must not be negative")
        places = self._normalize_decimals(decimals, default=2)

        step = _FILE_SIZE_STEPS[key]
        unit_index = self._select_file_size_unit(value, step, unit)
        chosen = _FILE_SIZE_UNITS[unit_index]
        divisor = float(step) ** unit_index
        scaled = value / divisor if divisor > 1 else value
        rounded = round(scaled, places)
        text = f"{rounded:,.{places}f}" if thousands_separator \
            else f"{rounded:.{places}f}"
        text = text.rstrip("0").rstrip(".")
        if text in ("", "-0"):
            text = "0"
        return {
            "status": "success",
            "mode": "file_size",
            "input": value,
            "formatted": f"{text} {chosen}",
            "value": rounded,
            "unit": chosen,
            "system": key,
        }

    @staticmethod
    def _select_file_size_unit(value: float, step: int,
                               unit: str | None) -> int:
        """Return the index into ``_FILE_SIZE_UNITS`` to format with.

        An explicit ``unit`` pins the index; otherwise the largest unit
        whose magnitude still fits ``value`` is chosen automatically.
        """
        if unit is not None:
            if not isinstance(unit, str):
                raise TypeError("unit must be a string")
            unit_key = unit.strip().upper()
            if unit_key not in _FILE_SIZE_UNITS:
                raise ValueError(
                    f"Unsupported unit {unit!r}. Supported: "
                    + ", ".join(_FILE_SIZE_UNITS)
                )
            return _FILE_SIZE_UNITS.index(unit_key)
        for idx in range(len(_FILE_SIZE_UNITS) - 1, -1, -1):
            if value >= step**idx:
                return idx
        return 0

    # ------------------------------------------------------------------
    # mode: duration
    # ------------------------------------------------------------------
    def _format_duration(self, value: float, style: str) -> dict:
        """Seconds to a combination of weeks/days/hours/minutes/seconds."""
        if not isinstance(style, str):
            raise TypeError("style must be a string")
        style_key = style.strip().lower()
        if style_key not in ("compact", "verbose"):
            raise ValueError(
                f"Unsupported style {style!r}. Supported: compact, verbose")
        if value < 0:
            raise ValueError("duration must not be negative")

        total_ms = round(value * 1000)
        breakdown: dict[str, float] = {}
        remainder = total_ms
        for name in ("week", "day", "hour", "minute"):
            length = _DURATION_UNITS_MS[name]
            breakdown[name + "s"] = remainder // length
            remainder %= length
        breakdown["milliseconds"] = remainder % 1000
        breakdown["seconds"] = (remainder - breakdown["milliseconds"]) // 1000

        formatted = (
            self._verbose_duration(breakdown)
            if style_key == "verbose"
            else self._compact_duration(breakdown)
        )

        return {
            "status": "success",
            "mode": "duration",
            "input": value,
            "formatted": formatted,
            "breakdown": {
                "weeks": int(breakdown["weeks"]),
                "days": int(breakdown["days"]),
                "hours": int(breakdown["hours"]),
                "minutes": int(breakdown["minutes"]),
                "seconds": breakdown["seconds"]
                + breakdown["milliseconds"] / 1000.0,
            },
            "style": style_key,
        }

    @staticmethod
    def _compact_duration(parts: dict[str, float]) -> str:
        """Compact style: ``1w 2d 3h 4m 5.5s``."""
        pieces = []
        compact_map = [
            ("weeks", "w"),
            ("days", "d"),
            ("hours", "h"),
            ("minutes", "m"),
        ]
        for key, suffix in compact_map:
            if parts[key]:
                pieces.append(f"{int(parts[key])}{suffix}")
        seconds = parts["seconds"] + parts["milliseconds"] / 1000.0
        if seconds:
            text = f"{seconds:.3f}".rstrip("0").rstrip(".")
            pieces.append(f"{text}s")
        if not pieces:
            return "0s"
        return " ".join(pieces)

    @staticmethod
    def _verbose_duration(parts: dict[str, float]) -> str:
        """Verbose style: ``1 day, 2 hours, 3.5 seconds``."""
        pieces = []
        for name in ("week", "day", "hour", "minute"):
            count = int(parts[name + "s"])
            if count:
                label = name if count == 1 else name + "s"
                pieces.append(f"{count} {label}")
        seconds = parts["seconds"] + parts["milliseconds"] / 1000.0
        if seconds:
            text = f"{seconds:.3f}".rstrip("0").rstrip(".")
            label = "second" if seconds == 1 else "seconds"
            pieces.append(f"{text} {label}")
        if not pieces:
            return "0 seconds"
        return ", ".join(pieces)

    # ------------------------------------------------------------------
    # mode: percentage
    # ------------------------------------------------------------------
    def _format_percentage(
        self,
        value: float,
        decimals: int | None,
        thousands_separator: bool,
    ) -> dict:
        """A fraction to a percentage string with the % sign."""
        if not isinstance(thousands_separator, bool):
            raise TypeError("thousands_separator must be a boolean")
        places = self._normalize_decimals(decimals, default=1)
        percent = value * 100.0
        rounded = round(percent, places)
        body = f"{rounded:,.{places}f}" if thousands_separator \
            else f"{rounded:.{places}f}"
        return {
            "status": "success",
            "mode": "percentage",
            "input": value,
            "formatted": f"{body}%",
            "percent_value": rounded,
        }

    # ------------------------------------------------------------------
    # mode: scientific
    # ------------------------------------------------------------------
    def _format_scientific(self, value: float,
                           decimals: int | None) -> dict:
        """Scientific notation with mantissa and exponent exposed."""
        places = self._normalize_decimals(decimals, default=6)
        text = f"{value:.{places}e}"
        mantissa_text, exponent_text = text.split("e")
        return {
            "status": "success",
            "mode": "scientific",
            "input": value,
            "formatted": text,
            "mantissa": float(mantissa_text),
            "exponent": int(exponent_text),
        }
