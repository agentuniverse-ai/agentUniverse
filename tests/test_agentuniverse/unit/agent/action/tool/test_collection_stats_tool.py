#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_collection_stats_tool.py

"""Offline unit tests for CollectionStatsTool.

The tool is built purely on the standard library (statistics, math,
json, collections) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: the descriptive
summary is checked against hand-computed literal ground truths (odd
and even medians, mode ties, inclusive-method quartiles on a known
11-value dataset, exact-fraction variances, 1.5*IQR outlier fences,
z-scores including the zero-stdev note), the parsing modes against
fixed inputs and error positions, and the variance/stdev fields
against the statistics module as an independent cross-check.
"""

import json
import math
import statistics
import unittest
from fractions import Fraction

from agentuniverse.agent.action.tool.common_tool import CollectionStatsTool
from agentuniverse.agent.action.tool.common_tool.collection_stats_tool import (
    CollectionStatsTool as DirectCollectionStatsTool,
)

# --------------------------------------------------------------------- #
# Hand-computed ground truths
# --------------------------------------------------------------------- #
# Dataset A (11 values, one clear outlier). Quartiles use the
# inclusive method: with N = 11 sorted values the quantile positions
# are 0.25*(N-1) = 2.5, 0.5*(N-1) = 5 and 0.75*(N-1) = 7.5, i.e.
# q1 = 4 + 0.5*(5-4) = 4.5, q2 = 7 (exact order statistic) and
# q3 = 9 + 0.5*(10-9) = 9.5.  IQR = 5, fences -3 and 17, so only 100
# is an outlier.  Sum = 167; variance uses the exact fractions
# sum(x^2)/N - mean^2 with sum(x^2) = 10535 and mean = 167/11:
# population variance = 87996/121, sample variance = 87996/110.
DATASET_A = [2, 4, 4, 5, 6, 7, 8, 9, 10, 12, 100]
A_SUM = 167
A_MEAN = Fraction(167, 11)
A_VARIANCE_POP = Fraction(87996, 121)
A_VARIANCE_SAMPLE = Fraction(87996, 110)
A_Q1, A_Q2, A_Q3 = 4.5, 7.0, 9.5
A_FENCE_LOWER, A_FENCE_UPPER = -3.0, 17.0

# Dataset B (4 values, even count).  Median = (2+3)/2 = 2.5.  Inclusive
# quartile positions 0.75, 1.5, 2.25 give q1 = 1 + 0.75*(2-1) = 1.75,
# q2 = 2.5 and q3 = 3 + 0.25*(10-3) = 4.75.  IQR = 3, fences -2.75 and
# 9.25, so 10 is an outlier.  Population variance = 50/4 = 12.5,
# sample variance = 50/3.  Every value occurs once, so all four are
# modes.
DATASET_B = [1, 2, 3, 10]
B_VARIANCE_POP = 12.5
B_VARIANCE_SAMPLE = Fraction(50, 3)
B_Q1, B_Q2, B_Q3 = 1.75, 2.5, 4.75
B_FENCE_LOWER, B_FENCE_UPPER = -2.75, 9.25


class CollectionStatsToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib CollectionStatsTool."""

    def setUp(self) -> None:
        self.tool = CollectionStatsTool()

    def assert_invalid(self, **kwargs) -> str:
        """Assert the call raises the standard ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        message = str(ctx.exception)
        self.assertIn("collection_stats_tool:", message)
        return message

    # ------------------------------------------------------------------ #
    # stats mode — ground truths
    # ------------------------------------------------------------------ #

    def test_stats_dataset_a_full_summary(self) -> None:
        result = self.tool.execute(mode="stats", numbers=list(DATASET_A))
        self.assertEqual(result["source"], "sequence")
        self.assertEqual(result["count"], 11)
        self.assertEqual(result["min"], 2.0)
        self.assertEqual(result["max"], 100.0)
        self.assertEqual(result["range"], 98.0)
        self.assertEqual(result["sum"], float(A_SUM))
        self.assertAlmostEqual(result["mean"], float(A_MEAN), places=12)
        self.assertEqual(result["median"], 7.0)
        self.assertEqual(result["mode"], [4.0])
        self.assertAlmostEqual(
            result["variance_population"], float(A_VARIANCE_POP), places=9
        )
        self.assertAlmostEqual(
            result["variance_sample"], float(A_VARIANCE_SAMPLE), places=9
        )
        self.assertEqual(result["quartiles"]["q1"], A_Q1)
        self.assertEqual(result["quartiles"]["q2"], A_Q2)
        self.assertEqual(result["quartiles"]["q3"], A_Q3)
        self.assertIn("inclusive", result["quartiles"]["method"])
        self.assertEqual(result["iqr"], 5.0)
        self.assertEqual(result["outlier_fences"]["lower"], A_FENCE_LOWER)
        self.assertEqual(result["outlier_fences"]["upper"], A_FENCE_UPPER)
        self.assertEqual(result["outliers"], [100.0])

    def test_stats_dataset_b_even_count(self) -> None:
        result = self.tool.execute(mode="stats", numbers=DATASET_B)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["sum"], 16.0)
        self.assertEqual(result["mean"], 4.0)
        self.assertEqual(result["median"], 2.5)
        self.assertEqual(result["mode"], [1.0, 2.0, 3.0, 10.0])
        self.assertAlmostEqual(
            result["variance_population"], B_VARIANCE_POP, places=12
        )
        self.assertAlmostEqual(
            result["variance_sample"], float(B_VARIANCE_SAMPLE), places=9
        )
        self.assertEqual(result["quartiles"]["q1"], B_Q1)
        self.assertEqual(result["quartiles"]["q2"], B_Q2)
        self.assertEqual(result["quartiles"]["q3"], B_Q3)
        self.assertEqual(result["iqr"], 3.0)
        self.assertEqual(result["outlier_fences"]["lower"], B_FENCE_LOWER)
        self.assertEqual(result["outlier_fences"]["upper"], B_FENCE_UPPER)
        self.assertEqual(result["outliers"], [10.0])

    def test_stats_unsorted_input_and_odd_median(self) -> None:
        result = self.tool.execute(mode="stats", numbers=[3, 1, 2])
        self.assertEqual(result["median"], 2.0)
        self.assertEqual(result["min"], 1.0)
        self.assertEqual(result["max"], 3.0)
        self.assertEqual(result["mode"], [1.0, 2.0, 3.0])

    def test_stats_mode_tie(self) -> None:
        result = self.tool.execute(mode="stats", numbers=[1, 1, 2, 2, 3])
        self.assertEqual(result["mode"], [1.0, 2.0])

    def test_stats_variance_stdev_cross_check_with_statistics(self) -> None:
        for data in (DATASET_A, DATASET_B, [5, -3, 12, 0.5, 7.25, -8]):
            result = self.tool.execute(mode="stats", numbers=list(data))
            self.assertAlmostEqual(
                result["variance_population"],
                statistics.pvariance(data),
                places=9,
            )
            self.assertAlmostEqual(
                result["variance_sample"], statistics.variance(data), places=9
            )
            self.assertAlmostEqual(
                result["stdev_population"], statistics.pstdev(data), places=9
            )
            self.assertAlmostEqual(
                result["stdev_sample"], statistics.stdev(data), places=9
            )
            q1, q2, q3 = statistics.quantiles(data, n=4, method="inclusive")
            self.assertAlmostEqual(result["quartiles"]["q1"], q1, places=12)
            self.assertAlmostEqual(result["quartiles"]["q2"], q2, places=12)
            self.assertAlmostEqual(
                result["quartiles"]["q3"], q3, places=12
            )
            # stdev is the exact square root of the variance, and the
            # IQR is exactly q3 - q1.
            self.assertAlmostEqual(
                result["stdev_population"] ** 2,
                result["variance_population"],
                places=9,
            )
            self.assertAlmostEqual(
                result["stdev_sample"] ** 2, result["variance_sample"], places=9
            )
            self.assertEqual(
                result["iqr"], result["quartiles"]["q3"] - result["quartiles"]["q1"]
            )

    def test_stats_median_quartiles_relationship(self) -> None:
        # q2 must equal the median for both parities.
        for data in (DATASET_A, DATASET_B, [7, -2], [1.5, 1.5, 9.0]):
            result = self.tool.execute(mode="stats", numbers=list(data))
            self.assertEqual(result["quartiles"]["q2"], result["median"])
            self.assertEqual(
                result["iqr"],
                result["quartiles"]["q3"] - result["quartiles"]["q1"],
            )

    def test_stats_deterministic(self) -> None:
        first = self.tool.execute(mode="stats", numbers=list(DATASET_A))
        second = self.tool.execute(mode="stats", numbers=list(DATASET_A))
        self.assertEqual(first, second)

    def test_stats_result_is_json_serializable(self) -> None:
        for mode_kwargs in (
            {"mode": "stats", "numbers": list(DATASET_A)},
            {"mode": "frequencies", "numbers": [1, 1, 2]},
            {"mode": "zscore", "numbers": [1, 2, 3, 4]},
        ):
            json.dumps(self.tool.execute(**mode_kwargs))

    # ------------------------------------------------------------------ #
    # frequencies mode
    # ------------------------------------------------------------------ #

    def test_frequencies_sorted_count_desc_then_value(self) -> None:
        result = self.tool.execute(
            mode="frequencies", numbers=[4, 1, 4, 3, 2, 4, 2]
        )
        self.assertEqual(result["count"], 7)
        self.assertEqual(result["distinct"], 4)
        self.assertEqual(
            result["frequencies"],
            [
                {"value": 4.0, "count": 3},
                {"value": 2.0, "count": 2},
                {"value": 1.0, "count": 1},
                {"value": 3.0, "count": 1},
            ],
        )
        self.assertNotIn("top_n", result)

    def test_frequencies_top_n(self) -> None:
        result = self.tool.execute(
            mode="frequencies", numbers=[4, 1, 4, 3, 2, 4, 2], top_n=2
        )
        self.assertEqual(result["top_n"], 2)
        self.assertEqual(
            result["frequencies"],
            [{"value": 4.0, "count": 3}, {"value": 2.0, "count": 2}],
        )

    def test_frequencies_top_n_above_distinct_returns_all(self) -> None:
        result = self.tool.execute(
            mode="frequencies", numbers=[1, 2, 2], top_n=99
        )
        self.assertEqual(result["distinct"], 2)
        self.assertEqual(
            result["frequencies"],
            [{"value": 2.0, "count": 2}, {"value": 1.0, "count": 1}],
        )

    # ------------------------------------------------------------------ #
    # zscore mode
    # ------------------------------------------------------------------ #

    def test_zscore_hand_computed(self) -> None:
        data = [1, 2, 3, 4]
        mean = 2.5
        stdev = math.sqrt(Fraction(5, 3))  # sample stdev of 1,2,3,4
        result = self.tool.execute(mode="zscore", numbers=data)
        self.assertEqual(result["mode"], "zscore")
        self.assertEqual(result["count"], 4)
        self.assertAlmostEqual(result["mean"], mean, places=12)
        self.assertAlmostEqual(result["stdev"], float(stdev), places=12)
        self.assertEqual(result["stdev_kind"], "sample")
        self.assertEqual(
            [entry["value"] for entry in result["zscores"]], [1.0, 2.0, 3.0, 4.0]
        )
        for value, entry in zip(data, result["zscores"]):
            self.assertAlmostEqual(
                entry["zscore"], (value - mean) / float(stdev), places=12
            )
        # The z-scores of a sample sum to zero.
        self.assertAlmostEqual(
            math.fsum(entry["zscore"] for entry in result["zscores"]),
            0.0,
            places=12,
        )

    def test_zscore_zero_stdev_structured_note(self) -> None:
        result = self.tool.execute(mode="zscore", numbers=[5, 5, 5])
        self.assertEqual(result["mean"], 5.0)
        self.assertEqual(result["stdev"], 0.0)
        self.assertEqual(
            result["zscores"],
            [
                {"value": 5.0, "zscore": None},
                {"value": 5.0, "zscore": None},
                {"value": 5.0, "zscore": None},
            ],
        )
        self.assertIn("stdev is 0", result["note"])
        self.assertIn("null", result["note"])

    def test_zscore_cross_check_with_statistics(self) -> None:
        data = [2.5, -1.25, 0.0, 7.5, 3.75]
        mean = statistics.fmean(data)
        stdev = statistics.stdev(data)
        result = self.tool.execute(mode="zscore", numbers=data)
        for value, entry in zip(data, result["zscores"]):
            self.assertAlmostEqual(
                entry["zscore"], (value - mean) / stdev, places=12
            )

    # ------------------------------------------------------------------ #
    # Parsing — accepted shapes
    # ------------------------------------------------------------------ #

    def test_parse_json_array_string(self) -> None:
        result = self.tool.execute(mode="stats", numbers="[1, 2.5, -3e2]")
        self.assertEqual(result["source"], "json_list")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["sum"], -296.5)

    def test_parse_one_per_line_text(self) -> None:
        result = self.tool.execute(
            mode="stats", numbers="1\n2.5\n-3e2\n\n  42 "
        )
        self.assertEqual(result["source"], "text")
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["sum"], -254.5)

    def test_parse_lenient_comma_and_space_separators(self) -> None:
        result = self.tool.execute(mode="stats", numbers="1, 2,3")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["sum"], 6.0)

    def test_parse_sequence_and_tuple(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="stats", numbers=[1, 2, 3])["count"], 3
        )
        self.assertEqual(
            self.tool.execute(mode="stats", numbers=(4, 6))["mean"], 5.0
        )

    def test_parse_numeric_string_elements_lenient(self) -> None:
        result = self.tool.execute(mode="stats", numbers=[" 1 ", "2.5"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["sum"], 3.5)

    def test_parse_count_bounds(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="stats", numbers="1\n2")["count"], 2
        )
        exact_max = "\n".join(["1"] * 10000)
        self.assertEqual(
            self.tool.execute(mode="stats", numbers=exact_max)["count"], 10000
        )
        self.assertEqual(
            self.tool.execute(mode="stats", numbers=exact_max)["mean"], 1.0
        )

    # ------------------------------------------------------------------ #
    # Parsing — content-level error payloads
    # ------------------------------------------------------------------ #

    def assert_content_error(self, error_type: str, **kwargs) -> dict:
        result = self.tool.execute(**kwargs)
        self.assertIn("error", result)
        self.assertEqual(result["error"]["type"], error_type)
        return result

    def test_error_non_numeric_token_reports_line_and_token(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="1\nfoo\n3"
        )
        self.assertIn("line 2", result["error"]["message"])
        self.assertIn("'foo'", result["error"]["message"])

    def test_error_non_numeric_token_position_within_line(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="1 2 x"
        )
        self.assertIn("line 1, token 3", result["error"]["message"])

    def test_error_nan_token_rejected(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="nan\n1"
        )
        self.assertIn("'nan'", result["error"]["message"])
        self.assertIn("line 1", result["error"]["message"])

    def test_error_infinity_token_rejected(self) -> None:
        self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="inf\n1\n2"
        )

    def test_error_exponent_overflow_rejected(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="1e999"
        )
        self.assertIn("not finite", result["error"]["message"])

    def test_error_underscore_and_hex_tokens_rejected(self) -> None:
        self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="1_0\n2\n3"
        )
        self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="0x10\n2\n3"
        )

    def test_error_json_non_numeric_element(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers='[1, "abc"]'
        )
        self.assertIn("index 1", result["error"]["message"])

    def test_error_json_nan_element(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="[1, NaN]"
        )
        self.assertIn("not finite", result["error"]["message"])

    def test_error_json_infinity_element(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="[Infinity, 1]"
        )
        self.assertIn("index 0", result["error"]["message"])

    def test_error_json_bool_element(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers="[true, 1]"
        )
        self.assertIn("index 0", result["error"]["message"])

    def test_error_sequence_bool_element(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers=[True, 2]
        )
        self.assertIn("index 0", result["error"]["message"])

    def test_error_sequence_int_overflow(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers=[10**400, 1]
        )
        self.assertIn("floating-point range", result["error"]["message"])

    def test_error_sequence_non_numeric_element(self) -> None:
        result = self.assert_content_error(
            "invalid_numbers", mode="stats", numbers=[1, None, 3]
        )
        self.assertIn("index 1", result["error"]["message"])

    def test_error_malformed_json_reports_position(self) -> None:
        result = self.assert_content_error(
            "invalid_json", mode="stats", numbers="[1, 2"
        )
        self.assertIn("column", result["error"]["message"])

    def test_error_payload_keeps_mode_context(self) -> None:
        result = self.tool.execute(mode="frequencies", numbers="1\nx\n2")
        self.assertEqual(result["mode"], "frequencies")
        self.assertEqual(result["error"]["type"], "invalid_numbers")

    # ------------------------------------------------------------------ #
    # Parameter-level error matrix (ValueError)
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="summary", numbers=[1, 2])
        self.assert_invalid(mode="STATS", numbers=[1, 2])
        self.assert_invalid(mode=None, numbers=[1, 2])

    def test_missing_or_wrong_numbers_type(self) -> None:
        self.assert_invalid(mode="stats")
        self.assert_invalid(mode="stats", numbers=None)
        self.assert_invalid(mode="stats", numbers=True)
        self.assert_invalid(mode="stats", numbers=42)
        self.assert_invalid(mode="stats", numbers={"a": 1})

    def test_invalid_count_bounds(self) -> None:
        self.assert_invalid(mode="stats", numbers=[1])
        self.assert_invalid(mode="stats", numbers="5")
        self.assert_invalid(mode="stats", numbers="[3]")
        self.assert_invalid(mode="stats", numbers="")
        self.assert_invalid(mode="stats", numbers="   \n ")
        self.assert_invalid(mode="zscore", numbers=[4])
        self.assert_invalid(mode="stats", numbers="\n".join(["1"] * 10001))

    def test_invalid_input_text_length(self) -> None:
        result = self.assert_invalid(
            mode="stats", numbers="1 " * 100001  # 200,002 characters
        )
        self.assertIn("character limit", str(result))

    def test_invalid_top_n(self) -> None:
        for bad in (0, -2, True, "3", 1.5):
            self.assert_invalid(
                mode="frequencies", numbers=[1, 1, 2], top_n=bad
            )
        # None stays valid and simply means "no truncation".
        result = self.tool.execute(
            mode="frequencies", numbers=[1, 1, 2], top_n=None
        )
        self.assertNotIn("top_n", result)

    def test_top_n_ignored_for_other_modes(self) -> None:
        result = self.tool.execute(mode="stats", numbers=[1, 2, 3], top_n=1)
        self.assertNotIn("frequencies", result)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectCollectionStatsTool, CollectionStatsTool)
        self.assertEqual(self.tool.name, "collection_stats_tool")
        self.assertIn("frequencies", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("CollectionStatsTool", __all__)


if __name__ == "__main__":
    unittest.main()
