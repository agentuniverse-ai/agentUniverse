#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_matrix_ops_tool.py

"""Offline unit tests for MatrixOpsTool.

The tool is built purely on the standard library (json, math, re,
fractions) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: transforms are checked
against hand-computed ground truths on non-square matrices,
determinants against exact known values (including a big-integer case
where floating point would cancel the answer away), and the error
contract against fixed messages and payloads.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import MatrixOpsTool
from agentuniverse.agent.action.tool.common_tool.matrix_ops_tool import (
    MatrixOpsTool as DirectMatrixOpsTool,
)

# --------------------------------------------------------------------- #
# Hand-computed ground truths
# --------------------------------------------------------------------- #
A_2X3 = [[1, 2, 3], [4, 5, 6]]
TRANSPOSED_A = [[1, 4], [2, 5], [3, 6]]
ANTI_TRANSPOSED_A = [[6, 3], [5, 2], [4, 1]]
ROT90_A = [[4, 1], [5, 2], [6, 3]]
ROT180_A = [[6, 5, 4], [3, 2, 1]]
ROT270_A = [[3, 6], [2, 5], [1, 4]]
B_3X2 = [[7, 8], [9, 10], [11, 12]]
PRODUCT_A_B = [[58, 64], [139, 154]]
ZIGZAG_3X3 = [1, 2, 4, 7, 5, 3, 6, 8, 9]  # JPEG order on [[1..9]]
ZIGZAG_A_2X3 = [1, 2, 4, 5, 3, 6]
# det([[2,0,1],[1,3,2],[1,1,4]]) = 2*(3*4-2*1) - 0*(1*4-2*1) + 1*(1*1-3*1) = 18
DET_3X3 = 18
# Deterministic cancellation victim: exact det is -2, but ~1e20-magnitude
# products lose it in double precision.
BIG = 10 ** 10
BIG_MATRIX = [[BIG, BIG + 1], [BIG + 2, BIG + 3]]
BIG_MATRIX_FLOAT = [[1e10, 1e10 + 1], [1e10 + 2, 1e10 + 3]]
FIVE_BY_FIVE = [
    [2, 7, 1, 5, 3],
    [0, 3, 9, 2, 8],
    [0, 0, 4, 6, 1],
    [0, 0, 0, 5, 7],
    [0, 0, 0, 0, 6],
]
# Upper triangular: det = product of the diagonal = 2*3*4*5*6 = 720.
DET_5X5 = 720
SYMMETRIC_3X3 = [[1, 2, 3], [2, 5, 6], [3, 6, 9]]


def _error_of(payload):
    """Extract the structured error dict from a tool payload."""
    return payload["error"]


class MatrixOpsToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib MatrixOpsTool."""

    def setUp(self) -> None:
        self.tool = MatrixOpsTool()

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def test_info_symmetric_square_matrix(self) -> None:
        result = self.tool.execute(mode="info", matrix=SYMMETRIC_3X3)
        self.assertEqual(
            result,
            {
                "mode": "info",
                "rows": 3,
                "cols": 3,
                "shape": [3, 3],
                "size": 9,
                "square": True,
                "symmetric": True,
                "tolerance": 1e-9,
                "diagonal": [1, 5, 9],
                "trace": 15,
            },
        )

    def test_info_asymmetric_square_matrix(self) -> None:
        result = self.tool.execute(mode="info", matrix=[[1, 2], [3, 4]])
        self.assertFalse(result["symmetric"])
        self.assertTrue(result["square"])
        self.assertEqual(result["diagonal"], [1, 4])

    def test_info_non_square_reports_partial_diagonal(self) -> None:
        result = self.tool.execute(mode="info", matrix=A_2X3)
        self.assertEqual(
            result["shape"], [2, 3],
        )
        self.assertFalse(result["square"])
        self.assertFalse(result["symmetric"])
        self.assertEqual(result["diagonal"], [1, 5])
        self.assertEqual(result["trace"], 6)
        self.assertEqual(result["size"], 6)

    def test_info_symmetry_within_default_tolerance(self) -> None:
        near = [[0.0, 1e-10], [1e-10, 2.0]]
        result = self.tool.execute(mode="info", matrix=near)
        self.assertTrue(result["symmetric"])

    def test_info_symmetry_outside_default_tolerance(self) -> None:
        off = [[0.0, 1e-6], [0.0, 2.0]]
        result = self.tool.execute(mode="info", matrix=off)
        self.assertFalse(result["symmetric"])

    def test_info_custom_tolerance(self) -> None:
        off = [[0.0, 1e-6], [0.0, 2.0]]
        self.assertFalse(
            self.tool.execute(mode="info", matrix=off)["symmetric"]
        )
        self.assertTrue(
            self.tool.execute(mode="info", matrix=off, tolerance=1e-3)[
                "symmetric"
            ]
        )

    def test_info_1x1_is_symmetric(self) -> None:
        result = self.tool.execute(mode="info", matrix=[[7]])
        self.assertTrue(result["square"])
        self.assertTrue(result["symmetric"])
        self.assertEqual(result["diagonal"], [7])

    # ------------------------------------------------------------------ #
    # transpose mode
    # ------------------------------------------------------------------ #

    def test_transpose_non_square(self) -> None:
        result = self.tool.execute(mode="transpose", matrix=A_2X3)
        self.assertEqual(
            result,
            {
                "mode": "transpose",
                "anti": False,
                "shape": [3, 2],
                "result": TRANSPOSED_A,
            },
        )

    def test_transpose_anti_diagonal_2x2(self) -> None:
        result = self.tool.execute(
            mode="transpose", matrix=[[1, 2], [3, 4]], anti=True
        )
        self.assertEqual(result["result"], [[4, 2], [3, 1]])
        self.assertTrue(result["anti"])

    def test_transpose_anti_diagonal_non_square(self) -> None:
        result = self.tool.execute(mode="transpose", matrix=A_2X3, anti=True)
        self.assertEqual(result["result"], ANTI_TRANSPOSED_A)
        self.assertEqual(result["shape"], [3, 2])

    def test_transpose_anti_single_row(self) -> None:
        result = self.tool.execute(mode="transpose", matrix=[[1, 2, 3]], anti=True)
        self.assertEqual(result["result"], [[3], [2], [1]])

    def test_transpose_round_trips(self) -> None:
        once = self.tool.execute(mode="transpose", matrix=A_2X3)["result"]
        twice = self.tool.execute(mode="transpose", matrix=once)["result"]
        self.assertEqual(twice, A_2X3)
        anti_once = self.tool.execute(
            mode="transpose", matrix=A_2X3, anti=True
        )["result"]
        anti_twice = self.tool.execute(
            mode="transpose", matrix=anti_once, anti=True
        )["result"]
        self.assertEqual(anti_twice, A_2X3)

    # ------------------------------------------------------------------ #
    # rotate mode
    # ------------------------------------------------------------------ #

    def test_rotate_90_clockwise_non_square(self) -> None:
        result = self.tool.execute(mode="rotate", matrix=A_2X3, degrees=90)
        self.assertEqual(
            result,
            {
                "mode": "rotate",
                "degrees": 90,
                "direction": "clockwise",
                "shape": [3, 2],
                "result": ROT90_A,
            },
        )

    def test_rotate_180_non_square(self) -> None:
        result = self.tool.execute(mode="rotate", matrix=A_2X3, degrees=180)
        self.assertEqual(result["result"], ROT180_A)
        self.assertEqual(result["shape"], [2, 3])

    def test_rotate_270_clockwise_non_square(self) -> None:
        result = self.tool.execute(mode="rotate", matrix=A_2X3, degrees=270)
        self.assertEqual(result["result"], ROT270_A)
        self.assertEqual(result["shape"], [3, 2])

    def test_rotate_180_twice_is_identity(self) -> None:
        once = self.tool.execute(mode="rotate", matrix=A_2X3, degrees=180)[
            "result"
        ]
        twice = self.tool.execute(mode="rotate", matrix=once, degrees=180)[
            "result"
        ]
        self.assertEqual(twice, A_2X3)

    def test_rotate_90_four_times_is_identity(self) -> None:
        current = A_2X3
        for _ in range(4):
            current = self.tool.execute(
                mode="rotate", matrix=current, degrees=90
            )["result"]
        self.assertEqual(current, A_2X3)

    def test_rotate_accepts_numeric_string_degrees(self) -> None:
        result = self.tool.execute(mode="rotate", matrix=A_2X3, degrees="90")
        self.assertEqual(result["result"], ROT90_A)
        self.assertEqual(result["degrees"], 90)

    def test_rotate_1x1(self) -> None:
        for degrees in (90, 180, 270):
            result = self.tool.execute(
                mode="rotate", matrix=[[7]], degrees=degrees
            )
            self.assertEqual(result["result"], [[7]])

    # ------------------------------------------------------------------ #
    # scale mode
    # ------------------------------------------------------------------ #

    def test_scale_multiply_by_default(self) -> None:
        result = self.tool.execute(
            mode="scale", matrix=[[1, 2], [3, 4]], scalar=2
        )
        self.assertEqual(
            result,
            {
                "mode": "scale",
                "scale_type": "multiply",
                "scalar": 2,
                "result": [[2, 4], [6, 8]],
            },
        )

    def test_scale_add(self) -> None:
        result = self.tool.execute(
            mode="scale", matrix=[[1, 2], [3, 4]], scalar=10, scale_type="add"
        )
        self.assertEqual(result["scale_type"], "add")
        self.assertEqual(result["result"], [[11, 12], [13, 14]])

    def test_scale_float_scalar(self) -> None:
        result = self.tool.execute(
            mode="scale", matrix=[[1, 2], [3, 4]], scalar=0.5
        )
        self.assertEqual(result["result"], [[0.5, 1.0], [1.5, 2.0]])

    def test_scale_preserves_integer_types(self) -> None:
        result = self.tool.execute(
            mode="scale", matrix=[[1, 2], [3, 4]], scalar=3
        )["result"]
        for row in result:
            for value in row:
                self.assertIsInstance(value, int)

    # ------------------------------------------------------------------ #
    # multiply mode
    # ------------------------------------------------------------------ #

    def test_multiply_matrix_ground_truth(self) -> None:
        result = self.tool.execute(mode="multiply", matrix=A_2X3, other=B_3X2)
        self.assertEqual(
            result,
            {
                "mode": "multiply",
                "kind": "matrix",
                "a_shape": [2, 3],
                "b_shape": [3, 2],
                "shape": [2, 2],
                "result": PRODUCT_A_B,
            },
        )

    def test_multiply_by_identity(self) -> None:
        identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        result = self.tool.execute(mode="multiply", matrix=A_2X3, other=identity)
        self.assertEqual(result["result"], A_2X3)

    def test_multiply_scalar_shortcut(self) -> None:
        result = self.tool.execute(mode="multiply", matrix=[[1, 2], [3, 4]], other=5)
        self.assertEqual(
            result,
            {
                "mode": "multiply",
                "kind": "scalar",
                "scalar": 5,
                "shape": [2, 2],
                "result": [[5, 10], [15, 20]],
            },
        )

    def test_multiply_scalar_float_shortcut(self) -> None:
        result = self.tool.execute(mode="multiply", matrix=[[1, 2]], other=0.5)
        self.assertEqual(result["kind"], "scalar")
        self.assertEqual(result["result"], [[0.5, 1.0]])

    def test_multiply_other_as_row_text(self) -> None:
        result = self.tool.execute(
            mode="multiply", matrix=A_2X3, other="7 8\n9 10\n11 12"
        )
        self.assertEqual(result["kind"], "matrix")
        self.assertEqual(result["result"], PRODUCT_A_B)

    def test_multiply_dimension_mismatch_error(self) -> None:
        result = self.tool.execute(
            mode="multiply", matrix=A_2X3, other=[[1, 2], [3, 4]]
        )
        error = _error_of(result)
        self.assertEqual(error["type"], "dimension_mismatch")
        self.assertIn("2x3", error["message"])
        self.assertIn("2x2", error["message"])

    def test_multiply_associative_ground_truth(self) -> None:
        # (A @ B) @ C == A @ (B @ C) on exact integers.
        c = [[1, 0], [2, 1]]
        left = self.tool.execute(
            mode="multiply",
            matrix=self.tool.execute(mode="multiply", matrix=A_2X3, other=B_3X2)[
                "result"
            ],
            other=c,
        )["result"]
        bc = self.tool.execute(mode="multiply", matrix=B_3X2, other=c)["result"]
        right = self.tool.execute(mode="multiply", matrix=A_2X3, other=bc)["result"]
        self.assertEqual(left, right)

    # ------------------------------------------------------------------ #
    # determinant mode
    # ------------------------------------------------------------------ #

    def test_determinant_identity_4x4(self) -> None:
        identity = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        result = self.tool.execute(mode="determinant", matrix=identity)
        self.assertEqual(
            result,
            {
                "mode": "determinant",
                "size": 4,
                "method": "cofactor_fraction",
                "exact": True,
                "result": 1,
                "value_float": 1.0,
            },
        )

    def test_determinant_2x2_known_value(self) -> None:
        result = self.tool.execute(
            mode="determinant", matrix=[[1, 2], [3, 4]]
        )
        self.assertEqual(result["result"], -2)
        self.assertTrue(result["exact"])

    def test_determinant_3x3_hand_computed(self) -> None:
        matrix = [[2, 0, 1], [1, 3, 2], [1, 1, 4]]
        result = self.tool.execute(mode="determinant", matrix=matrix)
        self.assertEqual(result["result"], DET_3X3)
        self.assertTrue(result["exact"])
        self.assertEqual(result["method"], "cofactor_fraction")

    def test_determinant_5x5_triangular_ground_truth(self) -> None:
        # Upper triangular with noisy off-diagonal entries: the
        # determinant is still the product of the diagonal.
        result = self.tool.execute(mode="determinant", matrix=FIVE_BY_FIVE)
        self.assertEqual(result["result"], DET_5X5)
        self.assertTrue(result["exact"])
        self.assertEqual(result["method"], "cofactor_fraction")

    def test_determinant_singular_matrix_is_exactly_zero(self) -> None:
        result = self.tool.execute(
            mode="determinant", matrix=[[1, 2], [2, 4]]
        )
        self.assertEqual(result["result"], 0)
        self.assertTrue(result["exact"])

    def test_determinant_duplicate_rows_singular(self) -> None:
        matrix = [[2, 0, 1], [1, 3, 2], [1, 3, 2]]
        result = self.tool.execute(mode="determinant", matrix=matrix)
        self.assertEqual(result["result"], 0)

    def test_determinant_big_integers_exact(self) -> None:
        result = self.tool.execute(mode="determinant", matrix=BIG_MATRIX)
        self.assertEqual(result["result"], -2)
        self.assertTrue(result["exact"])
        self.assertEqual(result["value_float"], -2.0)

    def test_determinant_float_fallback_is_approximate(self) -> None:
        result = self.tool.execute(mode="determinant", matrix=BIG_MATRIX_FLOAT)
        self.assertEqual(result["method"], "cofactor_float")
        self.assertFalse(result["exact"])
        self.assertIsInstance(result["result"], float)
        # Exact answer is -2; double precision cancels it away here.
        self.assertNotEqual(result["result"], -2)
        self.assertIn("note", result)

    def test_determinant_float_entries_simple_value(self) -> None:
        result = self.tool.execute(
            mode="determinant", matrix=[[0.5, 0.0], [0.0, 2.0]]
        )
        self.assertEqual(result["result"], 1.0)
        self.assertEqual(result["method"], "cofactor_float")
        self.assertFalse(result["exact"])

    def test_determinant_gaussian_fallback_beyond_cofactor_size(self) -> None:
        size = 13
        diagonal = [
            [value if row == col else 0 for col in range(size)]
            for row, value in enumerate(range(1, size + 1))
        ]
        result = self.tool.execute(mode="determinant", matrix=diagonal)
        self.assertEqual(result["method"], "gaussian_float")
        self.assertFalse(result["exact"])
        self.assertEqual(result["result"], 6227020800.0)  # 13!
        self.assertIn("note", result)

    def test_determinant_non_square_error(self) -> None:
        result = self.tool.execute(mode="determinant", matrix=A_2X3)
        error = _error_of(result)
        self.assertEqual(error["type"], "not_square")
        self.assertIn("2 rows x 3 columns", error["message"])

    def test_determinant_single_element(self) -> None:
        result = self.tool.execute(mode="determinant", matrix=[[7]])
        self.assertEqual(result["result"], 7)
        self.assertTrue(result["exact"])

    # ------------------------------------------------------------------ #
    # flatten mode
    # ------------------------------------------------------------------ #

    def test_flatten_row_major_default(self) -> None:
        result = self.tool.execute(mode="flatten", matrix=A_2X3)
        self.assertEqual(
            result,
            {
                "mode": "flatten",
                "order": "row-major",
                "shape": [2, 3],
                "length": 6,
                "result": [1, 2, 3, 4, 5, 6],
            },
        )

    def test_flatten_column_major(self) -> None:
        result = self.tool.execute(
            mode="flatten", matrix=A_2X3, order="column-major"
        )
        self.assertEqual(result["result"], [1, 4, 2, 5, 3, 6])

    def test_flatten_zigzag_3x3(self) -> None:
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = self.tool.execute(mode="flatten", matrix=matrix, order="zigzag")
        self.assertEqual(result["result"], ZIGZAG_3X3)

    def test_flatten_zigzag_non_square(self) -> None:
        result = self.tool.execute(mode="flatten", matrix=A_2X3, order="zigzag")
        self.assertEqual(result["result"], ZIGZAG_A_2X3)

    def test_flatten_round_trips_through_shapes(self) -> None:
        # Every order flattens the same multiset of values.
        values = {order: self.tool.execute(
            mode="flatten", matrix=A_2X3, order=order
        )["result"] for order in ("row-major", "column-major", "zigzag")}
        self.assertEqual(sorted(values["row-major"]), sorted(values["column-major"]))
        self.assertEqual(sorted(values["row-major"]), sorted(values["zigzag"]))

    # ------------------------------------------------------------------ #
    # Input formats: text and JSON strings
    # ------------------------------------------------------------------ #

    def test_text_rows_match_list_input(self) -> None:
        via_text = self.tool.execute(mode="transpose", matrix="1 2 3\n4 5 6")
        via_list = self.tool.execute(mode="transpose", matrix=A_2X3)
        self.assertEqual(via_text, via_list)

    def test_json_string_input(self) -> None:
        result = self.tool.execute(
            mode="determinant", matrix="[[1, 2], [3, 4]]"
        )
        self.assertEqual(result["result"], -2)

    def test_text_negative_and_scientific_tokens(self) -> None:
        result = self.tool.execute(
            mode="flatten", matrix="-1 2.5\n3e-1 4"
        )
        self.assertEqual(result["result"], [-1, 2.5, 0.3, 4])

    def test_text_blank_lines_are_skipped(self) -> None:
        result = self.tool.execute(mode="flatten", matrix="1 2\n\n  3 4  \n")
        self.assertEqual(result["result"], [1, 2, 3, 4])

    def test_text_token_with_sign_and_plus(self) -> None:
        result = self.tool.execute(mode="flatten", matrix="+5 -3")
        self.assertEqual(result["result"], [5, -3])

    def test_tuple_matrix_accepted(self) -> None:
        result = self.tool.execute(mode="transpose", matrix=((1, 2), (3, 4)))
        self.assertEqual(result["result"], [[1, 3], [2, 4]])

    # ------------------------------------------------------------------ #
    # Content-level structured errors
    # ------------------------------------------------------------------ #

    def test_ragged_json_matrix_error_has_row_index(self) -> None:
        result = self.tool.execute(mode="info", matrix=[[1, 2, 3], [4, 5]])
        error = _error_of(result)
        self.assertEqual(error["type"], "invalid_matrix")
        self.assertIn("row 2", error["message"])
        self.assertIn("3 columns", error["message"])
        self.assertIn("2", error["message"])

    def test_ragged_text_matrix_error_has_row_index(self) -> None:
        result = self.tool.execute(mode="info", matrix="1 2 3\n4 5")
        error = _error_of(result)
        self.assertEqual(error["type"], "invalid_matrix")
        self.assertIn("row 2", error["message"])

    def test_text_invalid_token_error(self) -> None:
        result = self.tool.execute(mode="info", matrix="1 two 3")
        error = _error_of(result)
        self.assertEqual(error["type"], "invalid_matrix_text")
        self.assertIn("row 1", error["message"])
        self.assertIn("'two'", error["message"])

    def test_text_nan_token_is_not_numeric(self) -> None:
        result = self.tool.execute(mode="info", matrix="1 2\nnan 4")
        error = _error_of(result)
        self.assertEqual(error["type"], "invalid_matrix_text")

    def test_text_overflowing_token_error(self) -> None:
        result = self.tool.execute(mode="info", matrix="1e999 2")
        error = _error_of(result)
        self.assertEqual(error["type"], "non_finite_entry")
        self.assertIn("row 1", error["message"])

    def test_json_nan_entry_error(self) -> None:
        result = self.tool.execute(mode="info", matrix="[[1, NaN]]")
        error = _error_of(result)
        self.assertEqual(error["type"], "non_finite_entry")
        self.assertIn("row 1, col 2", error["message"])

    def test_json_infinity_entry_error(self) -> None:
        result = self.tool.execute(mode="info", matrix="[[Infinity]]")
        self.assertEqual(_error_of(result)["type"], "non_finite_entry")

    def test_invalid_json_string_error(self) -> None:
        result = self.tool.execute(mode="info", matrix="[[1, 2")
        self.assertEqual(_error_of(result)["type"], "invalid_json")

    def test_json_non_array_error(self) -> None:
        result = self.tool.execute(mode="info", matrix='{"a": 1}')
        self.assertEqual(_error_of(result)["type"], "invalid_json")

    def test_non_numeric_cell_error(self) -> None:
        result = self.tool.execute(mode="info", matrix=[[1, "x"]])
        error = _error_of(result)
        self.assertEqual(error["type"], "non_numeric_entry")
        self.assertIn("row 1, col 2", error["message"])

    def test_boolean_cell_rejected(self) -> None:
        result = self.tool.execute(mode="info", matrix=[[True, 2]])
        error = _error_of(result)
        self.assertEqual(error["type"], "non_numeric_entry")
        self.assertIn("boolean", error["message"])

    def test_nan_cell_rejected(self) -> None:
        result = self.tool.execute(
            mode="info", matrix=[[1.0, float("nan")]]
        )
        self.assertEqual(_error_of(result)["type"], "non_finite_entry")

    def test_empty_row_error(self) -> None:
        result = self.tool.execute(mode="info", matrix=[[]])
        error = _error_of(result)
        self.assertEqual(error["type"], "invalid_matrix")
        self.assertIn("row 1", error["message"])

    def test_row_not_a_list_error(self) -> None:
        result = self.tool.execute(mode="info", matrix=[[1, 2], 3])
        error = _error_of(result)
        self.assertEqual(error["type"], "invalid_matrix")
        self.assertIn("row 2", error["message"])

    def test_flat_list_of_numbers_rejected(self) -> None:
        result = self.tool.execute(mode="info", matrix=[1, 2, 3])
        self.assertEqual(_error_of(result)["type"], "invalid_matrix")

    def test_too_many_columns_error(self) -> None:
        result = self.tool.execute(mode="info", matrix=[list(range(101))])
        error = _error_of(result)
        self.assertEqual(error["type"], "matrix_too_large")
        self.assertIn("row 1", error["message"])

    def test_multiply_ragged_other_is_structured_error(self) -> None:
        result = self.tool.execute(mode="multiply", matrix=[[1, 2]], other="3\n4 5")
        self.assertEqual(_error_of(result)["type"], "invalid_matrix")

    # ------------------------------------------------------------------ #
    # Parameter-level validation (raises ValueError)
    # ------------------------------------------------------------------ #

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="inverse", matrix=[[1]])

    def test_matrix_missing_or_wrong_type_raises(self) -> None:
        for bad in (None, 42, True, 3.5, {"a": 1}):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="info", matrix=bad)

    def test_empty_matrix_raises(self) -> None:
        for bad in ([], "", "   \n  "):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="info", matrix=bad)

    def test_too_many_rows_raises(self) -> None:
        matrix = [[1] for _ in range(101)]
        with self.assertRaises(ValueError):
            self.tool.execute(mode="info", matrix=matrix)

    def test_too_many_text_rows_raises(self) -> None:
        text = "\n".join(["1"] * 101)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="info", matrix=text)

    def test_bad_degrees_raises(self) -> None:
        for bad in (45, 0, "45", None, True, 90.0):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="rotate", matrix=[[1]], degrees=bad)

    def test_rotate_requires_degrees(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="rotate", matrix=[[1]])

    def test_bad_flatten_order_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="flatten", matrix=[[1]], order="diagonal")

    def test_bad_scale_type_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="scale", matrix=[[1]], scalar=2, scale_type="divide"
            )

    def test_bad_scalar_raises(self) -> None:
        for bad in (None, True, "2", float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="scale", matrix=[[1]], scalar=bad)

    def test_bad_tolerance_raises(self) -> None:
        for bad in (-1, "small", True, float("nan")):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="info", matrix=[[1]], tolerance=bad)

    def test_anti_must_be_boolean(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="transpose", matrix=[[1]], anti="yes")

    def test_multiply_requires_other(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="multiply", matrix=[[1]])

    def test_multiply_bad_other_type_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="multiply", matrix=[[1]], other=True)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="multiply", matrix=[[1]], other=complex(1, 2))

    # ------------------------------------------------------------------ #
    # Integers beyond the double range never crash the tool
    # ------------------------------------------------------------------ #

    def test_huge_int_scalar_keeps_integer_arithmetic(self) -> None:
        huge = 10**400
        result = self.tool.execute(mode="scale", matrix=[[1, 2]], scalar=huge)
        self.assertEqual(result["result"], [[huge, 2 * huge]])

    def test_huge_int_tolerance_accepted(self) -> None:
        result = self.tool.execute(
            mode="info", matrix=[[1, 2], [3, 4]], tolerance=10**400
        )
        self.assertTrue(result["symmetric"])
        self.assertEqual(result["tolerance"], 10**400)

    def test_huge_int_other_scalar_shortcut(self) -> None:
        huge = 10**400
        result = self.tool.execute(
            mode="multiply", matrix=[[1, 2], [3, 4]], other=huge
        )
        self.assertEqual(
            result["result"],
            [[huge, 2 * huge], [3 * huge, 4 * huge]],
        )

    def test_scale_huge_int_on_float_matrix_maps_to_infinities(self) -> None:
        huge = 10**400
        result = self.tool.execute(
            mode="scale", matrix=[[0.5, -1.0]], scalar=huge
        )
        self.assertEqual(result["result"], [[float("inf"), float("-inf")]])
        zero_kept = self.tool.execute(
            mode="scale", matrix=[[0.0, 2.0]], scalar=huge
        )
        self.assertEqual(zero_kept["result"], [[0.0, float("inf")]])

    def test_scale_add_huge_int_on_float_matrix(self) -> None:
        result = self.tool.execute(
            mode="scale",
            matrix=[[0.5, -1.25]],
            scalar=-(10**400),
            scale_type="add",
        )
        self.assertEqual(result["result"], [[float("-inf"), float("-inf")]])

    def test_multiply_huge_int_scalar_on_float_matrix(self) -> None:
        result = self.tool.execute(
            mode="multiply", matrix=[[0.5, -1.25]], other=10**400
        )
        self.assertEqual(result["kind"], "scalar")
        self.assertEqual(result["result"], [[float("inf"), float("-inf")]])

    def test_multiply_huge_int_matmul_overflows_to_inf(self) -> None:
        result = self.tool.execute(
            mode="multiply",
            matrix=[[0.5, 1.5]],
            other=[[10**400], [10**400]],
        )
        self.assertEqual(result["kind"], "matrix")
        self.assertEqual(result["result"], [[float("inf")]])

    def test_multiply_mixed_matmul_fallback_is_exact_then_float(self) -> None:
        huge = 10**200
        result = self.tool.execute(
            mode="multiply", matrix=[[0.5, 1.5]], other=[[huge], [huge]]
        )
        self.assertEqual(result["result"], [[2e200]])

    def test_info_trace_and_symmetry_with_huge_mixed_entries(self) -> None:
        result = self.tool.execute(
            mode="info", matrix=[[10**400, 1], [1, 0.5]]
        )
        self.assertEqual(result["trace"], float("inf"))
        self.assertEqual(result["diagonal"], [10**400, 0.5])
        mirrored = self.tool.execute(
            mode="info", matrix=[[0.5, 10**400], [1.5, 2.0]]
        )
        self.assertFalse(mirrored["symmetric"])
        equal_huge = self.tool.execute(
            mode="info", matrix=[[0.5, 10**400], [10**400, 2.0]]
        )
        self.assertTrue(equal_huge["symmetric"])

    def test_determinant_huge_exact_result_value_float_is_inf(self) -> None:
        huge = 10**200
        result = self.tool.execute(
            mode="determinant", matrix=[[huge, 1], [1, huge]]
        )
        self.assertTrue(result["exact"])
        self.assertEqual(result["method"], "cofactor_fraction")
        self.assertEqual(result["result"], huge * huge - 1)
        self.assertEqual(result["value_float"], float("inf"))

    def test_determinant_huge_int_with_float_entry_uses_float_path(self) -> None:
        result = self.tool.execute(
            mode="determinant", matrix=[[10**400, 0.5], [1.0, 2.0]]
        )
        self.assertFalse(result["exact"])
        self.assertEqual(result["method"], "cofactor_float")
        self.assertEqual(result["result"], float("inf"))

    def test_huge_payload_is_json_serializable(self) -> None:
        payload = self.tool.execute(
            mode="determinant", matrix=[[10**200, 1], [1, 10**200]]
        )
        json.dumps(payload)
        scaled = self.tool.execute(
            mode="scale", matrix=[[0.5]], scalar=10**400
        )
        json.dumps(scaled)

    # ------------------------------------------------------------------ #
    # Packaging
    # ------------------------------------------------------------------ #

    def test_exported_from_common_tool_package(self) -> None:
        self.assertIs(DirectMatrixOpsTool, MatrixOpsTool)


if __name__ == "__main__":
    unittest.main()
