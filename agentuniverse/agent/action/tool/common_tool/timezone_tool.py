#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: timezone_tool.py

"""IANA timezone intelligence tool built on the stdlib ``zoneinfo``.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-third-party dependency helper
for the world's clock rules: agents that must answer "is this zone
name real", "what is the UTC offset in Berlin right now", "when does
daylight saving start in 2026", "how do New York and Tokyo clocks
differ" and "when can three teams on three continents actually meet".

Everything is computed from the local IANA time zone database through
``zoneinfo`` — which requires either a system tz database or the
``tzdata`` pip package (see *tz database availability* below). The
tool never reads the wall clock, so every mode is deterministic given
its inputs.

Five modes:

* ``validate`` — a zone name to ``{valid, in_available_timezones,
  sample_offsets, abbreviation_at_samples, has_dst}``. Validity is
  decided by constructing ``ZoneInfo(key)`` and mapping
  ``ZoneInfoNotFoundError`` to ``valid: false`` (a structured
  payload, not an exception); the name's *shape* is still regex
  validated first, so malformed names raise. ``sample_offsets`` are
  taken at four fixed seasonal reference instants (the calendar
  dates of the 2024 equinoxes and solstices at 12:00 UTC) plus Jan 1
  and Jul 1 2024 for the ``has_dst`` decision — a fixed sampling
  basis, documented as such. Validation never enumerates
  ``zoneinfo.available_timezones()`` to decide validity — the
  ``ZoneInfo(key)`` constructor lookup is O(1) against the tz
  database; ``available_timezones()`` is consulted only for the
  ``in_available_timezones`` membership flag (set difference), and
  only after the key already resolved.
* ``offset`` — a zone plus an ISO datetime to its offset details:
  ``utc_offset`` (``±HH:MM``), ``tzname`` (abbreviation), ``dst``
  (delta or ``None``), ``is_dst``, ``utcoffset_seconds`` and
  ``utc_datetime``. Naive datetimes are interpreted *in the zone*;
  aware datetimes (``Z`` or ``±HH:MM`` suffix) are converted as
  instants. Real PEP 495 detection reports whether the local wall
  time is ``ambiguous`` (occured twice — fall-back) or ``impossible``
  (never occurred — spring-forward gap): both folds of the naive
  time are converted to UTC and back; the wall time is ambiguous
  when both folds round-trip and impossible when neither does.
* ``transitions`` — a zone plus a year (1970..2100) to its UTC
  offset transitions, each with ``at`` (the transition instant in
  zone wall time on the *new* offset side — the convention "clocks
  jump 02:00 → 03:00" reports 03:00), ``at_utc``, ``wall_before`` /
  ``wall_after`` (both sides, explicit), ``from_offset``,
  ``to_offset``, ``delta_minutes`` and abbreviations. A coarse 6-hour
  scan across the year detects candidate windows, each refined by
  bisection to one hour and then a minute-level scan; the honest
  granularity statement: this detects every pair of transitions at
  least 6 hours apart, and a sweep of the transition-dense tzdata
  zones (Ramadan-adjusting Casablanca/Cairo, Gaza/Hebron, Troll,
  Lord Howe, ...) shows the closest consecutive transitions between
  1970 and 2100 are 7 days apart (Asia/Gaza, October 2040), so
  nothing is missed; all post-1970 tzdata transitions are
  minute-aligned, so the located instants are exact to the minute.
  Southern/northern hemisphere inference comes from the month of the
  offset-increasing transition (Aug-Dec → southern, Feb-Jul →
  northern).
* ``compare`` — two zones to ``current_offset_diff`` (at a *fixed*
  reference instant, 2026-06-15T12:00Z — deterministic, no clock
  read), ``dst_policy_diff`` (one observes DST, the other does not),
  ``overlap_hours_per_day`` (UTC hours of the reference date on
  which both zones sit inside a 08:00-20:00 local working band),
  ``worst_case_diff`` (730 daily noon-UTC samples across 2026-2027,
  covering both hemispheres' transitions) and ``typically_same``
  (identical offsets at all sweep instants and abbreviations at all
  seasonal samples — true for aliases like
  ``America/Buenos_Aires`` vs ``America/Argentina/Buenos_Aires``).
* ``window`` — a list of 2..8 zones plus a local working window
  (``"09:00-17:00"``) and a date to each zone's UTC interval, the
  common UTC overlap (or ``None``), every participant's local time
  at the overlap start/end, and a recommendation whether shifting
  the meeting by one day widens the overlap (DST weekends change
  it). Window edges are mapped with ``fold=0`` semantics; edges that
  land inside a fall-back repeat or a spring-forward gap are
  flagged.

tz database availability: in an environment with neither a system
tz database nor the ``tzdata`` package, ``ZoneInfo`` lookups raise
``ZoneInfoNotFoundError`` for every key. The tool detects this once
by probing ``ZoneInfo("UTC")`` (present in every real tz database)
and reports it as a structured error — ``validate`` returns
``{"valid": false, "error_kind": "tz_database_unavailable", ...}``
with a hint to install ``tzdata``; every other mode raises a
``ValueError`` naming the same fix.

``is_dst`` is ``dst() != timedelta(0)`` — the documented caveats:
zones that never observe DST report ``is_dst: false`` (tzdata models
several of them, e.g. ``Asia/Kolkata``, with a zero DST delta, so
``dst`` reads ``+00:00`` rather than ``null``), and tzdata models a
few zones with non-hour or historically negative DST deltas, where
``dst`` and ``is_dst`` faithfully report the tzdata delta even
though the label "DST" reads oddly; offset arithmetic is unaffected
either way.

Canonical-name honesty: the stdlib cannot distinguish a canonical
zone from a legacy link (both ``US/Eastern`` and
``America/New_York`` resolve, and both appear in
``zoneinfo.available_timezones()`` on typical systems). ``validate``
therefore reports the ``in_available_timezones`` set difference
rather than pretending to resolve link targets; use ``compare``'s
``typically_same`` for behavioural alias detection.

Input validation is strict and happens before any computation:
unknown mode, malformed zone names (shape, length, segment count),
non-canonical datetimes, years outside 1970..2100, wrong-arity zone
lists, malformed working windows or dates all raise a
``ValueError``. Caps: at most 8 zones per ``window`` call; the
``compare`` sweep is a fixed 730 samples; ``validate`` samples are
fixed constants.
"""

