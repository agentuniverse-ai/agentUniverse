#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: date_range_tool.py

"""ISO date-range set operations tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency calendar-range
utility agents can call when scheduling work, merging availability
windows, or reconciling timelines.

The tool is intentionally distinct from the single-datetime arithmetic
of ``DateTimeTool`` (#3420) and from free-standing duration arithmetic
of ``DurationTool`` (#3513): it operates on *ranges of calendar days*
given as ``[start, end]`` ISO date pairs where both ends are INCLUSIVE
(a range ``["2026-01-01", "2026-01-03"]`` covers three days). All day
counts follow that convention.

Supported modes (all deterministic, ``datetime.date`` arithmetic only):

* ``intersect`` — intersection of two ranges: the overlap range and its
  inclusive day count, or ``None`` with the number of gap days
  strictly between the two ranges when they do not meet.
* ``union`` — union of two ranges: one merged range when the ranges
  overlap or touch on adjacent days, otherwise both ranges (sorted)
  together with the gap day count.
* ``contains`` — per-date verdicts for a list of ISO dates against one
  range (boundary dates count as contained).
* ``overlaps`` — whether two ranges share at least one day, plus the
  inclusive day count of the shared part (``0`` when disjoint).
* ``gap`` — number of calendar days strictly between two ranges
  (``0`` when they overlap or touch on adjacent days; symmetric in the
  argument order).
* ``subtract`` — range A minus range B: the remaining sub-range(s) of
  A as a sorted list (empty when B covers A entirely, a single
  sub-range when B bites one side, two sub-ranges when B is strictly
  inside A), plus the inclusive day count removed from A.
* ``multi_merge`` — the calendar-coalescing primitive: merge an
  arbitrary list of ranges into the sorted, non-overlapping minimal
  list (chains of overlapping or adjacent ranges collapse into one).

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, a range that is not a list/tuple
of exactly two ``YYYY-MM-DD`` strings, non-calendar dates such as
``2026-02-30``, ``start`` after ``end``, missing or mis-typed
arguments for the chosen mode, empty or over-cap date/range lists)
raise a ``ValueError`` with a precise message naming the offending
parameter, mirroring the other common tools.
"""

