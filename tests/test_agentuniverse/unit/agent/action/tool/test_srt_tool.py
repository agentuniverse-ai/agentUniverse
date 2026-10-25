#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_srt_tool.py

"""Offline unit tests for SrtTool.

The tool is built purely on the standard library (``re`` and integer
arithmetic on strings) and never touches the network, so this suite
runs fully offline. Every assertion is deterministic and the numeric
ground truths are hand-verified:

* ``00:00:01,500`` -> 1 * 1000 + 500 = 1500 ms;
  ``00:00:06.500`` -> 6500 ms; ``00:00:09,250`` -> 9250 ms.
* Stats sample durations 2500 / 1000 / 8000 / 1000 ms ->
  total 12500 ms, min 1000, max 8000, mean 12500 / 4 = 3125.0.
* Overlap: cue 1 ends at 2500 ms while cue 2 starts at 2000 ms ->
  500 ms of overlap; every other adjacent pair is disjoint.
* Reading speeds: 79 chars over 8 s = 9.875 -> 9.88 cps (below 42,
  flagged only for the >7 s duration); 68 chars over 1 s = 68.0 cps
  (above 42, flagged for speed).

Shift arithmetic is likewise hand-checked against the same samples,
including the documented clamping into [0, 99:59:59.999].
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import SrtTool
from agentuniverse.agent.action.tool.common_tool.srt_tool import (
    SrtTool as DirectSrtTool,
)

# --------------------------------------------------------------------- #
# Hand-verified samples
# --------------------------------------------------------------------- #
# Three cues mixing the ',' and '.' millisecond separators.
#   cue 1: 00:00:01,500 -> 00:00:04,000  (start 1500, end 4000)
#   cue 2: 00:00:04,500 -> 00:00:06,000  (start 4500, end 6000)
#   cue 3: 00:00:06.500 -> 00:00:09,250  (start 6500, end 9250, dot)
SAMPLE = (
    "1\n"
    "00:00:01,500 --> 00:00:04,000\n"
    "Hello there.\n"
    "\n"
    "2\n"
    "00:00:04,500 --> 00:00:06,000\n"
    "General Kenobi!\n"
    "You are a bold one.\n"
    "\n"
    "3\n"
    "00:00:06.500 --> 00:00:09,250\n"
    "Away with you!"
)

SAMPLE_CUES = [
    {"index": 1, "start": 1500, "end": 4000, "text": "Hello there."},
    {
        "index": 2,
        "start": 4500,
        "end": 6000,
        "text": "General Kenobi!\nYou are a bold one.",
    },
    {"index": 3, "start": 6500, "end": 9250, "text": "Away with you!"},
]

# Indices 1, 3, 5 at positions 1, 2, 3 -> two sequence warnings.
SKIP_INDEX_SAMPLE = (
    "1\n"
    "00:00:01,000 --> 00:00:02,000\n"
    "A\n"
    "\n"
    "3\n"
    "00:00:03,000 --> 00:00:04,000\n"
    "B\n"
    "\n"
    "5\n"
    "00:00:05,000 --> 00:00:06,000\n"
    "C"
)

# Out-of-order cue bodies; renumber keeps order-as-found (C stays first).
RENUMBER_SAMPLE = (
    "9\n"
    "00:00:05,000 --> 00:00:06,000\n"
    "C\n"
    "\n"
    "2\n"
    "00:00:01,000 --> 00:00:02,000\n"
    "A\n"
    "\n"
    "7\n"
    "00:00:03,000 --> 00:00:04,000\n"
    "B"
)

# Stats ground truth (durations and char counts verified by hand):
#   cue 1: 000->2500, "Hello"            = 5 chars, 2500 ms,  2.0 cps
#   cue 2: 2000->3000, "Overlap here"    = 12 chars, 1000 ms, 12.0 cps
#          (cue 1 end 2500 > cue 2 start 2000 -> 500 ms overlap)
#   cue 3: 10000->18000, 79 chars, 8000 ms, 9.875 -> 9.88 cps
#          (over 7 s -> flagged for duration only)
#   cue 4: 20000->21000, 68 chars, 1000 ms, 68.0 cps
#          (over 42 cps -> flagged for speed only)
STATS_SAMPLE = (
    "1\n"
    "00:00:00,000 --> 00:00:02,500\n"
    "Hello\n"
    "\n"
    "2\n"
    "00:00:02,000 --> 00:00:03,000\n"
    "Overlap here\n"
    "\n"
    "3\n"
    "00:00:10,000 --> 00:00:18,000\n"
    "This cue is deliberately made far too long for anyone to read in eight seconds.\n"
    "\n"
    "4\n"
    "00:00:20,000 --> 00:00:21,000\n"
    "A very long line of text crammed into a single short one-second cue!"
)


class SrtToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib SrtTool."""

    def setUp(self) -> None:
        self.tool = SrtTool()

    # ------------------------------------------------------------------ #
    # parse mode — ground truths and tolerance
    # ------------------------------------------------------------------ #

    def test_direct_module_import_matches_package_export(self) -> None:
        self.assertIs(DirectSrtTool, SrtTool)
        self.assertEqual(self.tool.name, "srt_tool")

    def test_parse_ground_truth_multi_cue(self) -> None:
        result = self.tool.execute(mode="parse", text=SAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "cue_count": 3,
                "cues": SAMPLE_CUES,
                "warnings": [],
                "warnings_truncated": False,
            },
        )

    def test_parse_tolerates_crlf_line_endings(self) -> None:
        result = self.tool.execute(
            mode="parse", text=SAMPLE.replace("\n", "\r\n")
        )
        self.assertEqual(result["cues"], SAMPLE_CUES)
        self.assertEqual(result["warnings"], [])

    def test_parse_tolerates_utf8_bom(self) -> None:
        result = self.tool.execute(mode="parse", text="\ufeff" + SAMPLE)
        self.assertEqual(result["cues"], SAMPLE_CUES)

    def test_parse_tolerates_bom_and_crlf_together(self) -> None:
        result = self.tool.execute(
            mode="parse", text="\ufeff" + SAMPLE.replace("\n", "\r\n")
        )
        self.assertEqual(result["cues"], SAMPLE_CUES)

    def test_parse_tolerates_bare_cr_line_endings(self) -> None:
        result = self.tool.execute(
            mode="parse", text=SAMPLE.replace("\n", "\r")
        )
        self.assertEqual(result["cues"], SAMPLE_CUES)

    def test_parse_short_hour_and_short_fraction_forms(self) -> None:
        # "0:00:01,5" -> hours 0, seconds 1, fraction "5" padded to
        # "500" -> 1500 ms; likewise the end "0:00:02,5" -> 2500 ms.
        result = self.tool.execute(
            mode="parse",
            text="1\n0:00:01,5 --> 0:00:02,5\nHi",
        )
        self.assertEqual(
            result["cues"],
            [{"index": 1, "start": 1500, "end": 2500, "text": "Hi"}],
        )

    def test_parse_dot_milliseconds_and_no_arrow_spaces(self) -> None:
        # Dot separator on both timestamps, no spaces around '-->'.
        result = self.tool.execute(
            mode="parse",
            text="1\n00:00:00.250-->00:00:01.750\nDot",
        )
        self.assertEqual(
            result["cues"],
            [{"index": 1, "start": 250, "end": 1750, "text": "Dot"}],
        )

    def test_parse_ignores_leading_and_trailing_blank_lines(self) -> None:
        result = self.tool.execute(mode="parse", text="\n\n" + SAMPLE + "\n\n\n")
        self.assertEqual(result["cue_count"], 3)
        self.assertEqual(result["cues"], SAMPLE_CUES)

    def test_parse_trailing_whitespace_on_timing_line(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="1\n00:00:01,000 --> 00:00:02,000   \nHi",
        )
        self.assertEqual(result["cues"][0]["start"], 1000)
        self.assertEqual(result["cues"][0]["end"], 2000)

    def test_parse_positional_coordinates_tolerated_and_dropped(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="1\n00:00:01,500 --> 00:00:04,000 X1:100 X2:600 Y1:50 Y2:150\n"
            "Hello there.",
        )
        self.assertEqual(result["cues"][0]["start"], 1500)
        self.assertEqual(result["cues"][0]["end"], 4000)
        # Canonical re-serialization drops the coordinate metadata.
        shifted = self.tool.execute(
            mode="shift",
            text=(
                "1\n00:00:01,500 --> 00:00:04,000 X1:100 X2:600 Y1:50 Y2:150\n"
                "Hello there."
            ),
            milliseconds=0,
        )
        self.assertEqual(
            shifted["result"],
            "1\n00:00:01,500 --> 00:00:04,000\nHello there.\n",
        )

    def test_parse_rstrips_trailing_spaces_in_text_lines(self) -> None:
        result = self.tool.execute(
            mode="parse", text="1\n00:00:01,000 --> 00:00:02,000\nHi   \nthere \t"
        )
        self.assertEqual(result["cues"][0]["text"], "Hi\nthere")

    def test_parse_allows_empty_cue_text(self) -> None:
        result = self.tool.execute(
            mode="parse", text="1\n00:00:01,000 --> 00:00:02,000"
        )
        self.assertEqual(
            result["cues"],
            [{"index": 1, "start": 1000, "end": 2000, "text": ""}],
        )

    def test_parse_index_gap_produces_warnings_not_errors(self) -> None:
        result = self.tool.execute(mode="parse", text=SKIP_INDEX_SAMPLE)
        self.assertEqual(result["cue_count"], 3)
        self.assertEqual(
            result["warnings"],
            [
                "cue position 2 is numbered 3; expected 2",
                "cue position 3 is numbered 5; expected 3",
            ],
        )
        self.assertFalse(result["warnings_truncated"])
        # The cues themselves are still usable, with their claimed numbers.
        self.assertEqual([c["index"] for c in result["cues"]], [1, 3, 5])

    def test_parse_duplicate_index_produces_warning(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text=(
                "1\n00:00:01,000 --> 00:00:02,000\nA\n"
                "\n1\n00:00:03,000 --> 00:00:04,000\nB"
            ),
        )
        self.assertEqual(
            result["warnings"],
            ["cue position 2 is numbered 1; expected 2"],
        )

    def test_parse_out_of_order_indices_produce_warnings(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text=(
                "2\n00:00:01,000 --> 00:00:02,000\nA\n"
                "\n1\n00:00:03,000 --> 00:00:04,000\nB"
            ),
        )
        self.assertEqual(
            result["warnings"],
            [
                "cue position 1 is numbered 2; expected 1",
                "cue position 2 is numbered 1; expected 2",
            ],
        )

    def test_parse_warnings_capped_at_twenty(self) -> None:
        parts = []
        for i in range(25):
            parts.append(
                f"{101 + i}\n00:00:{i % 10:02d},000 --> 00:00:{i % 10:02d},500\nCue {i}"
            )
        result = self.tool.execute(mode="parse", text="\n\n".join(parts))
        self.assertEqual(result["cue_count"], 25)
        self.assertEqual(len(result["warnings"]), 20)
        self.assertTrue(result["warnings_truncated"])
        self.assertEqual(
            result["warnings"][0], "cue position 1 is numbered 101; expected 1"
        )

    def test_parse_boundary_timestamp_99_59_59_999(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="1\n99:59:59,999 --> 99:59:59,999\nEnd of time",
        )
        self.assertEqual(result["cues"][0]["start"], 359_999_999)
        self.assertEqual(result["cues"][0]["end"], 359_999_999)

    def test_parse_is_deterministic(self) -> None:
        first = self.tool.execute(mode="parse", text=SAMPLE)
        second = self.tool.execute(mode="parse", text=SAMPLE)
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # shift mode — hand-verified arithmetic and clamping
    # ------------------------------------------------------------------ #

    def test_shift_positive_offset_ground_truth(self) -> None:
        # +500 ms: 1500->2000, 4000->4500, 4500->5000, 6000->6500,
        # 6500->7000, 9250->9750. Nothing clamps.
        result = self.tool.execute(mode="shift", text=SAMPLE, milliseconds=500)
        self.assertEqual(
            result,
            {
                "mode": "shift",
                "milliseconds": 500,
                "cue_count": 3,
                "clamped_cue_count": 0,
                "clamped_positions": [],
                "result": (
                    "1\n"
                    "00:00:02,000 --> 00:00:04,500\n"
                    "Hello there.\n"
                    "\n"
                    "2\n"
                    "00:00:05,000 --> 00:00:06,500\n"
                    "General Kenobi!\n"
                    "You are a bold one.\n"
                    "\n"
                    "3\n"
                    "00:00:07,000 --> 00:00:09,750\n"
                    "Away with you!\n"
                ),
            },
        )

    def test_shift_negative_offset_clamps_first_cue_at_zero(self) -> None:
        # -2000 ms: cue 1 start 1500-2000 = -500 -> clamped to 0,
        # cue 1 end 4000-2000 = 2000; cues 2 and 3 shift normally.
        result = self.tool.execute(
            mode="shift", text=SAMPLE, milliseconds=-2000
        )
        self.assertEqual(result["milliseconds"], -2000)
        self.assertEqual(result["clamped_cue_count"], 1)
        self.assertEqual(result["clamped_positions"], [1])
        self.assertEqual(
            result["result"],
            "1\n"
            "00:00:00,000 --> 00:00:02,000\n"
            "Hello there.\n"
            "\n"
            "2\n"
            "00:00:02,500 --> 00:00:04,000\n"
            "General Kenobi!\n"
            "You are a bold one.\n"
            "\n"
            "3\n"
            "00:00:04,500 --> 00:00:07,250\n"
            "Away with you!\n",
        )

    def test_shift_negative_beyond_every_cue_pins_all_to_zero(self) -> None:
        # -999999 ms moves every timestamp below zero, so every cue
        # clamps to 00:00:00,000 --> 00:00:00,000 (documented).
        result = self.tool.execute(
            mode="shift", text=SAMPLE, milliseconds=-999_999
        )
        self.assertEqual(result["clamped_positions"], [1, 2, 3])
        self.assertEqual(result["clamped_cue_count"], 3)
        self.assertEqual(
            result["result"],
            "1\n"
            "00:00:00,000 --> 00:00:00,000\n"
            "Hello there.\n"
            "\n"
            "2\n"
            "00:00:00,000 --> 00:00:00,000\n"
            "General Kenobi!\n"
            "You are a bold one.\n"
            "\n"
            "3\n"
            "00:00:00,000 --> 00:00:00,000\n"
            "Away with you!\n",
        )

    def test_shift_positive_clamps_at_representable_maximum(self) -> None:
        # +359999000 ms: 1500 + 359999000 = 360000500 > 359999999,
        # so every timestamp clamps to 99:59:59,999.
        result = self.tool.execute(
            mode="shift", text=SAMPLE, milliseconds=359_999_000
        )
        self.assertEqual(result["clamped_positions"], [1, 2, 3])
        self.assertTrue(result["result"].startswith(
            "1\n99:59:59,999 --> 99:59:59,999\nHello there.\n"
        ))

    def test_shift_zero_canonicalizes_separators_and_endings(self) -> None:
        # A zero shift re-serializes canonically: the dot separator of
        # cue 3 becomes a comma and a single trailing newline is added.
        result = self.tool.execute(mode="shift", text=SAMPLE, milliseconds=0)
        self.assertEqual(result["clamped_cue_count"], 0)
        self.assertEqual(result["result"], SAMPLE.replace("06.500", "06,500") + "\n")

    def test_shift_round_trip_parse_shift_parse(self) -> None:
        parsed = self.tool.execute(mode="parse", text=SAMPLE)["cues"]
        for offset in (750, -1200, 0):
            shifted_text = self.tool.execute(
                mode="shift", text=SAMPLE, milliseconds=offset
            )["result"]
            reparsed = self.tool.execute(mode="parse", text=shifted_text)
            expected = [
                {
                    **cue,
                    "start": max(min(cue["start"] + offset, 359_999_999), 0),
                    "end": max(min(cue["end"] + offset, 359_999_999), 0),
                }
                for cue in parsed
            ]
            self.assertEqual(reparsed["cues"], expected, f"offset {offset}")

    def test_shift_preserves_claimed_cue_numbers(self) -> None:
        result = self.tool.execute(
            mode="shift", text=SKIP_INDEX_SAMPLE, milliseconds=1000
        )
        # Numbers stay 1, 3, 5 — only renumber mode re-indexes.
        self.assertEqual(
            result["result"].split("\n")[0::4][:3], ["1", "3", "5"]
        )

    def test_shift_error_payload_keeps_shift_mode_context(self) -> None:
        result = self.tool.execute(
            mode="shift",
            text="1\n00:00:05,000 --> 00:00:04,000\nBackwards",
            milliseconds=100,
        )
        self.assertEqual(result["mode"], "shift")
        self.assertEqual(result["error"]["type"], "end_before_start")
        self.assertEqual(result["error"]["cue_position"], 1)
        self.assertEqual(result["error"]["cue_index"], 1)

    def test_shift_accepts_full_range_boundary_offsets(self) -> None:
        for boundary in (359_999_999, -359_999_999):
            result = self.tool.execute(
                mode="shift", text=SAMPLE, milliseconds=boundary
            )
            self.assertNotIn("error", result)
            self.assertEqual(result["cue_count"], 3)

    # ------------------------------------------------------------------ #
    # renumber mode
    # ------------------------------------------------------------------ #

    def test_renumber_ground_truth_preserves_order_as_found(self) -> None:
        result = self.tool.execute(mode="renumber", text=RENUMBER_SAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "renumber",
                "cue_count": 3,
                "result": (
                    "1\n"
                    "00:00:05,000 --> 00:00:06,000\n"
                    "C\n"
                    "\n"
                    "2\n"
                    "00:00:01,000 --> 00:00:02,000\n"
                    "A\n"
                    "\n"
                    "3\n"
                    "00:00:03,000 --> 00:00:04,000\n"
                    "B\n"
                ),
            },
        )

    def test_renumber_round_trips_to_sequential_indices(self) -> None:
        renumbered = self.tool.execute(
            mode="renumber", text=SKIP_INDEX_SAMPLE
        )["result"]
        reparsed = self.tool.execute(mode="parse", text=renumbered)
        self.assertEqual([c["index"] for c in reparsed["cues"]], [1, 2, 3])
        self.assertEqual(reparsed["warnings"], [])

    def test_renumber_on_sequential_sample_is_canonical_identity(self) -> None:
        result = self.tool.execute(mode="renumber", text=SAMPLE)
        self.assertEqual(
            result["result"], SAMPLE.replace("06.500", "06,500") + "\n"
        )

    # ------------------------------------------------------------------ #
    # stats mode — hand-verified arithmetic
    # ------------------------------------------------------------------ #

    def test_stats_ground_truth_full_report(self) -> None:
        result = self.tool.execute(mode="stats", text=STATS_SAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "stats",
                "cue_count": 4,
                "total_duration_ms": 12_500,
                "min_duration_ms": 1_000,
                "max_duration_ms": 8_000,
                "mean_duration_ms": 3_125.0,
                "overlap_count": 1,
                "overlapping_pairs": [
                    {
                        "first_position": 1,
                        "second_position": 2,
                        "first_index": 1,
                        "second_index": 2,
                        "overlap_ms": 500,
                    }
                ],
                "reading_warning_count": 2,
                "reading_warnings": [
                    {
                        "position": 3,
                        "index": 3,
                        "duration_ms": 8_000,
                        "chars": 79,
                        "chars_per_second": 9.88,
                        "reasons": ["duration_over_7s"],
                    },
                    {
                        "position": 4,
                        "index": 4,
                        "duration_ms": 1_000,
                        "chars": 68,
                        "chars_per_second": 68.0,
                        "reasons": ["reading_speed_over_42cps"],
                    },
                ],
            },
        )

    def test_stats_clean_sample_has_no_flags(self) -> None:
        # SAMPLE durations: 2500 / 1500 / 2750 -> total 6750,
        # min 1500, max 2750, mean 6750 / 3 = 2250.0. Cue 2 has
        # 15 + 19 = 34 non-newline chars over 1500 ms = 22.67 cps,
        # under every threshold; no adjacent pair overlaps.
        result = self.tool.execute(mode="stats", text=SAMPLE)
        self.assertEqual(result["cue_count"], 3)
        self.assertEqual(result["total_duration_ms"], 6_750)
        self.assertEqual(result["min_duration_ms"], 1_500)
        self.assertEqual(result["max_duration_ms"], 2_750)
        self.assertEqual(result["mean_duration_ms"], 2_250.0)
        self.assertEqual(result["overlap_count"], 0)
        self.assertEqual(result["overlapping_pairs"], [])
        self.assertEqual(result["reading_warning_count"], 0)
        self.assertEqual(result["reading_warnings"], [])

    def test_stats_flags_zero_duration_cue(self) -> None:
        result = self.tool.execute(
            mode="stats",
            text="1\n00:00:05,000 --> 00:00:05,000\nZero",
        )
        self.assertEqual(result["total_duration_ms"], 0)
        self.assertEqual(result["min_duration_ms"], 0)
        self.assertEqual(result["mean_duration_ms"], 0.0)
        self.assertEqual(result["reading_warning_count"], 1)
        warning = result["reading_warnings"][0]
        self.assertEqual(warning["reasons"], ["zero_duration"])
        self.assertIsNone(warning["chars_per_second"])
        self.assertEqual(warning["chars"], 4)

    def test_stats_flags_duration_and_speed_together(self) -> None:
        # 400 chars over 8000 ms: over 7 s AND 400 / 8 = 50 cps > 42.
        result = self.tool.execute(
            mode="stats",
            text="1\n00:00:10,000 --> 00:00:18,000\n" + "x" * 400,
        )
        self.assertEqual(result["reading_warning_count"], 1)
        warning = result["reading_warnings"][0]
        self.assertEqual(
            warning["reasons"],
            ["duration_over_7s", "reading_speed_over_42cps"],
        )
        self.assertEqual(warning["chars_per_second"], 50.0)

    def test_stats_counts_chars_without_line_breaks(self) -> None:
        # Two text lines of 5 chars each -> 10 chars over 2000 ms
        # = 5.0 cps, no flag; proves '\n' is not counted.
        result = self.tool.execute(
            mode="stats",
            text="1\n00:00:01,000 --> 00:00:03,000\nabcde\nfghij",
        )
        self.assertEqual(result["reading_warning_count"], 0)
        self.assertEqual(result["total_duration_ms"], 2_000)

    # ------------------------------------------------------------------ #
    # Content-level failures (structured error payloads)
    # ------------------------------------------------------------------ #

    def test_parse_error_missing_cue_number(self) -> None:
        result = self.tool.execute(
            mode="parse", text="00:00:01,000 --> 00:00:02,000\nHi"
        )
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["error"]["type"], "missing_cue_number")
        self.assertEqual(result["error"]["cue_position"], 1)
        self.assertIsNone(result["error"]["cue_index"])
        self.assertIn("does not start with a cue number", result["error"]["message"])

    def test_parse_error_block_with_only_a_number(self) -> None:
        result = self.tool.execute(mode="parse", text="1\n\n2\n00:00:01,000 --> 00:00:02,000\nHi")
        # Block 1 is just the number "1" with no timing line.
        self.assertEqual(result["error"]["type"], "missing_timing_line")
        self.assertEqual(result["error"]["cue_position"], 1)
        self.assertEqual(result["error"]["cue_index"], 1)

    def test_parse_error_timing_line_without_arrow(self) -> None:
        result = self.tool.execute(mode="parse", text="1\nHello\n")
        self.assertEqual(result["error"]["type"], "missing_timing_line")
        self.assertEqual(result["error"]["cue_index"], 1)

    def test_parse_error_minutes_out_of_range(self) -> None:
        result = self.tool.execute(
            mode="parse", text="1\n00:60:00,000 --> 00:01:00,000\nT\n"
        )
        self.assertEqual(result["error"]["type"], "invalid_timestamp")
        self.assertEqual(result["error"]["cue_position"], 1)
        self.assertEqual(result["error"]["cue_index"], 1)
        self.assertIn("out-of-range", result["error"]["message"])

    def test_parse_error_seconds_out_of_range(self) -> None:
        result = self.tool.execute(
            mode="parse", text="1\n00:00:61,500 --> 00:01:00,000\nT\n"
        )
        self.assertEqual(result["error"]["type"], "invalid_timestamp")

    def test_parse_error_three_digit_hours(self) -> None:
        result = self.tool.execute(
            mode="parse", text="1\n100:00:00,000 --> 100:00:01,000\nT\n"
        )
        self.assertEqual(result["error"]["type"], "invalid_timestamp")
        self.assertIn("malformed", result["error"]["message"])

    def test_parse_error_bad_millisecond_separator(self) -> None:
        result = self.tool.execute(
            mode="parse", text="1\n00:00:01;500 --> 00:00:02,000\nT\n"
        )
        self.assertEqual(result["error"]["type"], "invalid_timestamp")

    def test_parse_error_end_before_start(self) -> None:
        result = self.tool.execute(
            mode="parse", text="1\n00:00:05,000 --> 00:00:04,000\nT\n"
        )
        self.assertEqual(result["error"]["type"], "end_before_start")
        self.assertEqual(result["error"]["cue_position"], 1)
        self.assertEqual(result["error"]["cue_index"], 1)
        self.assertIn("ends before it starts", result["error"]["message"])

    def test_parse_error_reports_position_of_second_cue(self) -> None:
        # The first cue is fine; the malformed one is at position 2
        # and claims number 7.
        result = self.tool.execute(
            mode="parse",
            text="1\n00:00:01,000 --> 00:00:02,000\nA\n"
            "\n7\nnope\nB",
        )
        self.assertEqual(result["error"]["type"], "missing_timing_line")
        self.assertEqual(result["error"]["cue_position"], 2)
        self.assertEqual(result["error"]["cue_index"], 7)

    def test_renumber_and_stats_share_parse_errors(self) -> None:
        for mode in ("renumber", "stats"):
            result = self.tool.execute(
                mode=mode, text="1\n00:00:09,000 --> 00:00:08,000\nT\n"
            )
            self.assertEqual(result["mode"], mode)
            self.assertEqual(result["error"]["type"], "end_before_start")

    # ------------------------------------------------------------------ #
    # Parameter validation (ValueError before any computation)
    # ------------------------------------------------------------------ #

    def test_invalid_mode_rejected(self) -> None:
        for mode in (None, "validate", "PARSE", 1):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, text=SAMPLE)

    def test_invalid_text_types_rejected(self) -> None:
        for text in (None, 123, True, ["1"], b"1\n"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="parse", text=text)

    def test_invalid_empty_or_whitespace_text_rejected(self) -> None:
        for text in ("", "   ", "\n\n", "\r\n \t\n"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="parse", text=text)

    def test_invalid_oversized_text_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="parse", text="x" * 1_000_001)
        self.assertIn("1,000,000", str(ctx.exception))

    def test_invalid_cue_count_over_cap_rejected(self) -> None:
        cues = "\n\n".join(
            f"{i}\n00:00:01,000 --> 00:00:02,000\nCue {i}"
            for i in range(1, 10_002)
        )
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="parse", text=cues)
        self.assertIn("10,000", str(ctx.exception))

    def test_cue_count_exactly_at_cap_accepted(self) -> None:
        cues = "\n\n".join(
            f"{i}\n00:00:01,000 --> 00:00:02,000\nCue {i}"
            for i in range(1, 10_001)
        )
        result = self.tool.execute(mode="parse", text=cues)
        self.assertEqual(result["cue_count"], 10_000)
        self.assertEqual(result["warnings"], [])

    def test_invalid_milliseconds_rejected(self) -> None:
        for milliseconds in (None, "500", 1.5, True, [500]):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="shift", text=SAMPLE, milliseconds=milliseconds
                )

    def test_invalid_milliseconds_magnitude_rejected(self) -> None:
        for milliseconds in (360_000_000, -360_000_000, 10**12):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="shift", text=SAMPLE, milliseconds=milliseconds
                )


if __name__ == "__main__":
    unittest.main()
