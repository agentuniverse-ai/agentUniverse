#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: range_generator_tool.py

"""Deterministic sequence / range generation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency data generator agents
can call for test fixtures, sample payloads and schedule scaffolding.
It complements ``RandomPickTool`` (#3637), which *selects* from existing
items, by *generating* new deterministic ranges.

The tool is a strictly-validated façade over plain arithmetic,
``datetime.date`` and ``decimal.Decimal`` with four modes:

* ``numbers`` — arithmetic sequences from ``start`` toward ``end`` by
  ``step`` (default ``1``). ``start`` / ``end`` / ``step`` may be ints
  or floats; a negative ``step`` produces a descending range. Stopping
  rule: the last value is the greatest ``start + k * step`` that is
  ``<= end`` for a positive step (``>= end`` for a negative step), so
  the end is included exactly when it is hit and a non-hit remainder is
  dropped. Float ranges are stepped with ``Decimal(str(value))``
  arithmetic, so ``0.1``-style steps never accumulate binary drift
  (``0.1, 0.2, 0.3 ...`` — never ``0.30000000000000004``). The optional
  ``format`` renders each value: ``number`` (default — native int /
  float), ``int``, ``float2`` (rounded half-up to two decimals),
  ``hex`` (lowercase, no prefix), ``bin`` (no prefix) and
  ``padded-N`` (zero-padded decimal string of width ``N``, 1-64).
  ``int`` / ``hex`` / ``bin`` / ``padded-N`` require all-integer
  ``start`` / ``end`` / ``step``.
* ``dates`` — ISO ``YYYY-MM-DD`` date sequences from ``start`` to
  ``end`` by ``step_days`` (default ``1``); a negative ``step_days``
  walks backwards. The same stopping rule as ``numbers`` applies
  (calendar-valid dates only — ``2024-02-29`` is accepted, ``2023-02-29``
  is not).
* ``letters`` — single-case ASCII alphabetic ranges ``a``-``z`` /
  ``A``-``Z`` via ``ord`` arithmetic; the direction is inferred from
  the operands (``z`` → ``a`` descends). Mixed-case bounds are
  rejected.
* ``weekday`` — the next ``count`` (default ``1``) occurrences of a
  weekday given by name (``monday`` ... ``sunday``, three-letter
  abbreviations, case-insensitive) starting from a ``start`` date.
  Same-day rule: if the start date already falls on the target
  weekday it is included as the first item, otherwise the list begins
  with the first following occurrence.

Every mode caps the returned list at ``max_count`` items (default
``500``, per-call override allowed within ``1-10000``). The payload
always reports ``count`` (items actually returned), ``total`` (the
logical length of the untruncated sequence, computed arithmetically so
huge ranges cannot exhaust memory) and ``truncated``.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / format / weekday,
zero step, ``start`` beyond ``end`` for the step direction — rejected
rather than silently swapped, non-finite floats, non-ISO or
calendar-invalid dates, mixed-case or multi-character letter bounds,
out-of-range counts) raise a ``ValueError``, mirroring the other
common tools.
"""

import math
import re
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP, localcontext
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_ISO_DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
_PADDED = re.compile(r"\Apadded-([1-9][0-9]{0,3})\Z")


