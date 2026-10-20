#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_sequence_analyzer_tool.py

"""Offline unit tests for SequenceAnalyzerTool.

The tool is built purely on the standard library ``decimal`` module
and never touches the network, the clock or any randomness source,
so this suite runs fully offline and every assertion is
deterministic.

Two kinds of ground truth are combined. Classic textbook sequences
are pinned as literal expected values (arithmetic ``[1, 3, 5, 7, 9]``
with difference 2, geometric ``[2, 4, 8, 16, 32]`` with ratio 2,
Fibonacci ``[0, 1, 1, 2, 3, 5, 8, 13]`` predicting 21, triangular
``[0, 1, 3, 6, 10]`` as quadratic with second difference 1, the prime
run ``[2, 3, 5, 7, 11, 13]``), and structural properties — exact
Decimal detection, multi-type overlap, the strongest-type priority,
missing-value recovery per type, and the full validation error
matrix — are exercised on hand-computed cases including the
documented resolution rules: flat evidence outranks bridging in the
missing mode (``[null, 16, 64, 256]`` -> 4 geometric, not the
vacuous quadratic 112), a bridging fibonacci fit recovers
``[1, 1, 2, 3, null, 8]`` -> 5 even though the remaining terms alone
are not fibonacci-like, and ``[3, 6, 9, null]`` -> 15 because the
remaining terms are both arithmetic and fibonacci-like and the
priority prefers the latter.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import SequenceAnalyzerTool
from agentuniverse.agent.action.tool.common_tool.sequence_analyzer_tool import (
    SequenceAnalyzerTool as DirectSequenceAnalyzerTool,
)


class SequenceAnalyzerToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib analyzer."""

    def setUp(self) -> None:
        self.tool = SequenceAnalyzerTool()

    # ------------------------------------------------------------------ #
    # classify — classic sequences, one type each (literal ground truth)
    # ------------------------------------------------------------------ #

    def test_classify_arithmetic(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[1, 3, 5, 7, 9])
        self.assertEqual(result["types"], ["arithmetic"])
        self.assertEqual(result["strongest_type"], "arithmetic")
        self.assertEqual(result["params"], {"difference": 2})
        self.assertEqual(result["next_term"], 11)
        self.assertEqual(result["next_term_confidence"], 0.8)  # 0.6 + 2*0.1

    def test_classify_arithmetic_negative_difference(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[10, 7, 4, 1])
        self.assertEqual(result["types"], ["arithmetic"])
        self.assertEqual(result["params"], {"difference": -3})
        self.assertEqual(result["next_term"], -2)

    def test_classify_arithmetic_exact_decimals(self) -> None:
        # Floats enter through str(), so binary float noise cannot
        # break exactness: 0.2 - 0.1 is exactly 0.1 in Decimal.
        result = self.tool.execute(
            mode="classify", sequence=[0.1, 0.2, 0.3, 0.4]
        )
        self.assertEqual(result["types"], ["arithmetic"])
        self.assertEqual(result["params"]["difference"], 0.1)
        self.assertEqual(result["next_term"], 0.5)

    def test_classify_arithmetic_fractional_step(self) -> None:
        result = self.tool.execute(
            mode="classify", sequence=[0.5, 1.0, 1.5, 2.0]
        )
        self.assertEqual(result["types"], ["arithmetic"])
        self.assertEqual(result["params"]["difference"], 0.5)
        self.assertEqual(result["next_term"], 2.5)

    def test_classify_geometric_ratio_two(self) -> None:
        result = self.tool.execute(
            mode="classify", sequence=[2, 4, 8, 16, 32]
        )
        self.assertEqual(result["types"], ["geometric"])
        self.assertEqual(result["strongest_type"], "geometric")
        self.assertEqual(result["params"], {"ratio": 2})
        self.assertEqual(result["next_term"], 64)

    def test_classify_geometric_ratio_below_one(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[64, 32, 16, 8])
        self.assertEqual(result["types"], ["geometric"])
        self.assertEqual(result["params"]["ratio"], 0.5)
        self.assertEqual(result["next_term"], 4)

    def test_classify_geometric_non_terminating_ratio(self) -> None:
        # Ratio 1/3 cannot be written as a finite decimal; detection
        # still holds (exact cross-multiplication) and the predicted
        # next term 3*3/9 is exactly 1.
        result = self.tool.execute(mode="classify", sequence=[81, 27, 9, 3])
        self.assertEqual(result["types"], ["geometric"])
        self.assertAlmostEqual(result["params"]["ratio"], 1 / 3, places=15)
        self.assertEqual(result["next_term"], 1)

    def test_classify_geometric_negative_terms(self) -> None:
        # All-negative terms share a sign, so the ratio is +2.
        result = self.tool.execute(
            mode="classify", sequence=[-2, -4, -8, -16]
        )
        self.assertEqual(result["types"], ["geometric"])
        self.assertEqual(result["params"]["ratio"], 2)
        self.assertEqual(result["next_term"], -32)

    def test_classify_geometric_alternating_sign_excluded(self) -> None:
        # Ratio -2 < 0 is outside the documented geometric contract.
        result = self.tool.execute(mode="classify", sequence=[1, -2, 4, -8])
        self.assertEqual(result["types"], ["none"])
        self.assertIsNone(result["next_term"])

    def test_classify_fibonacci(self) -> None:
        result = self.tool.execute(
            mode="classify", sequence=[0, 1, 1, 2, 3, 5, 8, 13]
        )
        self.assertEqual(result["types"], ["fibonacci-like"])
        self.assertEqual(result["strongest_type"], "fibonacci-like")
        self.assertEqual(result["params"], {})
        self.assertEqual(result["next_term"], 21)
        self.assertEqual(result["next_term_confidence"], 0.99)  # capped

    def test_classify_fibonacci_lucas_style(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[2, 1, 3, 4, 7, 11])
        self.assertEqual(result["types"], ["fibonacci-like"])
        self.assertEqual(result["next_term"], 18)

    def test_classify_quadratic_squares(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[1, 4, 9, 16, 25])
        self.assertEqual(result["types"], ["quadratic"])
        self.assertEqual(result["strongest_type"], "quadratic")
        self.assertEqual(result["params"], {"second_difference": 2})
        self.assertEqual(result["next_term"], 36)
        self.assertEqual(result["next_term_confidence"], 0.7)  # 0.6 + 1*0.1

    def test_classify_quadratic_triangular(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[0, 1, 3, 6, 10])
        self.assertEqual(result["types"], ["quadratic"])
        self.assertEqual(result["params"]["second_difference"], 1)
        self.assertEqual(result["next_term"], 15)

    def test_classify_quadratic_needs_four_terms(self) -> None:
        # A 3-term sequence has a single second difference, which is
        # vacuously constant: quadratic stays undecidable and cannot
        # shadow the geometric reading.
        result = self.tool.execute(mode="classify", sequence=[1, 2, 4])
        self.assertEqual(result["types"], ["geometric"])
        self.assertEqual(result["next_term"], 8)

    def test_classify_arithmetic_is_not_double_reported_quadratic(self) -> None:
        # Zero second difference reduces to arithmetic by definition.
        result = self.tool.execute(mode="classify", sequence=[3, 6, 9, 12])
        self.assertEqual(result["types"], ["arithmetic"])
        self.assertNotIn("quadratic", result["types"])

    def test_classify_primes(self) -> None:
        result = self.tool.execute(
            mode="classify", sequence=[2, 3, 5, 7, 11, 13]
        )
        self.assertEqual(result["types"], ["primes"])
        self.assertIsNone(result["strongest_type"])
        self.assertIsNone(result["next_term"])
        self.assertEqual(result["next_term_confidence"], 0.0)

    def test_classify_primes_large_prime_within_bound(self) -> None:
        # 999999999989 is the largest prime below 10**12.
        result = self.tool.execute(
            mode="classify", sequence=[3, 5, 999999999989]
        )
        self.assertEqual(result["types"], ["primes"])
        self.assertIsNone(result["next_term"])

    def test_classify_primes_bound_skips_large_integers(self) -> None:
        # Documented bound: integers >= 10**12 skip the primes check.
        result = self.tool.execute(
            mode="classify", sequence=[2, 3, 999999999999999]
        )
        self.assertEqual(result["types"], ["none"])

    def test_classify_primes_rejects_non_primes(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[2, 3, 4, 5])
        self.assertNotIn("primes", result["types"])

    def test_classify_none_type_random(self) -> None:
        result = self.tool.execute(mode="classify", sequence=[3, 1, 4, 1, 5, 9])
        self.assertEqual(result["types"], ["none"])
        self.assertIsNone(result["strongest_type"])
        self.assertIsNone(result["next_term"])
        self.assertEqual(result["params"], {})
        self.assertEqual(result["next_term_confidence"], 0.0)

    # ------------------------------------------------------------------ #
    # classify — multi-type overlap and strongest-type priority
    # ------------------------------------------------------------------ #

    def test_classify_constant_multi_type_documented(self) -> None:
        # A constant sequence is arithmetic (d=0) and, when non-zero,
        # geometric (r=1) — documented overlap; priority then lets
        # geometric predict (the same value 6 regardless).
        result = self.tool.execute(mode="classify", sequence=[6, 6, 6, 6])
        self.assertEqual(
            result["types"], ["arithmetic", "geometric", "constant"]
        )
        self.assertEqual(result["strongest_type"], "geometric")
        self.assertEqual(result["params"], {"difference": 0, "ratio": 1})
        self.assertEqual(result["next_term"], 6)

    def test_classify_zero_constant_is_also_fibonacci(self) -> None:
        # 0 = 0 + 0, so [0, 0, 0] is fibonacci-like too; fibonacci
        # outranks geometric (absent here: zero terms), arithmetic
        # and constant.
        result = self.tool.execute(mode="classify", sequence=[0, 0, 0])
        self.assertEqual(
            result["types"], ["arithmetic", "fibonacci-like", "constant"]
        )
        self.assertEqual(result["strongest_type"], "fibonacci-like")
        self.assertEqual(result["next_term"], 0)

    def test_classify_fibonacci_and_primes_overlap(self) -> None:
        # 5 = 2 + 3 and all three terms are prime.
        result = self.tool.execute(mode="classify", sequence=[2, 3, 5])
        self.assertEqual(result["types"], ["fibonacci-like", "primes"])
        self.assertEqual(result["strongest_type"], "fibonacci-like")
        self.assertEqual(result["next_term"], 8)
        self.assertEqual(result["next_term_confidence"], 0.6)

    def test_classify_fibonacci_priority_over_arithmetic(self) -> None:
        # [5, 10, 15] is both arithmetic (d=5) and fibonacci-like
        # (15 = 5 + 10); the priority predicts 25 (= 10 + 15), not
        # the arithmetic 20.
        result = self.tool.execute(mode="classify", sequence=[5, 10, 15])
        self.assertEqual(
            result["types"], ["arithmetic", "fibonacci-like"]
        )
        self.assertEqual(result["strongest_type"], "fibonacci-like")
        self.assertEqual(result["next_term"], 25)

    def test_classify_quadratic_priority_over_others(self) -> None:
        # Overlap between quadratic and anything predicting a
        # different value is impossible by construction (non-zero
        # second difference conflicts with every weaker type); the
        # payload still reports the priority pick explicitly.
        result = self.tool.execute(
            mode="classify", sequence=[2, 3, 5, 8, 12, 17, 23, 30]
        )
        self.assertEqual(result["types"], ["quadratic"])
        self.assertEqual(result["strongest_type"], "quadratic")
        self.assertEqual(result["params"], {"second_difference": 1})
        self.assertEqual(result["next_term"], 38)

    def test_classify_echoes_sequence(self) -> None:
        sequence = [4, -1.5, 6, 13.5]
        result = self.tool.execute(mode="classify", sequence=sequence)
        self.assertEqual(result["sequence"], sequence)
        self.assertEqual(result["mode"], "classify")

    def test_classify_minimum_and_maximum_lengths(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="classify", sequence=[1, 1, 1])["types"][
                0
            ],
            "arithmetic",
        )
        long_sequence = [2 * i for i in range(100)]  # 100 terms
        result = self.tool.execute(mode="classify", sequence=long_sequence)
        self.assertEqual(result["types"], ["arithmetic"])
        self.assertEqual(result["next_term"], 200)
        self.assertEqual(result["next_term_confidence"], 0.99)  # capped

    # ------------------------------------------------------------------ #
    # next_n — continuation chains per strongest type
    # ------------------------------------------------------------------ #

    def test_next_n_arithmetic_chain(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[1, 3, 5], k=4)
        self.assertEqual(result["strongest_type"], "arithmetic")
        self.assertEqual(result["k"], 4)
        self.assertEqual(result["next_terms"], [7, 9, 11, 13])

    def test_next_n_geometric_chain(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[2, 6, 18], k=3)
        self.assertEqual(result["strongest_type"], "geometric")
        self.assertEqual(result["next_terms"], [54, 162, 486])

    def test_next_n_geometric_fractional_chain(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[64, 32, 16], k=3)
        self.assertEqual(result["next_terms"], [8, 4, 2])

    def test_next_n_geometric_non_terminating_chain(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[81, 27, 9], k=3)
        self.assertEqual(result["next_terms"][0], 3)
        self.assertEqual(result["next_terms"][1], 1)
        self.assertAlmostEqual(result["next_terms"][2], 1 / 3, places=15)

    def test_next_n_fibonacci_chain(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[1, 1, 2], k=5)
        self.assertEqual(result["strongest_type"], "fibonacci-like")
        self.assertEqual(result["next_terms"], [3, 5, 8, 13, 21])

    def test_next_n_quadratic_chain(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[1, 4, 9, 16], k=3)
        self.assertEqual(result["strongest_type"], "quadratic")
        self.assertEqual(result["next_terms"], [25, 36, 49])

    def test_next_n_constant_chain(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[9, 9, 9], k=2)
        self.assertEqual(result["strongest_type"], "geometric")  # r = 1
        self.assertEqual(result["next_terms"], [9, 9])

    def test_next_n_k_one(self) -> None:
        result = self.tool.execute(mode="next_n", sequence=[5, 10, 15, 20], k=1)
        self.assertEqual(result["strongest_type"], "arithmetic")
        self.assertEqual(result["next_terms"], [25])

    def test_next_n_k_digit_string(self) -> None:
        result = self.tool.execute(
            mode="next_n", sequence=[5, 10, 15, 20], k="3"
        )
        self.assertEqual(result["k"], 3)
        self.assertEqual(result["next_terms"], [25, 30, 35])

    def test_next_n_none_type_cannot_extend(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="next_n", sequence=[3, 1, 4, 1, 5, 9], k=2)

    def test_next_n_primes_only_cannot_extend(self) -> None:
        # Primality is a property, not a generator.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="next_n", sequence=[2, 3, 5, 7], k=1)

    # ------------------------------------------------------------------ #
    # missing — single-null recovery per type (literal ground truth)
    # ------------------------------------------------------------------ #

    def test_missing_arithmetic_interior(self) -> None:
        result = self.tool.execute(
            mode="missing", sequence=[2, 4, None, 8, 10]
        )
        self.assertEqual(result["missing_index"], 2)
        self.assertEqual(result["missing_value"], 6)
        self.assertEqual(result["type"], "arithmetic")
        self.assertEqual(
            result["completed_sequence"], [2, 4, 6, 8, 10]
        )

    def test_missing_arithmetic_leading(self) -> None:
        result = self.tool.execute(
            mode="missing", sequence=[None, 4, 8, 12, 16]
        )
        self.assertEqual(result["missing_value"], 0)
        self.assertEqual(result["type"], "arithmetic")

    def test_missing_arithmetic_trailing(self) -> None:
        result = self.tool.execute(mode="missing", sequence=[2, 4, 6, 8, None])
        self.assertEqual(result["missing_value"], 10)
        self.assertEqual(result["type"], "arithmetic")

    def test_missing_arithmetic_priority_quirk_fibonacci_wins(self) -> None:
        # [3, 6, 9, 15] is genuinely fibonacci-like AND [3, 6, 9, 12]
        # is genuinely arithmetic; the documented priority order
        # (fibonacci-like > arithmetic) resolves to 15.
        result = self.tool.execute(mode="missing", sequence=[3, 6, 9, None])
        self.assertEqual(result["missing_value"], 15)
        self.assertEqual(result["type"], "fibonacci-like")

    def test_missing_geometric_interior(self) -> None:
        result = self.tool.execute(
            mode="missing", sequence=[3, 6, None, 24, 48]
        )
        self.assertEqual(result["missing_value"], 12)
        self.assertEqual(result["type"], "geometric")

    def test_missing_geometric_negative_terms(self) -> None:
        result = self.tool.execute(
            mode="missing", sequence=[-2, -4, None, -16, -32]
        )
        self.assertEqual(result["missing_value"], -8)
        self.assertEqual(result["type"], "geometric")

    def test_missing_geometric_leading(self) -> None:
        result = self.tool.execute(mode="missing", sequence=[None, 16, 64, 256])
        self.assertEqual(result["missing_value"], 4)
        self.assertEqual(result["type"], "geometric")

    def test_missing_fibonacci_classic(self) -> None:
        # The remaining flat terms [1, 1, 2, 3, 8] are not themselves
        # fibonacci-like — only the position-aware fit recovers 5.
        result = self.tool.execute(
            mode="missing", sequence=[1, 1, 2, 3, None, 8]
        )
        self.assertEqual(result["missing_index"], 4)
        self.assertEqual(result["missing_value"], 5)
        self.assertEqual(result["type"], "fibonacci-like")
        self.assertEqual(
            result["completed_sequence"], [1, 1, 2, 3, 5, 8]
        )

    def test_missing_fibonacci_leading(self) -> None:
        result = self.tool.execute(mode="missing", sequence=[None, 1, 1, 2, 3])
        self.assertEqual(result["missing_value"], 0)
        self.assertEqual(result["type"], "fibonacci-like")

    def test_missing_fibonacci_trailing(self) -> None:
        result = self.tool.execute(mode="missing", sequence=[3, 5, 8, 13, None])
        self.assertEqual(result["missing_value"], 21)
        self.assertEqual(result["type"], "fibonacci-like")

    def test_missing_quadratic_interior(self) -> None:
        result = self.tool.execute(
            mode="missing", sequence=[1, 4, 9, None, 25, 36]
        )
        self.assertEqual(result["missing_value"], 16)
        self.assertEqual(result["type"], "quadratic")

    def test_missing_quadratic_leading(self) -> None:
        result = self.tool.execute(
            mode="missing", sequence=[None, 3, 6, 10, 15]
        )
        self.assertEqual(result["missing_value"], 1)
        self.assertEqual(result["type"], "quadratic")

    def test_missing_flat_evidence_outranks_bridging(self) -> None:
        # Any three numbers admit a vacuous "constant" second
        # difference, so a pure priority scan would let quadratic
        # claim [null, 16, 64, 256] with 112; the remaining terms are
        # geometric, and flat evidence wins: 4.
        result = self.tool.execute(
            mode="missing", sequence=[None, 16, 64, 256]
        )
        self.assertEqual(result["missing_value"], 4)
        self.assertEqual(result["type"], "geometric")
        self.assertEqual(
            result["completed_sequence"], [4, 16, 64, 256]
        )

    def test_missing_flat_evidence_short_geometric_run(self) -> None:
        result = self.tool.execute(mode="missing", sequence=[None, 2, 4, 8])
        self.assertEqual(result["missing_value"], 1)
        self.assertEqual(result["type"], "geometric")

    def test_missing_constant_from_flat_evidence(self) -> None:
        # The remaining terms [7, 7, 7] are arithmetic + geometric
        # (r = 1) + constant; priority picks geometric, filling 7
        # (a fibonacci-like completion [7, 0, 7, 7] also exists but
        # is only reachable through the weaker bridging tier).
        result = self.tool.execute(mode="missing", sequence=[7, None, 7, 7])
        self.assertEqual(result["missing_value"], 7)
        self.assertEqual(result["type"], "geometric")
        self.assertEqual(result["completed_sequence"], [7, 7, 7, 7])

    def test_missing_constant_clean_tail(self) -> None:
        # [5, 5, 5, 10] breaks the fibonacci recurrence, so the
        # geometric (r = 1) completion is the strongest that fits.
        result = self.tool.execute(mode="missing", sequence=[5, 5, 5, None])
        self.assertEqual(result["missing_value"], 5)
        self.assertEqual(result["type"], "geometric")

    def test_missing_null_string_markers(self) -> None:
        for marker in ("null", "None"):
            result = self.tool.execute(
                mode="missing", sequence=[2, 4, marker, 8, 10]
            )
            self.assertEqual(result["missing_value"], 6)
            self.assertEqual(
                result["completed_sequence"], [2, 4, 6, 8, 10]
            )

    def test_missing_unresolvable_non_terminating_fill(self) -> None:
        # The only quadratic completion would be 10/3, which no exact
        # Decimal sequence can verify; nothing weaker fits either.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="missing", sequence=[0, 1, None, 7, 9])

    def test_missing_unresolvable_mixed_growth(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="missing", sequence=[1, 2, 4, None, 9])

    # ------------------------------------------------------------------ #
    # Validation error matrix (strict, raised before any computation)
    # ------------------------------------------------------------------ #

    def _assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_error_unknown_mode(self) -> None:
        self._assert_invalid(mode="detect", sequence=[1, 2, 3])
        self._assert_invalid(mode=None, sequence=[1, 2, 3])

    def test_error_sequence_not_a_list(self) -> None:
        self._assert_invalid(mode="classify", sequence="1,2,3")
        self._assert_invalid(mode="classify", sequence=None)
        self._assert_invalid(mode="classify", sequence=17)

    def test_error_sequence_length_bounds(self) -> None:
        self._assert_invalid(mode="classify", sequence=[1, 2])
        self._assert_invalid(mode="classify", sequence=list(range(101)))

    def test_error_boolean_trap(self) -> None:
        self._assert_invalid(mode="classify", sequence=[1, True, 3])
        self._assert_invalid(mode="next_n", sequence=[1, 2, 3], k=True)

    def test_error_non_finite_floats(self) -> None:
        self._assert_invalid(mode="classify", sequence=[1.0, float("nan"), 3.0])
        self._assert_invalid(
            mode="classify", sequence=[1.0, float("inf"), 3.0]
        )

    def test_error_non_number_elements(self) -> None:
        self._assert_invalid(mode="classify", sequence=[1, "3", 5])
        self._assert_invalid(mode="classify", sequence=[1, None, 3])

    def test_error_k_bounds(self) -> None:
        self._assert_invalid(mode="next_n", sequence=[1, 2, 3], k=0)
        self._assert_invalid(mode="next_n", sequence=[1, 2, 3], k=11)
        self._assert_invalid(mode="next_n", sequence=[1, 2, 3], k=None)
        self._assert_invalid(mode="next_n", sequence=[1, 2, 3], k=1.5)
        self._assert_invalid(mode="next_n", sequence=[1, 2, 3], k="many")

    def test_error_k_only_for_next_n(self) -> None:
        self._assert_invalid(mode="classify", sequence=[1, 2, 3], k=2)
        self._assert_invalid(
            mode="missing", sequence=[1, 2, None, 4], k=2
        )

    def test_error_missing_requires_exactly_one_null(self) -> None:
        self._assert_invalid(mode="missing", sequence=[1, 2, 3, 4])
        self._assert_invalid(mode="missing", sequence=[1, None, 3, None])

    def test_error_missing_length_bounds(self) -> None:
        self._assert_invalid(mode="missing", sequence=[1, 2, None])
        self._assert_invalid(
            mode="missing", sequence=[0] * 100 + [None]
        )

    def test_error_messages_are_prefixed(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="classify", sequence=[1, 2])
        self.assertTrue(
            str(ctx.exception).startswith("sequence_analyzer_tool:")
        )

    # ------------------------------------------------------------------ #
    # Determinism and output hygiene
    # ------------------------------------------------------------------ #

    def test_deterministic_repeated_calls(self) -> None:
        first = self.tool.execute(
            mode="classify", sequence=[1.5, 2.5, 3.5, 4.5]
        )
        second = self.tool.execute(
            mode="classify", sequence=[1.5, 2.5, 3.5, 4.5]
        )
        self.assertEqual(first, second)
        self.assertEqual(
            repr(first["next_term"]), repr(second["next_term"])
        )

    def test_results_are_json_serializable(self) -> None:
        payloads = [
            self.tool.execute(mode="classify", sequence=[2, 4, 8, 16]),
            self.tool.execute(mode="next_n", sequence=[1, 4, 9, 16], k=3),
            self.tool.execute(
                mode="missing", sequence=[1, 1, 2, None, 5, 8]
            ),
        ]
        for payload in payloads:
            json.dumps(payload)  # must not raise

    def test_tuple_sequence_accepted(self) -> None:
        result = self.tool.execute(mode="classify", sequence=(3, 6, 9, 12))
        self.assertEqual(result["types"], ["arithmetic"])

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(SequenceAnalyzerTool, DirectSequenceAnalyzerTool)


if __name__ == "__main__":
    unittest.main()
