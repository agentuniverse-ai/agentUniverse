#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_chunk_overlap_tool.py

"""Offline unit tests for ChunkOverlapTool.

The tool is built purely on the standard library (no network, no
third-party package), so this suite runs fully offline. Every
assertion is a pinned literal, hand-computed from the documented
definitions:

* textual overlap — the largest k with chunk[i][-k:] == chunk[i+1][:k];
* positional adjacency — greedy-sequential location (first occurrence
  at or after previous start + 1), then contiguous (start == previous
  end) / overlapping (start < end) / gapped (start > end);
* coverage — the union of the located spans over the source; missing
  spans are the complement; duplicated regions are the source regions
  where two or more located spans intersect (touching spans are NOT
  duplicated);
* offsets are Python str code-point indices (one CJK ideograph = 1).

The worked sliding-window example used throughout:

    source   "0123456789"  (10 chars), window 4 / overlap 2 / step 2
    chunks   "0123" "2345" "4567" "6789"        spans (0,4) (2,6) (4,8) (6,10)

    sizes    [4, 4, 4, 4]  min 4 / mean 4.0 / median 4 / max 4 / total 16
    textual  3 pairs, every overlap "23"/"45"/"67" -> 2 chars
    position every consecutive pair overlaps 2 chars; union (0, 10)
             -> covered 10/10 = 1.0; duplicated depth-2 region [2, 8)
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import ChunkOverlapTool
from agentuniverse.agent.action.tool.common_tool.chunk_overlap_tool import (
    ChunkOverlapTool as DirectChunkOverlapTool,
)

SOURCE = "0123456789"


def sliding_window(text: str, size: int, overlap: int) -> list:
    """A simulated sliding-window splitter — the tool under inspection
    never splits anything itself, so the tests build chunk lists with
    this reference splitter (or by hand for the bug-shaped cases)."""
    step = size - overlap
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            break
        start += step
    return chunks


WINDOW_CHUNKS = sliding_window(SOURCE, 4, 2)


class AnalyzeSlidingWindowTest(unittest.TestCase):
    """analyze mode over a known-good sliding-window result."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_sizes_arithmetic(self) -> None:
        result = self.tool.execute(
            mode="analyze", chunks=WINDOW_CHUNKS, source_text=SOURCE
        )
        self.assertEqual(
            result["sizes"],
            {"min": 4, "mean": 4.0, "median": 4, "max": 4, "total": 16},
        )
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["source_chars"], 10)

    def test_textual_overlap_stats(self) -> None:
        result = self.tool.execute(
            mode="analyze", chunks=WINDOW_CHUNKS, source_text=SOURCE
        )
        self.assertEqual(
            result["overlap_stats"],
            {
                "pairs": 3,
                "pairs_with_overlap": 3,
                "max_overlap_chars": 2,
                "mean_overlap_chars": 2.0,
                "scan_cap": 10000,
                "scan_cap_reached": False,
            },
        )

    def test_positional_adjacency_overlapping(self) -> None:
        adjacency = self.tool.execute(
            mode="analyze", chunks=WINDOW_CHUNKS, source_text=SOURCE
        )["adjacency"]
        self.assertEqual(adjacency["pairs"], 3)
        self.assertEqual(adjacency["overlapping_pairs"], 3)
        self.assertEqual(adjacency["contiguous_pairs"], 0)
        self.assertEqual(adjacency["gapped_pairs"], 0)
        self.assertEqual(adjacency["unlocated_pairs"], 0)
        self.assertEqual(adjacency["max_overlap_chars"], 2)
        self.assertEqual(adjacency["max_gap_chars"], 0)
        self.assertEqual(
            adjacency["pairs_detail"][0],
            {
                "pair": [0, 1],
                "first": [0, 4],
                "second": [2, 6],
                "chars": 2,
                "type": "overlapping",
            },
        )
        self.assertFalse(adjacency["detail_truncated"])

    def test_full_coverage(self) -> None:
        coverage = self.tool.execute(
            mode="analyze", chunks=WINDOW_CHUNKS, source_text=SOURCE
        )["coverage"]
        self.assertEqual(coverage["source_chars"], 10)
        self.assertEqual(coverage["covered_chars"], 10)
        self.assertEqual(coverage["covered_ratio"], 1.0)
        self.assertEqual(coverage["missing_span_count"], 0)
        self.assertEqual(coverage["missing_spans"], [])
        self.assertFalse(coverage["missing_spans_truncated"])

    def test_duplicated_region_from_window_overlap(self) -> None:
        duplicated = self.tool.execute(
            mode="analyze", chunks=WINDOW_CHUNKS, source_text=SOURCE
        )["coverage"]["duplicated_regions"]
        self.assertEqual(duplicated["region_count"], 1)
        self.assertEqual(duplicated["total_chars"], 6)
        self.assertEqual(
            duplicated["regions"],
            [
                {
                    "start": 2,
                    "end": 8,
                    "chars": 6,
                    "preview": "234567",
                }
            ],
        )
        self.assertFalse(duplicated["truncated"])


