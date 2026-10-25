#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: iso_week_tool.py

"""ISO-8601 week-date arithmetic tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency calendar helper for
the reporting-cadence world: agents that must align on weeks like
``"2026-W42"`` — sprint planning, weekly digests, payroll cut-offs —
instead of plain calendar ranges (``DateRangeTool``) or workday
arithmetic (``BusinessDayTool``).

The tool is a thin, strictly-validated façade over
``datetime.date.isocalendar`` / ``datetime.date.fromisocalendar`` and
supports six modes:

* ``info`` — an ISO calendar date (``"2026-10-20"``) to its ISO week
  coordinates: ``iso_year``, ``iso_week``, ``weekday`` (1=Monday ..
  7=Sunday) with ``weekday_name`` and the full ISO week date string
  (``"2026-W43-2"``).
* ``week_bounds`` — a week spec (``"2026-W42"``) or a date to the
  Monday..Sunday ISO dates of that week.
* ``from_week`` — an ``iso_year`` + ``week`` (1-53) pair to its bounds
  plus a ``valid`` flag; week 53 exists only in long ISO years, which
  is decided by checking the resulting Monday's own ISO year rather
  than by a hardcoded year table.
* ``add_weeks`` — a date or week spec plus a (possibly negative) week
  count to the shifted week's bounds, correct across ISO year
  boundaries (e.g. ``2020-W53`` + 1 week = ``2021-W01``).
* ``weeks_between`` — two dates / week specs to the inclusive week
  count between them (same week = 1).
* ``range_weeks`` — a start and end week spec to the list of ISO week
  ids between them inclusive (``["2026-W42", "2026-W43", ...]``),
  capped at 500 entries.

Key ISO-8601 properties the tool pins down: weeks run Monday..Sunday;
week 1 of an ISO year is the week containing the first Thursday of
its January, so days Dec 29 - Jan 4 always belong to exactly one ISO
year (``2021-01-01`` is ``2020-W53-5``, ``2016-01-03`` is
``2015-W53-7``); and an ISO year has 53 weeks only when it starts on
a Thursday, or starts on a Wednesday of a leap year — the tool
derives this from the calendar itself, never from a lookup table.

Input validation is strict and happens before any computation:
malformed parameters — unknown mode, non-string or non-canonical
dates, week specs that do not match ``YYYY-Www`` with a zero-padded
two-digit week, ISO years outside 1..9999, weeks outside 1..53, week
53 of a short ISO year used as an *input anchor*, non-integer week
counts, reversed or oversized ranges, arithmetic that would leave the
``datetime.date`` range — raise a ``ValueError``. The ``from_week``
mode is the deliberate exception: since its purpose is to answer
"does this week exist", it reports a nonexistent week 53 as
``{"valid": false, "reason": ...}`` instead of raising.
"""

import datetime
import re
from typing import Any, ClassVar, Dict

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Canonical ISO calendar date: exactly YYYY-MM-DD, zero-padded.
_DATE_RE = re.compile(r"\A(\d{4})-(\d{2})-(\d{2})\Z", re.ASCII)
# Canonical ISO week spec: exactly YYYY-Www, zero-padded two-digit week.
_WEEK_RE = re.compile(r"\A(\d{4})-W(\d{2})\Z", re.ASCII)

WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class IsoWeekTool(Tool):
    """ISO-8601 week-date arithmetic tool built purely on the stdlib.

    Attributes:
        max_add_weeks (int): Upper bound on the absolute value of the
            ``weeks`` shift of the ``add_weeks`` mode.
        max_range_weeks (int): Upper bound on the number of week ids
            the ``range_weeks`` mode may return.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "iso_week_tool"
    description: str = (
        "ISO week arithmetic tool — pure Python stdlib datetime, no "
        "network required. Resolve a date to its ISO week coordinates "
        "(mode='info': iso_year, iso_week, weekday 1=Mon..7=Sun with "
        "name, full ISO week date '2026-W42-1'), get a week's "
        "Monday..Sunday bounds from a week spec or a date "
        "(mode='week_bounds'), build bounds from iso_year + week 1-53 "
        "with long-year week 53 validity (mode='from_week'), shift a "
        "date or week by N weeks across year boundaries "
        "(mode='add_weeks'), count weeks inclusively between two "
        "dates/weeks (mode='weeks_between'), and list week ids "
        "between two weeks capped at 500 (mode='range_weeks')."
    )

    MODES: ClassVar[tuple] = (
        "info",
        "week_bounds",
        "from_week",
        "add_weeks",
        "weeks_between",
        "range_weeks",
    )

    max_add_weeks: int = 520_000
    max_range_weeks: int = 500

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        date: Any = None,
        iso_year: Any = None,
        week: Any = None,
        weeks: Any = None,
        start: Any = None,
        end: Any = None,
    ) -> Dict[str, Any]:
        """Run one ISO week arithmetic operation.

        Args:
            mode (str): One of ``info`` / ``week_bounds`` /
                ``from_week`` / ``add_weeks`` / ``weeks_between`` /
                ``range_weeks``.
            date (str): Canonical ISO calendar date (``YYYY-MM-DD``)
                or ISO week spec (``YYYY-Www``); required by ``info``
                (date only), ``week_bounds`` and ``add_weeks``.
            iso_year (int | str): ISO year 1..9999; required by
                ``from_week`` (together with ``week``).
            week (int | str): ISO week 1..53; required by
                ``from_week`` (together with ``iso_year``).
            weeks (int | str): Signed week count for ``add_weeks``
                (``-520000..520000``).
            start (str): Inclusive start date or week spec; required
                by ``weeks_between`` and ``range_weeks``.
            end (str): Inclusive end date or week spec; required by
                ``weeks_between`` and ``range_weeks``.

        Returns:
            Dict[str, Any]: The operation result: ISO week
                coordinates / bounds / counts plus the call context.
                ``from_week`` reports a nonexistent week 53 as
                ``{"valid": false, "reason": ...}``.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens), if a week-spec anchor names a
                week that does not exist (e.g. ``2025-W53``), if
                ``start`` is after ``end``, or if the requested range
                or shift exceeds its cap or leaves the datetime range.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "info":
            clean_date = self._parse_date(date, label="date")
            return self._run_info(clean_date)
        if mode == "week_bounds":
            anchor = self._parse_week_anchor(date, label="date")
            return self._bounds_payload("week_bounds", anchor, input_value=date)
        if mode == "from_week":
            clean_year = self._validate_int(
                iso_year, label="iso_year", minimum=1, maximum=9999
            )
            clean_week = self._validate_int(
                week, label="week", minimum=1, maximum=53
            )
            return self._run_from_week(clean_year, clean_week)
        if mode == "add_weeks":
            anchor = self._parse_week_anchor(date, label="date")
            shift = self._validate_int(
                weeks,
                label="weeks",
                minimum=-self.max_add_weeks,
                maximum=self.max_add_weeks,
            )
            return self._run_add_weeks(anchor, shift, input_value=date)
        # weeks_between / range_weeks
        start_anchor = self._parse_week_anchor(start, label="start")
        end_anchor = self._parse_week_anchor(end, label="end")
        if mode == "weeks_between":
            return self._run_weeks_between(start_anchor, end_anchor, start, end)
        return self._run_range_weeks(start_anchor, end_anchor, start, end)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"iso_week_tool: {message}")

    @classmethod
    def _validate_int(
        cls, value: Any, label: str, minimum: int, maximum: int
    ) -> int:
        """Validate an integer parameter given as int or digit string."""
        if isinstance(value, bool):
            cls._invalid(f"{label} must be an integer (got {value!r})")
        if isinstance(value, int):
            number = value
        elif isinstance(value, str) and re.fullmatch(
            r"-?\d+", value.strip(), re.ASCII
        ):
            number = int(value.strip())
        else:
            cls._invalid(f"{label} must be an integer (got {value!r})")
        if not minimum <= number <= maximum:
            cls._invalid(
                f"{label} must be between {minimum} and {maximum} "
                f"(got {number})"
            )
        return number

    @classmethod
    def _parse_date(cls, value: Any, label: str) -> datetime.date:
        """Parse a canonical ``YYYY-MM-DD`` ISO calendar date.

        Only the exact zero-padded form is accepted: ``fromisoformat``
        on modern Python also takes ``YYYYMMDD`` and ISO week dates,
        which would blur the tool's input contract, so the regex gate
        runs first.
        """
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
            or not _DATE_RE.match(value)
        ):
            cls._invalid(
                f"{label} must be an ISO calendar date in YYYY-MM-DD "
                f"form (got {value!r})"
            )
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            cls._invalid(f"{label} is not a valid calendar date (got {value!r})")

    @classmethod
    def _week_monday(cls, iso_year: int, week: int) -> datetime.date:
        """Return the Monday of ISO week ``week`` of ``iso_year``.

        Week 1 of an ISO year is the week of the first Thursday in
        January, and Jan 4 is always in week 1, so its Monday anchors
        the whole year. Weeks beyond the year's last simply run past
        it — callers decide via :meth:`_week_exists` whether that is
        an error or a ``valid: false`` answer.
        """
        jan4 = datetime.date(iso_year, 1, 4)
        week1_monday = jan4 - datetime.timedelta(days=jan4.weekday())
        return week1_monday + datetime.timedelta(weeks=week - 1)

    @classmethod
    def _week_exists(cls, iso_year: int, week: int) -> bool:
        """Whether ISO ``iso_year`` really has week number ``week``.

        Every ISO year has weeks 1..52; a 53rd week exists only in
        long years. The check is derived from the calendar itself:
        the Monday computed for the week must still belong to the
        requested ISO year (for a short year, "week 53"'s Monday
        already falls into week 1 of the next ISO year).
        """
        try:
            monday = cls._week_monday(iso_year, week)
        except OverflowError:
            return False
        return monday.isocalendar()[0] == iso_year

    @classmethod
    def _parse_week_spec(cls, value: Any, label: str) -> datetime.date:
        """Parse a canonical ``YYYY-Www`` week spec to its Monday.

        The week must exist: week 53 of a short ISO year (for example
        ``2025-W53``) is rejected with a ``ValueError``.
        """
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
        ):
            cls._invalid(
                f"{label} must be an ISO week spec in YYYY-Www form "
                f"or an ISO date in YYYY-MM-DD form (got {value!r})"
            )
        match = _WEEK_RE.match(value)
        if match:
            iso_year, week = int(match.group(1)), int(match.group(2))
            if not 1 <= iso_year <= 9999:
                cls._invalid(
                    f"{label} ISO year must be 0001..9999 (got {value!r})"
                )
            if not 1 <= week <= 53:
                cls._invalid(
                    f"{label} week must be 01..53 (got {value!r})"
                )
            if not cls._week_exists(iso_year, week):
                cls._invalid(
                    f"{label} names ISO week {week} of {iso_year}, but "
                    f"that ISO year has "
                    f"{53 if cls._week_exists(iso_year, 53) else 52} "
                    f"weeks (got {value!r})"
                )
            return cls._week_monday(iso_year, week)
        # Not a week spec — fall through to the strict date parser so
        # both spellings share one error contract, then snap the date
        # to the Monday of its week: every week-level mode anchors on
        # Mondays so counts and bounds stay exact.
        clean_date = cls._parse_date(value, label)
        return clean_date - datetime.timedelta(days=clean_date.weekday())

    @classmethod
    def _parse_week_anchor(cls, value: Any, label: str) -> datetime.date:
        """Parse a date *or* week spec to the Monday of its week."""
        return cls._parse_week_spec(value, label)

    # ------------------------------------------------------------------ #
    # Shared output helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _week_id(cls, monday: datetime.date) -> str:
        """Format a week's Monday as the ISO week id ``YYYY-Www``."""
        iso_year, iso_week, _ = monday.isocalendar()
        return f"{iso_year:04d}-W{iso_week:02d}"

    @classmethod
    def _bounds_payload(
        cls,
        mode: str,
        monday: datetime.date,
        input_value: Any = None,
    ) -> Dict[str, Any]:
        """Build the monday..sunday bounds result for a week."""
        try:
            sunday = (monday + datetime.timedelta(days=6)).isoformat()
        except OverflowError:
            # Only reachable at the very end of the datetime range:
            # e.g. 9999-W52 exists, but its Sunday is in year 10000.
            iso_year, iso_week, _ = monday.isocalendar()
            cls._invalid(
                f"ISO week {iso_week} of {iso_year:04d} ends beyond the "
                "supported date range (year 1..9999)"
            )
        iso_year, iso_week, _ = monday.isocalendar()
        payload: Dict[str, Any] = {
            "mode": mode,
            "iso_year": iso_year,
            "iso_week": iso_week,
            "monday": monday.isoformat(),
            "sunday": sunday,
        }
        if input_value is not None:
            payload["input"] = input_value
        return payload

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    def _run_info(self, value: datetime.date) -> Dict[str, Any]:
        """Resolve an ISO date to its full week coordinates."""
        iso_year, iso_week, weekday = value.isocalendar()
        return {
            "mode": "info",
            "input": value.isoformat(),
            "iso_year": iso_year,
            "iso_week": iso_week,
            "weekday": weekday,
            "weekday_name": WEEKDAY_NAMES[weekday - 1],
            "iso_week_date": (
                f"{iso_year:04d}-W{iso_week:02d}-{weekday}"
            ),
        }

    def _run_from_week(self, iso_year: int, week: int) -> Dict[str, Any]:
        """Build week bounds from iso_year + week, reporting validity.

        Weeks 1..52 exist in every ISO year. Week 53 exists only in
        long ISO years, which is decided by checking whether the
        computed Monday still belongs to ``iso_year`` — never by a
        hardcoded year list.
        """
        if not self._week_exists(iso_year, week):
            last_week = 53 if self._week_exists(iso_year, 53) else 52
            return {
                "mode": "from_week",
                "iso_year": iso_year,
                "week": week,
                "valid": False,
                "reason": (
                    f"ISO year {iso_year:04d} has {last_week} weeks; "
                    f"week {week} does not exist"
                ),
            }
        monday = self._week_monday(iso_year, week)
        payload = self._bounds_payload("from_week", monday)
        payload["week"] = week
        payload["valid"] = True
        return payload

    def _run_add_weeks(
        self, anchor: datetime.date, shift: int, input_value: Any
    ) -> Dict[str, Any]:
        """Shift a week anchor by ``shift`` weeks (either sign)."""
        try:
            shifted = anchor + datetime.timedelta(weeks=shift)
        except OverflowError:
            self._invalid(
                f"shifting by {shift} weeks leaves the supported "
                "date range (year 1..9999)"
            )
        payload = self._bounds_payload("add_weeks", shifted, input_value)
        payload["weeks"] = shift
        return payload

    def _ordered_anchors(
        self,
        start_anchor: datetime.date,
        end_anchor: datetime.date,
        start: Any,
        end: Any,
    ) -> None:
        """Reject reversed ranges before counting or listing."""
        if start_anchor > end_anchor:
            self._invalid(
                f"start must not be after end (got start={start!r}, "
                f"end={end!r})"
            )

    def _run_weeks_between(
        self,
        start_anchor: datetime.date,
        end_anchor: datetime.date,
        start: Any,
        end: Any,
    ) -> Dict[str, Any]:
        """Count weeks between two anchors, inclusive of both."""
        self._ordered_anchors(start_anchor, end_anchor, start, end)
        return {
            "mode": "weeks_between",
            "start": start,
            "end": end,
            "weeks": (end_anchor - start_anchor).days // 7 + 1,
        }

    def _run_range_weeks(
        self,
        start_anchor: datetime.date,
        end_anchor: datetime.date,
        start: Any,
        end: Any,
    ) -> Dict[str, Any]:
        """List the ISO week ids from start to end, inclusive."""
        self._ordered_anchors(start_anchor, end_anchor, start, end)
        count = (end_anchor - start_anchor).days // 7 + 1
        if count > self.max_range_weeks:
            self._invalid(
                f"range spans {count} weeks, over the "
                f"{self.max_range_weeks}-week cap"
            )
        return {
            "mode": "range_weeks",
            "start": start,
            "end": end,
            "count": count,
            "weeks": [
                self._week_id(start_anchor + datetime.timedelta(weeks=i))
                for i in range(count)
            ],
        }
