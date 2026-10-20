#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_grade_calculator_tool.py

"""Offline unit tests for GradeCalculatorTool.

The tool is built purely on the standard library (json, math) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic and checked against hand-computed literal
ground truths:

* weighted mode — the three-assignment transcript below aggregates to
  a weighted mean of exactly 86.70 with per-assignment contributions
  25.50 / 25.20 / 36.00 (total weight 100), the raw {score, max}
  pair 42 of 50 converts to the 84.00 percent, fraction weights give
  the identical mean (scale invariance) and a total weight of 90
  triggers the documented warning field;
* drop_lowest — ranking by weighted impact (percent * weight) rather
  than by raw score is exercised both ways: the classic case drops
  the weak low-weight homework, and the counterexample drops an 85
  (weight 9, impact 765) ahead of a 60 (weight 90, impact 5400) even
  though 60 is the lower raw score;
* letter mode — exact band boundaries (89.99 vs 90, 59.99 vs 60),
  the full default table with its evenly spaced 4.0-scale grade
  points, and a custom three-band table (points 4.0 / 2.0 / 0.0);
* curve mode — flat_add with the 100 cap and capped-count, and
  scale_to_max with the documented rescale arithmetic including the
  all-identical-scores degenerate case and the all-zero error.

The parameter error matrix covers every malformed-input branch
(unknown mode, missing collections, bad weights, bounds on drop_n,
non-monotonic custom thresholds, amount misuse, oversized input).
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import GradeCalculatorTool
from agentuniverse.agent.action.tool.common_tool.grade_calculator_tool import (
    GradeCalculatorTool as DirectGradeCalculatorTool,
)

# --------------------------------------------------------------------- #
# Hand-computed ground truths
# --------------------------------------------------------------------- #
# Transcript A (3 assignments, percent-style weights summing to 100).
#   Quiz 1:  85/100 plain          -> percent 85, weight 30, wp 2550
#   Midterm: 42 of 50 (score pair) -> percent 84, weight 30, wp 2520
#   Final:   90/100 plain          -> percent 90, weight 40, wp 3600
# Weighted mean = 8670 / 100 = 86.7 ; unweighted = 259/3 = 86.33... ;
# contributions = 25.5, 25.2, 36.0 (each wp / total weight).
TRANSCRIPT_A = [
    {"name": "Quiz 1", "score": 85, "weight": 30},
    {"name": "Midterm", "score": {"score": 42, "max": 50}, "weight": 30},
    {"name": "Final", "score": 90, "weight": 40},
]
A_WEIGHTED_MEAN = 86.7
A_UNWEIGHTED_MEAN = 86.33
A_CONTRIBUTIONS = [25.5, 25.2, 36.0]
A_WEIGHTED_POINTS = [2550.0, 2520.0, 3600.0]
A_TOTAL_WEIGHT = 100.0

# Transcript A in fraction form: identical percents, weights /100.
# The weighted mean is scale invariant -> still 86.7 exactly, but the
# total weight is 1, so the != 100 warning must appear.
TRANSCRIPT_A_FRACTIONS = [
    {"name": "Quiz 1", "score": 85, "weight": 0.3},
    {"name": "Midterm", "score": {"score": 42, "max": 50}, "weight": 0.3},
    {"name": "Final", "score": 90, "weight": 0.4},
]

# Transcript B (3 assignments, drop_n=1). Weighted impacts:
#   Quiz:     92 * 20 = 1840
#   Homework: 70 * 10 =  700  <- lowest impact, dropped
#   Exam:     81 * 70 = 5670
# Before: mean 8210 / 100 = 82.1 ; after dropping Homework the kept
# total weight is 90 and the kept weighted sum is 7510, so the
# recomputed mean is 7510 / 90 = 83.444... -> 83.44 (change +1.34).
TRANSCRIPT_B = [
    {"name": "Quiz", "score": 92, "weight": 20},
    {"name": "Homework", "score": 70, "weight": 10},
    {"name": "Exam", "score": 81, "weight": 70},
]
B_BEFORE_MEAN = 82.1
B_AFTER_MEAN = 83.44
B_AFTER_TOTAL_WEIGHT = 90.0
B_MEAN_CHANGE = 1.34

# Transcript C (impact ranking differs from raw-score ranking).
#   Essay: 85 * 9  =  765  <- lowest impact, dropped by the tool
#   Exam:  60 * 90 = 5400
# Raw-score ranking would drop the 60 instead; impact ranking drops
# the 85.  Before: (765 + 5400) / 99 = 62.2727... -> 62.27 ; after:
# only the Exam remains, mean 60.0, total weight 90, change -2.27.
TRANSCRIPT_C = [
    {"name": "Essay", "score": 85, "weight": 9},
    {"name": "Exam", "score": 60, "weight": 90},
]
C_BEFORE_MEAN = 62.27
C_AFTER_MEAN = 60.0
C_MEAN_CHANGE = -2.27

# Custom letter table (3 bands): points are evenly spaced 4.0, 2.0, 0.0.
CUSTOM_TABLE = [
    {"letter": "A", "min_score": 93},
    {"letter": "B", "min_score": 85},
    {"letter": "C", "min_score": 0},
]


class GradeCalculatorToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib GradeCalculatorTool."""

    def setUp(self) -> None:
        self.tool = GradeCalculatorTool()

    def assert_invalid(self, **kwargs) -> str:
        """Assert the call raises the standard ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        message = str(ctx.exception)
        self.assertIn("grade_calculator_tool:", message)
        return message

    def assert_content_error(self, result: dict, error_type: str) -> str:
        """Assert a structured content-level error payload."""
        self.assertIn("error", result)
        self.assertNotIn("weighted_mean", result)
        self.assertEqual(result["error"]["type"], error_type)
        return result["error"]["message"]

    # ------------------------------------------------------------------ #
    # weighted mode — ground truths
    # ------------------------------------------------------------------ #

    def test_weighted_transcript_a(self) -> None:
        result = self.tool.execute(mode="weighted", assignments=TRANSCRIPT_A)
        self.assertEqual(result["mode"], "weighted")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["total_weight"], A_TOTAL_WEIGHT)
        self.assertEqual(result["weighted_mean"], A_WEIGHTED_MEAN)
        self.assertEqual(result["unweighted_mean"], A_UNWEIGHTED_MEAN)
        self.assertNotIn("weight_warning", result)
        table = result["assignments"]
        self.assertEqual(
            [entry["name"] for entry in table],
            ["Quiz 1", "Midterm", "Final"],
        )
        self.assertEqual([entry["percent"] for entry in table], [85.0, 84.0, 90.0])
        self.assertEqual(
            [entry["weighted_points"] for entry in table], A_WEIGHTED_POINTS
        )
        self.assertEqual(
            [entry["contribution"] for entry in table], A_CONTRIBUTIONS
        )
        # The raw score pair keeps its raw marks; plain entries have no max.
        self.assertEqual(table[1]["score"], 42)
        self.assertEqual(table[1]["max"], 50)
        self.assertNotIn("max", table[0])
        # The contribution table adds up to the weighted mean.
        self.assertAlmostEqual(
            sum(entry["contribution"] for entry in table),
            result["weighted_mean"],
            places=6,
        )

    def test_weighted_json_string_input(self) -> None:
        payload = json.dumps(TRANSCRIPT_A)
        result = self.tool.execute(mode="weighted", assignments=payload)
        self.assertEqual(result["weighted_mean"], A_WEIGHTED_MEAN)
        self.assertEqual(result["count"], 3)

    def test_weighted_sibling_max_form(self) -> None:
        result = self.tool.execute(
            mode="weighted",
            assignments=[
                {"name": "Midterm", "score": 42, "max": 50, "weight": 100},
            ],
        )
        self.assertEqual(result["assignments"][0]["percent"], 84.0)
        self.assertEqual(result["weighted_mean"], 84.0)
        self.assertEqual(result["unweighted_mean"], 84.0)

    def test_weighted_fraction_weights_same_mean_with_warning(self) -> None:
        result = self.tool.execute(
            mode="weighted", assignments=TRANSCRIPT_A_FRACTIONS
        )
        self.assertEqual(result["weighted_mean"], A_WEIGHTED_MEAN)
        self.assertEqual(result["total_weight"], 1.0)
        warning = result["weight_warning"]
        self.assertIn("1.0", warning)
        self.assertIn("not 100", warning)

    def test_weighted_off_hundred_total_warns(self) -> None:
        result = self.tool.execute(
            mode="weighted",
            assignments=[
                {"name": "A", "score": 80, "weight": 50},
                {"name": "B", "score": 90, "weight": 40},
            ],
        )
        # 8000 + 3600 = 7600 over 90 -> 84.444... -> 84.44
        self.assertEqual(result["weighted_mean"], 84.44)
        self.assertEqual(result["total_weight"], 90.0)
        self.assertIn("weight_warning", result)

    def test_weighted_near_hundred_within_tolerance(self) -> None:
        result = self.tool.execute(
            mode="weighted",
            assignments=[
                {"name": "A", "score": 80, "weight": 33.333333},
                {"name": "B", "score": 90, "weight": 33.333333},
                {"name": "C", "score": 70, "weight": 33.333333},
            ],
        )
        # 99.999999 is within the 0.01 tolerance of 100: no warning.
        self.assertNotIn("weight_warning", result)

    def test_weighted_default_assignment_names(self) -> None:
        result = self.tool.execute(
            mode="weighted",
            assignments=[{"score": 50, "weight": 1}],
        )
        self.assertEqual(result["assignments"][0]["name"], "assignment 1")

    def test_weighted_zero_weight_assignment(self) -> None:
        result = self.tool.execute(
            mode="weighted",
            assignments=[
                {"name": "Extra", "score": 100, "weight": 0},
                {"name": "Real", "score": 70, "weight": 10},
            ],
        )
        self.assertEqual(result["weighted_mean"], 70.0)
        self.assertEqual(result["assignments"][0]["contribution"], 0.0)
        self.assertIn("weight_warning", result)

    # ------------------------------------------------------------------ #
    # drop_lowest mode — ground truths
    # ------------------------------------------------------------------ #

    def test_drop_lowest_transcript_b(self) -> None:
        result = self.tool.execute(
            mode="drop_lowest", assignments=TRANSCRIPT_B, drop_n=1
        )
        self.assertEqual(result["mode"], "drop_lowest")
        self.assertEqual(result["drop_n"], 1)
        self.assertEqual(result["before"]["weighted_mean"], B_BEFORE_MEAN)
        self.assertEqual(result["before"]["count"], 3)
        self.assertEqual(result["after"]["count"], 2)
        self.assertEqual(result["after"]["total_weight"], B_AFTER_TOTAL_WEIGHT)
        self.assertEqual(result["after"]["weighted_mean"], B_AFTER_MEAN)
        self.assertEqual(result["mean_change"], B_MEAN_CHANGE)
        self.assertEqual(
            [dropped["name"] for dropped in result["dropped"]], ["Homework"]
        )
        self.assertEqual(result["dropped"][0]["impact"], 700.0)
        # The kept table recomputes contributions against the kept total.
        kept_names = [entry["name"] for entry in result["after"]["assignments"]]
        self.assertEqual(kept_names, ["Quiz", "Exam"])

    def test_drop_lowest_impact_differs_from_raw_score(self) -> None:
        result = self.tool.execute(
            mode="drop_lowest", assignments=TRANSCRIPT_C, drop_n=1
        )
        # The Essay (85, weight 9, impact 765) has the LOWEST impact even
        # though the Exam's raw score 60 is lower: dropping follows the
        # weighted impact, not the raw score.
        self.assertEqual(
            [dropped["name"] for dropped in result["dropped"]], ["Essay"]
        )
        self.assertEqual(result["dropped"][0]["impact"], 765.0)
        self.assertEqual(result["before"]["weighted_mean"], C_BEFORE_MEAN)
        self.assertEqual(result["after"]["weighted_mean"], C_AFTER_MEAN)
        self.assertEqual(result["after"]["count"], 1)
        self.assertEqual(result["mean_change"], C_MEAN_CHANGE)

    def test_drop_lowest_drop_two_and_tie_break(self) -> None:
        result = self.tool.execute(
            mode="drop_lowest",
            assignments=[
                {"name": "A", "score": 80, "weight": 10},
                {"name": "B", "score": 40, "weight": 20},
                {"name": "C", "score": 80, "weight": 10},
                {"name": "D", "score": 90, "weight": 60},
            ],
            drop_n=2,
        )
        # Impacts: A 800, B 800, C 800, D 5400. The three-way 800 tie is
        # broken deterministically by the original element order, so the
        # dropped pair is A then B and the survivors are C and D.
        self.assertEqual(
            [dropped["name"] for dropped in result["dropped"]], ["A", "B"]
        )
        # Kept: C (800) + D (5400) over weight 70 -> 6200/70 = 88.571... -> 88.57
        self.assertEqual(result["after"]["weighted_mean"], 88.57)

    def test_drop_lowest_defaults_to_one(self) -> None:
        result = self.tool.execute(mode="drop_lowest", assignments=TRANSCRIPT_B)
        self.assertEqual(result["drop_n"], 1)
        self.assertEqual(len(result["dropped"]), 1)

    def test_drop_lowest_json_string_input(self) -> None:
        result = self.tool.execute(
            mode="drop_lowest",
            assignments=json.dumps(TRANSCRIPT_B),
            drop_n=1,
        )
        self.assertEqual(result["after"]["weighted_mean"], B_AFTER_MEAN)

    # ------------------------------------------------------------------ #
    # letter mode — ground truths
    # ------------------------------------------------------------------ #

    def test_letter_default_table_and_boundaries(self) -> None:
        tool = self.tool
        self.assertEqual(tool.execute(mode="letter", score=95)["letter"], "A")
        self.assertEqual(tool.execute(mode="letter", score=90)["letter"], "A")
        self.assertEqual(tool.execute(mode="letter", score=89.99)["letter"], "B")
        self.assertEqual(tool.execute(mode="letter", score=80)["letter"], "B")
        self.assertEqual(tool.execute(mode="letter", score=70)["letter"], "C")
        self.assertEqual(tool.execute(mode="letter", score=60)["letter"], "D")
        self.assertEqual(tool.execute(mode="letter", score=59.99)["letter"], "F")
        self.assertEqual(tool.execute(mode="letter", score=0)["letter"], "F")

    def test_letter_default_grade_points_table(self) -> None:
        result = self.tool.execute(mode="letter", score=84.99)
        self.assertEqual(result["table_kind"], "default")
        self.assertEqual(result["letter"], "B")
        self.assertEqual(result["grade_points"], 3.0)
        self.assertEqual(result["band_min_score"], 80.0)
        self.assertEqual(
            result["table"],
            [
                {"letter": "A", "min_score": 90.0, "grade_points": 4.0},
                {"letter": "B", "min_score": 80.0, "grade_points": 3.0},
                {"letter": "C", "min_score": 70.0, "grade_points": 2.0},
                {"letter": "D", "min_score": 60.0, "grade_points": 1.0},
                {"letter": "F", "min_score": 0.0, "grade_points": 0.0},
            ],
        )

    def test_letter_custom_table(self) -> None:
        result = self.tool.execute(
            mode="letter", score=92.99, thresholds=CUSTOM_TABLE
        )
        self.assertEqual(result["table_kind"], "custom")
        self.assertEqual(result["letter"], "B")
        self.assertEqual(result["grade_points"], 2.0)
        # Evenly spaced points across 3 bands: 4.0 / 2.0 / 0.0.
        self.assertEqual(
            [band["grade_points"] for band in result["table"]], [4.0, 2.0, 0.0]
        )
        # Exact custom boundaries: 93 is an A, 85 a B, 84.99 the catch-all C.
        self.assertEqual(
            self.tool.execute(
                mode="letter", score=93, thresholds=CUSTOM_TABLE
            )["letter"],
            "A",
        )
        self.assertEqual(
            self.tool.execute(
                mode="letter", score=85, thresholds=CUSTOM_TABLE
            )["letter"],
            "B",
        )
        self.assertEqual(
            self.tool.execute(
                mode="letter", score=84.99, thresholds=CUSTOM_TABLE
            )["letter"],
            "C",
        )
        self.assertEqual(
            self.tool.execute(
                mode="letter", score=0, thresholds=CUSTOM_TABLE
            )["grade_points"],
            0.0,
        )

    def test_letter_custom_table_mapping_and_json_forms(self) -> None:
        mapping = {"A": 93, "B": 85, "C": 0}
        via_mapping = self.tool.execute(
            mode="letter", score=90, thresholds=mapping
        )
        via_json = self.tool.execute(
            mode="letter", score=90, thresholds=json.dumps(CUSTOM_TABLE)
        )
        self.assertEqual(via_mapping["letter"], "B")
        self.assertEqual(via_mapping["letter"], via_json["letter"])
        self.assertEqual(via_mapping["grade_points"], via_json["grade_points"])

    # ------------------------------------------------------------------ #
    # curve mode — ground truths
    # ------------------------------------------------------------------ #

    def test_curve_flat_add_with_cap(self) -> None:
        result = self.tool.execute(
            mode="curve", scores=[78, 96, 62], curve="flat_add", amount=5
        )
        self.assertEqual(result["mode"], "curve")
        self.assertEqual(result["curve"], "flat_add")
        self.assertEqual(result["source"], "sequence")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["original"]["mean"], 78.67)
        self.assertEqual(result["original"]["min"], 62.0)
        self.assertEqual(result["original"]["max"], 96.0)
        # 96 + 5 = 101 caps at 100.
        self.assertEqual(result["curved_scores"], [83.0, 100.0, 67.0])
        self.assertEqual(result["capped_count"], 1)
        self.assertEqual(result["new_mean"], 83.33)
        self.assertEqual(result["new_min"], 67.0)
        self.assertEqual(result["new_max"], 100.0)
        self.assertIn("min(100", result["formula"])

    def test_curve_flat_add_all_capped(self) -> None:
        result = self.tool.execute(
            mode="curve", scores=[98, 99], curve="flat_add", amount=10
        )
        self.assertEqual(result["curved_scores"], [100.0, 100.0])
        self.assertEqual(result["capped_count"], 2)
        self.assertEqual(result["new_mean"], 100.0)

    def test_curve_scale_to_max(self) -> None:
        result = self.tool.execute(
            mode="curve", scores=[75, 60, 90], curve="scale_to_max"
        )
        # 100 / 90 = 1.1111... ; 75 -> 83.33, 60 -> 66.67, 90 -> 100.
        self.assertEqual(result["curved_scores"], [83.33, 66.67, 100.0])
        self.assertEqual(result["scale_factor"], 1.1111)
        self.assertEqual(result["new_mean"], 83.33)
        self.assertEqual(result["new_max"], 100.0)
        self.assertIn("100 / max(scores)", result["formula"])
        self.assertNotIn("amount", result)

    def test_curve_scale_to_max_identical_scores(self) -> None:
        result = self.tool.execute(
            mode="curve", scores=[80, 80, 80], curve="scale_to_max"
        )
        self.assertEqual(result["scale_factor"], 1.25)
        self.assertEqual(result["curved_scores"], [100.0, 100.0, 100.0])
        self.assertEqual(result["new_mean"], 100.0)

    def test_curve_scale_to_max_already_capped(self) -> None:
        result = self.tool.execute(
            mode="curve", scores=[50, 100], curve="scale_to_max"
        )
        self.assertEqual(result["scale_factor"], 1.0)
        self.assertEqual(result["curved_scores"], [50.0, 100.0])

    def test_curve_json_string_input(self) -> None:
        result = self.tool.execute(
            mode="curve", scores="[78, 96, 62]", curve="flat_add", amount=5
        )
        self.assertEqual(result["source"], "json")
        self.assertEqual(result["curved_scores"], [83.0, 100.0, 67.0])

    def test_curve_scale_to_max_all_zero_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="curve", scores=[0, 0], curve="scale_to_max"
        )
        message = self.assert_content_error(result, "degenerate_scores")
        self.assertIn("max(scores) > 0", message)

    # ------------------------------------------------------------------ #
    # Parameter error matrix (ValueError before any computation)
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        message = self.assert_invalid(mode="grading", assignments=TRANSCRIPT_A)
        self.assertIn("mode must be one of", message)

    def test_invalid_assignments_shape(self) -> None:
        self.assert_invalid(mode="weighted")
        self.assert_invalid(mode="weighted", assignments=42)
        self.assert_invalid(mode="weighted", assignments="")
        self.assert_invalid(mode="weighted", assignments=[])

    def test_invalid_drop_n_bounds(self) -> None:
        message = self.assert_invalid(
            mode="drop_lowest", assignments=TRANSCRIPT_B, drop_n=3
        )
        self.assertIn("strictly less than the assignment count", message)
        self.assert_invalid(
            mode="drop_lowest", assignments=TRANSCRIPT_C, drop_n=2
        )
        self.assert_invalid(
            mode="drop_lowest", assignments=TRANSCRIPT_B, drop_n=0
        )
        self.assert_invalid(
            mode="drop_lowest", assignments=TRANSCRIPT_B, drop_n=-1
        )
        self.assert_invalid(
            mode="drop_lowest", assignments=TRANSCRIPT_B, drop_n=1.0
        )
        self.assert_invalid(
            mode="drop_lowest", assignments=TRANSCRIPT_B, drop_n=True
        )

    def test_invalid_letter_score(self) -> None:
        self.assert_invalid(mode="letter")
        self.assert_invalid(mode="letter", score=None)
        self.assert_invalid(mode="letter", score=100.01)
        self.assert_invalid(mode="letter", score=-0.5)
        self.assert_invalid(mode="letter", score="90")
        self.assert_invalid(mode="letter", score=True)

    def test_invalid_custom_thresholds(self) -> None:
        single = [{"letter": "A", "min_score": 90}]
        self.assert_invalid(mode="letter", score=90, thresholds=single)
        eleven = [
            {"letter": chr(ord("A") + i), "min_score": 100 - 10 * i}
            for i in range(11)
        ]
        self.assert_invalid(mode="letter", score=90, thresholds=eleven)
        not_descending = [
            {"letter": "B", "min_score": 80},
            {"letter": "A", "min_score": 90},
        ]
        message = self.assert_invalid(
            mode="letter", score=90, thresholds=not_descending
        )
        self.assertIn("strictly descending", message)
        equal = [
            {"letter": "A", "min_score": 90},
            {"letter": "B", "min_score": 90},
        ]
        self.assert_invalid(mode="letter", score=90, thresholds=equal)
        duplicate = [
            {"letter": "A", "min_score": 90},
            {"letter": "A", "min_score": 80},
        ]
        self.assert_invalid(mode="letter", score=90, thresholds=duplicate)
        out_of_range = [
            {"letter": "A", "min_score": 101},
            {"letter": "B", "min_score": 0},
        ]
        self.assert_invalid(mode="letter", score=90, thresholds=out_of_range)
        bad_keys = [{"letter": "A", "minimum": 90}]
        self.assert_invalid(mode="letter", score=90, thresholds=bad_keys)
        empty_letter = [{"letter": "  ", "min_score": 90}, {"letter": "B", "min_score": 0}]
        self.assert_invalid(mode="letter", score=90, thresholds=empty_letter)

    def test_content_error_malformed_thresholds_json(self) -> None:
        result = self.tool.execute(
            mode="letter", score=90, thresholds='[{"letter": "A"'
        )
        message = self.assert_content_error(result, "invalid_json")
        self.assertIn("not valid JSON", message)

    def test_invalid_curve_parameters(self) -> None:
        self.assert_invalid(
            mode="curve", scores=[80], curve="bell", amount=5
        )
        self.assert_invalid(mode="curve", scores=[80], curve="flat_add")
        self.assert_invalid(
            mode="curve", scores=[80], curve="flat_add", amount=0
        )
        self.assert_invalid(
            mode="curve", scores=[80], curve="flat_add", amount=-5
        )
        self.assert_invalid(
            mode="curve", scores=[80], curve="flat_add", amount=True
        )
        message = self.assert_invalid(
            mode="curve", scores=[80], curve="scale_to_max", amount=5
        )
        self.assertIn("flat_add only", message)
        self.assert_invalid(mode="curve", curve="flat_add", amount=5)
        self.assert_invalid(mode="curve", scores=[], curve="flat_add", amount=5)

    def test_invalid_weight_bounds(self) -> None:
        message = self.assert_invalid(
            mode="weighted",
            assignments=[
                {"name": "A", "score": 80, "weight": 0},
                {"name": "B", "score": 90, "weight": 0},
            ],
        )
        self.assertIn("positive total", message)

    # ------------------------------------------------------------------ #
    # Content error matrix (structured payloads, no exception)
    # ------------------------------------------------------------------ #

    def assert_assignments_error(
        self, assignments, expected_fragment
    ) -> str:
        result = self.tool.execute(mode="weighted", assignments=assignments)
        message = self.assert_content_error(result, "invalid_assignments")
        self.assertIn(expected_fragment, message)
        return message

    def test_content_error_malformed_json(self) -> None:
        result = self.tool.execute(
            mode="weighted", assignments='[{"score": 80, '
        )
        message = self.assert_content_error(result, "invalid_json")
        self.assertIn("not valid JSON", message)

    def test_content_error_not_an_array(self) -> None:
        result = self.tool.execute(mode="weighted", assignments='{"a": 1}')
        self.assert_content_error(result, "invalid_json")

    def test_content_error_element_shapes(self) -> None:
        self.assert_assignments_error([42], "must be an object")
        self.assert_assignments_error(["x"], "must be an object")
        self.assert_assignments_error(
            [{"weight": 10}], "missing the score key"
        )
        self.assert_assignments_error(
            [{"score": 80}], "missing the weight key"
        )
        self.assert_assignments_error(
            [{"score": 80, "weight": 10, "wight": 1}], "unknown key"
        )
        self.assert_assignments_error(
            [{"name": "", "score": 80, "weight": 10}],
            "non-empty string",
        )

    def test_content_error_bad_numbers(self) -> None:
        self.assert_assignments_error(
            [{"score": "80", "weight": 10}], "is not a number"
        )
        self.assert_assignments_error(
            [{"score": True, "weight": 10}], "is not a number"
        )
        self.assert_assignments_error(
            [{"score": 80, "weight": -1}], "greater than or equal to 0"
        )
        self.assert_assignments_error(
            [{"score": 101, "weight": 10}], "between 0 and 100"
        )
        self.assert_assignments_error(
            [{"score": -1, "weight": 10}], "between 0 and 100"
        )

    def test_content_error_bad_score_pairs(self) -> None:
        self.assert_assignments_error(
            [{"score": {"score": 42}, "weight": 10}],
            "both score and max",
        )
        self.assert_assignments_error(
            [{"score": {"score": 42, "max": 0}, "weight": 10}],
            "greater than 0",
        )
        self.assert_assignments_error(
            [{"score": {"score": 42, "max": 40}, "weight": 10}],
            "between 0 and its max",
        )
        self.assert_assignments_error(
            [{"score": {"score": -1, "max": 40}, "weight": 10}],
            "between 0 and its max",
        )
        self.assert_assignments_error(
            [{"score": {"score": 42, "max": 50}, "weight": 10, "max": 50}],
            "one form or the other",
        )
        self.assert_assignments_error(
            [{"score": 42, "max": 0, "weight": 10}], "greater than 0"
        )
        self.assert_assignments_error(
            [{"score": 55, "max": 50, "weight": 10}], "between 0 and its max"
        )

    def test_content_error_curve_scores(self) -> None:
        result = self.tool.execute(
            mode="curve", scores='[80, "x"]', curve="flat_add", amount=5
        )
        self.assert_content_error(result, "invalid_scores")
        result = self.tool.execute(
            mode="curve", scores='{"a": 1}', curve="flat_add", amount=5
        )
        self.assert_content_error(result, "invalid_json")
        result = self.tool.execute(
            mode="curve", scores=[80, 101], curve="flat_add", amount=5
        )
        self.assert_content_error(result, "invalid_scores")

    def test_content_error_index_positions(self) -> None:
        message = self.assert_assignments_error(
            [
                {"score": 80, "weight": 10},
                {"score": 200, "weight": 10},
            ],
            "between 0 and 100",
        )
        self.assertIn("index 1", message)

    # ------------------------------------------------------------------ #
    # Plumbing
    # ------------------------------------------------------------------ #

    def test_direct_module_import_matches_package_export(self) -> None:
        self.assertIs(DirectGradeCalculatorTool, GradeCalculatorTool)

    def test_tool_metadata(self) -> None:
        self.assertEqual(self.tool.name, "grade_calculator_tool")
        self.assertIn("weighted", self.tool.description)
        self.assertIn("drop_lowest", self.tool.description)
        self.assertIn("letter", self.tool.description)
        self.assertIn("curve", self.tool.description)


if __name__ == "__main__":
    unittest.main()