class SizeStatisticsTest(unittest.TestCase):
    """analyze-mode size statistics — pinned arithmetic."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_odd_median_is_int(self) -> None:
        sizes = self.tool.execute(
            mode="analyze", chunks=["abc", "ab", "abcd", "a", "ab"]
        )["sizes"]
        self.assertEqual(
            sizes,
            {"min": 1, "mean": 2.4, "median": 2, "max": 4, "total": 12},
        )

    def test_even_median_is_mean_of_middles(self) -> None:
        sizes = self.tool.execute(
            mode="analyze", chunks=["abc", "ab", "a", "abcd"]
        )["sizes"]
        self.assertEqual(
            sizes,
            {"min": 1, "mean": 2.5, "median": 2.5, "max": 4, "total": 10},
        )

    def test_mean_rounding(self) -> None:
        sizes = self.tool.execute(
            mode="analyze", chunks=["a", "a", "aa"]
        )["sizes"]
        self.assertEqual(sizes["mean"], 1.3333)
        self.assertEqual(sizes["median"], 1)


class AdjacencyClassificationTest(unittest.TestCase):
    """contiguous vs overlapping vs gapped vs unlocated — by hand."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_contiguous(self) -> None:
        adjacency = self.tool.execute(
            mode="analyze", chunks=["abc", "def"], source_text="abcdef"
        )["adjacency"]
        self.assertEqual(adjacency["contiguous_pairs"], 1)
        self.assertEqual(adjacency["overlapping_pairs"], 0)
        self.assertEqual(adjacency["gapped_pairs"], 0)
        self.assertEqual(adjacency["pairs_detail"][0]["type"], "contiguous")
        self.assertNotIn("chars", adjacency["pairs_detail"][0])

    def test_gapped_with_exact_missing_span(self) -> None:
        result = self.tool.execute(
            mode="analyze", chunks=["abcd", "hij"], source_text="abcdefghij"
        )
        adjacency = result["adjacency"]
        self.assertEqual(adjacency["gapped_pairs"], 1)
        self.assertEqual(adjacency["max_gap_chars"], 3)
        self.assertEqual(adjacency["pairs_detail"][0]["chars"], 3)
        coverage = result["coverage"]
        self.assertEqual(coverage["covered_chars"], 7)
        self.assertEqual(coverage["covered_ratio"], 0.7)
        self.assertEqual(
            coverage["missing_spans"],
            [{"start": 4, "end": 7, "chars": 3, "preview": "efg"}],
        )

    def test_textual_overlap_with_contiguous_spans(self) -> None:
        # The two overlap notions are distinct and this is the telling
        # case: the spans are CONTIGUOUS (positional overlap 0) yet the
        # chunk texts share "cd" — textual overlap 2. (The converse is
        # impossible for located spans: an overlapping region is the
        # same substring on both sides, so positional overlap always
        # implies an equal textual overlap.)
        result = self.tool.execute(
            mode="analyze", chunks=["abcd", "cdef"], source_text="abcdcdef"
        )
        self.assertEqual(result["adjacency"]["contiguous_pairs"], 1)
        self.assertEqual(result["adjacency"]["max_overlap_chars"], 0)
        self.assertEqual(result["overlap_stats"]["max_overlap_chars"], 2)
        self.assertEqual(result["overlap_stats"]["pairs_with_overlap"], 1)

    def test_unlocated_when_chunk_absent_from_source(self) -> None:
        adjacency = self.tool.execute(
            mode="analyze", chunks=["abc", "zzz"], source_text="abcdef"
        )["adjacency"]
        self.assertEqual(adjacency["unlocated_pairs"], 1)
        self.assertEqual(adjacency["pairs_detail"][0]["type"], "unlocated")
        self.assertEqual(adjacency["pairs_detail"][0]["first"], [0, 3])

    def test_no_source_means_no_adjacency(self) -> None:
        result = self.tool.execute(mode="analyze", chunks=["abc", "bcd"])
        self.assertIsNone(result["adjacency"])
        self.assertIsNone(result["coverage"])
        self.assertNotIn("source_chars", result)

    def test_greedy_location_order_is_pinned(self) -> None:
        # chunk 1 ("bc") is located at the first occurrence at or after
        # previous start + 1 -> position 1, not the later "bc".
        result = self.tool.execute(
            mode="analyze", chunks=["abc", "bc"], source_text="abcabc"
        )
        self.assertEqual(result["adjacency"]["overlapping_pairs"], 1)
        self.assertEqual(result["coverage"]["covered_ratio"], 0.5)
        duplicated = result["coverage"]["duplicated_regions"]
        self.assertEqual(duplicated["total_chars"], 2)


