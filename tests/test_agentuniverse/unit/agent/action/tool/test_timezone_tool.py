#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_timezone_tool.py

"""Offline unit tests for TimezoneTool.

The tool is built on the standard library ``zoneinfo`` and never
touches the network or the clock, so this suite runs fully offline
and every assertion is deterministic.

Four kinds of ground truth are combined:

(a) *zoneinfo self-consistency* — for a broad set of real zones
    (both hemispheres, half-hour and 45-minute offsets, +14
    Kiritimati, reintroduced-DST Cairo, date-line Apia) the tool's
    ``offset`` mode is checked at 24 sampled naive datetimes of 2024
    against the same zone recomputed directly through
    ``dt.replace(tzinfo=ZoneInfo(...))``, plus aware inputs against
    ``instant.astimezone(zone)``.
(b) *transition verification* — every transition the tool reports
    for 13 zones × 2023-2025 is re-probed one hour before/after the
    instant (offset before/after must equal ``from_offset`` /
    ``to_offset``), the wall-clock arithmetic is checked on both
    sides, and counts are pinned to known reality (US 2/year, India
    0, Lord Howe exactly 2 with ±30-minute deltas, São Paulo and
    Tehran 0 since their abolitions).
(c) *ambiguous/impossible literals* — the classic New York fall-back
    hour (2024-11-03 01:30, two valid readings) and spring-forward
    gap (2024-03-10 02:30, no valid reading), hand-verified fold
    offsets, Lord Howe's half-hour fall-back, and the entire skipped
    day of Pacific/Apia 2011-12-30.
(d) *compare/window literals* — hand-computed New York / London /
    Tokyo examples at the fixed 2026-06-15 reference, the alias pair
    America/Buenos_Aires vs America/Argentina/Buenos_Aires, meeting
    windows on a normal Monday and across the 2026-03-08 US DST
    weekend.

The suite skips gracefully when the environment has no tz database
at all (neither a system zoneinfo directory nor the ``tzdata``
package).
"""

import datetime
import unittest
from datetime import timezone as TZ
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from agentuniverse.agent.action.tool.common_tool import TimezoneTool
from agentuniverse.agent.action.tool.common_tool.timezone_tool import (
    TimezoneTool as DirectTimezoneTool,
    REFERENCE_INSTANT,
)

UTC = TZ.utc


def _zoneinfo_works() -> bool:
    """The suite needs a resolvable tz database."""
    try:
        ZoneInfo("UTC")
        ZoneInfo("America/New_York")
    except (ZoneInfoNotFoundError, OSError):
        return False
    return True


def _fmt(delta: datetime.timedelta) -> str:
    total = int(delta.total_seconds())
    sign = "+" if total >= 0 else "-"
    hours, rem = divmod(abs(total), 3600)
    minutes, seconds = divmod(rem, 60)
    if seconds:
        return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{sign}{hours:02d}:{minutes:02d}"


