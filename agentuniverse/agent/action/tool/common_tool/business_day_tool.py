#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: business_day_tool.py

"""Business-day (workday) arithmetic tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency calendar utility
agents can call when scheduling work, settling deadlines, or counting
trading days.

The tool is intentionally distinct from ``DateRangeTool`` (#3690,
interval set operations on inclusive ``[start, end]`` calendar ranges)
and from ``DateTimeTool`` (#3420, single-datetime parsing, formatting
and second/minute/day arithmetic): it performs *business-day*
arithmetic — day walking and counting that skips configured weekend
days and a configured holiday calendar.

A business day is a calendar date that is neither a configured weekend
day nor a configured holiday. The weekend is configurable:

* ``sat_sun`` (default) — Saturday and Sunday, the ISO convention;
* ``fri_sat`` — Friday and Saturday, common in MENP (Middle East,
  North Africa, Pakistan) markets;
* ``sun_only`` — Sunday only, a rare one-day-weekend calendar
  (kept for completeness; verify the market before relying on it).

Holidays are supplied by the caller as either a list of ISO date
strings (``["2026-10-19", ...]``) or a ``{date: name}`` mapping
(``{"2026-10-19": "Deepavali", ...}``) whose names are echoed by the
``is_business`` verdict; both forms are accepted by every mode. No
locale holiday tables are bundled — the caller owns the calendar.

Supported modes (all deterministic, ``datetime.date`` arithmetic only):

* ``add`` — ``date`` plus ``days`` business days (``days`` may be
  negative to walk backwards). The walk steps one calendar day at a
  time in the requested direction and stops on the ``days``-th
  business day encountered, so a Friday + 1 lands on Monday and a
  Monday - 1 lands on the previous Friday, skipping weekends and
  holidays in between. ``days=0`` returns the input date unchanged,
  even when it falls on a weekend or holiday (a zero offset never
  rolls — numpy / pandas business-day offset semantics).
* ``count`` — number of business days between ``start_date`` and
  ``end_date``. Both ends inclusive by default; ``include_ends=False``
  counts the strictly-between span (both endpoints excluded), so a
  Monday..Friday week counts 5 inclusive / 3 exclusive.
* ``is_business`` — verdict for one ``date``: ``business``,
  ``weekend`` or ``holiday``. Weekends take precedence: a holiday
  falling on a weekend day is reported as a weekend. When holidays
  were given as a ``{date: name}`` mapping the holiday name is
  echoed as ``holiday_name`` (``None`` otherwise).
* ``next`` — the next business day strictly after ``date``. With
  ``same_day=True`` a ``date`` that is already a business day is
  returned unchanged; non-business dates always roll forward.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, dates that are not strict
``YYYY-MM-DD`` calendar dates such as ``2026-02-30`` or ``2026-2-3``,
``days`` outside ±3650 or of the wrong type, an unknown ``weekend``
preset, holidays that are neither a list of ISO dates nor a
``{date: name}`` dict, more than 1000 holidays, non-boolean
``include_ends`` / ``same_day`` flags, ``start_date`` after
``end_date``, and results that would leave the representable
``datetime.date`` range 0001-01-01..9999-12-31) raise a
``ValueError`` with a precise message, mirroring the other common
tools.
"""

import re
from datetime import date, timedelta
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Strict YYYY-MM-DD only — datetime.date.fromisoformat alone would also
# accept compact ("20261020") and ISO week ("2026-W43-1") forms.
_STRICT_ISO = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
_INTEGER_STRING = re.compile(r"\A-?\d+\Z")

_WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class BusinessDayTool(Tool):
    """Business-day (workday) arithmetic tool built purely on the stdlib.

    Attributes:
        max_days (int): Bound on the ``add`` mode offset, in business
            days, in either direction (default ±3650 ≈ ten years).
        max_holidays (int): Upper bound on the number of holiday
            entries accepted per call.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "business_day_tool"
    description: str = (
        "Business day tool — pure Python stdlib workday arithmetic, no "
        "network required. Add or subtract N business days from a date "
        "(mode='add', N=0 returns the input unchanged), count business "
        "days between two dates with inclusive or exclusive ends "
        "(mode='count'), test whether a date is a business day with a "
        "weekend/holiday reason and echoed holiday name (mode="
        "'is_business'), and find the next business day strictly after "
        "a date or the same day when it is already a business day "
        "(mode='next'). Weekends are configurable (sat_sun default, "
        "fri_sat for MENP markets, sun_only rare) and holidays are "
        "supplied as a list of ISO dates or a {date: name} mapping."
    )

    MODES: ClassVar[tuple] = ("add", "count", "is_business", "next")
    WEEKENDS: ClassVar[dict[str, frozenset]] = {
        "sat_sun": frozenset({5, 6}),
        "fri_sat": frozenset({4, 5}),
        "sun_only": frozenset({6}),
    }
    # ClassVar (not pydantic fields): plain constants on the class.
    max_days: ClassVar[int] = 3650
    max_holidays: ClassVar[int] = 1000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        date_str: Any = None,
        days: Any = None,
        start_date: Any = None,
        end_date: Any = None,
        holidays: Any = None,
        weekend: Any = None,
        include_ends: Any = None,
        same_day: Any = None,
    ) -> dict[str, Any]:
        """Run one business-day operation.

        Args:
            mode (str): One of ``add`` / ``count`` / ``is_business`` /
                ``next``.
            date_str (str): The reference date as a ``YYYY-MM-DD``
                string — required for the ``add``, ``is_business`` and
                ``next`` modes; not used by ``count``.
            days (int): Number of business days to add for the ``add``
                mode — negative walks backwards, ``0`` returns the
                input date unchanged; bounded to ±3650. Integer strings
                such as ``"5"`` or ``"-5"`` are accepted.
            start_date (str): Count mode start (``YYYY-MM-DD``).
            end_date (str): Count mode end (``YYYY-MM-DD``); must not
                be before ``start_date``.
            holidays (list | dict): Holiday calendar — a list of ISO
                date strings or a ``{date: name}`` dict whose names are
                echoed by ``is_business``; accepted by every mode.
            weekend (str): Weekend preset — ``sat_sun`` (default),
                ``fri_sat`` or ``sun_only`` (case-insensitive).
            include_ends (bool): Count mode — count both endpoints
                (default ``True``) or only the strictly-between span
                (``False`` excludes both endpoints).
            same_day (bool): Next mode — when ``True`` a date that is
                already a business day is returned unchanged; the
                default ``False`` always returns a day strictly after.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` key plus
                the call context — for ``is_business`` the verdict
                fields ``is_business`` / ``reason`` / ``weekday`` /
                ``holiday_name``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        weekend_name = self._validate_weekend(weekend)
        weekend_days = self.WEEKENDS[weekend_name]
        holiday_dates, holiday_names = self._validate_holidays(holidays)

        if mode == "count":
            clean_flag = self._validate_flag(include_ends, "include_ends")
            return self._run_count(
                start_date, end_date, weekend_name, weekend_days,
                holiday_dates, True if clean_flag is None else clean_flag,
            )

        clean_date = self._validate_date(date_str, "date")
        if mode == "add":
            clean_days = self._validate_days(days)
            return self._run_add(
                clean_date, clean_days, weekend_name, weekend_days,
                holiday_dates,
            )
        if mode == "is_business":
            return self._run_is_business(
                clean_date, weekend_name, weekend_days,
                holiday_dates, holiday_names,
            )
        clean_same_day = self._validate_flag(same_day, "same_day")
        return self._run_next(
            clean_date, weekend_name, weekend_days, holiday_dates,
            False if clean_same_day is None else clean_same_day,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"business_day_tool: {message}")

    @classmethod
    def _validate_date(cls, value: Any, label: str) -> date:
        """Validate one strict ``YYYY-MM-DD`` calendar date."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a YYYY-MM-DD date string (got {value!r})")
        if not _STRICT_ISO.match(value):
            cls._invalid(
                f"{label} must be a strict YYYY-MM-DD date string, "
                f"e.g. '2026-10-20' (got {value[:32]!r})"
            )
        try:
            return date.fromisoformat(value)
        except ValueError:
            cls._invalid(
                f"{label} is not a valid calendar date (got {value!r})"
            )
        raise AssertionError("unreachable")  # pragma: no cover

    @classmethod
    def _validate_days(cls, days: Any) -> int:
        """Validate the ``add`` mode business-day offset."""
        if isinstance(days, bool):
            cls._invalid(
                f"days must be an integer within ±{cls.max_days} (got {days!r})"
            )
        if isinstance(days, int):
            clean = days
        elif isinstance(days, str) and _INTEGER_STRING.match(days):
            clean = int(days)
        else:
            cls._invalid(
                f"days must be an integer (or integer string) within "
                f"±{cls.max_days} (got {days!r})"
            )
        if abs(clean) > cls.max_days:
            cls._invalid(f"days must be within ±{cls.max_days} (got {clean})")
        return clean

    @classmethod
    def _validate_weekend(cls, weekend: Any) -> str:
        """Validate the weekend preset label."""
        if weekend is None:
            return "sat_sun"
        if isinstance(weekend, bool) or not isinstance(weekend, str):
            cls._invalid(
                "weekend must be one of: "
                f"{', '.join(cls.WEEKENDS)} (got {weekend!r})"
            )
        label = weekend.strip().lower()
        if label not in cls.WEEKENDS:
            cls._invalid(
                "weekend must be one of: "
                f"{', '.join(cls.WEEKENDS)} (got {weekend!r})"
            )
        return label

    @classmethod
    def _validate_holidays(cls, holidays: Any) -> tuple[set, dict]:
        """Validate the holiday calendar; return (dates, names).

        ``dates`` is the set of ``datetime.date`` holidays (used by
        every mode); ``names`` maps ``datetime.date`` to the caller's
        label and is empty when holidays were given as a plain list.
        """
        if holidays is None:
            return set(), {}
        if isinstance(holidays, (bool, str)) or not isinstance(
            holidays, (list, tuple, dict)
        ):
            cls._invalid(
                "holidays must be a list of YYYY-MM-DD date strings or a "
                "{date: name} mapping (got "
                f"{type(holidays).__name__}: {str(holidays)[:64]!r})"
            )
        if len(holidays) > cls.max_holidays:
            cls._invalid(
                f"holidays exceed the {cls.max_holidays}-entry "
                f"limit (got {len(holidays)} entries)"
            )
        dates: set = set()
        names: dict = {}
        if isinstance(holidays, dict):
            for key, name in holidays.items():
                clean = cls._validate_date(key, "holidays key")
                if name is None or isinstance(name, bool) or not isinstance(name, str):
                    cls._invalid(
                        "holidays names must be non-empty strings "
                        f"(got {name!r} for {key!r})"
                    )
                if not name:
                    cls._invalid(
                        f"holidays names must be non-empty strings (got '' for {key!r})"
                    )
                dates.add(clean)
                names[clean] = name
            return dates, names
        for index, entry in enumerate(holidays):
            if entry is None or isinstance(entry, bool) or not isinstance(entry, str):
                cls._invalid(
                    f"holidays[{index}] must be a YYYY-MM-DD date string "
                    f"(got {entry!r})"
                )
            dates.add(cls._validate_date(entry, f"holidays[{index}]"))
        return dates, names

    @classmethod
    def _validate_flag(cls, flag: Any, label: str) -> "bool | None":
        """Validate an optional boolean flag (``None`` means default)."""
        if flag is None or isinstance(flag, bool):
            return flag
        cls._invalid(f"{label} must be a boolean (got {flag!r})")

    # ------------------------------------------------------------------ #
    # Shared calendar helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _shift(day: date, step: int) -> date:
        """Move one calendar day, converting range overflow to ValueError."""
        try:
            return day + timedelta(days=step)
        except OverflowError:
            BusinessDayTool._invalid(
                "the walk leaves the representable datetime.date range "
                "(0001-01-01..9999-12-31) — narrow the date or the offset"
            )
        raise AssertionError("unreachable")  # pragma: no cover

    @staticmethod
    def _is_business(
        day: date, weekend_days: frozenset, holiday_dates: set
    ) -> bool:
        """Business-day test: not a weekend day and not a holiday."""
        return day.weekday() not in weekend_days and day not in holiday_dates

    # ------------------------------------------------------------------ #
    # add mode
    # ------------------------------------------------------------------ #

    def _run_add(
        self,
        start: date,
        days: int,
        weekend_name: str,
        weekend_days: frozenset,
        holiday_dates: set,
    ) -> dict[str, Any]:
        """Walk ``days`` business days forward (or backward) from ``start``."""
        step = 1 if days >= 0 else -1
        remaining = abs(days)
        current = start
        holidays_skipped = 0
        for _ in range(remaining):
            current = self._shift(current, step)
            while not self._is_business(current, weekend_days, holiday_dates):
                if current in holiday_dates:
                    holidays_skipped += 1
                current = self._shift(current, step)
        return {
            "mode": "add",
            "date": start.isoformat(),
            "days": days,
            "weekend": weekend_name,
            "holidays_skipped": holidays_skipped,
            "result": current.isoformat(),
        }

    # ------------------------------------------------------------------ #
    # count mode
    # ------------------------------------------------------------------ #

    def _run_count(
        self,
        start_value: Any,
        end_value: Any,
        weekend_name: str,
        weekend_days: frozenset,
        holiday_dates: set,
        include_ends: bool,
    ) -> dict[str, Any]:
        """Count business days between two dates."""
        start = self._validate_date(start_value, "start_date")
        end = self._validate_date(end_value, "end_date")
        if start > end:
            self._invalid(
                f"start_date must not be after end_date "
                f"(got {start.isoformat()} > {end.isoformat()})"
            )

        if include_ends:
            first, last = start, end
        elif (end - start).days < 2:
            # Strictly-between span of 0 or 1 calendar days is empty.
            first = last = None
        else:
            first, last = start + timedelta(days=1), end - timedelta(days=1)

        if first is None:
            calendar_days = weekend_days_count = holidays_in_range = 0
        else:
            calendar_days = (last - first).days + 1
            weekend_days_count = self._count_weekday_in_range(
                first, last, weekend_days
            )
            holidays_in_range = sum(
                1
                for day in holiday_dates
                if first <= day <= last and day.weekday() not in weekend_days
            )

        return {
            "mode": "count",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "weekend": weekend_name,
            "include_ends": include_ends,
            "calendar_days": calendar_days,
            "weekend_days": weekend_days_count,
            "holidays_in_range": holidays_in_range,
            "result": calendar_days - weekend_days_count - holidays_in_range,
        }

    @staticmethod
    def _count_weekday_in_range(
        first: date, last: date, weekday_values: frozenset
    ) -> int:
        """Count the days in ``[first, last]`` whose weekday is in the set.

        Pure ordinal arithmetic — O(1) per weekday value, so counting a
        multi-year span never iterates its days.
        """
        total = 0
        span = (last - first).days
        for value in weekday_values:
            offset = (value - first.weekday()) % 7
            if offset <= span:
                total += 1 + (span - offset) // 7
        return total

    # ------------------------------------------------------------------ #
    # is_business mode
    # ------------------------------------------------------------------ #

    def _run_is_business(
        self,
        day: date,
        weekend_name: str,
        weekend_days: frozenset,
        holiday_dates: set,
        holiday_names: dict,
    ) -> dict[str, Any]:
        """Verdict for one date: business / weekend / holiday."""
        weekday = day.weekday()
        if weekday in weekend_days:
            is_business, reason, holiday_name = False, "weekend", None
        elif day in holiday_dates:
            is_business = False
            reason = "holiday"
            holiday_name = holiday_names.get(day)
        else:
            is_business, reason, holiday_name = True, "business", None
        return {
            "mode": "is_business",
            "date": day.isoformat(),
            "weekend": weekend_name,
            "weekday": _WEEKDAY_NAMES[weekday],
            "is_business": is_business,
            "reason": reason,
            "holiday_name": holiday_name,
            "result": is_business,
        }

    # ------------------------------------------------------------------ #
    # next mode
    # ------------------------------------------------------------------ #

    def _run_next(
        self,
        day: date,
        weekend_name: str,
        weekend_days: frozenset,
        holiday_dates: set,
        same_day: bool,
    ) -> dict[str, Any]:
        """The next business day strictly after ``day`` (or the same day)."""
        current = day
        if same_day and self._is_business(current, weekend_days, holiday_dates):
            return {
                "mode": "next",
                "date": day.isoformat(),
                "weekend": weekend_name,
                "same_day": True,
                "calendar_days_advanced": 0,
                "result": current.isoformat(),
            }
        current = self._shift(current, 1)
        while not self._is_business(current, weekend_days, holiday_dates):
            current = self._shift(current, 1)
        return {
            "mode": "next",
            "date": day.isoformat(),
            "weekend": weekend_name,
            "same_day": same_day,
            "calendar_days_advanced": (current - day).days,
            "result": current.isoformat(),
        }
