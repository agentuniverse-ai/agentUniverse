#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_time_range_tool.py

"""Offline unit tests for TimeRangeTool.

The tool is built purely on the Python standard library, never reads
the wall clock and never touches the network, so this suite runs
fully offline and every assertion is deterministic.

Two kinds of ground truth are combined. Hand-computed clock-time
scenarios are pinned as literal expected values — same-day overlaps,
subtraction splits, the midnight-crossing shift case
(``22:00``-``06:00`` vs ``05:00``-``07:00`` shares exactly 60
minutes), exclusive-end boundary membership, touching-range merges
and gap arithmetic — and structural properties of the circular-arc
algebra (overlap / subtraction / merge / gap versus per-minute set
membership) are verified with exhaustive sweeps over anchor starts
and arc lengths, so the wraparound handling is checked at every
rotation of the clock rather than at a few lucky positions.
"""

import os
import unittest

from agentuniverse.agent.action.tool.common_tool import TimeRangeTool
from agentuniverse.agent.action.tool.common_tool import time_range_tool as \
    time_range_module
from agentuniverse.agent.action.tool.common_tool.time_range_tool import (
    MINUTES_PER_DAY,
    TimeRangeTool as DirectTimeRangeTool,
)

YAML_PATH = os.path.join(
    os.path.dirname(os.path.abspath(time_range_module.__file__)),
    "time_range_tool.yaml",
)


def fmt(minute: int) -> str:
    """Format minutes since midnight as strict ``HH:MM``."""
    return f"{minute // 60:02d}:{minute % 60:02d}"


def arc_members(start: int, length: int) -> frozenset:
    """The set of minutes covered by a circular arc (ground truth)."""
    return frozenset((start + i) % MINUTES_PER_DAY for i in range(length))


def payload_members(payloads) -> frozenset:
    """Minutes covered by a list of serialized range payloads."""
    covered: frozenset = frozenset()
    for item in payloads:
        start = int(item["start"][:2]) * 60 + int(item["start"][3:])
        covered |= arc_members(start, item["minutes"])
    return covered


class TimeRangeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TimeRangeTool."""

    def setUp(self) -> None:
        self.tool = TimeRangeTool()

    # Helper: run a two-range mode without repeating keyword noise.
    def two(self, mode, a, b, c, d, **extra):
        return self.tool.execute(
            mode=mode, start=a, end=b, start2=c, end2=d, **extra
        )

    # ------------------------------------------------------------------ #
    # info mode — duration, midnight flag, day-local segments
    # ------------------------------------------------------------------ #

    def test_info_same_day_range(self) -> None:
        result = self.tool.execute(
            mode="info", start="09:00", end="12:00"
        )
        self.assertEqual(result["duration_minutes"], 180)
        self.assertFalse(result["crosses_midnight"])
        self.assertEqual(result["start_minutes"], 540)
        self.assertEqual(result["end_minutes"], 720)
        self.assertEqual(result["segments"], [[540, 720]])
        self.assertEqual((result["start"], result["end"]), ("09:00", "12:00"))

    def test_info_overnight_shift(self) -> None:
        result = self.tool.execute(mode="info", start="22:00", end="06:00")
        self.assertEqual(result["duration_minutes"], 480)
        self.assertTrue(result["crosses_midnight"])
        self.assertEqual(result["segments"], [[1320, 1440], [0, 360]])

    def test_info_range_ending_at_midnight(self) -> None:
        result = self.tool.execute(mode="info", start="22:00", end="00:00")
        self.assertEqual(result["duration_minutes"], 120)
        self.assertTrue(result["crosses_midnight"])
        self.assertEqual(result["segments"], [[1320, 1440]])

    def test_info_one_minute_range(self) -> None:
        result = self.tool.execute(mode="info", start="09:00", end="09:01")
        self.assertEqual(result["duration_minutes"], 1)
        self.assertFalse(result["crosses_midnight"])

    def test_info_nearly_full_day(self) -> None:
        result = self.tool.execute(mode="info", start="00:01", end="00:00")
        self.assertEqual(result["duration_minutes"], 1439)
        self.assertTrue(result["crosses_midnight"])

    # ------------------------------------------------------------------ #
    # overlap mode — literal ground truths
    # ------------------------------------------------------------------ #

    def test_overlap_disjoint_same_day(self) -> None:
        result = self.two("overlap", "09:00", "12:00", "14:00", "17:00")
        self.assertEqual(result["overlap_minutes"], 0)
        self.assertFalse(result["overlaps"])
        self.assertEqual(result["overlap_ranges"], [])

    def test_overlap_partial_same_day(self) -> None:
        result = self.two("overlap", "09:00", "12:00", "11:00", "14:00")
        self.assertEqual(result["overlap_minutes"], 60)
        self.assertEqual(
            result["overlap_ranges"],
            [{"start": "11:00", "end": "12:00", "minutes": 60,
              "crosses_midnight": False}],
        )

    def test_overlap_containment(self) -> None:
        result = self.two("overlap", "09:00", "17:00", "10:00", "11:00")
        self.assertEqual(result["overlap_minutes"], 60)

    def test_overlap_identical_ranges(self) -> None:
        result = self.two("overlap", "09:00", "12:00", "09:00", "12:00")
        self.assertEqual(result["overlap_minutes"], 180)

    def test_overlap_touching_ranges_is_zero_end_exclusive(self) -> None:
        result = self.two("overlap", "09:00", "12:00", "12:00", "15:00")
        self.assertEqual(result["overlap_minutes"], 0)
        self.assertFalse(result["overlaps"])

    def test_overlap_overnight_shift_vs_morning(self) -> None:
        # The pinned ground truth of the overnight-shift world: a
        # 22:00-06:00 shift and a 05:00-07:00 window share 05:00-06:00.
        result = self.two("overlap", "22:00", "06:00", "05:00", "07:00")
        self.assertEqual(result["overlap_minutes"], 60)
        self.assertTrue(result["overlaps"])
        self.assertEqual(
            result["overlap_ranges"],
            [{"start": "05:00", "end": "06:00", "minutes": 60,
              "crosses_midnight": False}],
        )

    def test_overlap_two_overnight_shifts(self) -> None:
        result = self.two("overlap", "22:00", "06:00", "23:00", "07:00")
        self.assertEqual(result["overlap_minutes"], 420)
        self.assertEqual(result["overlap_ranges"][0]["start"], "23:00")
        self.assertEqual(result["overlap_ranges"][0]["end"], "06:00")
        self.assertTrue(result["overlap_ranges"][0]["crosses_midnight"])

    def test_overlap_overnight_contains_day_range(self) -> None:
        # 23:00-02:00 fully covers 00:30-01:30.
        result = self.two("overlap", "23:00", "02:00", "00:30", "01:30")
        self.assertEqual(result["overlap_minutes"], 60)

    def test_overlap_symmetry(self) -> None:
        first = self.two("overlap", "22:00", "06:00", "05:00", "07:00")
        second = self.two("overlap", "05:00", "07:00", "22:00", "06:00")
        self.assertEqual(
            first["overlap_minutes"], second["overlap_minutes"]
        )

    # ------------------------------------------------------------------ #
    # overlap mode — exhaustive sweep against per-minute membership
    # ------------------------------------------------------------------ #

    def test_overlap_sweep_matches_set_intersection(self) -> None:
        checked = 0
        for a_start in range(0, MINUTES_PER_DAY, 180):
            for a_len in (1, 90, 480, 1000, 1439):
                for b_start in range(0, MINUTES_PER_DAY, 173):
                    for b_len in (1, 60, 480, 1439):
                        with self.subTest(
                            a=(a_start, a_len), b=(b_start, b_len)
                        ):
                            result = self.two(
                                "overlap",
                                fmt(a_start),
                                fmt((a_start + a_len) % MINUTES_PER_DAY),
                                fmt(b_start),
                                fmt((b_start + b_len) % MINUTES_PER_DAY),
                            )
                            expected = len(
                                arc_members(a_start, a_len)
                                & arc_members(b_start, b_len)
                            )
                            self.assertEqual(
                                result["overlap_minutes"], expected
                            )
                            self.assertEqual(
                                payload_members(result["overlap_ranges"]),
                                (
                                    arc_members(a_start, a_len)
                                    & arc_members(b_start, b_len)
                                ),
                            )
                        checked += 1
        self.assertGreater(checked, 1000)

    # ------------------------------------------------------------------ #
    # contains mode — half-open boundary semantics
    # ------------------------------------------------------------------ #

    def test_contains_boundaries_same_day(self) -> None:
        cases = [("09:00", True), ("11:59", True), ("12:00", False),
                 ("08:59", False), ("12:01", False)]
        for time, expected in cases:
            with self.subTest(time=time):
                result = self.tool.execute(
                    mode="contains", start="09:00", end="12:00", time=time
                )
                self.assertEqual(result["contains"], expected)

    def test_contains_boundaries_overnight(self) -> None:
        cases = [("22:00", True), ("23:59", True), ("00:00", True),
                 ("05:59", True), ("06:00", False), ("12:00", False),
                 ("21:59", False)]
        for time, expected in cases:
            with self.subTest(time=time):
                result = self.tool.execute(
                    mode="contains", start="22:00", end="06:00", time=time
                )
                self.assertEqual(result["contains"], expected)

    def test_contains_single_minute_range(self) -> None:
        self.assertTrue(self.tool.execute(
            mode="contains", start="09:00", end="09:01", time="09:00"
        )["contains"])
        self.assertFalse(self.tool.execute(
            mode="contains", start="09:00", end="09:01", time="09:01"
        )["contains"])

    def test_contains_sweep_matches_membership(self) -> None:
        for start in range(0, MINUTES_PER_DAY, 97):
            for length in (1, 61, 480, 1439):
                for probe in range(0, MINUTES_PER_DAY, 149):
                    with self.subTest(s=start, l=length, t=probe):
                        result = self.tool.execute(
                            mode="contains",
                            start=fmt(start),
                            end=fmt((start + length) % MINUTES_PER_DAY),
                            time=fmt(probe),
                        )
                        self.assertEqual(
                            result["contains"],
                            probe in arc_members(start, length),
                        )

    # ------------------------------------------------------------------ #
    # subtract mode — literal ground truths
    # ------------------------------------------------------------------ #

    def test_subtract_splits_same_day_range(self) -> None:
        result = self.two("subtract", "09:00", "18:00", "12:00", "13:00")
        self.assertEqual(
            result["remaining"],
            [
                {"start": "09:00", "end": "12:00", "minutes": 180,
                 "crosses_midnight": False},
                {"start": "13:00", "end": "18:00", "minutes": 300,
                 "crosses_midnight": False},
            ],
        )
        self.assertEqual(result["remaining_minutes"], 480)
        self.assertEqual(result["removed_minutes"], 60)

    def test_subtract_disjoint_leaves_range_intact(self) -> None:
        result = self.two("subtract", "09:00", "12:00", "14:00", "17:00")
        self.assertEqual(result["remaining_minutes"], 180)
        self.assertEqual(len(result["remaining"]), 1)

    def test_subtract_full_cover_leaves_nothing(self) -> None:
        result = self.two("subtract", "09:00", "12:00", "08:00", "13:00")
        self.assertEqual(result["remaining"], [])
        self.assertEqual(result["remaining_minutes"], 0)
        self.assertEqual(result["removed_minutes"], 180)

    def test_subtract_touching_hole_keeps_range(self) -> None:
        # [12:00, 13:00) removes nothing from [09:00, 12:00): ends are
        # exclusive, so the hole starts exactly where the range ends.
        result = self.two("subtract", "09:00", "12:00", "12:00", "13:00")
        self.assertEqual(result["remaining_minutes"], 180)
        self.assertEqual(len(result["remaining"]), 1)

    def test_subtract_overnight_shift_by_morning_window(self) -> None:
        result = self.two("subtract", "22:00", "06:00", "05:00", "07:00")
        self.assertEqual(result["remaining_minutes"], 420)
        self.assertEqual(
            result["remaining"],
            [{"start": "22:00", "end": "05:00", "minutes": 420,
              "crosses_midnight": True}],
        )

    def test_subtract_day_range_by_overnight_hole(self) -> None:
        # 16:00-09:00 removes both the early morning (08:00-09:00)
        # and the evening tail (16:00-17:00) of 08:00-17:00.
        result = self.two("subtract", "08:00", "17:00", "16:00", "09:00")
        self.assertEqual(
            result["remaining"],
            [{"start": "09:00", "end": "16:00", "minutes": 420,
              "crosses_midnight": False}],
        )

    def test_subtract_sweep_matches_set_difference(self) -> None:
        for a_start in range(0, MINUTES_PER_DAY, 180):
            for a_len in (60, 480, 1000):
                for b_start in range(0, MINUTES_PER_DAY, 173):
                    for b_len in (1, 120, 480, 1439):
                        with self.subTest(
                            a=(a_start, a_len), b=(b_start, b_len)
                        ):
                            result = self.two(
                                "subtract",
                                fmt(a_start),
                                fmt((a_start + a_len) % MINUTES_PER_DAY),
                                fmt(b_start),
                                fmt((b_start + b_len) % MINUTES_PER_DAY),
                            )
                            expected = (
                                arc_members(a_start, a_len)
                                - arc_members(b_start, b_len)
                            )
                            self.assertEqual(
                                result["remaining_minutes"], len(expected)
                            )
                            self.assertEqual(
                                payload_members(result["remaining"]),
                                expected,
                            )
                            # Remaining pieces stay disjoint and sorted.
                            starts = [r["start"] for r in result["remaining"]]
                            self.assertEqual(starts, sorted(starts))
                            for i, piece in enumerate(result["remaining"]):
                                for other in result["remaining"][i + 1:]:
                                    self.assertEqual(
                                        payload_members([piece])
                                        & payload_members([other]),
                                        frozenset(),
                                    )

    # ------------------------------------------------------------------ #
    # merge mode — coalescing, touching chains, wraparound, full day
    # ------------------------------------------------------------------ #

    def test_merge_touching_ranges_coalesce(self) -> None:
        result = self.tool.execute(
            mode="merge", ranges=[["09:00", "12:00"], ["12:00", "15:00"]]
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            result["ranges"],
            [{"start": "09:00", "end": "15:00", "minutes": 360,
              "crosses_midnight": False}],
        )
        self.assertFalse(result["full_day"])
        self.assertNotIn("note", result)

    def test_merge_overlapping_ranges_coalesce(self) -> None:
        result = self.tool.execute(
            mode="merge",
            ranges=[["09:00", "12:00"], ["11:00", "14:00"],
                    ["13:00", "17:00"]],
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["ranges"][0]["minutes"], 480)

    def test_merge_output_is_sorted_and_non_overlapping(self) -> None:
        result = self.tool.execute(
            mode="merge",
            ranges=[["14:00", "16:00"], ["09:00", "10:00"],
                    ["11:00", "12:00"]],
        )
        starts = [r["start"] for r in result["ranges"]]
        self.assertEqual(starts, ["09:00", "11:00", "14:00"])
        self.assertEqual(result["total_minutes"], 240)

    def test_merge_overnight_join_across_midnight(self) -> None:
        result = self.tool.execute(
            mode="merge", ranges=["22:00-06:00", "23:00-07:00"]
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            result["ranges"],
            [{"start": "22:00", "end": "07:00", "minutes": 540,
              "crosses_midnight": True}],
        )
        self.assertIn("note", result)

    def test_merge_chain_touching_through_midnight(self) -> None:
        result = self.tool.execute(
            mode="merge",
            ranges=["01:00-03:00", "03:00-05:00", "22:00-01:00"],
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["ranges"][0]["start"], "22:00")
        self.assertEqual(result["ranges"][0]["end"], "05:00")
        self.assertEqual(result["ranges"][0]["minutes"], 420)

    def test_merge_mixed_day_and_overnight(self) -> None:
        result = self.tool.execute(
            mode="merge", ranges=["09:00-12:00", "22:00-06:00"]
        )
        starts = [r["start"] for r in result["ranges"]]
        self.assertEqual(starts, ["09:00", "22:00"])
        self.assertTrue(result["ranges"][1]["crosses_midnight"])
        self.assertEqual(result["total_minutes"], 660)

    def test_merge_two_wrap_ranges_tile_to_full_day(self) -> None:
        result = self.tool.execute(
            mode="merge", ranges=[["00:00", "12:00"], ["12:00", "00:00"]]
        )
        self.assertTrue(result["full_day"])
        self.assertEqual(result["ranges"], [])
        self.assertEqual(result["total_minutes"], 1440)
        self.assertIn("note", result)

    def test_merge_wrap_complement_pairs_to_full_day(self) -> None:
        # 06:00-02:00 together with 02:00-06:00 tiles the whole day.
        result = self.tool.execute(
            mode="merge", ranges=["06:00-02:00", "02:00-06:00"]
        )
        self.assertTrue(result["full_day"])
        self.assertEqual(result["total_minutes"], MINUTES_PER_DAY)

    def test_merge_single_range_passes_through(self) -> None:
        result = self.tool.execute(mode="merge", ranges=[["09:00", "12:00"]])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total_minutes"], 180)

    def test_merge_accepts_both_item_spellings(self) -> None:
        by_pairs = self.tool.execute(
            mode="merge", ranges=[["22:00", "06:00"]]
        )
        by_string = self.tool.execute(mode="merge", ranges=["22:00-06:00"])
        self.assertEqual(by_pairs["ranges"], by_string["ranges"])

    def test_merge_sweep_covers_union_exactly(self) -> None:
        # Deterministic pseudo-scattered anchors: wrap-friendly strides.
        specs = [
            [(0, 120), (120, 60)],
            [(1380, 120), (0, 420)],           # overnight + early head
            [(600, 300), (1320, 480), (60, 120)],
            [(0, 1439), (719, 2)],             # almost everything
            [(300, 1440 - 300 - 1)],
        ]
        for case in specs:
            with self.subTest(case=case):
                ranges = [
                    [fmt(s), fmt((s + l) % MINUTES_PER_DAY)]
                    for s, l in case
                ]
                result = self.tool.execute(mode="merge", ranges=ranges)
                expected: frozenset = frozenset()
                for s, l in case:
                    expected |= arc_members(s, l)
                self.assertEqual(result["total_minutes"], len(expected))
                self.assertEqual(
                    payload_members(result["ranges"]), expected
                )
                # Payloads stay sorted, disjoint and non-touching.
                payloads = result["ranges"]
                starts = [p["start"] for p in payloads]
                self.assertEqual(starts, sorted(starts))
                for i, piece in enumerate(payloads):
                    for other in payloads[i + 1:]:
                        self.assertEqual(
                            payload_members([piece]) & payload_members([other]),
                            frozenset(),
                        )

    # ------------------------------------------------------------------ #
    # gap mode — idle minutes and complement arcs
    # ------------------------------------------------------------------ #

    def test_gap_between_two_shifts(self) -> None:
        result = self.two("gap", "09:00", "12:00", "13:00", "17:00")
        self.assertEqual(result["gap_minutes"], 60)
        self.assertFalse(result["connected"])
        gaps = {g["start"]: g["minutes"] for g in result["gaps"]}
        self.assertEqual(gaps["12:00"], 60)   # the idle window
        self.assertEqual(gaps["17:00"], 960)  # 17:00 -> 09:00 wraps
        self.assertEqual(result["union_minutes"], 420)

    def test_gap_touching_ranges_is_zero(self) -> None:
        result = self.two("gap", "09:00", "12:00", "12:00", "17:00")
        self.assertEqual(result["gap_minutes"], 0)
        self.assertTrue(result["connected"])

    def test_gap_overlapping_ranges_is_zero(self) -> None:
        result = self.two("gap", "09:00", "12:00", "11:00", "14:00")
        self.assertEqual(result["gap_minutes"], 0)
        self.assertTrue(result["connected"])

    def test_gap_overnight_vs_day_shift(self) -> None:
        # 22:00-06:00 and 09:00-17:00 leave 06:00-09:00 (180) and
        # 17:00-22:00 (300); the idle window is the smaller one.
        result = self.two("gap", "22:00", "06:00", "09:00", "17:00")
        self.assertEqual(result["gap_minutes"], 180)
        self.assertEqual(len(result["gaps"]), 2)
        self.assertEqual(result["union_minutes"], 960)

    def test_gap_complement_tiles_full_day(self) -> None:
        result = self.two("gap", "00:00", "12:00", "12:00", "00:00")
        self.assertEqual(result["gap_minutes"], 0)
        self.assertEqual(result["gaps"], [])
        self.assertTrue(result["connected"])
        self.assertEqual(result["union_minutes"], 1440)

    def test_gap_disjoint_wrap_pieces(self) -> None:
        # 23:00-01:00 and 01:30-03:00 leave 01:00-01:30 (30) and the
        # big 03:00-23:00 wrap (1200).
        result = self.two("gap", "23:00", "01:00", "01:30", "03:00")
        self.assertEqual(result["gap_minutes"], 30)
        minutes = sorted(g["minutes"] for g in result["gaps"])
        self.assertEqual(minutes, [30, 1200])

    def test_gap_sweep_matches_complement(self) -> None:
        for a_start in range(0, MINUTES_PER_DAY, 180):
            for a_len in (60, 480):
                for b_start in range(0, MINUTES_PER_DAY, 173):
                    for b_len in (60, 480, 1439):
                        with self.subTest(
                            a=(a_start, a_len), b=(b_start, b_len)
                        ):
                            result = self.two(
                                "gap",
                                fmt(a_start),
                                fmt((a_start + a_len) % MINUTES_PER_DAY),
                                fmt(b_start),
                                fmt((b_start + b_len) % MINUTES_PER_DAY),
                            )
                            union = (
                                arc_members(a_start, a_len)
                                | arc_members(b_start, b_len)
                            )
                            complement = set(range(MINUTES_PER_DAY)) - union
                            self.assertEqual(
                                payload_members(result["gaps"]),
                                frozenset(complement),
                            )
                            self.assertEqual(
                                result["union_minutes"], len(union)
                            )
                            if result["connected"]:
                                self.assertEqual(result["gap_minutes"], 0)
                            else:
                                gap_lengths = [
                                    g["minutes"] for g in result["gaps"]
                                ]
                                self.assertEqual(
                                    result["gap_minutes"],
                                    min(gap_lengths),
                                )

    # ------------------------------------------------------------------ #
    # Error matrix — strict validation before any computation
    # ------------------------------------------------------------------ #

    def test_error_unknown_mode(self) -> None:
        for mode in (None, "times", "overlaps", "TIMERANGE", 1, True):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode)

    def test_error_malformed_times(self) -> None:
        bad = [
            "9:00", "09:0", "09:000", "24:00", "12:60", "009:00",
            " 09:00", "09:00 ", "09-00", "0900", "09:00:00", "",
            "09;00", "09:6O", 900, 9.0, True, False, ["09:00"],
            {"time": "09:00"}, b"09:00",
        ]
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="info", start=value, end="12:00"
                    )
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="info", start="09:00", end=value
                    )

    def test_error_hour_24_and_minutes_60_plus(self) -> None:
        # The regex gate rejects the whole 24:xx hour family and the
        # 60+ minutes family before any arithmetic can happen.
        for value in ("24:00", "24:59", "25:00", "12:60", "12:99",
                      "23:60", "0:60"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="info", start=value, end="12:00")

    def test_error_missing_parameters(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="info", start="09:00")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="info", end="12:00")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="contains", start="09:00", end="12:00")
        for mode in ("overlap", "subtract", "gap"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode, start="09:00", end="12:00")
                with self.assertRaises(ValueError):
                    self.two(mode, "09:00", "12:00", "14:00", None)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="merge")

    def test_error_empty_range_rejected(self) -> None:
        for start, end in (("09:00", "09:00"), ("00:00", "00:00"),
                           ("22:00", "22:00")):
            with self.subTest(pair=(start, end)):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="info", start=start, end=end)

    def test_error_merge_empty_range_rejected(self) -> None:
        for ranges in ([["22:00", "22:00"]], ["05:00-05:00"],
                       [["09:00", "10:00"], ["03:00", "03:00"]]):
            with self.subTest(ranges=ranges):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="merge", ranges=ranges)

    def test_error_merge_bad_container(self) -> None:
        for ranges in ("09:00-12:00", 42, None, {"ranges": []}, True,
                       ["09:00-12:00"] * 0):
            with self.subTest(ranges=ranges):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="merge", ranges=ranges)

    def test_error_merge_bad_items(self) -> None:
        for ranges in ([], [["09:00"]], [["09:00", "10:00", "11:00"]],
                       [900], [["09:00", 1000]], [["09:00", "10:00"], 5],
                       ["9:00-10:00"], ["09:00 - 10:00"], ["09:00"],
                       [["09:00", "10:00"], "garbage"], [None], [[]]):
            with self.subTest(ranges=ranges):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="merge", ranges=ranges)

    def test_error_merge_over_cap(self) -> None:
        ranges = [["09:00", "10:00"]] * 101
        with self.assertRaises(ValueError):
            self.tool.execute(mode="merge", ranges=ranges)
        # Exactly at the cap is accepted.
        ok = self.tool.execute(mode="merge", ranges=[["09:00", "10:00"]] * 100)
        self.assertEqual(ok["total_minutes"], 60)

    def test_error_messages_name_the_tool(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="nonsense")
        self.assertTrue(str(ctx.exception).startswith("time_range_tool:"))
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="info", start="9:00", end="12:00")
        self.assertTrue(str(ctx.exception).startswith("time_range_tool:"))
        self.assertIn("HH:MM", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # Determinism and module surface
    # ------------------------------------------------------------------ #

    def test_deterministic_repeated_calls(self) -> None:
        first = self.tool.execute(
            mode="merge",
            ranges=["22:00-06:00", "23:00-07:00", "09:00-12:00"],
        )
        second = self.tool.execute(
            mode="merge",
            ranges=["22:00-06:00", "23:00-07:00", "09:00-12:00"],
        )
        self.assertEqual(first, second)

    def test_exported_from_package_init(self) -> None:
        self.assertIs(DirectTimeRangeTool, TimeRangeTool)
        from agentuniverse.agent.action.tool.common_tool import (  # noqa: F401
            __all__ as common_tool_all,
        )

        self.assertIn("TimeRangeTool", common_tool_all)

    def test_tool_name_and_description(self) -> None:
        self.assertEqual(self.tool.name, "time_range_tool")
        self.assertTrue(self.tool.description)

    def test_yaml_exists_and_declares_component(self) -> None:
        self.assertTrue(os.path.isfile(YAML_PATH))
        with open(YAML_PATH, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("class: TimeRangeTool", content)
        self.assertIn(
            "module: agentuniverse.agent.action.tool.common_tool."
            "time_range_tool",
            content,
        )
        self.assertIn('name: time_range_tool', content)


if __name__ == "__main__":
    unittest.main()