class TimezoneToolTest(unittest.TestCase):
    """Offline deterministic test cases for the zoneinfo tool."""

    @classmethod
    def setUpClass(cls) -> None:
        if not _zoneinfo_works():
            raise unittest.SkipTest(
                "no tz database available (install the tzdata package)"
            )
        cls.tool = TimezoneTool()

    # ------------------------------------------------------------------ #
    # (a) zoneinfo self-consistency — 24 datetimes per zone
    # ------------------------------------------------------------------ #

    # Broad coverage: both hemispheres, :30 and :45 offsets, +14,
    # DST-observers, never-DST, abolished-DST, Etc sign inversion.
    ZONES = [
        "Pacific/Kiritimati",
        "Pacific/Apia",
        "Pacific/Auckland",
        "Pacific/Chatham",
        "Pacific/Tongatapu",
        "Pacific/Marquesas",
        "Pacific/Pago_Pago",
        "Pacific/Honolulu",
        "America/New_York",
        "America/Chicago",
        "America/Denver",
        "America/Los_Angeles",
        "America/Anchorage",
        "America/St_Johns",
        "America/Havana",
        "America/Santiago",
        "America/Sao_Paulo",
        "America/Argentina/Buenos_Aires",
        "America/Bogota",
        "America/Phoenix",
        "UTC",
        "Europe/London",
        "Europe/Dublin",
        "Europe/Lisbon",
        "Europe/Berlin",
        "Europe/Paris",
        "Europe/Moscow",
        "Europe/Kyiv",
        "Europe/Istanbul",
        "Africa/Cairo",
        "Africa/Casablanca",
        "Africa/Lagos",
        "Africa/Nairobi",
        "Africa/Johannesburg",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Kolkata",
        "Asia/Karachi",
        "Asia/Kathmandu",
        "Asia/Dhaka",
        "Asia/Yangon",
        "Asia/Dubai",
        "Asia/Tehran",
        "Asia/Jerusalem",
        "Australia/Sydney",
        "Australia/Lord_Howe",
        "Australia/Adelaide",
        "Australia/Eucla",
        "Australia/Perth",
        "Etc/GMT+5",
        "Etc/GMT-14",
    ]

    @staticmethod
    def _sample_naive_datetimes() -> list:
        """24 deterministic naive datetimes across 2024: the 3rd at
        04:17 and the 18th at 16:43 of every month (odd times so no
        assertion accidentally rides a transition boundary)."""
        out = []
        for month in range(1, 13):
            out.append(datetime.datetime(2024, month, 3, 4, 17))
            out.append(datetime.datetime(2024, month, 18, 16, 43))
        return out

    def test_offset_naive_matches_zoneinfo_recomputed(self) -> None:
        for key in self.ZONES:
            zone = ZoneInfo(key)
            for naive in self._sample_naive_datetimes():
                aware0 = naive.replace(tzinfo=zone, fold=0)
                result = self.tool.execute(
                    mode="offset", zone=key,
                    datetime_str=naive.isoformat(),
                )
                with self.subTest(zone=key, dt=naive.isoformat()):
                    self.assertEqual(result["utc_offset"],
                                     _fmt(aware0.utcoffset()))
                    self.assertEqual(
                        result["utcoffset_seconds"],
                        int(aware0.utcoffset().total_seconds()),
                    )
                    self.assertEqual(result["tzname"], aware0.tzname())
                    expected_dst = aware0.dst()
                    self.assertEqual(
                        result["dst"],
                        _fmt(expected_dst)
                        if expected_dst is not None
                        else None,
                    )
                    self.assertFalse(result["ambiguous"])
                    self.assertFalse(result["impossible"])
                    self.assertEqual(
                        result["interpretation"],
                        "naive_interpreted_in_zone",
                    )

    def test_offset_aware_matches_astimezone(self) -> None:
        instant = datetime.datetime(2026, 6, 15, 12, 0, tzinfo=UTC)
        for key in self.ZONES:
            zone = ZoneInfo(key)
            local = instant.astimezone(zone)
            result = self.tool.execute(
                mode="offset", zone=key,
                datetime_str="2026-06-15T12:00:00Z",
            )
            with self.subTest(zone=key):
                self.assertEqual(
                    result["interpretation"], "aware_converted"
                )
                self.assertEqual(result["utc_offset"],
                                 _fmt(local.utcoffset()))
                self.assertEqual(result["tzname"], local.tzname())
                self.assertEqual(result["utc_datetime"],
                                 "2026-06-15T12:00:00Z")
                # A wall time reached from a real instant can repeat,
                # but never be impossible.
                self.assertFalse(result["impossible"])

    def test_offset_explicit_offset_suffix_converts(self) -> None:
        # 12:00+05:30 in Kolkata is 06:30 UTC and the wall stays put;
        # the same instant expressed for New York is 01:30 EDT.
        result = self.tool.execute(
            mode="offset", zone="Asia/Kolkata",
            datetime_str="2026-06-15T12:00:00+05:30",
        )
        self.assertEqual(result["utc_datetime"], "2026-06-15T06:30:00Z")
        self.assertEqual(result["local_datetime"], "2026-06-15T12:00:00")
        ny = self.tool.execute(
            mode="offset", zone="America/New_York",
            datetime_str="2026-06-15T12:00:00+05:30",
        )
        self.assertEqual(ny["utc_offset"], "-04:00")
        self.assertEqual(ny["local_datetime"], "2026-06-15T02:30:00")

    # ------------------------------------------------------------------ #
    # Hand-pinned seasonal literals
    # ------------------------------------------------------------------ #

    def test_validate_seasonal_literals(self) -> None:
        london = self.tool.execute(mode="validate", zone="Europe/London")
        self.assertTrue(london["valid"])
        self.assertTrue(london["in_available_timezones"])
        self.assertEqual(
            [row["utc_offset"] for row in london["sample_offsets"]],
            ["+00:00", "+01:00", "+01:00", "+00:00"],  # Mar/Jun/Sep/Dec
        )
        self.assertEqual(london["abbreviation_at_samples"],
                         ["GMT", "BST", "BST", "GMT"])
        self.assertTrue(london["has_dst"])

        kolkata = self.tool.execute(mode="validate", zone="Asia/Kolkata")
        self.assertEqual(
            [row["utc_offset"] for row in kolkata["sample_offsets"]],
            ["+05:30"] * 4,
        )
        self.assertFalse(kolkata["has_dst"])

        kiritimati = self.tool.execute(
            mode="validate", zone="Pacific/Kiritimati"
        )
        self.assertEqual(
            [row["utc_offset"] for row in kiritimati["sample_offsets"]],
            ["+14:00"] * 4,
        )
        self.assertFalse(kiritimati["has_dst"])

        # Etc/GMT+5 is UTC-05:00 (POSIX sign inversion).
        etc = self.tool.execute(mode="validate", zone="Etc/GMT+5")
        self.assertEqual(
            [row["utc_offset"] for row in etc["sample_offsets"]],
            ["-05:00"] * 4,
        )
        self.assertFalse(etc["has_dst"])

    def test_offset_history_literals(self) -> None:
        # London winter/summer vs UTC.
        self.assertEqual(
            self.tool.execute(
                mode="offset", zone="Europe/London",
                datetime_str="2024-01-15T12:00",
            )["utc_offset"],
            "+00:00",
        )
        summer = self.tool.execute(
            mode="offset", zone="Europe/London",
            datetime_str="2024-07-15T12:00",
        )
        self.assertEqual(summer["utc_offset"], "+01:00")
        self.assertTrue(summer["is_dst"])
        self.assertEqual(summer["dst"], "+01:00")
        # Cairo reintroduced DST in 2023: +02 standard, +03 in summer.
        self.assertEqual(
            self.tool.execute(
                mode="offset", zone="Africa/Cairo",
                datetime_str="2024-01-15T12:00",
            )["utc_offset"],
            "+02:00",
        )
        self.assertEqual(
            self.tool.execute(
                mode="offset", zone="Africa/Cairo",
                datetime_str="2024-07-15T12:00",
            )["utc_offset"],
            "+03:00",
        )
        # Apia date-line flip: -10:00 before, +14:00 after the skip.
        self.assertEqual(
            self.tool.execute(
                mode="offset", zone="Pacific/Apia",
                datetime_str="2011-12-29T12:00",
            )["utc_offset"],
            "-10:00",
        )
        self.assertEqual(
            self.tool.execute(
                mode="offset", zone="Pacific/Apia",
                datetime_str="2011-12-31T12:00",
            )["utc_offset"],
            "+14:00",
        )

    def test_validate_is_deterministic(self) -> None:
        first = self.tool.execute(mode="validate", zone="Asia/Tokyo")
        second = self.tool.execute(mode="validate", zone="Asia/Tokyo")
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # (b) transitions — verification oracles 2023-2025
    # ------------------------------------------------------------------ #

    TRANSITION_ZONES = [
        "America/New_York",
        "Europe/London",
        "Europe/Dublin",
        "Australia/Lord_Howe",
        "America/Santiago",
        "Pacific/Auckland",
        "Africa/Cairo",
        "Africa/Casablanca",
        "America/Anchorage",
        "Asia/Kolkata",       # never DST -> 0
        "Asia/Tokyo",         # never DST -> 0
        "America/Sao_Paulo",  # DST abolished 2019 -> 0
        "Asia/Tehran",        # DST abolished 2022 -> 0
    ]

    def _probe(self, key: str, moment_utc: datetime.datetime):
        return moment_utc.astimezone(ZoneInfo(key)).utcoffset()

    def test_transitions_verified_probes_and_counts(self) -> None:
        expected_counts = {
            "Asia/Kolkata": 0,
            "Asia/Tokyo": 0,
            "America/Sao_Paulo": 0,
            "Asia/Tehran": 0,
        }
        for key in self.TRANSITION_ZONES:
            for year in (2023, 2024, 2025):
                result = self.tool.execute(
                    mode="transitions", zone=key, year=year
                )
                with self.subTest(zone=key, year=year):
                    self.assertEqual(result["mode"], "transitions")
                    self.assertEqual(result["zone"], key)
                    self.assertEqual(result["year"], year)
                    self.assertEqual(
                        result["count"], len(result["transitions"])
                    )
                    if key in expected_counts:
                        self.assertEqual(
                            result["count"], expected_counts[key]
                        )
                        self.assertEqual(
                            result["hemisphere_inference"],
                            "no_dst_or_unknown",
                        )
                    else:
                        self.assertEqual(result["count"], 2)
                    for item in result["transitions"]:
                        moment = datetime.datetime.strptime(
                            item["at_utc"], "%Y-%m-%dT%H:%M:%SZ"
                        ).replace(tzinfo=UTC)
                        one_hour = datetime.timedelta(hours=1)
                        one_minute = datetime.timedelta(minutes=1)
                        # Offset just before/after the instant.
                        self.assertEqual(
                            _fmt(self._probe(key, moment - one_hour)),
                            item["from_offset"],
                        )
                        self.assertEqual(
                            _fmt(self._probe(key, moment + one_hour)),
                            item["to_offset"],
                        )
                        self.assertEqual(
                            _fmt(self._probe(key, moment - one_minute)),
                            item["from_offset"],
                        )
                        self.assertEqual(
                            _fmt(self._probe(key, moment)),
                            item["to_offset"],
                        )
                        # Wall arithmetic on both sides of the jump.
                        naive_utc = moment.replace(tzinfo=None)
                        fmt_from = datetime.timedelta(
                            minutes=self._minutes(item["from_offset"])
                        )
                        fmt_to = datetime.timedelta(
                            minutes=self._minutes(item["to_offset"])
                        )
                        self.assertEqual(
                            naive_utc + fmt_from,
                            datetime.datetime.fromisoformat(
                                item["wall_before"]
                            ),
                        )
                        self.assertEqual(
                            naive_utc + fmt_to,
                            datetime.datetime.fromisoformat(
                                item["wall_after"]
                            ),
                        )
                        self.assertEqual(
                            item["at"],
                            item["wall_after"] + item["to_offset"],
                        )
                        # Kind and delta agree in sign and size.
                        delta_minutes = self._minutes(item["to_offset"]) - \
                            self._minutes(item["from_offset"])
                        self.assertEqual(
                            item["delta_minutes"], delta_minutes
                        )
                        self.assertEqual(
                            item["kind"],
                            "dst_start" if delta_minutes > 0 else "dst_end",
                        )

    @staticmethod
    def _minutes(offset_str: str) -> int:
        sign = -1 if offset_str[0] == "-" else 1
        hours, minutes = offset_str[1:].split(":")[:2]
        return sign * (int(hours) * 60 + int(minutes))

    def test_transitions_new_york_2024_literals(self) -> None:
        result = self.tool.execute(
            mode="transitions", zone="America/New_York", year=2024
        )
        self.assertEqual(
            result["transitions"],
            [
                {
                    "at": "2024-03-10T03:00:00-04:00",
                    "at_utc": "2024-03-10T07:00:00Z",
                    "wall_before": "2024-03-10T02:00:00",
                    "wall_after": "2024-03-10T03:00:00",
                    "from_offset": "-05:00",
                    "to_offset": "-04:00",
                    "delta_minutes": 60,
                    "delta": "+01:00",
                    "abbreviation_before": "EST",
                    "abbreviation_after": "EDT",
                    "kind": "dst_start",
                },
                {
                    "at": "2024-11-03T01:00:00-05:00",
                    "at_utc": "2024-11-03T06:00:00Z",
                    "wall_before": "2024-11-03T02:00:00",
                    "wall_after": "2024-11-03T01:00:00",
                    "from_offset": "-04:00",
                    "to_offset": "-05:00",
                    "delta_minutes": -60,
                    "delta": "-01:00",
                    "abbreviation_before": "EDT",
                    "abbreviation_after": "EST",
                    "kind": "dst_end",
                },
            ],
        )
        self.assertEqual(result["hemisphere_inference"], "northern")

    def test_transitions_lord_howe_half_hour(self) -> None:
        for year in (2023, 2024, 2025):
            result = self.tool.execute(
                mode="transitions", zone="Australia/Lord_Howe", year=year
            )
            with self.subTest(year=year):
                self.assertEqual(result["count"], 2)
                deltas = sorted(
                    t["delta_minutes"] for t in result["transitions"]
                )
                self.assertEqual(deltas, [-30, 30])  # ±30-minute DST
                self.assertEqual(
                    result["hemisphere_inference"], "southern"
                )
        result = self.tool.execute(
            mode="transitions", zone="Australia/Lord_Howe", year=2024
        )
        # The spring-forward lands mid-hour in UTC (02:00 local at
        # +10:30 = 15:30 UTC) — minute-level refinement catches it.
        self.assertEqual(
            [t["at_utc"] for t in result["transitions"]],
            ["2024-04-06T15:00:00Z", "2024-10-05T15:30:00Z"],
        )
        self.assertEqual(result["transitions"][0]["from_offset"], "+11:00")
        self.assertEqual(result["transitions"][0]["to_offset"], "+10:30")

    def test_transitions_santiago_southern(self) -> None:
        result = self.tool.execute(
            mode="transitions", zone="America/Santiago", year=2024
        )
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["hemisphere_inference"], "southern")
        # Offset increases in September (spring) and decreases in
        # April (autumn) — the southern flip.
        kinds = {
            datetime.datetime.strptime(
                t["at_utc"], "%Y-%m-%dT%H:%M:%SZ"
            ).month: t["kind"]
            for t in result["transitions"]
        }
        self.assertEqual(kinds[4], "dst_end")
        self.assertEqual(kinds[9], "dst_start")

    # ------------------------------------------------------------------ #
    # (c) ambiguous / impossible — hand-verified PEP 495 literals
    # ------------------------------------------------------------------ #

    def test_ambiguous_new_york_fall_back(self) -> None:
        result = self.tool.execute(
            mode="offset", zone="America/New_York",
            datetime_str="2024-11-03T01:30",
        )
        self.assertTrue(result["ambiguous"])
        self.assertFalse(result["impossible"])
        # The two readings: 01:30 EDT (-04:00) then 01:30 EST (-05:00).
        self.assertEqual(result["fold_offsets"],
                         {"fold_0": "-04:00", "fold_1": "-05:00"})
        # fold=0 (first occurrence) is the primary reading.
        self.assertEqual(result["utc_offset"], "-04:00")
        self.assertEqual(result["tzname"], "EDT")
        self.assertEqual(result["utc_datetime"], "2024-11-03T05:30:00Z")

    def test_impossible_new_york_spring_forward(self) -> None:
        result = self.tool.execute(
            mode="offset", zone="America/New_York",
            datetime_str="2024-03-10T02:30",
        )
        self.assertTrue(result["impossible"])
        self.assertFalse(result["ambiguous"])
        self.assertEqual(result["fold_offsets"],
                         {"fold_0": "-05:00", "fold_1": "-04:00"})
        self.assertIn("never existed", result["note"])

    def test_ambiguous_lord_howe_half_hour_fall_back(self) -> None:
        # Fall-back is 02:00 -> 01:30, so 01:45 happens twice.
        result = self.tool.execute(
            mode="offset", zone="Australia/Lord_Howe",
            datetime_str="2024-04-07T01:45",
        )
        self.assertTrue(result["ambiguous"])
        self.assertEqual(result["fold_offsets"],
                         {"fold_0": "+11:00", "fold_1": "+10:30"})

    def test_impossible_apia_skipped_day(self) -> None:
        # Samoa skipped 2011-12-30 entirely when it moved the date
        # line: every wall time of that day is impossible.
        result = self.tool.execute(
            mode="offset", zone="Pacific/Apia",
            datetime_str="2011-12-30T12:00",
        )
        self.assertTrue(result["impossible"])
        self.assertFalse(result["ambiguous"])

    def test_plain_time_is_neither(self) -> None:
        result = self.tool.execute(
            mode="offset", zone="Asia/Kolkata",
            datetime_str="2026-03-02T10:00",
        )
        self.assertFalse(result["ambiguous"])
        self.assertFalse(result["impossible"])
        self.assertEqual(result["utc_offset"], "+05:30")
        # tzdata models never-DST Kolkata with a zero DST delta.
        self.assertEqual(result["dst"], "+00:00")
        self.assertFalse(result["is_dst"])

    # ------------------------------------------------------------------ #
    # (d) compare / window — hand-verified NY / London / Tokyo
    # ------------------------------------------------------------------ #

    def test_compare_new_york_london(self) -> None:
        result = self.tool.execute(
            mode="compare", zone="America/New_York",
            other_zone="Europe/London",
        )
        self.assertEqual(result["reference_utc"], "2026-06-15T12:00:00Z")
        self.assertEqual(
            result["offsets_at_reference"],
            {"America/New_York": "-04:00", "Europe/London": "+01:00"},
        )
        self.assertEqual(result["current_offset_diff"]["minutes"], -300)
        self.assertEqual(result["current_offset_diff"]["human"], "-05:00")
        # Both shift by one hour together, so the gap is constant 5h.
        self.assertEqual(result["worst_case_diff"]["minutes"], 300)
        self.assertEqual(
            result["worst_case_diff"]["sampled_days"], 730
        )
        self.assertFalse(result["dst_policy"]["differs"])
        self.assertTrue(result["dst_policy"]["zone_a_dst"])
        self.assertFalse(result["typically_same"])
        # Both inside a 08:00-20:00 local band: UTC 12:00-19:00.
        self.assertEqual(
            result["working_band"]["overlap_hours_per_day_utc"], 7
        )
        self.assertEqual(
            result["working_band"]["utc_hour_ranges"],
            [{"start_hour": 12, "end_hour": 19}],
        )

    def test_compare_tokyo_new_york(self) -> None:
        result = self.tool.execute(
            mode="compare", zone="Asia/Tokyo",
            other_zone="America/New_York",
        )
        self.assertEqual(result["current_offset_diff"]["minutes"], 780)
        self.assertEqual(result["current_offset_diff"]["human"], "+13:00")
        # Winter: +09:00 vs -05:00 = 14h.
        self.assertEqual(result["worst_case_diff"]["minutes"], 840)
        self.assertTrue(result["dst_policy"]["differs"])
        self.assertFalse(result["dst_policy"]["zone_a_dst"])
        self.assertTrue(result["dst_policy"]["zone_b_dst"])

    def test_compare_kolkata_london_worst_case(self) -> None:
        result = self.tool.execute(
            mode="compare", zone="Asia/Kolkata",
            other_zone="Europe/London",
        )
        # Winter: +05:30 vs +00:00 = 5h30m; summer: 4h30m.
        self.assertEqual(result["worst_case_diff"]["minutes"], 330)
        self.assertTrue(result["dst_policy"]["differs"])

    def test_compare_alias_pair_typically_same(self) -> None:
        result = self.tool.execute(
            mode="compare", zone="America/Buenos_Aires",
            other_zone="America/Argentina/Buenos_Aires",
        )
        self.assertTrue(result["typically_same"])
        self.assertEqual(result["worst_case_diff"]["minutes"], 0)
        self.assertIn("aliases", result["typically_same_note"])

    def test_window_new_york_london_monday(self) -> None:
        result = self.tool.execute(
            mode="window", zones=["America/New_York", "Europe/London"],
            working_window="09:00-17:00", date="2026-06-15",
        )
        self.assertEqual(
            result["utc_intervals"]["America/New_York"],
            {
                "start_utc": "2026-06-15T13:00:00Z",
                "end_utc": "2026-06-15T21:00:00Z",
                "duration_minutes": 480,
                "start_edge_ambiguous": False,
                "start_edge_impossible": False,
                "end_edge_ambiguous": False,
                "end_edge_impossible": False,
            },
        )
        self.assertEqual(
            result["utc_intervals"]["Europe/London"]["start_utc"],
            "2026-06-15T08:00:00Z",
        )
        self.assertEqual(
            result["common_utc_overlap"],
            {
                "start_utc": "2026-06-15T13:00:00Z",
                "end_utc": "2026-06-15T16:00:00Z",
                "duration_minutes": 180,
            },
        )
        self.assertEqual(
            result["local_times_at_overlap"],
            {
                "America/New_York": {
                    "start": "2026-06-15T09:00:00",
                    "end": "2026-06-15T12:00:00",
                },
                "Europe/London": {
                    "start": "2026-06-15T14:00:00",
                    "end": "2026-06-15T17:00:00",
                },
            },
        )
        rec = result["recommendation"]
        self.assertEqual(rec["best_date"], "2026-06-15")
        self.assertEqual(rec["day_shift"], 0)
        self.assertEqual(rec["gain_minutes"], 0)

    def test_window_three_continents_no_overlap(self) -> None:
        result = self.tool.execute(
            mode="window",
            zones=["America/New_York", "Europe/London", "Asia/Tokyo"],
            working_window="09:00-17:00", date="2026-06-15",
        )
        self.assertIsNone(result["common_utc_overlap"])
        self.assertEqual(result["local_times_at_overlap"], {})
        self.assertIsNone(result["recommendation"]["best_date"])
        # Tokyo 09:00-17:00 JST = 00:00-08:00 UTC.
        self.assertEqual(
            result["utc_intervals"]["Asia/Tokyo"]["start_utc"],
            "2026-06-15T00:00:00Z",
        )

    def test_window_dst_weekend_day_shift(self) -> None:
        # 2026-03-08 is the US spring-forward (second Sunday); London
        # follows only on 2026-03-29, so on 03-07 (EST + GMT) the
        # 09:00-17:00 overlap is 3h, on 03-08 (EDT + GMT) it is 4h.
        result = self.tool.execute(
            mode="window", zones=["America/New_York", "Europe/London"],
            working_window="09:00-17:00", date="2026-03-07",
        )
        self.assertEqual(
            result["utc_intervals"]["America/New_York"]["start_utc"],
            "2026-03-07T14:00:00Z",  # 09:00 EST
        )
        self.assertEqual(
            result["common_utc_overlap"]["duration_minutes"], 180
        )
        rec = result["recommendation"]
        self.assertEqual(rec["best_date"], "2026-03-08")
        self.assertEqual(rec["day_shift"], 1)
        self.assertEqual(rec["gain_minutes"], 60)

    def test_window_edges_flagged_across_transitions(self) -> None:
        # Fall-back morning: the 01:00 edge is ambiguous.
        fall = self.tool.execute(
            mode="window", zones=["America/New_York", "Europe/London"],
            working_window="01:00-02:00", date="2024-11-03",
        )
        ny = fall["utc_intervals"]["America/New_York"]
        self.assertTrue(ny["start_edge_ambiguous"])
        self.assertFalse(ny["end_edge_ambiguous"])
        # Spring-forward morning: the 02:30 edge never existed.
        spring = self.tool.execute(
            mode="window", zones=["America/New_York", "Europe/London"],
            working_window="01:30-02:30", date="2024-03-10",
        )
        ny = spring["utc_intervals"]["America/New_York"]
        self.assertTrue(ny["end_edge_impossible"])
        self.assertFalse(ny["start_edge_impossible"])

    # ------------------------------------------------------------------ #
    # validate error contract
    # ------------------------------------------------------------------ #

    def test_validate_unknown_zone_is_answered_not_raised(self) -> None:
        result = self.tool.execute(
            mode="validate", zone="America/Nowhere"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["error_kind"], "unknown_zone")
        self.assertIn("ZoneInfoNotFoundError", result["error"])
        self.assertTrue(result["tz_database_available"])

    def test_other_modes_reject_unknown_zone(self) -> None:
        for kwargs in (
            {"mode": "offset", "zone": "America/Nowhere",
             "datetime_str": "2024-01-01T00:00"},
            {"mode": "transitions", "zone": "America/Nowhere",
             "year": 2024},
            {"mode": "compare", "zone": "America/Nowhere",
             "other_zone": "UTC"},
            {"mode": "window", "zones": ["America/Nowhere", "UTC"],
             "working_window": "09:00-17:00", "date": "2026-06-15"},
        ):
            with self.subTest(mode=kwargs["mode"]):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(**kwargs)
                self.assertIn("tzdata", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # strict validation
    # ------------------------------------------------------------------ #

    def test_bad_mode_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="nonsense", zone="UTC")

    def test_malformed_zone_names_rejected(self) -> None:
        bad = [
            "New York", "/Europe/Berlin", "Europe//Berlin",
            "Europe/Berlin/", "e" * 100, "", 123, None, True,
            "Europe/Berlin/extra/too/many/segments",
        ]
        for value in bad:
            with self.subTest(zone=value):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="validate", zone=value)

    def test_bad_datetimes_rejected(self) -> None:
        bad = [
            None, 123, "2024-13-01T00:00", "2024-02-30T10:00",
            "2024-03-10 02:30", "2024-03-10T2:30", "2024-03-10T02:30Z ",
            "2024-01-01T00:00+99:00", "2024-01-01T00:00+00:60",
            "2024-01-01", "2024-01-01T00:00:00.5",
        ]
        for value in bad:
            with self.subTest(datetime_str=value):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="offset", zone="UTC", datetime_str=value
                    )

    def test_bad_years_rejected(self) -> None:
        for year in (1969, 2101, "abc", None, 2.5, True):
            with self.subTest(year=year):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="transitions", zone="UTC", year=year
                    )

    def test_year_as_string_accepted(self) -> None:
        result = self.tool.execute(
            mode="transitions", zone="Asia/Kolkata", year="2024"
        )
        self.assertEqual(result["count"], 0)

    def test_bad_window_inputs_rejected(self) -> None:
        base = {
            "mode": "window",
            "working_window": "09:00-17:00",
            "date": "2026-06-15",
        }
        with self.assertRaises(ValueError):
            self.tool.execute(**base, zones=["UTC"])
        with self.assertRaises(ValueError):
            self.tool.execute(
                **base, zones=["UTC"] * 9
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                **base, zones=["UTC", "UTC"]
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="window", zones="UTC,Europe/Berlin",
                working_window="09:00-17:00", date="2026-06-15",
            )
        for window in ("17:00-09:00", "9:00-17:00", "09:00-17:00:00",
                       "24:00-25:00", "09:00-09:00", None, 5):
            with self.subTest(window=window):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="window", zones=["UTC", "Europe/Berlin"],
                        working_window=window, date="2026-06-15",
                    )
        for date in ("2026-02-30", "2026-6-15", "20260615", None, 7):
            with self.subTest(date=date):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="window", zones=["UTC", "Europe/Berlin"],
                        working_window="09:00-17:00", date=date,
                    )

    def test_compare_requires_two_zones(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="compare", zone="UTC", other_zone=None)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="compare", zone=None, other_zone="UTC")

    # ------------------------------------------------------------------ #
    # wiring
    # ------------------------------------------------------------------ #

    def test_exported_from_package(self) -> None:
        self.assertIs(TimezoneTool, DirectTimezoneTool)
        self.assertEqual(self.tool.name, "timezone_tool")
        self.assertIsInstance(self.tool.description, str)
        self.assertIn("validate", self.tool.MODES)


if __name__ == "__main__":
    unittest.main()