class CoverageSemanticsTest(unittest.TestCase):
    """coverage conventions — union, duplicates, empty inputs."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_duplicated_chunk_text_locates_once_only(self) -> None:
        # Two identical chunks over a source with two occurrences chain
        # contiguously; over a source with one occurrence the second
        # copy stays unlocated (reported, never guessed).
        chained = self.tool.execute(
            mode="analyze", chunks=["abc", "abc"], source_text="abcabc"
        )
        self.assertEqual(chained["adjacency"]["contiguous_pairs"], 1)
        self.assertEqual(chained["coverage"]["covered_ratio"], 1.0)
        self.assertEqual(
            chained["coverage"]["duplicated_regions"]["region_count"], 0
        )
        single = self.tool.execute(
            mode="analyze", chunks=["abc", "abc"], source_text="abc"
        )
        self.assertEqual(single["adjacency"]["unlocated_pairs"], 1)
        self.assertEqual(single["coverage"]["covered_ratio"], 1.0)

    def test_empty_chunk_list_reports_everything_missing(self) -> None:
        result = self.tool.execute(
            mode="analyze", chunks=[], source_text="abc"
        )
        self.assertEqual(result["count"], 0)
        self.assertEqual(
            result["sizes"],
            {
                "min": None,
                "mean": None,
                "median": None,
                "max": None,
                "total": 0,
            },
        )
        self.assertEqual(result["overlap_stats"]["pairs"], 0)
        self.assertEqual(result["adjacency"]["pairs"], 0)
        coverage = result["coverage"]
        self.assertEqual(coverage["covered_ratio"], 0.0)
        self.assertEqual(
            coverage["missing_spans"],
            [{"start": 0, "end": 3, "chars": 3, "preview": "abc"}],
        )

    def test_empty_chunk_list_without_source(self) -> None:
        result = self.tool.execute(mode="analyze", chunks=[])
        self.assertEqual(result["count"], 0)
        self.assertIsNone(result["adjacency"])
        self.assertIsNone(result["coverage"])
        self.assertEqual(result["overlap_stats"]["mean_overlap_chars"], 0.0)

    def test_empty_chunk_string_conventions(self) -> None:
        result = self.tool.execute(
            mode="analyze", chunks=["", "ab"], source_text="ab"
        )
        self.assertEqual(result["sizes"]["min"], 0)
        self.assertEqual(result["sizes"]["total"], 2)
        self.assertEqual(result["adjacency"]["unlocated_pairs"], 1)
        self.assertEqual(result["coverage"]["covered_ratio"], 1.0)

    def test_empty_source_convention(self) -> None:
        result = self.tool.execute(
            mode="analyze", chunks=["a"], source_text=""
        )
        self.assertEqual(result["coverage"]["covered_ratio"], 0.0)
        self.assertEqual(result["coverage"]["missing_span_count"], 0)
        self.assertEqual(result["adjacency"]["pairs"], 0)

    def test_missing_spans_capped_at_twenty(self) -> None:
        source = "".join(chr(65 + i) for i in range(42))  # 42 distinct chars
        chunks = [source[i] for i in range(0, 42, 2)]  # every other char
        coverage = self.tool.execute(
            mode="analyze", chunks=chunks, source_text=source
        )["coverage"]
        self.assertEqual(coverage["missing_span_count"], 21)
        self.assertEqual(len(coverage["missing_spans"]), 20)
        self.assertTrue(coverage["missing_spans_truncated"])
        self.assertEqual(
            coverage["missing_spans"][0],
            {"start": 1, "end": 2, "chars": 1, "preview": "B"},
        )

    def test_duplicated_regions_capped_at_twenty(self) -> None:
        # 22 separate 2-char duplicated regions, CJK source so every
        # offset is also a code-point offset proof.
        source = "".join(chr(0x4E00 + i) for i in range(230))
        chunks = []
        for k in range(0, 220, 10):
            chunks.append(source[k:k + 4])
            chunks.append(source[k + 2:k + 6])
        duplicated = self.tool.execute(
            mode="analyze", chunks=chunks, source_text=source
        )["coverage"]["duplicated_regions"]
        self.assertEqual(duplicated["region_count"], 22)
        self.assertEqual(duplicated["total_chars"], 44)
        self.assertEqual(len(duplicated["regions"]), 20)
        self.assertTrue(duplicated["truncated"])
        self.assertEqual(
            duplicated["regions"][0],
            {"start": 2, "end": 4, "chars": 2, "preview": source[2:4]},
        )


class CoverageModeDetailTest(unittest.TestCase):
    """coverage mode — per-chunk positions and the source heatmap."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_per_chunk_positions_and_span(self) -> None:
        result = self.tool.execute(
            mode="coverage", chunks=["abc"], source_text="abcabcabc"
        )
        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(result["source_chars"], 9)
        self.assertEqual(
            result["per_chunk"],
            [
                {
                    "index": 0,
                    "chars": 3,
                    "found": True,
                    "positions": [0, 3, 6],
                    "position_count": 3,
                    "positions_truncated": False,
                    "span": [0, 3],
                }
            ],
        )

    def test_positions_capped_at_hundred(self) -> None:
        result = self.tool.execute(
            mode="coverage", chunks=["ab"], source_text="ab" * 300
        )
        entry = result["per_chunk"][0]
        self.assertEqual(entry["position_count"], 300)
        self.assertEqual(len(entry["positions"]), 100)
        self.assertEqual(entry["positions"][:3], [0, 2, 4])
        self.assertTrue(entry["positions_truncated"])

    def test_chunk_not_found_detail(self) -> None:
        result = self.tool.execute(
            mode="coverage", chunks=["zzz"], source_text="abcdef"
        )
        self.assertEqual(
            result["per_chunk"][0],
            {
                "index": 0,
                "chars": 3,
                "found": False,
                "positions": [],
                "position_count": 0,
                "positions_truncated": False,
                "span": None,
            },
        )

    def test_heatmap_buckets(self) -> None:
        result = self.tool.execute(
            mode="coverage", chunks=["a" * 100], source_text="a" * 250
        )
        heatmap = result["heatmap"]
        self.assertEqual(heatmap["bucket_chars"], 100)
        self.assertEqual(heatmap["bucket_count"], 3)
        self.assertEqual(heatmap["fully_covered_buckets"], 1)
        self.assertEqual(heatmap["partially_covered_buckets"], 0)
        self.assertEqual(heatmap["uncovered_buckets"], 2)
        self.assertEqual(
            heatmap["buckets"],
            [
                {"start": 0, "end": 100, "covered_ratio": 1.0},
                {"start": 100, "end": 200, "covered_ratio": 0.0},
                {"start": 200, "end": 250, "covered_ratio": 0.0},
            ],
        )
        self.assertFalse(heatmap["truncated"])
        self.assertEqual(result["coverage"]["covered_ratio"], 0.4)

    def test_heatmap_partial_bucket(self) -> None:
        result = self.tool.execute(
            mode="coverage", chunks=["a" * 150], source_text="a" * 250
        )
        heatmap = result["heatmap"]
        self.assertEqual(heatmap["fully_covered_buckets"], 1)
        self.assertEqual(heatmap["partially_covered_buckets"], 1)
        self.assertEqual(heatmap["uncovered_buckets"], 1)
        self.assertEqual(heatmap["buckets"][1]["covered_ratio"], 0.5)

    def test_heatmap_ratio_rounding(self) -> None:
        result = self.tool.execute(
            mode="coverage", chunks=["abc"], source_text="abcabcabc"
        )
        first_bucket = result["heatmap"]["buckets"][0]
        self.assertEqual(first_bucket["covered_ratio"], 0.3333)