class RangeGeneratorTool(Tool):
    """Deterministic range / sequence generator built purely on the stdlib.

    Attributes:
        max_count (int): Default cap on the number of generated items
            (overridable per call within ``1-10000``).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "range_generator_tool"
    description: str = (
        "Range generator tool — deterministic sequence generation, pure "
        "Python stdlib, no network required. Arithmetic number ranges "
        "with int/float steps via exact Decimal arithmetic "
        "(mode='numbers', optional format: int/float2/hex/bin/padded-N), "
        "ISO date ranges by step_days across month/year/leap boundaries "
        "(mode='dates'), single-case a-z/A-Z letter ranges via ord "
        "arithmetic (mode='letters'), and the next N occurrences of a "
        "named weekday from a start date (mode='weekday'). All modes cap "
        "output at max_count items (default 500) and report the logical "
        "total."
    )

    MODES: ClassVar[tuple] = ("numbers", "dates", "letters", "weekday")
    NATIVE_FORMATS: ClassVar[tuple] = ("number", "int", "float2", "hex", "bin")
    INT_ONLY_FORMATS: ClassVar[tuple] = ("int", "hex", "bin")
    # python date.weekday(): Monday=0 ... Sunday=6.
    WEEKDAYS: ClassVar[dict[str, int]] = {
        "monday": 0, "mon": 0,
        "tuesday": 1, "tue": 1,
        "wednesday": 2, "wed": 2,
        "thursday": 3, "thu": 3,
        "friday": 4, "fri": 4,
        "saturday": 5, "sat": 5,
        "sunday": 6, "sun": 6,
    }
    MAX_COUNT_LIMIT: ClassVar[int] = 10_000
    MAX_PAD_WIDTH: ClassVar[int] = 64

    max_count: int = 500

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        start: Any = None,
        end: Any = None,
        step: Any = None,
        step_days: Any = None,
        count: Any = None,
        format: Any = None,  # noqa: A002 — mirrors the YAML arg name
        weekday: Any = None,
        max_count: Any = None,
    ) -> dict[str, Any]:
        """Generate one deterministic range.

        Args:
            mode (str): One of ``numbers`` / ``dates`` / ``letters`` /
                ``weekday``.
            start (int | float | str): Range start — a number
                (``numbers``), an ISO ``YYYY-MM-DD`` date string
                (``dates`` / ``weekday``) or a single ASCII letter
                (``letters``).
            end (int | float | str): Range end — a number or an ISO
                date string; not used by ``weekday``.
            step (int | float): ``numbers`` step, default ``1``;
                negative for descending ranges. Must be non-zero.
            step_days (int): ``dates`` step in days, default ``1``;
                negative walks backwards. Must be non-zero.
            count (int): ``weekday`` mode — how many occurrences to
                generate, default ``1``, at least ``1``.
            format (str): ``numbers`` rendering — ``number`` (default),
                ``int``, ``float2``, ``hex``, ``bin`` or
                ``padded-N`` (width 1-64). ``int`` / ``hex`` / ``bin`` /
                ``padded-N`` require integer ``start`` / ``end`` /
                ``step``.
            weekday (str): ``weekday`` mode — target weekday by full or
                three-letter name, case-insensitive.
            max_count (int): Per-call override of the output cap;
                ``1-10000``, defaults to the tool's ``max_count``
                attribute (500).

        Returns:
            Dict[str, Any]: The generated sequence under ``result`` plus
                the call context and the truncation report
                (``count`` / ``total`` / ``truncated``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        cap = self._validate_max_count(max_count)
        if mode == "numbers":
            return self._run_numbers(start, end, step, format, cap)
        if mode == "dates":
            return self._run_dates(start, end, step_days, cap)
        if mode == "letters":
            return self._run_letters(start, end, cap)
        return self._run_weekday(start, weekday, count, cap)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"range_generator_tool: {message}")

    @classmethod
    def _validate_max_count(cls, max_count: Any, default: int = 500) -> int:
        """Validate the per-call output cap (``None`` keeps the default)."""
        if max_count is None:
            return default
        if isinstance(max_count, bool) or not isinstance(max_count, int):
            cls._invalid(
                f"max_count must be an integer between 1 and "
                f"{cls.MAX_COUNT_LIMIT:,} (got {max_count!r})"
            )
        if not 1 <= max_count <= cls.MAX_COUNT_LIMIT:
            cls._invalid(
                f"max_count must be between 1 and "
                f"{cls.MAX_COUNT_LIMIT:,} (got {max_count:,})"
            )
        return max_count

    @classmethod
    def _validate_number(cls, value: Any, label: str) -> int | float:
        """Validate one numeric input (``start`` / ``end`` / ``step``)."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            cls._invalid(f"{label} must be an int or float (got {value!r})")
        if isinstance(value, float) and not math.isfinite(value):
            cls._invalid(f"{label} must be a finite number (got {value!r})")
        return value

    @classmethod
    def _validate_step(cls, step: Any, default: int = 1) -> int | float:
        """Validate a step value (non-zero number; ``None`` → default)."""
        if step is None:
            return default
        clean = cls._validate_number(step, "step")
        if clean == 0:
            cls._invalid("step must be non-zero (got 0)")
        return clean

    @classmethod
    def _validate_direction(
        cls, start: int | float, end: int | float, step: int | float
    ) -> None:
        """Reject a ``start`` beyond ``end`` for the given step sign.

        Ascending ranges need a positive step, descending ranges a
        negative one; the tool never silently swaps its bounds.
        """
        if step > 0 and start > end:
            cls._invalid(
                f"start must be <= end for a positive step "
                f"(got start={start!r} > end={end!r}); for a descending "
                "range pass a negative step"
            )
        if step < 0 and start < end:
            cls._invalid(
                f"start must be >= end for a negative step "
                f"(got start={start!r} < end={end!r})"
            )

    @classmethod
    def _validate_format(cls, format: Any) -> tuple[str, int]:
        """Validate the ``numbers`` ``format`` option.

        Returns the format label and, for ``padded-N``, the width.
        """
        if format is None:
            return "number", 0
        if isinstance(format, bool) or not isinstance(format, str):
            cls._invalid(f"format must be a string (got {format!r})")
        if format in cls.NATIVE_FORMATS:
            return format, 0
        padded = _PADDED.match(format)
        if padded and 1 <= int(padded.group(1)) <= cls.MAX_PAD_WIDTH:
            return "padded", int(padded.group(1))
        cls._invalid(
            "format must be one of: "
            f"{', '.join(cls.NATIVE_FORMATS)} or padded-N with N between "
            f"1 and {cls.MAX_PAD_WIDTH} (got {format!r})"
        )

    @classmethod
    def _validate_iso_date(cls, value: Any, label: str) -> date:
        """Validate an ISO ``YYYY-MM-DD`` calendar date string."""
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
        ):
            cls._invalid(
                f"{label} must be an ISO YYYY-MM-DD date string "
                f"(got {value!r})"
            )
        if not _ISO_DATE.match(value):
            cls._invalid(
                f"{label} must be an ISO YYYY-MM-DD date string "
                f"(got {value[:64]!r})"
            )
        try:
            return date.fromisoformat(value)
        except ValueError:
            # Calendar-invalid dates, e.g. 2023-02-29, 2024-04-31.
            cls._invalid(
                f"{label} is not a valid calendar date (got {value!r})"
            )

    @classmethod
    def _validate_positive_int(cls, value: Any, label: str, default: int) -> int:
        """Validate a required positive integer (``count``)."""
        if value is None:
            return default
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(f"{label} must be a positive integer (got {value!r})")
        if value < 1:
            cls._invalid(f"{label} must be a positive integer (got {value:,})")
        return value

    # ------------------------------------------------------------------ #
    # Shared payload helper (total is computed arithmetically, never by
    # enumeration, so huge ranges cannot exhaust memory)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _payload(
        context: dict[str, Any], values: list[Any], total: int, cap: int
    ) -> dict[str, Any]:
        """Assemble the result payload with the truncation report."""
        truncated = total > cap
        return {
            **context,
            "count": min(total, cap),
            "total": total,
            "truncated": truncated,
            "result": values[:cap],
        }

    # ------------------------------------------------------------------ #
    # numbers mode
    # ------------------------------------------------------------------ #

    def _run_numbers(
        self,
        start: Any,
        end: Any,
        step: Any,
        format: Any,
        cap: int,
    ) -> dict[str, Any]:
        """Generate an arithmetic number range with exact stepping."""
        clean_start = self._validate_number(start, "start")
        clean_end = self._validate_number(end, "end")
        clean_step = self._validate_step(step)
        self._validate_direction(clean_start, clean_end, clean_step)
        fmt, pad_width = self._validate_format(format)

        use_decimal = any(
            isinstance(v, float) for v in (clean_start, clean_end, clean_step)
        )
        int_only = fmt in self.INT_ONLY_FORMATS or fmt == "padded"
        if int_only and use_decimal:
            self._invalid(
                f"format {fmt!r} requires integer start/end/step "
                "(got float values)"
            )

        if use_decimal:
            d_start = Decimal(str(clean_start))
            d_end = Decimal(str(clean_end))
            d_step = Decimal(str(clean_step))
            with localcontext() as ctx:
                ctx.prec = 60
                quotient = (d_end - d_start) / d_step
                steps = int(
                    quotient.to_integral_value(rounding=ROUND_FLOOR)
                )
                total = steps + 1
                values = [
                    d_start + d_step * i for i in range(min(total, cap))
                ]
        else:
            steps = (clean_end - clean_start) // clean_step
            total = int(steps) + 1
            values = [clean_start + clean_step * i for i in range(min(total, cap))]

        context: dict[str, Any] = {
            "mode": "numbers",
            "start": clean_start,
            "end": clean_end,
            "step": clean_step,
            "format": fmt,
        }
        rendered = self._render_numbers(values, fmt, pad_width, use_decimal)
        return self._payload(context, rendered, total, cap)

    @classmethod
    def _render_numbers(
        cls,
        values: list[Any],
        fmt: str,
        pad_width: int,
        use_decimal: bool,
    ) -> list[Any]:
        """Render raw values (int or Decimal) per the format option."""
        if fmt == "number":
            if use_decimal:
                return [float(v) for v in values]
            return values
        if fmt == "int":
            return [int(v) for v in values]
        if fmt == "float2":
            quantum = Decimal("0.01")
            with localcontext() as ctx:
                ctx.prec = 80
                dec_values = (
                    values if use_decimal else [Decimal(int(v)) for v in values]
                )
                return [
                    float(v.quantize(quantum, rounding=ROUND_HALF_UP))
                    for v in dec_values
                ]
        if fmt == "hex":
            return [format(int(v), "x") for v in values]
        if fmt == "bin":
            return [format(int(v), "b") for v in values]
        # padded-N
        return [str(int(v)).zfill(pad_width) for v in values]

    # ------------------------------------------------------------------ #
    # dates mode
    # ------------------------------------------------------------------ #

    def _run_dates(
        self, start: Any, end: Any, step_days: Any, cap: int
    ) -> dict[str, Any]:
        """Generate an ISO date range stepping by whole days."""
        start_date = self._validate_iso_date(start, "start")
        end_date = self._validate_iso_date(end, "end")
        clean_step = self._validate_step(step_days, default=1)
        if isinstance(clean_step, float):
            self._invalid(f"step_days must be an integer (got {clean_step!r})")
        self._validate_direction_date(start_date, end_date, clean_step)

        delta_days = (end_date - start_date).days
        steps = delta_days // clean_step
        total = steps + 1
        values = [
            (start_date + timedelta(days=clean_step * i)).isoformat()
            for i in range(min(total, cap))
        ]
        context: dict[str, Any] = {
            "mode": "dates",
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "step_days": clean_step,
        }
        return self._payload(context, values, total, cap)

    @classmethod
    def _validate_direction_date(
        cls, start: date, end: date, step_days: int
    ) -> None:
        """Reject a ``start`` date beyond ``end`` for the step direction."""
        if step_days > 0 and start > end:
            cls._invalid(
                f"start must be on or before end for a positive step_days "
                f"(got start={start.isoformat()} > end={end.isoformat()}); "
                "for a descending range pass a negative step_days"
            )
        if step_days < 0 and start < end:
            cls._invalid(
                f"start must be on or after end for a negative step_days "
                f"(got start={start.isoformat()} < end={end.isoformat()})"
            )

    # ------------------------------------------------------------------ #
    # letters mode
    # ------------------------------------------------------------------ #

    def _run_letters(self, start: Any, end: Any, cap: int) -> dict[str, Any]:
        """Generate a single-case ASCII letter range via ord arithmetic."""
        clean_start = self._validate_letter(start, "start")
        clean_end = self._validate_letter(end, "end")
        if clean_start.islower() != clean_end.islower():
            self._invalid(
                "start and end must be letters of the same case "
                f"(got start={clean_start!r}, end={clean_end!r})"
            )

        start_ord, end_ord = ord(clean_start), ord(clean_end)
        # Direction is inferred: 'a'..'z' ascends, 'z'..'a' descends.
        step = 1 if start_ord <= end_ord else -1
        total = abs(end_ord - start_ord) + 1
        values = [
            chr(start_ord + step * i) for i in range(min(total, cap))
        ]
        context: dict[str, Any] = {
            "mode": "letters",
            "start": clean_start,
            "end": clean_end,
        }
        return self._payload(context, values, total, cap)

    @classmethod
    def _validate_letter(cls, value: Any, label: str) -> str:
        """Validate a single ASCII letter bound."""
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
            or len(value) != 1
            or not ("a" <= value <= "z" or "A" <= value <= "Z")
        ):
            cls._invalid(
                f"{label} must be a single ASCII letter a-z or A-Z "
                f"(got {value!r})"
            )
        return value

    # ------------------------------------------------------------------ #
    # weekday mode
    # ------------------------------------------------------------------ #

    def _run_weekday(
        self, start: Any, weekday: Any, count: Any, cap: int
    ) -> dict[str, Any]:
        """List the next occurrences of a named weekday.

        Same-day rule: a start date that already falls on the target
        weekday is the first item of the result.
        """
        start_date = self._validate_iso_date(start, "start")
        if (
            weekday is None
            or isinstance(weekday, bool)
            or not isinstance(weekday, str)
        ):
            self._invalid(
                "weekday must be one of: "
                f"{', '.join(sorted(set(self.WEEKDAYS)))} "
                f"(case-insensitive) (got {weekday!r})"
            )
        label = weekday.strip().lower()
        if label not in self.WEEKDAYS:
            self._invalid(
                "weekday must be one of: "
                f"{', '.join(sorted(set(self.WEEKDAYS)))} "
                f"(case-insensitive) (got {weekday[:64]!r})"
            )
        clean_count = self._validate_positive_int(count, "count", default=1)

        target = self.WEEKDAYS[label]
        offset = (target - start_date.weekday()) % 7
        first = start_date + timedelta(days=offset)
        values = [
            (first + timedelta(days=7 * i)).isoformat()
            for i in range(min(clean_count, cap))
        ]
        context: dict[str, Any] = {
            "mode": "weekday",
            "start": start_date.isoformat(),
            "weekday": label,
        }
        return self._payload(context, values, clean_count, cap)