import re
from datetime import date
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Strict ISO calendar date: exactly YYYY-MM-DD (datetime.date.fromisoformat
# alone would also accept compact 20260101 and week forms on Python 3.11+).
_ISO_DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")

# A validated range: inclusive [start, end] as date objects.
_Range = tuple[date, date]


class DateRangeTool(Tool):
    """ISO date-range set operations tool built purely on the stdlib.

    Class attributes (see the module docstring for the semantics):
        max_dates (int): Upper bound on the number of dates accepted by
            the ``contains`` mode.
        max_ranges (int): Upper bound on the number of ranges accepted
            by the ``multi_merge`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "date_range_tool"
    description: str = (
        "Date range tool — pure Python stdlib interval set operations on "
        "inclusive [start, end] ISO date pairs. Intersection with gap "
        "reporting (mode='intersect'), union merging overlapping or "
        "adjacent ranges (mode='union'), per-date containment verdicts "
        "(mode='contains'), overlap test with shared day count "
        "(mode='overlaps'), gap day count between ranges (mode='gap'), "
        "range subtraction into remaining sub-ranges (mode='subtract'), "
        "and many-range coalescing into a sorted non-overlapping list "
        "(mode='multi_merge')."
    )

    MODES: ClassVar[tuple] = (
        "intersect",
        "union",
        "contains",
        "overlaps",
        "gap",
        "subtract",
        "multi_merge",
    )

    max_dates: ClassVar[int] = 1000
    max_ranges: ClassVar[int] = 1000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        range_a: Any = None,
        range_b: Any = None,
        dates: Any = None,
        ranges: Any = None,
    ) -> dict[str, Any]:
        """Run one date-range set operation.

        Args:
            mode (str): One of ``intersect`` / ``union`` / ``contains`` /
                ``overlaps`` / ``gap`` / ``subtract`` / ``multi_merge``.
            range_a (list | tuple): First range as ``[start, end]`` ISO
                date strings, both ends inclusive. Required for every
                mode except ``multi_merge``; used as the base range of
                ``subtract`` and the container range of ``contains``.
            range_b (list | tuple): Second range in the same form.
                Required for ``intersect`` / ``union`` / ``overlaps`` /
                ``gap`` / ``subtract``; not used by ``contains`` or
                ``multi_merge``.
            dates (list): List of ``YYYY-MM-DD`` date strings checked
                against ``range_a``. Required for ``contains``.
            ranges (list): List of ``[start, end]`` ranges to coalesce.
                Required for ``multi_merge``.

        Returns:
            Dict[str, Any]: The operation result — always the ``mode``
                plus the normalized input ranges and a mode-specific
                payload (see the mode docstrings above).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "multi_merge":
            clean_ranges = self._validate_ranges(ranges, "ranges")
            return self._run_multi_merge(clean_ranges)
        clean_a = self._validate_range(range_a, "range_a")
        if mode == "contains":
            clean_dates = self._validate_dates(dates)
            return self._run_contains(clean_a, clean_dates)
        clean_b = self._validate_range(range_b, "range_b")
        if mode == "intersect":
            return self._run_intersect(clean_a, clean_b)
        if mode == "union":
            return self._run_union(clean_a, clean_b)
        if mode == "overlaps":
            return self._run_overlaps(clean_a, clean_b)
        if mode == "gap":
            return self._run_gap(clean_a, clean_b)
        return self._run_subtract(clean_a, clean_b)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"date_range_tool: {message}")

    @classmethod
    def _validate_iso_date(cls, value: Any, label: str) -> date:
        """Validate one ``YYYY-MM-DD`` calendar date string."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(
                f"{label} must be an ISO date string YYYY-MM-DD (got {value!r})"
            )
        if not _ISO_DATE.match(value):
            cls._invalid(
                f"{label} must be an ISO date string in YYYY-MM-DD form, "
                f"e.g. '2026-01-31' (got {value!r})"
            )
        try:
            return date.fromisoformat(value)
        except ValueError:
            cls._invalid(
                f"{label} is not a valid calendar date in YYYY-MM-DD form "
                f"(got {value!r})"
            )
        raise AssertionError("unreachable")  # pragma: no cover

    @classmethod
    def _validate_range(cls, value: Any, label: str) -> _Range:
        """Validate one ``[start, end]`` range with inclusive ends."""
        if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
            cls._invalid(
                f"{label} must be a [start, end] pair of ISO date strings, "
                f"e.g. ['2026-01-01', '2026-01-31'] (got {value!r})"
            )
        if len(value) != 2:
            cls._invalid(
                f"{label} must contain exactly 2 elements [start, end] "
                f"(got {len(value)} element{'s' if len(value) != 1 else ''})"
            )
        start = cls._validate_iso_date(value[0], f"{label}[0] (start)")
        end = cls._validate_iso_date(value[1], f"{label}[1] (end)")
        if start > end:
            cls._invalid(
                f"{label} start must not be after end "
                f"(got start {start.isoformat()} > end {end.isoformat()})"
            )
        return (start, end)

    @classmethod
    def _validate_dates(cls, value: Any) -> list[date]:
        """Validate the ``contains`` mode list of ISO dates."""
        if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
            cls._invalid(f"dates must be a list of ISO date strings (got {value!r})")
        if len(value) == 0:
            cls._invalid("dates must contain at least one ISO date string")
        if len(value) > cls.max_dates:
            cls._invalid(
                f"dates exceeds the {cls.max_dates:,}-item limit "
                f"(got {len(value):,} items)"
            )
        return [
            cls._validate_iso_date(item, f"dates[{index}]")
            for index, item in enumerate(value)
        ]

    @classmethod
    def _validate_ranges(cls, value: Any, label: str) -> list[_Range]:
        """Validate the ``multi_merge`` mode list of ranges."""
        if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
            cls._invalid(
                f"{label} must be a list of [start, end] ranges (got {value!r})"
            )
        if len(value) == 0:
            cls._invalid(f"{label} must contain at least one range")
        if len(value) > cls.max_ranges:
            cls._invalid(
                f"{label} exceeds the {cls.max_ranges:,}-range limit "
                f"(got {len(value):,} ranges)"
            )
        return [
            cls._validate_range(item, f"{label}[{index}]")
            for index, item in enumerate(value)
        ]

    # ------------------------------------------------------------------ #
    # Range arithmetic helpers (all counts are inclusive of both ends)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _days(start: date, end: date) -> int:
        """Inclusive day count of a ``start <= end`` span."""
        return (end - start).days + 1

    @staticmethod
    def _as_pair(range_: _Range) -> list[str]:
        """Render a validated range as ``[start, end]`` ISO strings."""
        return [range_[0].isoformat(), range_[1].isoformat()]

    @classmethod
    def _sorted(cls, first: _Range, second: _Range) -> tuple[_Range, _Range]:
        """Order two ranges by start (ties by end) — makes every two-range
        mode symmetric in its arguments."""
        if (second[0], second[1]) < (first[0], first[1]):
            return second, first
        return first, second

    # ------------------------------------------------------------------ #
    # Two-range modes
    # ------------------------------------------------------------------ #

    def _run_intersect(self, range_a: _Range, range_b: _Range) -> dict[str, Any]:
        """Intersection of two ranges, with the gap when they do not meet."""
        start = max(range_a[0], range_b[0])
        end = min(range_a[1], range_b[1])
        if start <= end:
            return {
                "mode": "intersect",
                "range_a": self._as_pair(range_a),
                "range_b": self._as_pair(range_b),
                "intersection": [start.isoformat(), end.isoformat()],
                "days": self._days(start, end),
                "gap_days": 0,
            }
        earlier, later = self._sorted(range_a, range_b)
        return {
            "mode": "intersect",
            "range_a": self._as_pair(range_a),
            "range_b": self._as_pair(range_b),
            "intersection": None,
            "days": 0,
            "gap_days": self._gap_between(earlier, later),
        }

    def _run_union(self, range_a: _Range, range_b: _Range) -> dict[str, Any]:
        """Union of two ranges: one range when they overlap or touch."""
        first, second = self._sorted(range_a, range_b)
        # Adjacent days (second.start == first.end + 1 day) leave no
        # calendar hole, so such ranges merge like overlapping ones.
        if second[0].toordinal() <= first[1].toordinal() + 1:
            return {
                "mode": "union",
                "range_a": self._as_pair(range_a),
                "range_b": self._as_pair(range_b),
                "union": [
                    [first[0].isoformat(), max(first[1], second[1]).isoformat()]
                ],
                "merged": True,
                "gap_days": 0,
            }
        return {
            "mode": "union",
            "range_a": self._as_pair(range_a),
            "range_b": self._as_pair(range_b),
            "union": [self._as_pair(first), self._as_pair(second)],
            "merged": False,
            "gap_days": self._gap_between(first, second),
        }

    def _run_overlaps(self, range_a: _Range, range_b: _Range) -> dict[str, Any]:
        """Whether the two ranges share at least one calendar day."""
        start = max(range_a[0], range_b[0])
        end = min(range_a[1], range_b[1])
        days = self._days(start, end) if start <= end else 0
        return {
            "mode": "overlaps",
            "range_a": self._as_pair(range_a),
            "range_b": self._as_pair(range_b),
            "overlaps": days > 0,
            "overlap_days": days,
        }

    def _run_gap(self, range_a: _Range, range_b: _Range) -> dict[str, Any]:
        """Calendar days strictly between the two ranges."""
        first, second = self._sorted(range_a, range_b)
        gap_days = self._gap_between(first, second)
        return {
            "mode": "gap",
            "range_a": self._as_pair(range_a),
            "range_b": self._as_pair(range_b),
            "gap_days": gap_days,
            "overlaps": second[0] <= first[1],
        }

    def _run_subtract(self, range_a: _Range, range_b: _Range) -> dict[str, Any]:
        """Range A minus range B as a sorted list of remaining sub-ranges."""
        difference: list[_Range] = []
        # Left remainder: the part of A before B starts (may be empty
        # when B covers A's start).
        if range_b[0] > range_a[0]:
            difference.append(
                (range_a[0], min(range_a[1], self._prev_day(range_b[0])))
            )
        # Right remainder: the part of A after B ends (may be empty
        # when B covers A's end).
        if range_b[1] < range_a[1]:
            difference.append(
                (max(range_a[0], self._next_day(range_b[1])), range_a[1])
            )
        removed_start = max(range_a[0], range_b[0])
        removed_end = min(range_a[1], range_b[1])
        removed_days = (
            self._days(removed_start, removed_end)
            if removed_start <= removed_end
            else 0
        )
        return {
            "mode": "subtract",
            "range_a": self._as_pair(range_a),
            "range_b": self._as_pair(range_b),
            "difference": [self._as_pair(item) for item in difference],
            "removed_days": removed_days,
        }

    # ------------------------------------------------------------------ #
    # contains / multi_merge modes
    # ------------------------------------------------------------------ #

    def _run_contains(self, range_: _Range, dates: list[date]) -> dict[str, Any]:
        """Per-date containment verdicts, preserving the input order."""
        verdicts = [
            {"date": item.isoformat(), "contained": range_[0] <= item <= range_[1]}
            for item in dates
        ]
        contained_count = sum(1 for item in verdicts if item["contained"])
        return {
            "mode": "contains",
            "range_a": self._as_pair(range_),
            "results": verdicts,
            "contained_count": contained_count,
            "total": len(verdicts),
        }

    def _run_multi_merge(self, ranges: list[_Range]) -> dict[str, Any]:
        """Coalesce many ranges into the sorted non-overlapping minimal list."""
        merged: list[list[date]] = []
        for start, end in sorted(ranges):
            # A range starting at most one day after the current block's
            # end overlaps or touches it, so the block extends.
            if merged and start.toordinal() <= merged[-1][1].toordinal() + 1:
                if end > merged[-1][1]:
                    merged[-1][1] = end
            else:
                merged.append([start, end])
        return {
            "mode": "multi_merge",
            "input_count": len(ranges),
            "merged": [
                [block[0].isoformat(), block[1].isoformat()] for block in merged
            ],
            "merged_count": len(merged),
        }

    # ------------------------------------------------------------------ #
    # Small date helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _prev_day(value: date) -> date:
        """The calendar day before ``value`` (only called for values after
        ``date.min`` — the callers require a strictly earlier date to exist)."""
        return date.fromordinal(value.toordinal() - 1)

    @staticmethod
    def _next_day(value: date) -> date:
        """The calendar day after ``value`` (only called for values before
        ``date.max``)."""
        return date.fromordinal(value.toordinal() + 1)

    @classmethod
    def _gap_between(cls, earlier: _Range, later: _Range) -> int:
        """Days strictly between two non-overlapping, pre-sorted ranges
        (``0`` when they touch on adjacent days)."""
        gap = later[0].toordinal() - earlier[1].toordinal() - 1
        return max(gap, 0)