class OverlapMatrixTest(unittest.TestCase):
    """overlap_matrix mode — pairwise suffix/prefix overlaps."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()
        self.chunks = ["hello world", "world peace", "peace treaty"]

    def test_consecutive_window_default(self) -> None:
        result = self.tool.execute(mode="overlap_matrix", chunks=self.chunks)
        self.assertEqual(result["window"], 1)
        self.assertEqual(result["pairs_checked"], 2)
        self.assertEqual(result["pairs_with_overlap"], 2)
        self.assertEqual(result["max_overlap_chars"], 5)
        self.assertEqual(result["mean_overlap_chars"], 5.0)
        self.assertEqual(
            result["overlaps"],
            [
                {"i": 0, "j": 1, "chars": 5, "overlap_text": "world"},
                {"i": 1, "j": 2, "chars": 5, "overlap_text": "peace"},
            ],
        )

    def test_window_two_adds_the_far_pair(self) -> None:
        result = self.tool.execute(
            mode="overlap_matrix", chunks=self.chunks, window=2
        )
        self.assertEqual(result["pairs_checked"], 3)
        self.assertEqual(result["pairs_with_overlap"], 2)
        self.assertEqual(result["mean_overlap_chars"], 3.3333)
        self.assertEqual(len(result["overlaps"]), 2)

    def test_directional_single_char_overlap(self) -> None:
        result = self.tool.execute(
            mode="overlap_matrix", chunks=["abcd", "dcba"]
        )
        self.assertEqual(
            result["overlaps"],
            [{"i": 0, "j": 1, "chars": 1, "overlap_text": "d"}],
        )

    def test_no_overlap_reports_empty_entries(self) -> None:
        result = self.tool.execute(
            mode="overlap_matrix", chunks=["abc", "xyz"]
        )
        self.assertEqual(result["pairs_checked"], 1)
        self.assertEqual(result["pairs_with_overlap"], 0)
        self.assertEqual(result["overlaps"], [])
        self.assertEqual(result["mean_overlap_chars"], 0.0)

    def test_single_chunk_and_empty_list(self) -> None:
        single = self.tool.execute(mode="overlap_matrix", chunks=["abc"])
        self.assertEqual(single["chunk_count"], 1)
        self.assertEqual(single["pairs_checked"], 0)
        empty = self.tool.execute(mode="overlap_matrix", chunks=[])
        self.assertEqual(empty["chunk_count"], 0)
        self.assertEqual(empty["overlaps"], [])

    def test_scan_cap_flag_and_preview(self) -> None:
        # Both chunks exceed the 10,000-char scan cap and genuinely
        # share 10,000 characters (found at the cap on the first try).
        result = self.tool.execute(
            mode="overlap_matrix",
            chunks=["b" + "a" * 10001, "a" * 10001],
        )
        self.assertTrue(result["scan_cap_reached"])
        self.assertEqual(result["max_overlap_chars"], 10000)
        self.assertEqual(result["overlaps"][0]["chars"], 10000)
        self.assertEqual(result["overlaps"][0]["overlap_text"], "a" * 40)

    def test_scan_cap_with_no_match(self) -> None:
        result = self.tool.execute(
            mode="overlap_matrix", chunks=["a" * 10005, "b" * 10005]
        )
        self.assertTrue(result["scan_cap_reached"])
        self.assertEqual(result["pairs_with_overlap"], 0)


class ValidateModeTest(unittest.TestCase):
    """validate mode — per-rule pass/fail with offending indices."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_min_chars_pass_and_fail(self) -> None:
        ok = self.tool.execute(
            mode="validate", chunks=WINDOW_CHUNKS, policy={"min_chars": 4}
        )["rules"][0]
        self.assertTrue(ok["pass"])
        self.assertEqual(ok["violations"], 0)
        bad = self.tool.execute(
            mode="validate",
            chunks=["abc", "ab", "a"],
            policy={"min_chars": 2},
        )["rules"][0]
        self.assertFalse(bad["pass"])
        self.assertEqual(bad["violations"], 1)
        self.assertEqual(bad["offending_indices"], [2])

    def test_max_chars(self) -> None:
        bad = self.tool.execute(
            mode="validate",
            chunks=["abc", "a", "abcdef"],
            policy={"max_chars": 3},
        )["rules"][0]
        self.assertFalse(bad["pass"])
        self.assertEqual(bad["offending_indices"], [2])

    def test_max_overlap_offending_pairs(self) -> None:
        bad = self.tool.execute(
            mode="validate", chunks=WINDOW_CHUNKS, policy={"max_overlap": 1}
        )["rules"][0]
        self.assertFalse(bad["pass"])
        self.assertEqual(bad["violations"], 3)
        self.assertEqual(
            bad["offending_pairs"], [[0, 1], [1, 2], [2, 3]]
        )
        ok = self.tool.execute(
            mode="validate", chunks=WINDOW_CHUNKS, policy={"max_overlap": 2}
        )["rules"][0]
        self.assertTrue(ok["pass"])

    def test_min_coverage_pass_and_fail(self) -> None:
        ok = self.tool.execute(
            mode="validate",
            chunks=["abcd", "hij"],
            source_text="abcdefghij",
            policy={"min_coverage": 0.7},
        )["rules"][0]
        self.assertTrue(ok["pass"])
        self.assertEqual(ok["covered_ratio"], 0.7)
        bad = self.tool.execute(
            mode="validate",
            chunks=["abcd", "hij"],
            source_text="abcdefghij",
            policy={"min_coverage": 0.8},
        )["rules"][0]
        self.assertFalse(bad["pass"])

    def test_full_policy_matrix_with_all_pass(self) -> None:
        result = self.tool.execute(
            mode="validate",
            chunks=WINDOW_CHUNKS,
            source_text=SOURCE,
            policy={
                "min_chars": 4,
                "max_chars": 4,
                "max_overlap": 2,
                "min_coverage": 1.0,
            },
        )
        self.assertEqual(len(result["rules"]), 4)
        self.assertTrue(result["all_pass"])
        self.assertEqual(
            [rule["rule"] for rule in result["rules"]],
            ["min_chars", "max_chars", "max_overlap", "min_coverage"],
        )

    def test_one_failing_rule_flips_all_pass(self) -> None:
        result = self.tool.execute(
            mode="validate",
            chunks=WINDOW_CHUNKS,
            source_text=SOURCE,
            policy={"min_chars": 5, "min_coverage": 1.0},
        )
        self.assertEqual(len(result["rules"]), 2)
        self.assertFalse(result["rules"][0]["pass"])
        self.assertTrue(result["rules"][1]["pass"])
        self.assertFalse(result["all_pass"])

    def test_empty_chunk_list_vacuous_pass_and_coverage_fail(self) -> None:
        vacuous = self.tool.execute(
            mode="validate", chunks=[], policy={"min_chars": 1}
        )["rules"][0]
        self.assertTrue(vacuous["pass"])
        self.assertEqual(vacuous["violations"], 0)
        failing = self.tool.execute(
            mode="validate",
            chunks=[],
            source_text="abc",
            policy={"min_coverage": 0.5},
        )["rules"][0]
        self.assertFalse(failing["pass"])
        self.assertEqual(failing["covered_ratio"], 0.0)

    def test_offending_indices_capped_at_hundred(self) -> None:
        rule = self.tool.execute(
            mode="validate", chunks=[""] * 105, policy={"min_chars": 1}
        )["rules"][0]
        self.assertEqual(rule["violations"], 105)
        self.assertEqual(len(rule["offending_indices"]), 100)
        self.assertTrue(rule["offending_truncated"])

    def test_source_allowed_without_min_coverage(self) -> None:
        result = self.tool.execute(
            mode="validate",
            chunks=["abc"],
            source_text="abc",
            policy={"min_chars": 1},
        )
        self.assertTrue(result["all_pass"])