import datetime
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from agentuniverse.agent.action.tool.tool import Tool

# IANA zone key shape: 1..4 slash-separated segments of letters,
# digits, '+', '-' or '_' (covers Etc/GMT+5, Etc/GMT-14, GMT0, ...).
_ZONE_RE = re.compile(r"\A[A-Za-z0-9+\-_]{1,44}(?:/[A-Za-z0-9+\-_]{1,44}){0,3}\Z")
# Strict ISO datetime: date, 'T', HH:MM[:SS], optional Z or ±HH:MM.
_DT_RE = re.compile(
    r"\A(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?"
    r"(Z|[+-]\d{2}:\d{2})?\Z"
)
# Working window: HH:MM-HH:MM, 24-hour clock.
_WINDOW_RE = re.compile(
    r"\A([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)\Z"
)
_DATE_RE = re.compile(r"\A(\d{4})-(\d{2})-(\d{2})\Z")

UTC = datetime.timezone.utc

# Fixed seasonal sampling basis (validate / compare): the calendar
# dates of the 2024 equinoxes and solstices at 12:00 UTC — chosen so
# that both hemispheres' DST seasons are represented. Astronomical
# exactness to the minute is irrelevant for seasonal offset
# sampling; the instants are fixed constants so results are
# deterministic.
SEASONAL_SAMPLES: Tuple[Tuple[str, str], ...] = (
    ("march_equinox", "2024-03-20T12:00:00Z"),
    ("june_solstice", "2024-06-20T12:00:00Z"),
    ("september_equinox", "2024-09-22T12:00:00Z"),
    ("december_solstice", "2024-12-21T12:00:00Z"),
)
# Additional has_dst probes: mid-winter and mid-summer on both
# sides of the equator.
_HAS_DST_EXTRA_SAMPLES: Tuple[Tuple[str, str], ...] = (
    ("jan_1", "2024-01-01T12:00:00Z"),
    ("jul_1", "2024-07-01T12:00:00Z"),
)
# Fixed reference instant for compare's "current" fields —
# deterministic by construction (no wall clock is read anywhere).
REFERENCE_INSTANT = datetime.datetime(2026, 6, 15, 12, 0, tzinfo=UTC)
# compare's worst-case sweep: daily noon-UTC samples across two
# full years (both hemispheres' transitions included).
_COMPARE_SWEEP_START = datetime.datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
_COMPARE_SWEEP_DAYS = 730

_TRANSITIONS_MIN_YEAR = 1970
_TRANSITIONS_MAX_YEAR = 2100
_MAX_WINDOW_ZONES = 8
# Coarse transition scan step; see the module docstring for the
# verified minimum inter-transition gap (7 days, tzdata 1970-2100).
_SCAN_STEP = datetime.timedelta(hours=6)
_MINUTE = datetime.timedelta(minutes=1)
_HOUR = datetime.timedelta(hours=1)


