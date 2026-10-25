#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_jaro_winkler_tool.py

"""Offline unit tests for JaroWinklerTool.

The tool is built purely on the standard library (no network, no
third-party similarity package), so this suite runs fully offline.
Every assertion is deterministic: the scores below are pinned literals
cross-checked against the published Jaro / Jaro-Winkler reference
vectors (MARTHA/MARHTA 0.9444 & 0.9611, DIXON/DICKSONX 0.7667 &
0.8133, DWAYNE/DUANE 0.8222 & 0.8400) and values recomputed with the
standard algorithm as defined by Jaro (1989) and Winkler (1990)
(match window floor(max(len)/2) - 1, transpositions counted as half
the out-of-order matched characters, prefix boost l * p * (1 - jaro)
with l capped at 4 and p = 0.1, applied only when jaro > 0.7). The
remaining constants — JONES/JOHNSON 0.7905 & 0.8324, the match-window
edges, the transposition counts, the cluster transitivity chain and
every validation error — were computed / derived from that same
standard algorithm and pinned here.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import JaroWinklerTool
from agentuniverse.agent.action.tool.common_tool.jaro_winkler_tool import (
    JaroWinklerTool as DirectJaroWinklerTool,
)


class JaroSimilarityTest(unittest.TestCase):
    """similarity mode — published vectors, counts and conventions."""

    def setUp(self) -> None:
        self.tool = JaroWinklerTool()

    def test_published_vector_martha_marhta(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="similarity", text_a="MARTHA", text_b="MARHTA"),
            {
                "mode": "similarity",
                "text_a": "MARTHA",
                "text_b": "MARHTA",
                "jaro": 0.9444,
                "jaro_winkler": 0.9611,
            },
        )

    def test_published_vector_dixon_dicksonx(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="DIXON", text_b="DICKSONX"
        )
        self.assertEqual(result["jaro"], 0.7667)
        self.assertEqual(result["jaro_winkler"], 0.8133)

    def test_published_vector_dwayne_duane(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="DWAYNE", text_b="DUANE"
        )
        self.assertEqual(result["jaro"], 0.8222)
        self.assertEqual(result["jaro_winkler"], 0.84)

    def test_jones_johnson_recomputed(self) -> None:
        # jaro 0.7905 agrees with the published value; jaro_winkler is
        # recomputed from the standard algorithm and pinned.
        result = self.tool.execute(
            mode="similarity", text_a="JONES", text_b="JOHNSON"
        )
        self.assertEqual(result["jaro"], 0.7905)
        self.assertEqual(result["jaro_winkler"], 0.8324)

    def test_identical_strings_score_one(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="MARTHA", text_b="MARTHA"
        )
        self.assertEqual(result["jaro"], 1.0)
        self.assertEqual(result["jaro_winkler"], 1.0)

    def test_disjoint_strings_score_zero(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="MARTHA", text_b="ZZZZZZ"
        )
        self.assertEqual(result["jaro"], 0.0)
        self.assertEqual(result["jaro_winkler"], 0.0)

    def test_empty_conventions(self) -> None:
        both = self.tool.execute(mode="similarity", text_a="", text_b="")
        self.assertEqual(both["jaro"], 1.0)
        self.assertEqual(both["jaro_winkler"], 1.0)
        left = self.tool.execute(mode="similarity", text_a="", text_b="a")
        self.assertEqual(left["jaro"], 0.0)
        self.assertEqual(left["jaro_winkler"], 0.0)
        right = self.tool.execute(mode="similarity", text_a="a", text_b="")
        self.assertEqual(right["jaro"], 0.0)
        self.assertEqual(right["jaro_winkler"], 0.0)

    def test_symmetry(self) -> None:
        forward = self.tool.execute(
            mode="similarity", text_a="DIXON", text_b="DICKSONX"
        )
        backward = self.tool.execute(
            mode="similarity", text_a="DICKSONX", text_b="DIXON"
        )
        self.assertEqual(forward["jaro"], backward["jaro"])
        self.assertEqual(
            forward["jaro_winkler"], backward["jaro_winkler"]
        )

    def test_unicode_input(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="café", text_b="cafe"
        )
        self.assertEqual(result["jaro"], 0.8333)
        self.assertEqual(result["jaro_winkler"], 0.8833)

    # ------------------------------------------------------------------ #
    # Internal counts: matches / transpositions per the standard algorithm
    # ------------------------------------------------------------------ #

    def test_match_and_transposition_counts(self) -> None:
        # The canonical single-transposition example: 6 matches, the
        # swapped T/H pair counts as one transposition.
        matches, transpositions, score = DirectJaroWinklerTool._jaro_counts(
            "MARTHA", "MARHTA"
        )
        self.assertEqual(matches, 6)
        self.assertEqual(transpositions, 1)
        self.assertEqual(round(score, 4), 0.9444)
        # A rotation with matches but no out-of-order pair.
        matches, transpositions, score = DirectJaroWinklerTool._jaro_counts(
            "CRATE", "TRACE"
        )
        self.assertEqual(matches, 3)
        self.assertEqual(transpositions, 0)
        self.assertEqual(round(score, 4), 0.7333)
        # MARTHA vs MARTIN: 4 matches, 0 transpositions.
        matches, transpositions, _ = DirectJaroWinklerTool._jaro_counts(
            "MARTHA", "MARTIN"
        )
        self.assertEqual(matches, 4)
        self.assertEqual(transpositions, 0)

    def test_match_window_edges(self) -> None:
        # Window = floor(max(len)/2) - 1 clamped to 0: a two-character
        # adjacent swap falls outside a zero-length window.
        result = self.tool.execute(mode="similarity", text_a="AB", text_b="BA")
        self.assertEqual(result["jaro"], 0.0)
        self.assertEqual(result["jaro_winkler"], 0.0)
        # Same three characters but only the middle one is within the
        # zero-length window of a 3-character pair.
        result = self.tool.execute(mode="similarity", text_a="ABC", text_b="CBA")
        self.assertEqual(result["jaro"], 0.5556)
        # A shift by exactly the window still matches; the final D of
        # DABC is one position beyond ABCD's window, so m = 3.
        result = self.tool.execute(mode="similarity", text_a="ABCD", text_b="DABC")
        self.assertEqual(result["jaro"], 0.8333)
        self.assertEqual(result["jaro_winkler"], 0.8333)  # no common prefix
        # Single characters: window clamps to 0, exact match only.
        result = self.tool.execute(mode="similarity", text_a="A", text_b="A")
        self.assertEqual(result["jaro"], 1.0)
        result = self.tool.execute(mode="similarity", text_a="A", text_b="B")
        self.assertEqual(result["jaro"], 0.0)


class CompareModeTest(unittest.TestCase):
    """compare mode — thresholded boolean plus both scores."""

    def setUp(self) -> None:
        self.tool = JaroWinklerTool()

    def test_default_threshold_accepts_strong_match(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="compare", text_a="MARTHA", text_b="MARHTA"),
            {
                "mode": "compare",
                "text_a": "MARTHA",
                "text_b": "MARHTA",
                "threshold": 0.85,
                "matches": True,
                "jaro": 0.9444,
                "jaro_winkler": 0.9611,
            },
        )

    def test_default_threshold_rejects_weak_match(self) -> None:
        # jaro_winkler 0.84 < the 0.85 default.
        result = self.tool.execute(
            mode="compare", text_a="DWAYNE", text_b="DUANE"
        )
        self.assertFalse(result["matches"])
        self.assertEqual(result["threshold"], 0.85)

    def test_explicit_threshold(self) -> None:
        result = self.tool.execute(
            mode="compare", text_a="DWAYNE", text_b="DUANE", threshold=0.8
        )
        self.assertTrue(result["matches"])
        self.assertEqual(result["threshold"], 0.8)

    def test_threshold_boundary_is_inclusive(self) -> None:
        # A score exactly at the threshold matches (>=).
        result = self.tool.execute(
            mode="compare", text_a="MARTHA", text_b="MARHTA", threshold=0.9611
        )
        self.assertTrue(result["matches"])
        result = self.tool.execute(
            mode="compare", text_a="MARTHA", text_b="MARHTA", threshold=0.9612
        )
        self.assertFalse(result["matches"])
        # Extremes of the range.
        result = self.tool.execute(
            mode="compare", text_a="MARTHA", text_b="MARTHA", threshold=1
        )
        self.assertTrue(result["matches"])
        result = self.tool.execute(
            mode="compare", text_a="ABC", text_b="CBA", threshold=0
        )
        self.assertTrue(result["matches"])

    def test_empty_conventions_in_compare(self) -> None:
        result = self.tool.execute(mode="compare", text_a="", text_b="")
        self.assertTrue(result["matches"])
        result = self.tool.execute(mode="compare", text_a="", text_b="a")
        self.assertFalse(result["matches"])


class BestMatchModeTest(unittest.TestCase):
    """best_match mode — deterministic ranking and alphabetical ties."""

    def setUp(self) -> None:
        self.tool = JaroWinklerTool()

    def test_ranking_by_jaro_winkler(self) -> None:
        result = self.tool.execute(
            mode="best_match",
            text="MARTHA",
            candidates=["ZZZZZZ", "MARTIN", "MARHTA"],
        )
        self.assertEqual(result["mode"], "best_match")
        self.assertEqual(result["text"], "MARTHA")
        self.assertEqual(result["candidate_count"], 3)
        self.assertEqual(result["top_n"], 10)
        self.assertEqual(
            result["matches"],
            [
                {"candidate": "MARHTA", "jaro": 0.9444, "jaro_winkler": 0.9611},
                {"candidate": "MARTIN", "jaro": 0.7778, "jaro_winkler": 0.8667},
                {"candidate": "ZZZZZZ", "jaro": 0.0, "jaro_winkler": 0.0},
            ],
        )

    def test_ties_broken_alphabetically(self) -> None:
        result = self.tool.execute(
            mode="best_match",
            text="ABCF",
            candidates=["ABCG", "ABCE", "ABCD"],
        )
        self.assertEqual(
            [entry["candidate"] for entry in result["matches"]],
            ["ABCD", "ABCE", "ABCG"],
        )
        for entry in result["matches"]:
            self.assertEqual(entry["jaro"], 0.8333)
            self.assertEqual(entry["jaro_winkler"], 0.8833)

    def test_top_n_truncates(self) -> None:
        result = self.tool.execute(
            mode="best_match",
            text="MARTHA",
            candidates=["ZZZZZZ", "MARTIN", "MARHTA"],
            top_n=2,
        )
        self.assertEqual(result["top_n"], 2)
        self.assertEqual(
            [entry["candidate"] for entry in result["matches"]],
            ["MARHTA", "MARTIN"],
        )

    def test_top_n_larger_than_candidate_count(self) -> None:
        result = self.tool.execute(
            mode="best_match", text="ABCF", candidates=["ABCD"], top_n=5
        )
        self.assertEqual(len(result["matches"]), 1)

    def test_empty_text_against_candidates(self) -> None:
        result = self.tool.execute(
            mode="best_match", text="", candidates=["a", ""]
        )
        self.assertEqual(
            [entry["candidate"] for entry in result["matches"]], ["", "a"]
        )
        self.assertEqual(result["matches"][0]["jaro_winkler"], 1.0)
        self.assertEqual(result["matches"][1]["jaro_winkler"], 0.0)


class ClusterModeTest(unittest.TestCase):
    """cluster mode — union-find transitivity and deterministic ordering."""

    def setUp(self) -> None:
        self.tool = JaroWinklerTool()

    def test_transitive_grouping_via_intermediate(self) -> None:
        # Pairwise Jaro-Winkler (standard params): MARTHA-MARHTA 0.9611,
        # MARTHA-MARTIN 0.8667, MARHTA-MARTIN 0.8444. With threshold
        # 0.85 the last pair is BELOW the threshold, yet union-find
        # merges all three through MARTHA — a cluster is a connected
        # component, not a clique.
        result = self.tool.execute(
            mode="cluster",
            items=["MARTIN", "ZZZZZZ", "MARHTA", "MARTHA"],
            threshold=0.85,
        )
        self.assertEqual(result["mode"], "cluster")
        self.assertEqual(result["threshold"], 0.85)
        self.assertEqual(result["item_count"], 4)
        self.assertEqual(result["group_count"], 2)
        # Groups sorted by size descending; members alphabetically.
        self.assertEqual(
            result["groups"],
            [["MARHTA", "MARTHA", "MARTIN"], ["ZZZZZZ"]],
        )

    def test_pairwise_below_threshold_of_cluster_members(self) -> None:
        # Direct check of the transitivity claim above: MARHTA and
        # MARTIN themselves score below the threshold...
        result = self.tool.execute(
            mode="compare", text_a="MARHTA", text_b="MARTIN", threshold=0.85
        )
        self.assertFalse(result["matches"])
        self.assertEqual(result["jaro_winkler"], 0.8444)
        # ...while both reach the threshold against MARTHA.
        self.assertTrue(
            self.tool.execute(
                mode="compare", text_a="MARTHA", text_b="MARHTA", threshold=0.85
            )["matches"]
        )
        self.assertTrue(
            self.tool.execute(
                mode="compare", text_a="MARTHA", text_b="MARTIN", threshold=0.85
            )["matches"]
        )

    def test_default_threshold(self) -> None:
        result = self.tool.execute(mode="cluster", items=["ABCD", "ABCE"])
        self.assertEqual(result["threshold"], 0.85)
        # 0.8833 >= 0.85 -> one group.
        self.assertEqual(result["groups"], [["ABCD", "ABCE"]])

    def test_singleton_groups_and_group_ordering(self) -> None:
        # Two size-1 groups and two size-2 groups (DWAYNE/DUANE score
        # 0.84, above 0.8): size descending, ties by first member
        # alphabetically.
        result = self.tool.execute(
            mode="cluster",
            items=["ZZZZ", "DWAYNE", "DUANE", "AAAA", "BBBB", "ABCD", "ABCE"],
            threshold=0.8,
        )
        self.assertEqual(
            result["groups"],
            [["ABCD", "ABCE"], ["DUANE", "DWAYNE"], ["AAAA"], ["BBBB"], ["ZZZZ"]],
        )

    def test_duplicates_stay_together(self) -> None:
        result = self.tool.execute(
            mode="cluster", items=["B", "A", "A"]
        )
        self.assertEqual(result["groups"], [["A", "A"], ["B"]])

    def test_identical_items_form_one_group(self) -> None:
        result = self.tool.execute(
            mode="cluster", items=["MARTHA", "MARTHA", "MARTHA"]
        )
        self.assertEqual(result["group_count"], 1)
        self.assertEqual(
            result["groups"], [["MARTHA", "MARTHA", "MARTHA"]]
        )

    def test_empty_string_items(self) -> None:
        result = self.tool.execute(mode="cluster", items=["", "", "a"])
        self.assertEqual(result["groups"], [["", ""], ["a"]])


class ParameterTest(unittest.TestCase):
    """Configurable prefix_scale / boost_threshold / casefold."""

    def setUp(self) -> None:
        self.tool = JaroWinklerTool()

    def test_default_parameters_match_published_scores(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="MARTHA", text_b="MARHTA"
        )
        self.assertEqual(result["jaro_winkler"], 0.9611)

    def test_prefix_scale_override(self) -> None:
        # Common prefix MAR = 3 characters: jw = 0.9444 +
        # 3 * 0.2 * (1 - 0.9444) = 0.9778 (jaro is unchanged).
        result = self.tool.execute(
            mode="similarity",
            text_a="MARTHA",
            text_b="MARHTA",
            prefix_scale=0.2,
        )
        self.assertEqual(result["jaro"], 0.9444)
        self.assertEqual(result["jaro_winkler"], 0.9778)
        # The documented upper bound 0.25 is accepted.
        result = self.tool.execute(
            mode="similarity",
            text_a="MARTHA",
            text_b="MARHTA",
            prefix_scale=0.25,
        )
        self.assertEqual(result["jaro_winkler"], 0.9861)

    def test_boost_threshold_override(self) -> None:
        # DWAYNE/DUANE: jaro 0.8222 > the default 0.7, so the boost
        # applies (0.8400); with the gate above the jaro score the
        # boost is skipped and jw equals jaro.
        result = self.tool.execute(
            mode="similarity", text_a="DWAYNE", text_b="DUANE",
            boost_threshold=0.9,
        )
        self.assertEqual(result["jaro"], 0.8222)
        self.assertEqual(result["jaro_winkler"], 0.8222)

    def test_case_sensitive_by_default(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="Martha", text_b="MARHTA"
        )
        self.assertEqual(result["jaro"], 0.4444)
        self.assertEqual(result["jaro_winkler"], 0.4444)

    def test_casefold_option(self) -> None:
        result = self.tool.execute(
            mode="similarity", text_a="Martha", text_b="MARHTA", casefold=True
        )
        self.assertEqual(result["jaro"], 0.9444)
        self.assertEqual(result["jaro_winkler"], 0.9611)
        # Original strings are preserved in the output.
        self.assertEqual(result["text_a"], "Martha")
        self.assertEqual(result["text_b"], "MARHTA")

    def test_casefold_full_unicode_folding(self) -> None:
        # German sharp s folds to "ss": "STRASSE".casefold() ==
        # "strasse" == "straße".casefold() -> exact match.
        result = self.tool.execute(
            mode="similarity", text_a="STRASSE", text_b="straße", casefold=True
        )
        self.assertEqual(result["jaro"], 1.0)
        self.assertEqual(result["jaro_winkler"], 1.0)
        # Case-sensitive they share almost nothing.
        result = self.tool.execute(
            mode="similarity", text_a="STRASSE", text_b="straße"
        )
        self.assertEqual(result["jaro_winkler"], 0.0)

    def test_casefold_in_cluster(self) -> None:
        result = self.tool.execute(
            mode="cluster",
            items=["Martha", "MARHTA", "ZZZZZZ"],
            threshold=0.9,
            casefold=True,
        )
        self.assertEqual(result["groups"], [["MARHTA", "Martha"], ["ZZZZZZ"]])


class ValidationTest(unittest.TestCase):
    """Strict input validation — the full error matrix."""

    def setUp(self) -> None:
        self.tool = JaroWinklerTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode(self) -> None:
        self.assert_invalid(mode="levenshtein", text_a="a", text_b="b")
        self.assert_invalid(mode=None, text_a="a", text_b="b")

    def test_similarity_requires_two_strings(self) -> None:
        for bad in (None, 123, True, ["MARTHA"], b"MARTHA"):
            self.assert_invalid(mode="similarity", text_a=bad, text_b="MARHTA")
            self.assert_invalid(mode="similarity", text_a="MARTHA", text_b=bad)

    def test_compare_requires_two_strings(self) -> None:
        self.assert_invalid(mode="compare", text_a="MARTHA")
        self.assert_invalid(mode="compare", text_b="MARHTA")

    def test_threshold_bounds_and_type(self) -> None:
        for bad in ("0.9", True, -0.1, 1.1, float("nan"), float("inf")):
            self.assert_invalid(
                mode="compare", text_a="MARTHA", text_b="MARHTA", threshold=bad
            )
        # Valid extremes.
        self.tool.execute(
            mode="compare", text_a="MARTHA", text_b="MARHTA", threshold=0
        )
        self.tool.execute(
            mode="compare", text_a="MARTHA", text_b="MARHTA", threshold=1
        )

    def test_prefix_scale_bounds_and_type(self) -> None:
        for bad in ("0.1", True, 0, -0.1, 0.3, float("nan")):
            self.assert_invalid(
                mode="similarity",
                text_a="MARTHA",
                text_b="MARHTA",
                prefix_scale=bad,
            )

    def test_boost_threshold_bounds_and_type(self) -> None:
        for bad in ("0.7", True, -0.1, 1.5, float("nan")):
            self.assert_invalid(
                mode="similarity",
                text_a="MARTHA",
                text_b="MARHTA",
                boost_threshold=bad,
            )

    def test_top_n_validation(self) -> None:
        for bad in (0, -1, 2.5, "5", True):
            self.assert_invalid(
                mode="best_match",
                text="MARTHA",
                candidates=["MARHTA"],
                top_n=bad,
            )

    def test_casefold_validation(self) -> None:
        for bad in ("yes", 1, [True]):
            self.assert_invalid(
                mode="similarity", text_a="a", text_b="b", casefold=bad
            )

    def test_candidates_must_be_non_empty_string_list(self) -> None:
        for bad in (None, "MARHTA", 42, [], ("MARHTA",), [42], [None], [True]):
            self.assert_invalid(
                mode="best_match", text="MARTHA", candidates=bad
            )

    def test_cluster_items_must_be_non_empty_string_list(self) -> None:
        for bad in (None, "MARTHA", [], [42], [["A"]]):
            self.assert_invalid(mode="cluster", items=bad)

    def test_string_length_cap(self) -> None:
        long_string = "A" * 2_001
        self.assert_invalid(
            mode="similarity", text_a=long_string, text_b="MARTHA"
        )
        # At the cap it is accepted.
        self.tool.execute(mode="similarity", text_a="A" * 2_000, text_b="A")
        self.assert_invalid(
            mode="best_match", text="MARTHA", candidates=[long_string]
        )
        self.assert_invalid(mode="cluster", items=[long_string])

    def test_list_size_caps(self) -> None:
        self.assert_invalid(
            mode="best_match",
            text="MARTHA",
            candidates=["CAND"] * 1_001,
        )
        self.tool.execute(
            mode="best_match", text="MARTHA", candidates=["CAND"] * 1_000
        )
        self.assert_invalid(mode="cluster", items=["ITEM"] * 501)
        self.tool.execute(mode="cluster", items=["ITEM"] * 500)

    def test_error_messages_are_prefixed(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="nonsense")
        self.assertIn("jaro_winkler_tool:", str(ctx.exception))
        self.assertIn("mode must be one of", str(ctx.exception))


class ExportTest(unittest.TestCase):
    """Package export wiring."""

    def test_common_tool_package_export(self) -> None:
        self.assertIs(JaroWinklerTool, DirectJaroWinklerTool)
        self.assertEqual(JaroWinklerTool().name, "jaro_winkler_tool")

    def test_mode_catalogue(self) -> None:
        self.assertEqual(
            JaroWinklerTool.MODES,
            ("similarity", "compare", "best_match", "cluster"),
        )


if __name__ == "__main__":
    unittest.main()