class CjkOffsetSafetyTest(unittest.TestCase):
    """offsets are code-point indices — one CJK ideograph = 1 char."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_cjk_sliding_window_offsets(self) -> None:
        source = "汉字测试文本数据"  # 8 ideographs
        chunks = sliding_window(source, 4, 2)
        self.assertEqual(
            chunks, ["汉字测试", "测试文本", "文本数据"]
        )
        result = self.tool.execute(
            mode="analyze", chunks=chunks, source_text=source
        )
        self.assertEqual(result["coverage"]["covered_ratio"], 1.0)
        self.assertEqual(
            result["coverage"]["duplicated_regions"]["regions"][0],
            {"start": 2, "end": 6, "chars": 4, "preview": "测试文本"},
        )
        self.assertEqual(result["overlap_stats"]["max_overlap_chars"], 2)

    def test_cjk_offset_not_byte_offset(self) -> None:
        # "汉字" sits at code-point offset 1 (a byte offset would say 4).
        result = self.tool.execute(
            mode="coverage", chunks=["汉字"], source_text="a汉字b"
        )
        self.assertEqual(result["per_chunk"][0]["positions"], [1])
        self.assertEqual(result["per_chunk"][0]["span"], [1, 3])

    def test_cjk_missing_span(self) -> None:
        result = self.tool.execute(
            mode="analyze",
            chunks=["汉字测试", "数据"],
            source_text="汉字测试文本数据",
        )
        self.assertEqual(
            result["coverage"]["missing_spans"],
            [{"start": 4, "end": 6, "chars": 2, "preview": "文本"}],
        )


class EmptyAndBoundaryTest(unittest.TestCase):
    """documented null conventions and caps."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def test_adjacency_detail_capped(self) -> None:
        source = "".join(str(i % 10) for i in range(210))
        chunks = list(source)  # 210 single-char chunks, all contiguous
        adjacency = self.tool.execute(
            mode="analyze", chunks=chunks, source_text=source
        )["adjacency"]
        self.assertEqual(adjacency["contiguous_pairs"], 209)
        self.assertEqual(len(adjacency["pairs_detail"]), 100)
        self.assertTrue(adjacency["detail_truncated"])

    def test_single_chunk_has_no_pairs(self) -> None:
        result = self.tool.execute(
            mode="analyze", chunks=["abc"], source_text="abc"
        )
        self.assertEqual(result["overlap_stats"]["pairs"], 0)
        self.assertEqual(result["adjacency"]["pairs"], 0)
        self.assertEqual(result["coverage"]["covered_ratio"], 1.0)

    def test_determinism(self) -> None:
        first = self.tool.execute(
            mode="analyze", chunks=WINDOW_CHUNKS, source_text=SOURCE
        )
        second = self.tool.execute(
            mode="analyze", chunks=WINDOW_CHUNKS, source_text=SOURCE
        )
        self.assertEqual(first, second)