def _fmt_offset(delta: datetime.timedelta) -> str:
    """Format a utcoffset as ``±HH:MM`` (``±HH:MM:SS`` when seconds
    are present, which only happens for pre-1970 LMT-style data)."""
    total = int(delta.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    if seconds:
        return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{sign}{hours:02d}:{minutes:02d}"


def _offset_minutes(delta: datetime.timedelta) -> int:
    """Signed whole minutes of a utcoffset (exact post-1970)."""
    return int(delta.total_seconds() // 60)


def _fmt_utc(moment: datetime.datetime) -> str:
    """Canonical ISO 8601 UTC string ending in ``Z``."""
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class TimezoneTool(Tool):
    """IANA timezone intelligence tool built on the stdlib
    ``zoneinfo`` module.

    Attributes:
        max_window_zones (int): Upper bound on the number of zones a
            single ``window`` call may coordinate.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "timezone_tool"
    description: str = (
        "IANA timezone intelligence tool — stdlib zoneinfo + tzdata, "
        "no network, fully deterministic. Validate zone names "
        "(mode='validate': valid flag from ZoneInfo lookup, "
        "in_available_timezones set difference, offsets/abbreviations "
        "at four fixed 2024 seasonal reference instants, has_dst). "
        "Query a zone at a datetime (mode='offset': naive datetimes "
        "interpreted in the zone, aware ones converted; utc_offset "
        "±HH:MM, tzname, dst delta, is_dst, utcoffset_seconds, and "
        "PEP 495 ambiguous/impossible wall-time detection via "
        "two-fold UTC round-trips). List a year's DST transitions "
        "(mode='transitions': 6-hour scan + bisection + minute "
        "refinement, wall time on the new-offset side, hemisphere "
        "inference). Compare two zones (mode='compare': fixed-"
        "reference offset diff, DST policy diff, working-band "
        "overlap hours, 730-day worst-case diff, alias-level "
        "typically_same). Find cross-zone meeting windows "
        "(mode='window': per-zone UTC intervals, common overlap or "
        "null, per-participant local times, widest-overlap day "
        "recommendation)."
    )

    MODES: ClassVar[tuple] = (
        "validate",
        "offset",
        "transitions",
        "compare",
        "window",
    )

    max_window_zones: int = _MAX_WINDOW_ZONES

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        zone: Any = None,
        datetime_str: Any = None,
        year: Any = None,
        other_zone: Any = None,
        zones: Any = None,
        working_window: Any = None,
        date: Any = None,
    ) -> Dict[str, Any]:
        """Run one IANA timezone intelligence operation.

        Args:
            mode (str): One of ``validate`` / ``offset`` /
                ``transitions`` / ``compare`` / ``window``.
            zone (str): IANA zone key; required by ``validate``,
                ``offset`` and ``transitions``, and by ``compare``
                (together with ``other_zone``).
            datetime_str (str): ISO datetime ``YYYY-MM-DDTHH:MM[:SS]``
                with an optional ``Z`` or ``±HH:MM`` suffix; required
                by ``offset``. Naive values are interpreted in
                ``zone``, aware ones are converted as instants.
            year (int | str): Year 1970..2100; required by
                ``transitions``.
            other_zone (str): Second IANA zone key for ``compare``.
            zones (list[str]): 2..8 IANA zone keys; required by
                ``window``.
            working_window (str): Local working window ``HH:MM-HH:MM``
                (e.g. ``"09:00-17:00"``); required by ``window``.
            date (str): Canonical ISO date ``YYYY-MM-DD``; required
                by ``window``.

        Returns:
            Dict[str, Any]: The operation result — zone validity,
                offset details, the transition list, the zone
                comparison or the meeting-window analysis, plus the
                call context. ``validate`` reports a well-formed but
                unknown zone (or a missing tz database) as a
                structured ``{"valid": false, ...}`` payload instead
                of raising.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens), if a zone key required by
                ``offset`` / ``transitions`` / ``compare`` /
                ``window`` does not resolve in the local tz
                database, if the year is outside 1970..2100, if the
                zone list has the wrong arity, or if the working
                window or date is invalid.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "validate":
            key = self._parse_zone_name(zone, label="zone")
            return self._run_validate(key)
        if mode == "offset":
            key = self._parse_zone_name(zone, label="zone")
            naive, tz_in = self._parse_datetime(datetime_str)
            return self._run_offset(key, naive, tz_in, datetime_str)
        if mode == "transitions":
            key = self._parse_zone_name(zone, label="zone")
            clean_year = self._validate_int(
                year,
                label="year",
                minimum=_TRANSITIONS_MIN_YEAR,
                maximum=_TRANSITIONS_MAX_YEAR,
            )
            return self._run_transitions(key, clean_year)
        if mode == "compare":
            key_a = self._parse_zone_name(zone, label="zone")
            key_b = self._parse_zone_name(other_zone, label="other_zone")
            return self._run_compare(key_a, key_b)
        # window
        zone_list = self._parse_zone_list(zones)
        start_h, start_m, end_h, end_m = self._parse_window(working_window)
        clean_date = self._parse_date(date, label="date")
        return self._run_window(
            zone_list,
            (start_h, start_m),
            (end_h, end_m),
            clean_date,
            working_window,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"timezone_tool: {message}")

    @classmethod
    def _validate_int(
        cls, value: Any, label: str, minimum: int, maximum: int
    ) -> int:
        """Validate an integer parameter given as int or digit string."""
        if isinstance(value, bool):
            cls._invalid(f"{label} must be an integer (got {value!r})")
        if isinstance(value, int):
            number = value
        elif isinstance(value, str) and re.fullmatch(r"-?\d+", value.strip()):
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
    def _parse_zone_name(cls, value: Any, label: str) -> str:
        """Validate the *shape* of an IANA zone key.

        Only the shape is checked here — whether the key exists in
        the tz database is a ``ZoneInfo`` lookup, never an
        ``available_timezones()`` enumeration.
        """
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
            or len(value) > 64
            or value.startswith("/")
            or value.endswith("/")
            or "//" in value
            or not _ZONE_RE.match(value)
        ):
            cls._invalid(
                f"{label} must be an IANA zone key such as "
                f"'Europe/Berlin' or 'Etc/GMT+5' (got {value!r})"
            )
        return value

    @classmethod
    def _parse_datetime(
        cls, value: Any
    ) -> Tuple[datetime.datetime, Optional[datetime.timezone]]:
        """Parse the strict ISO datetime of the ``offset`` mode.

        Returns the naive wall time plus the parsed input offset
        (``None`` for a naive input). Only the exact canonical form
        is accepted — no space separator, no abbreviated years.
        """
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
            or not _DT_RE.match(value)
        ):
            cls._invalid(
                "datetime_str must be an ISO datetime "
                "YYYY-MM-DDTHH:MM[:SS] with optional Z or ±HH:MM "
                f"suffix (got {value!r})"
            )
        match = _DT_RE.match(value)
        year, month, day, hour, minute = (
            int(match.group(i)) for i in range(1, 6)
        )
        second = int(match.group(6) or 0)
        try:
            naive = datetime.datetime(year, month, day, hour, minute, second)
        except ValueError:
            cls._invalid(
                f"datetime_str is not a valid calendar datetime (got {value!r})"
            )
        tz_in: Optional[datetime.timezone] = None
        suffix = match.group(7)
        if suffix:
            if suffix == "Z":
                tz_in = UTC
            else:
                sign = -1 if suffix[0] == "-" else 1
                off_h, off_m = int(suffix[1:3]), int(suffix[4:6])
                if off_h > 23 or off_m > 59:
                    cls._invalid(
                        f"datetime_str offset suffix is out of range "
                        f"(got {value!r})"
                    )
                tz_in = datetime.timezone(
                    sign * datetime.timedelta(hours=off_h, minutes=off_m)
                )
        return naive, tz_in

    @classmethod
    def _parse_zone_list(cls, value: Any) -> List[str]:
        """Validate the zone list of the ``window`` mode (2..8)."""
        if (
            value is None
            or isinstance(value, (str, bytes))
            or not isinstance(value, (list, tuple))
            or not 2 <= len(value) <= _MAX_WINDOW_ZONES
        ):
            cls._invalid(
                f"zones must be a list of 2..{_MAX_WINDOW_ZONES} IANA "
                f"zone keys (got {value!r})"
            )
        keys: List[str] = []
        for item in value:
            keys.append(cls._parse_zone_name(item, label="zones item"))
        if len(set(keys)) != len(keys):
            cls._invalid("zones must not contain duplicates")
        return keys

    @classmethod
    def _parse_window(cls, value: Any) -> Tuple[int, int, int, int]:
        """Parse the working window ``HH:MM-HH:MM`` (start < end)."""
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
            or not _WINDOW_RE.match(value)
        ):
            cls._invalid(
                f"working_window must look like '09:00-17:00' with a "
                f"24-hour clock (got {value!r})"
            )
        match = _WINDOW_RE.match(value)
        assert match is not None  # guarded above
        sh, sm, eh, em = (int(match.group(i)) for i in range(1, 5))
        if (sh, sm) >= (eh, em):
            cls._invalid(
                f"working_window start must be before end (got {value!r})"
            )
        return sh, sm, eh, em

    @classmethod
    def _parse_date(cls, value: Any, label: str) -> datetime.date:
        """Parse a canonical ``YYYY-MM-DD`` ISO calendar date."""
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

    # ------------------------------------------------------------------ #
    # tz database access
    # ------------------------------------------------------------------ #

    @classmethod
    def _tz_database_available(cls) -> bool:
        """Probe the tz database once (``UTC`` exists in every real
        database; a failure here means the environment has neither a
        system tz database nor the ``tzdata`` package)."""
        try:
            ZoneInfo("UTC")
        except (ZoneInfoNotFoundError, OSError):
            return False
        return True

    @classmethod
    def _resolve_zone(cls, key: str) -> ZoneInfo:
        """Resolve a shape-valid zone key, mapping lookup failure to
        the standard error naming the tzdata dependency."""
        try:
            return ZoneInfo(key)
        except ZoneInfoNotFoundError:
            cls._invalid(
                f"unknown IANA zone {key!r} in the local tz database — "
                f"if no zone resolves, install the 'tzdata' package "
                f"(ZoneInfoNotFoundError)"
            )
        except OSError as exc:  # pragma: no cover - corrupted tz files
            cls._invalid(
                f"the tz database could not be read for {key!r}: {exc}"
            )

    # ------------------------------------------------------------------ #
    # Helpers over instants
    # ------------------------------------------------------------------ #

    @staticmethod
    def _offset_at(zone: ZoneInfo, moment_utc: datetime.datetime):
        """utcoffset *at an instant*.

        ``zone.utcoffset(dt)`` interprets ``dt``'s wall fields as a
        time *in the zone* regardless of ``dt.tzinfo``, so every
        instant-based probe must round-trip through ``astimezone``.
        """
        return moment_utc.astimezone(zone).utcoffset()

    @classmethod
    def _sample_instants(cls) -> List[Tuple[str, datetime.datetime]]:
        """The fixed seasonal sampling basis as (label, instant)."""
        samples = []
        for label, iso in SEASONAL_SAMPLES + _HAS_DST_EXTRA_SAMPLES:
            naive = datetime.datetime.fromisoformat(
                iso.replace("Z", "+00:00")
            )
            samples.append((label, naive.astimezone(UTC)))
        return samples

    @classmethod
    def _seasonal_rows(cls, zone: ZoneInfo) -> List[Dict[str, Any]]:
        """Offset/abbreviation rows at the four seasonal samples."""
        rows = []
        for label, iso in SEASONAL_SAMPLES:
            moment = datetime.datetime.fromisoformat(
                iso.replace("Z", "+00:00")
            ).astimezone(UTC)
            local = moment.astimezone(zone)
            rows.append(
                {
                    "label": label,
                    "utc": iso,
                    "utc_offset": _fmt_offset(local.utcoffset()),
                    "abbreviation": local.tzname(),
                    "local_wall": local.replace(tzinfo=None).isoformat(),
                }
            )
        return rows

    @classmethod
    def _has_dst_by_sampling(cls, zone: ZoneInfo) -> bool:
        """Any utcoffset difference across the fixed six samples."""
        offsets = {
            _offset_minutes(moment.astimezone(zone).utcoffset())
            for _, moment in cls._sample_instants()
        }
        return len(offsets) > 1

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(self, key: str) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "mode": "validate",
            "zone": key,
            "tz_database_available": self._tz_database_available(),
        }
        if not payload["tz_database_available"]:
            payload.update(
                {
                    "valid": False,
                    "error_kind": "tz_database_unavailable",
                    "hint": (
                        "no tz database found: install the 'tzdata' "
                        "pip package or provide a system zoneinfo "
                        "directory"
                    ),
                }
            )
            return payload
        try:
            zone = ZoneInfo(key)
        except ZoneInfoNotFoundError as exc:
            # A well-formed name that the local tz database does not
            # know: answered, not raised.
            payload.update(
                {
                    "valid": False,
                    "error_kind": "unknown_zone",
                    "error": f"ZoneInfoNotFoundError: {exc}",
                }
            )
            return payload
        seasonal = self._seasonal_rows(zone)
        payload.update(
            {
                "valid": True,
                # Set-difference note, not a canonicality claim: the
                # stdlib cannot separate canonical zones from legacy
                # links (both are listed by available_timezones() on
                # typical systems); see compare/typically_same.
                "in_available_timezones": key in available_timezones(),
                "sample_offsets": [
                    {
                        "label": row["label"],
                        "utc": row["utc"],
                        "utc_offset": row["utc_offset"],
                        "abbreviation": row["abbreviation"],
                    }
                    for row in seasonal
                ],
                "abbreviation_at_samples": [
                    row["abbreviation"] for row in seasonal
                ],
                "has_dst": self._has_dst_by_sampling(zone),
                "sample_basis": "fixed 2024 reference: both equinoxes, "
                "both solstices (12:00 UTC), Jan 1 and Jul 1",
            }
        )
        return payload

    # ------------------------------------------------------------------ #
    # offset mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _fold_flags(
        cls, zone: ZoneInfo, naive: datetime.datetime
    ) -> Tuple[bool, bool, datetime.timedelta, datetime.timedelta,
               datetime.datetime]:
        """Real PEP 495 detection for a naive wall time.

        Converts both folds of the naive time to UTC and back: the
        wall time is ambiguous when both folds round-trip (two
        distinct instants share it) and impossible when neither
        round-trips (a spring-forward gap, or a whole skipped day
        such as Pacific/Apia 2011-12-30).
        """
        d0 = naive.replace(tzinfo=zone, fold=0)
        d1 = naive.replace(tzinfo=zone, fold=1)
        o0, o1 = d0.utcoffset(), d1.utcoffset()
        u0 = d0.astimezone(UTC)
        u1 = d1.astimezone(UTC)
        if o0 == o1:
            return False, False, o0, o1, u0
        rt0 = u0.astimezone(zone).replace(tzinfo=None) == naive
        rt1 = u1.astimezone(zone).replace(tzinfo=None) == naive
        ambiguous = rt0 and rt1
        impossible = not rt0 and not rt1
        return ambiguous, impossible, o0, o1, u0

    def _run_offset(
        self,
        key: str,
        naive: datetime.datetime,
        tz_in: Optional[datetime.timezone],
        raw_input: Any,
    ) -> Dict[str, Any]:
        zone = self._resolve_zone(key)
        if tz_in is None:
            interpretation = "naive_interpreted_in_zone"
            ambiguous, impossible, o0, o1, moment_utc = self._fold_flags(
                zone, naive
            )
        else:
            interpretation = "aware_converted"
            moment_utc = naive.replace(tzinfo=tz_in).astimezone(UTC)
            wall = moment_utc.astimezone(zone)
            # The derived wall time exists by construction (it came
            # from a real instant), but it may still be a repeated
            # wall time; the gap case cannot occur here.
            ambiguous, impossible, o0, o1, _ = self._fold_flags(
                zone, wall.replace(tzinfo=None)
            )
        primary = moment_utc.astimezone(zone)
        dst_delta = primary.dst()
        payload: Dict[str, Any] = {
            "mode": "offset",
            "zone": key,
            "input_datetime": raw_input,
            "interpretation": interpretation,
            "utc_offset": _fmt_offset(primary.utcoffset()),
            "utcoffset_seconds": int(primary.utcoffset().total_seconds()),
            "tzname": primary.tzname(),
            "dst": _fmt_offset(dst_delta) if dst_delta is not None else None,
            "is_dst": dst_delta is not None and dst_delta != datetime.timedelta(0),
            "local_datetime": primary.replace(tzinfo=None).isoformat(),
            "utc_datetime": _fmt_utc(moment_utc),
            "ambiguous": ambiguous,
            "impossible": impossible,
            "fold_offsets": {
                "fold_0": _fmt_offset(o0),
                "fold_1": _fmt_offset(o1),
            },
        }
        if impossible:
            payload["note"] = (
                "this wall time never existed in the zone (clocks "
                "jumped over it); offsets follow fold=0 (pre-gap) "
                "semantics"
            )
        return payload

    # ------------------------------------------------------------------ #
    # transitions mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _locate_transition(
        cls,
        zone: ZoneInfo,
        lo: datetime.datetime,
        hi: datetime.datetime,
        off_lo: datetime.timedelta,
    ) -> datetime.datetime:
        """Locate a transition instant inside ``(lo, hi]`` to the
        minute.

        ``off_lo`` is the offset at ``lo`` (the invariant side).
        Bisection narrows the bracket to one hour, then a forward
        minute scan finds the first minute carrying the new offset —
        every post-1970 tzdata transition is minute-aligned, so the
        result is exact.
        """
        while hi - lo > _HOUR:
            mid = lo + (hi - lo) / 2
            if cls._offset_at(zone, mid) == off_lo:
                lo = mid
            else:
                hi = mid
        step = lo + _MINUTE
        while cls._offset_at(zone, step) == off_lo:
            lo = step
            step = step + _MINUTE
        return step

    def _run_transitions(self, key: str, year: int) -> Dict[str, Any]:
        zone = self._resolve_zone(key)
        start = datetime.datetime(year, 1, 1, tzinfo=UTC)
        end = datetime.datetime(year + 1, 1, 1, tzinfo=UTC)
        transitions: List[Dict[str, Any]] = []
        increase_months: List[int] = []
        prev = start
        prev_off = self._offset_at(zone, prev)
        probe = start
        while probe < end:
            probe = min(probe + _SCAN_STEP, end)
            off = self._offset_at(zone, probe)
            if off != prev_off:
                moment = self._locate_transition(
                    zone, prev, probe, prev_off
                )
                from_off = self._offset_at(
                    zone, moment - _MINUTE
                )
                to_off = self._offset_at(zone, moment)
                naive_utc = moment.replace(tzinfo=None)
                wall_before = naive_utc + from_off
                wall_after = naive_utc + to_off
                delta_minutes = int(
                    (to_off - from_off).total_seconds() // 60
                )
                transitions.append(
                    {
                        # 'at' is the instant on the NEW-offset side of
                        # the jump ("clocks jump 02:00 -> 03:00"
                        # reports 03:00); wall_before keeps the other
                        # side explicit.
                        "at": wall_after.isoformat()
                        + _fmt_offset(to_off),
                        "at_utc": _fmt_utc(moment),
                        "wall_before": wall_before.isoformat(),
                        "wall_after": wall_after.isoformat(),
                        "from_offset": _fmt_offset(from_off),
                        "to_offset": _fmt_offset(to_off),
                        "delta_minutes": delta_minutes,
                        "delta": _fmt_offset(to_off - from_off),
                        "abbreviation_before": (moment - _MINUTE)
                        .astimezone(zone)
                        .tzname(),
                        "abbreviation_after": moment.astimezone(zone).tzname(),
                        "kind": "dst_start"
                        if delta_minutes > 0
                        else "dst_end",
                    }
                )
                if delta_minutes > 0:
                    increase_months.append(moment.astimezone(zone).month)
                prev_off = to_off
            prev = probe
        if increase_months:
            if any(month >= 8 for month in increase_months):
                hemisphere = "southern"
            else:
                hemisphere = "northern"
        else:
            hemisphere = "no_dst_or_unknown"
        return {
            "mode": "transitions",
            "zone": key,
            "year": year,
            "transitions": transitions,
            "count": len(transitions),
            "hemisphere_inference": hemisphere,
            "scan_note": (
                f"coarse {int(_SCAN_STEP.total_seconds() // 3600)}-hour "
                "scan across the year, then bisection to one hour and "
                "a minute scan; the closest consecutive tzdata "
                "transitions 1970-2100 are 7 days apart (verified "
                "sweep), and post-1970 transitions are minute-aligned"
            ),
        }

    # ------------------------------------------------------------------ #
    # compare mode
    # ------------------------------------------------------------------ #

    def _run_compare(self, key_a: str, key_b: str) -> Dict[str, Any]:
        zone_a = self._resolve_zone(key_a)
        zone_b = self._resolve_zone(key_b)
        # Fixed-reference "current" difference (deterministic).
        off_a = self._offset_at(zone_a, REFERENCE_INSTANT)
        off_b = self._offset_at(zone_b, REFERENCE_INSTANT)
        diff = _offset_minutes(off_a - off_b)
        # DST policy on the fixed 2024 sampling basis.
        a_dst = self._has_dst_by_sampling(zone_a)
        b_dst = self._has_dst_by_sampling(zone_b)
        # Working-band overlap hours on the reference date: UTC
        # hours where both zones sit inside 08:00-20:00 local.
        hours: List[int] = []
        for hour in range(24):
            moment = datetime.datetime(
                REFERENCE_INSTANT.year,
                REFERENCE_INSTANT.month,
                REFERENCE_INSTANT.day,
                hour,
                tzinfo=UTC,
            )
            la = moment.astimezone(zone_a)
            lb = moment.astimezone(zone_b)
            if (
                8 <= la.hour < 20 and 8 <= lb.hour < 20
            ):
                hours.append(hour)
        ranges: List[Dict[str, int]] = []
        for hour in hours:
            if ranges and hour == ranges[-1]["end_hour"]:
                ranges[-1]["end_hour"] = hour + 1
            else:
                ranges.append({"start_hour": hour, "end_hour": hour + 1})
        # Worst-case sweep: daily noon UTC across two full years.
        moment = _COMPARE_SWEEP_START
        step = datetime.timedelta(days=1)
        worst_minutes = None
        worst_at: Optional[datetime.datetime] = None
        same_offsets = True
        checked = 0
        while checked < _COMPARE_SWEEP_DAYS:
            oa = self._offset_at(zone_a, moment)
            ob = self._offset_at(zone_b, moment)
            if oa != ob:
                same_offsets = False
            minutes = abs(_offset_minutes(oa - ob))
            if worst_minutes is None or minutes > worst_minutes:
                worst_minutes = minutes
                worst_at = moment
            moment += step
            checked += 1
        # Alias-level identity: identical offsets across the whole
        # sweep and identical abbreviations at the seasonal samples.
        same_abbrs = [row["abbreviation"] for row in self._seasonal_rows(zone_a)] == [
            row["abbreviation"] for row in self._seasonal_rows(zone_b)
        ]
        typically_same = same_offsets and same_abbrs
        payload: Dict[str, Any] = {
            "mode": "compare",
            "zone_a": key_a,
            "zone_b": key_b,
            "reference_utc": _fmt_utc(REFERENCE_INSTANT),
            "offsets_at_reference": {
                key_a: _fmt_offset(off_a),
                key_b: _fmt_offset(off_b),
            },
            "current_offset_diff": {
                "minutes": diff,
                "human": _fmt_offset(off_a - off_b),
                "note": "signed as zone minus other_zone, evaluated at "
                "the fixed reference instant (deterministic; no wall "
                "clock is read)",
            },
            "dst_policy": {
                "zone_a_dst": a_dst,
                "zone_b_dst": b_dst,
                "differs": a_dst != b_dst,
                "sample_basis": "fixed 2024 reference instants",
            },
            "working_band": {
                "band_local": "08:00-20:00",
                "overlap_hours_per_day_utc": len(hours),
                "utc_hour_ranges": ranges,
                "date_utc": REFERENCE_INSTANT.date().isoformat(),
            },
            "worst_case_diff": {
                "minutes": worst_minutes,
                "human": _fmt_offset(
                    datetime.timedelta(minutes=worst_minutes)
                ),
                "first_at_utc": _fmt_utc(worst_at) if worst_at else None,
                "sampled_days": _COMPARE_SWEEP_DAYS,
                "note": "daily noon-UTC samples across 2026-2027, "
                "covering both hemispheres' transitions",
            },
            "typically_same": typically_same,
        }
        if typically_same:
            payload["typically_same_note"] = (
                "identical offsets at all sweep instants and "
                "abbreviations at all seasonal samples — aliases or "
                "identical rules"
            )
        return payload

    # ------------------------------------------------------------------ #
    # window mode
    # ------------------------------------------------------------------ #

    def _run_window(
        self,
        keys: List[str],
        start_hm: Tuple[int, int],
        end_hm: Tuple[int, int],
        day: datetime.date,
        raw_window: Any,
    ) -> Dict[str, Any]:
        zones = [(key, self._resolve_zone(key)) for key in keys]
        intervals: Dict[str, Dict[str, Any]] = {}
        starts: List[datetime.datetime] = []
        ends: List[datetime.datetime] = []
        for key, zone in zones:
            u_s, u_e, flags = self._window_edges(zone, day, start_hm, end_hm)
            starts.append(u_s)
            ends.append(u_e)
            intervals[key] = {
                "start_utc": _fmt_utc(u_s),
                "end_utc": _fmt_utc(u_e),
                "duration_minutes": int((u_e - u_s).total_seconds() // 60),
                **flags,
            }
        overlap_start = max(starts)
        overlap_end = min(ends)
        common: Optional[Dict[str, Any]] = None
        local_times: Dict[str, Dict[str, str]] = {}
        if overlap_start < overlap_end:
            common = {
                "start_utc": _fmt_utc(overlap_start),
                "end_utc": _fmt_utc(overlap_end),
                "duration_minutes": int(
                    (overlap_end - overlap_start).total_seconds() // 60
                ),
            }
            for key, zone in zones:
                local_times[key] = {
                    "start": overlap_start.astimezone(zone)
                    .replace(tzinfo=None)
                    .isoformat(),
                    "end": overlap_end.astimezone(zone)
                    .replace(tzinfo=None)
                    .isoformat(),
                }
        # Widest-overlap day recommendation across D-1 / D / D+1.
        # The adjacent dates are recomputed from scratch (fold=0
        # conversions of their own wall edges) — an arithmetic UTC
        # shift would be wrong exactly on the DST weekends this
        # recommendation exists to expose.
        day_results = []
        for shift in (-1, 0, 1):
            alt_day = day + datetime.timedelta(days=shift)
            alt_starts, alt_ends = [], []
            for _, zone in zones:
                u_s, u_e, _ = self._window_edges(
                    zone, alt_day, start_hm, end_hm
                )
                alt_starts.append(u_s)
                alt_ends.append(u_e)
            s, e = max(alt_starts), min(alt_ends)
            day_results.append(
                {
                    "date": alt_day.isoformat(),
                    "day_shift": shift,
                    "duration_minutes": int((e - s).total_seconds() // 60)
                    if s < e
                    else None,
                }
            )
        with_overlap = [r for r in day_results if r["duration_minutes"]]
        requested_minutes = common["duration_minutes"] if common else None
        if with_overlap:
            # Ties keep the requested date (day_shift 0 wins).
            best = max(
                with_overlap,
                key=lambda r: (r["duration_minutes"], -abs(r["day_shift"])),
            )
            gain = (
                best["duration_minutes"] - requested_minutes
                if requested_minutes is not None
                else best["duration_minutes"]
            )
            if best["day_shift"] == 0:
                suggestion = f"keep {day.isoformat()}"
            elif requested_minutes is None:
                suggestion = (
                    f"shift the meeting to {best['date']} for "
                    f"{best['duration_minutes']} min of overlap "
                    f"(none on {day.isoformat()})"
                )
            else:
                suggestion = (
                    f"shift the meeting to {best['date']} for "
                    f"+{gain} min of overlap"
                )
            recommendation = {
                "best_date": best["date"],
                "best_duration_minutes": best["duration_minutes"],
                "requested_duration_minutes": requested_minutes,
                "day_shift": best["day_shift"],
                "gain_minutes": gain,
                "suggestion": suggestion,
            }
        else:
            recommendation = {
                "best_date": None,
                "best_duration_minutes": None,
                "requested_duration_minutes": requested_minutes,
                "day_shift": None,
                "gain_minutes": 0,
                "suggestion": (
                    "no overlap on this date or on the adjacent days "
                    "with the given working window"
                ),
            }
        return {
            "mode": "window",
            "date": day.isoformat(),
            "working_window": raw_window,
            "utc_intervals": intervals,
            "common_utc_overlap": common,
            "local_times_at_overlap": local_times,
            "recommendation": recommendation,
            "edge_note": (
                "window edges are mapped with fold=0 semantics; edges "
                "landing inside a fall-back repeat or a spring-forward "
                "gap are flagged per zone"
            ),
        }

    @classmethod
    def _window_edges(
        cls,
        zone: ZoneInfo,
        day: datetime.date,
        start_hm: Tuple[int, int],
        end_hm: Tuple[int, int],
    ) -> Tuple[datetime.datetime, datetime.datetime, Dict[str, bool]]:
        """Map a local working window's wall edges to UTC instants.

        Both edges use ``fold=0`` (first-occurrence) semantics, so
        the mapping is monotone; edges that land inside a fall-back
        repeat or a spring-forward gap are flagged.
        """
        naive_start = datetime.datetime.combine(
            day, datetime.time(*start_hm)
        )
        naive_end = datetime.datetime.combine(day, datetime.time(*end_hm))
        amb_s, imp_s, _, _, u_s = cls._fold_flags(zone, naive_start)
        amb_e, imp_e, _, _, u_e = cls._fold_flags(zone, naive_end)
        flags = {
            "start_edge_ambiguous": amb_s,
            "start_edge_impossible": imp_s,
            "end_edge_ambiguous": amb_e,
            "end_edge_impossible": imp_e,
        }
        return u_s, u_e, flags