class ErrorMatrixTest(unittest.TestCase):
    """every malformed input raises ValueError before any computation."""

    def setUp(self) -> None:
        self.tool = ChunkOverlapTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode(self) -> None:
        self.assert_invalid(mode="frobnicate", chunks=["a"])
        self.assert_invalid(mode=None, chunks=["a"])

    def test_chunks_not_a_list_or_bad_members(self) -> None:
        self.assert_invalid(mode="analyze", chunks="abc")
        self.assert_invalid(mode="analyze", chunks={"0": "a"})
        self.assert_invalid(mode="analyze", chunks=["a", 3])
        self.assert_invalid(mode="analyze", chunks=["a", None])
        self.assert_invalid(mode="analyze", chunks=[True])
        self.assert_invalid(mode="analyze", chunks=[["a"]])

    def test_chunks_caps(self) -> None:
        self.assert_invalid(mode="analyze", chunks=["a"] * 10_001)
        self.assert_invalid(mode="analyze", chunks=["a" * 10_000_001])

    def test_source_validation(self) -> None:
        self.assert_invalid(mode="analyze", chunks=["a"], source_text=123)
        self.assert_invalid(mode="analyze", chunks=["a"], source_text=["ab"])
        self.assert_invalid(
            mode="analyze", chunks=["a"], source_text="a" * 10_000_001
        )

    def test_window_validation(self) -> None:
        base = {"mode": "overlap_matrix", "chunks": ["abc", "bcd"]}
        self.assert_invalid(**base, window=0)
        self.assert_invalid(**base, window=-1)
        self.assert_invalid(**base, window=101)
        self.assert_invalid(**base, window=True)
        self.assert_invalid(**base, window=1.5)
        self.assert_invalid(**base, window="1")

    def test_window_pair_budget(self) -> None:
        # 2500 chunks x window 100 -> (2500-100)*100 + 100*99/2
        # = 244,950 pairs > 200,000.
        self.assert_invalid(
            mode="overlap_matrix", chunks=["a"] * 2500, window=100
        )

    def test_policy_shape(self) -> None:
        base = {"mode": "validate", "chunks": ["abc"]}
        self.assert_invalid(**base, policy="min_chars")
        self.assert_invalid(**base, policy=[])
        self.assert_invalid(**base, policy={})
        self.assert_invalid(**base, policy={"min_len": 1})

    def test_policy_values(self) -> None:
        base = {"mode": "validate", "chunks": ["abc"]}
        self.assert_invalid(**base, policy={"min_chars": "3"})
        self.assert_invalid(**base, policy={"min_chars": -1})
        self.assert_invalid(**base, policy={"min_chars": True})
        self.assert_invalid(**base, policy={"min_chars": 1.5})
        self.assert_invalid(**base, policy={"max_chars": 0})
        self.assert_invalid(**base, policy={"max_overlap": -1})
        self.assert_invalid(**base, policy={"min_chars": 5, "max_chars": 4})
        self.assert_invalid(**base, policy={"min_coverage": 1.5})
        self.assert_invalid(**base, policy={"min_coverage": -0.1})
        self.assert_invalid(**base, policy={"min_coverage": "0.5"})
        self.assert_invalid(**base, policy={"min_coverage": True})

    def test_min_coverage_requires_source(self) -> None:
        self.assert_invalid(
            mode="validate", chunks=["abc"], policy={"min_coverage": 0.5}
        )

    def test_mode_parameter_mismatches(self) -> None:
        self.assert_invalid(mode="analyze", chunks=["a"], window=1)
        self.assert_invalid(
            mode="analyze", chunks=["a"], policy={"min_chars": 1}
        )
        self.assert_invalid(mode="coverage", chunks=["a"])  # no source
        self.assert_invalid(
            mode="coverage", chunks=["a"], source_text="a", window=1
        )
        self.assert_invalid(
            mode="coverage",
            chunks=["a"],
            source_text="a",
            policy={"min_chars": 1},
        )
        self.assert_invalid(
            mode="overlap_matrix", chunks=["a"], source_text="a"
        )
        self.assert_invalid(
            mode="overlap_matrix", chunks=["a"], policy={"min_chars": 1}
        )
        self.assert_invalid(
            mode="validate", chunks=["a"], policy={"min_chars": 1}, window=1
        )

    def test_error_message_prefix(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="nope", chunks=["a"])
        self.assertTrue(str(ctx.exception).startswith("chunk_overlap_tool:"))


class ToolSurfaceTest(unittest.TestCase):
    """registration, metadata and the yaml-backed surface."""

    def test_export_from_package_init(self) -> None:
        self.assertIs(DirectChunkOverlapTool, ChunkOverlapTool)

    def test_instance_attributes(self) -> None:
        tool = ChunkOverlapTool()
        self.assertEqual(tool.name, "chunk_overlap_tool")
        self.assertIn("Chunking QA tool", tool.description)

    def test_class_level_constants(self) -> None:
        self.assertEqual(
            ChunkOverlapTool.MODES,
            ("analyze", "coverage", "overlap_matrix", "validate"),
        )
        self.assertEqual(ChunkOverlapTool.MAX_CHUNKS, 10_000)
        self.assertEqual(ChunkOverlapTool.MAX_SOURCE_CHARS, 10_000_000)
        self.assertEqual(ChunkOverlapTool.BUCKET_CHARS, 100)

    def test_description_mentions_companion_tools(self) -> None:
        description = ChunkOverlapTool().description
        self.assertIn("TextChunkerTool", description)
        self.assertIn("CREATE chunks", description)
        self.assertIn("this tool checks them", description)

    def test_execute_signature_accepts_keyword_args(self) -> None:
        tool = ChunkOverlapTool()
        result = tool.execute(
            mode="analyze", chunks=["abc"], source_text="abc"
        )
        self.assertEqual(result["mode"], "analyze")


if __name__ == "__main__":
    unittest.main()
