#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_list_ops_tool.py

"""Offline unit tests for ListOpsTool.

The tool is built purely on the standard library (``json`` plus core
datatypes) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: each mode is checked
against literal ground-truth outputs — the stable orderings (union
walks list a first then unseen list-b elements, intersection and
difference keep a-order, symmetric difference is a-only then b-only),
the Python equality collapse of ``1`` / ``1.0`` / ``true``, object
mode with nested key paths, the missing-key and unhashable-element
errors listing element indices, dedupe previews capped at 20, the
flatten depth matrix, the cycle guard, empty lists and the full
validation error matrix.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import ListOpsTool
from agentuniverse.agent.action.tool.common_tool.list_ops_tool import (
    ListOpsTool as DirectListOpsTool,
)

A_ABC = ["a", "b", "c"]
B_BCD = ["b", "c", "d"]


class ListOpsToolSetModesTest(unittest.TestCase):
    """Ground-truth cases for the four two-list set modes."""

    def setUp(self) -> None:
        self.tool = ListOpsTool()

    def test_union_stable_order_ground_truth(self) -> None:
        # a first-occurrence order, then b's unseen elements in b order.
        result = self.tool.execute(
            mode="union",
            a=["b", "a", "b", "c"],
            b=["c", "d", "a", "d"],
        )
        self.assertEqual(
            result,
            {
                "mode": "union",
                "by": "value",
                "key": None,
                "result": ["b", "a", "c", "d"],
                "counts": {
                    "a": 4,
                    "b": 4,
                    "result": 4,
                    "removed": 4,
                    "kept": 4,
                },
            },
        )

    def test_intersection_keeps_a_order_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="intersection", a=["c", "a", "b", "a"], b=B_BCD
        )
        self.assertEqual(
            result,
            {
                "mode": "intersection",
                "by": "value",
                "key": None,
                "result": ["c", "b"],
                "counts": {
                    "a": 4,
                    "b": 3,
                    "result": 2,
                    "removed": 5,
                    "kept": 2,
                },
            },
        )

    def test_difference_keeps_a_order_ground_truth(self) -> None:
        # "c" and "b" are in b; "a" survives, first occurrence only.
        result = self.tool.execute(
            mode="difference", a=["c", "a", "b", "a"], b=B_BCD
        )
        self.assertEqual(result["result"], ["a"])
        self.assertEqual(
            result["counts"],
            {"a": 4, "b": 3, "result": 1, "removed": 6, "kept": 1},
        )

    def test_symmetric_difference_a_then_b_ground_truth(self) -> None:
        # a-only part in a order first, then b-only part in b order.
        result = self.tool.execute(
            mode="symmetric_difference",
            a=["e", "b", "f", "c"],
            b=["c", "g", "b", "h"],
        )
        self.assertEqual(result["result"], ["e", "f", "g", "h"])
        self.assertEqual(
            result["counts"],
            {"a": 4, "b": 4, "result": 4, "removed": 4, "kept": 4},
        )

    def test_union_disjoint_preserves_both_orders(self) -> None:
        result = self.tool.execute(mode="union", a=A_ABC, b=["x", "y"])
        self.assertEqual(result["result"], ["a", "b", "c", "x", "y"])
        self.assertEqual(result["counts"]["removed"], 0)

    def test_union_identical_lists_collapses(self) -> None:
        result = self.tool.execute(mode="union", a=A_ABC, b=A_ABC)
        self.assertEqual(result["result"], A_ABC)
        self.assertEqual(
            result["counts"],
            {"a": 3, "b": 3, "result": 3, "removed": 3, "kept": 3},
        )

    def test_intersection_empty_when_disjoint(self) -> None:
        result = self.tool.execute(
            mode="intersection", a=["x"], b=["y", "z"]
        )
        self.assertEqual(result["result"], [])
        self.assertEqual(result["counts"]["kept"], 0)
        self.assertEqual(result["counts"]["removed"], 3)

    def test_difference_with_empty_b_is_dedupe_of_a(self) -> None:
        result = self.tool.execute(
            mode="difference", a=["x", "x", "y"], b=[]
        )
        self.assertEqual(result["result"], ["x", "y"])

    def test_set_modes_with_empty_lists(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="union", a=[], b=["b", "a", "b"])[
                "result"
            ],
            ["b", "a"],
        )
        self.assertEqual(
            self.tool.execute(mode="intersection", a=[], b=A_ABC)["result"],
            [],
        )
        self.assertEqual(
            self.tool.execute(mode="difference", a=[], b=A_ABC)["result"],
            [],
        )
        self.assertEqual(
            self.tool.execute(
                mode="symmetric_difference", a=[], b=["b", "b"]
            )["result"],
            ["b"],
        )

    def test_scalar_mixed_types_and_null(self) -> None:
        result = self.tool.execute(
            mode="union", a=[None, "1", 2], b=[1, 2.0, "two"]
        )
        # 2 and 2.0 collapse (first form kept); "1"/1/"two" stay distinct.
        self.assertEqual(result["result"], [None, "1", 2, 1, "two"])

    def test_python_equality_collapse_documented(self) -> None:
        # 1 == 1.0 == True under Python equality, so all three collapse
        # onto the first occurrence's original form; "1" stays distinct.
        deduped = self.tool.execute(
            mode="dedupe", a=[1.0, 1, True, "1", 1.0]
        )
        self.assertEqual(deduped["result"], [1.0, "1"])
        union = self.tool.execute(mode="union", a=[1], b=[True, 1.0])
        self.assertEqual(union["result"], [1])
        intersection = self.tool.execute(
            mode="intersection", a=[True], b=[1]
        )
        self.assertEqual(intersection["result"], [True])

    def test_json_array_string_inputs(self) -> None:
        result = self.tool.execute(
            mode="union", a='["a", "b"]', b='["b", "c"]'
        )
        self.assertEqual(result["result"], ["a", "b", "c"])
        self.assertEqual(result["counts"], {"a": 2, "b": 2, "result": 3, "removed": 1, "kept": 3})
        self.assertEqual(
            self.tool.execute(
                mode="difference", a='[1, 2]', b='[2]'
            )["result"],
            [1],
        )

    def test_object_mode_union_first_element_per_key(self) -> None:
        users_a = [
            {"id": 1, "name": "first-one"},
            {"id": 2, "name": "two"},
            {"id": 1, "name": "duplicate-one"},
        ]
        users_b = [
            {"id": 2, "name": "two-again"},
            {"id": 3, "name": "three"},
        ]
        result = self.tool.execute(
            mode="union", a=users_a, b=users_b, key="id"
        )
        # The FIRST element per key value wins, whole and unchanged.
        self.assertEqual(
            result["result"],
            [
                {"id": 1, "name": "first-one"},
                {"id": 2, "name": "two"},
                {"id": 3, "name": "three"},
            ],
        )
        self.assertEqual(result["by"], "key")
        self.assertEqual(result["key"], "id")
        self.assertEqual(
            result["counts"],
            {"a": 3, "b": 2, "result": 3, "removed": 2, "kept": 3},
        )

    def test_object_mode_intersection_and_difference(self) -> None:
        a = [{"id": 1}, {"id": 2}, {"id": 3, "tag": "x"}]
        b = [{"id": 3}, {"id": 4}]
        self.assertEqual(
            self.tool.execute(
                mode="intersection", a=a, b=b, key="id"
            )["result"],
            [{"id": 3, "tag": "x"}],
        )
        self.assertEqual(
            self.tool.execute(
                mode="difference", a=a, b=b, key="id"
            )["result"],
            [{"id": 1}, {"id": 2}],
        )
        self.assertEqual(
            self.tool.execute(
                mode="symmetric_difference", a=a, b=b, key="id"
            )["result"],
            [{"id": 1}, {"id": 2}, {"id": 4}],
        )

    def test_object_mode_nested_key_path(self) -> None:
        a = [
            {"meta": {"id": 7}, "v": 1},
            {"meta": {"id": 8}, "v": 2},
        ]
        b = [{"meta": {"id": 8}, "v": 99}, {"meta": {"id": 9}, "v": 3}]
        result = self.tool.execute(
            mode="union", a=a, b=b, key="meta.id"
        )
        self.assertEqual(
            result["result"],
            [
                {"meta": {"id": 7}, "v": 1},
                {"meta": {"id": 8}, "v": 2},
                {"meta": {"id": 9}, "v": 3},
            ],
        )

    def test_object_mode_missing_key_error_lists_index(self) -> None:
        a = [{"id": 1}, {"name": "no-id-here"}, {"id": 3}]
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="union", a=a, b=[], key="id")
        message = str(ctx.exception)
        self.assertIn("index 1", message)
        self.assertIn("'id'", message)
        self.assertIn("missing", message)
        # The b list is validated too.
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="union", a=[], b=[{"id": 1}, {}], key="id")
        self.assertIn("index 1", str(ctx.exception))

    def test_object_mode_nested_path_unresolvable_error(self) -> None:
        a = [{"meta": {"id": 1}}, {"meta": "not-an-object"}]
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="dedupe", a=a, key="meta.id")
        message = str(ctx.exception)
        self.assertIn("index 1", message)
        self.assertIn("meta.id", message)
        self.assertIn("not an object", message)

    def test_object_mode_non_object_element_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="dedupe", a=[{"id": 1}, 5, {"id": 2}], key="id"
            )
        message = str(ctx.exception)
        self.assertIn("index 1", message)
        self.assertIn("not an object", message)

    def test_object_mode_unhashable_key_value_error(self) -> None:
        a = [{"id": 1}, {"id": ["nested", "list"]}]
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="dedupe", a=a, key="id")
        message = str(ctx.exception)
        self.assertIn("index 1", message)
        self.assertIn("unhashable", message)

    def test_object_mode_key_values_collapse_like_scalars(self) -> None:
        a = [{"k": 1}, {"k": True}]
        result = self.tool.execute(mode="dedupe", a=a, key="k")
        self.assertEqual(result["result"], [{"k": 1}])
        self.assertEqual(result["removed_count"], 1)

    def test_scalar_mode_unhashable_element_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="union", a=[1, [2, 3]], b=[4])
        message = str(ctx.exception)
        self.assertIn("a element at index 1", message)
        self.assertIn("not a hashable scalar", message)
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="dedupe", a=[{"id": 1}])
        self.assertIn("a element at index 0", str(ctx.exception))
        self.assertIn("key='...'", str(ctx.exception))

    def test_b_required_for_set_modes(self) -> None:
        for mode in ("union", "intersection", "difference", "symmetric_difference"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode=mode, a=[1, 2])
                self.assertIn("b is required", str(ctx.exception))

    def test_results_are_json_serializable(self) -> None:
        result = self.tool.execute(
            mode="symmetric_difference",
            a=[1, "two", None, True],
            b=["two", 3, None],
        )
        json.dumps(result)


class ListOpsToolDedupeTest(unittest.TestCase):
    """Ground-truth cases for the dedupe mode."""

    def setUp(self) -> None:
        self.tool = ListOpsTool()

    def test_dedupe_scalar_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="dedupe", a=["x", "y", "x", "z", "y", "x"]
        )
        self.assertEqual(
            result,
            {
                "mode": "dedupe",
                "by": "value",
                "key": None,
                "result": ["x", "y", "z"],
                "removed_count": 3,
                "removed_items": ["x", "y", "x"],
                "removed_items_truncated": False,
                "counts": {
                    "a": 6,
                    "result": 3,
                    "removed": 3,
                    "kept": 3,
                },
            },
        )

    def test_dedupe_no_duplicates(self) -> None:
        result = self.tool.execute(mode="dedupe", a=[1, 2, 3])
        self.assertEqual(result["removed_count"], 0)
        self.assertEqual(result["removed_items"], [])
        self.assertFalse(result["removed_items_truncated"])

    def test_dedupe_empty_list(self) -> None:
        result = self.tool.execute(mode="dedupe", a=[])
        self.assertEqual(result["result"], [])
        self.assertEqual(result["removed_count"], 0)
        self.assertEqual(result["counts"], {"a": 0, "result": 0, "removed": 0, "kept": 0})

    def test_dedupe_preview_capped_at_twenty(self) -> None:
        items = ["dup"] * 25 + ["solo"]
        result = self.tool.execute(mode="dedupe", a=items)
        self.assertEqual(result["removed_count"], 24)
        self.assertEqual(result["removed_items"], ["dup"] * 20)
        self.assertTrue(result["removed_items_truncated"])

    def test_dedupe_object_mode_reports_whole_elements(self) -> None:
        a = [
            {"id": 1, "tag": "keep"},
            {"id": 2, "tag": "keep"},
            {"id": 1, "tag": "drop"},
        ]
        result = self.tool.execute(mode="dedupe", a=a, key="id")
        self.assertEqual(result["by"], "key")
        self.assertEqual(
            result["result"],
            [{"id": 1, "tag": "keep"}, {"id": 2, "tag": "keep"}],
        )
        self.assertEqual(result["removed_count"], 1)
        self.assertEqual(result["removed_items"], [{"id": 1, "tag": "drop"}])


class ListOpsToolUniqueCountTest(unittest.TestCase):
    """Ground-truth cases for the unique_count mode."""

    def setUp(self) -> None:
        self.tool = ListOpsTool()

    def test_unique_count_scalar_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="unique_count", a=["b", "a", "b", "c", "a", "b"]
        )
        # Counts sorted descending; ties keep first-occurrence order.
        self.assertEqual(
            result,
            {
                "mode": "unique_count",
                "by": "value",
                "key": None,
                "distinct_count": 3,
                "value_counts": [
                    {"value": "b", "count": 3},
                    {"value": "a", "count": 2},
                    {"value": "c", "count": 1},
                ],
                "counts_total": 3,
                "counts_truncated": False,
                "top_n": None,
                "counts": {"a": 6, "result": 3, "removed": 3, "kept": 3},
            },
        )

    def test_unique_count_ties_keep_first_occurrence_order(self) -> None:
        result = self.tool.execute(
            mode="unique_count", a=["z", "y", "z", "y", "x"]
        )
        # z and y both appear twice; z occurred first so it ranks first.
        self.assertEqual(
            result["value_counts"],
            [
                {"value": "z", "count": 2},
                {"value": "y", "count": 2},
                {"value": "x", "count": 1},
            ],
        )

    def test_unique_count_equality_collapse(self) -> None:
        result = self.tool.execute(mode="unique_count", a=[1, 1.0, True, 2])
        self.assertEqual(result["distinct_count"], 2)
        self.assertEqual(
            result["value_counts"],
            [{"value": 1, "count": 3}, {"value": 2, "count": 1}],
        )

    def test_unique_count_top_n_caps_and_flags(self) -> None:
        result = self.tool.execute(
            mode="unique_count",
            a=["a", "b", "a", "c", "d", "c"],
            top_n=2,
        )
        self.assertEqual(result["top_n"], 2)
        self.assertEqual(result["counts_total"], 4)
        self.assertTrue(result["counts_truncated"])
        self.assertEqual(
            result["value_counts"],
            [{"value": "a", "count": 2}, {"value": "c", "count": 2}],
        )

    def test_unique_count_top_n_covers_all_no_flag(self) -> None:
        result = self.tool.execute(
            mode="unique_count", a=["a", "b", "a"], top_n=5
        )
        self.assertFalse(result["counts_truncated"])
        self.assertEqual(len(result["value_counts"]), 2)

    def test_unique_count_empty_list(self) -> None:
        result = self.tool.execute(mode="unique_count", a=[])
        self.assertEqual(result["distinct_count"], 0)
        self.assertEqual(result["value_counts"], [])

    def test_unique_count_object_mode(self) -> None:
        a = [
            {"id": 1},
            {"id": 2},
            {"id": 1},
            {"id": 2},
            {"id": 2},
            {"id": 3},
        ]
        result = self.tool.execute(mode="unique_count", a=a, key="id")
        self.assertEqual(result["by"], "key")
        self.assertEqual(result["distinct_count"], 3)
        self.assertEqual(
            result["value_counts"],
            [
                {"value": 2, "count": 3},
                {"value": 1, "count": 2},
                {"value": 3, "count": 1},
            ],
        )
        self.assertEqual(
            result["counts"], {"a": 6, "result": 3, "removed": 3, "kept": 3}
        )
        # Nested key path works too.
        nested = self.tool.execute(
            mode="unique_count", a=[{"meta": {"id": 3}}], key="meta.id"
        )
        self.assertEqual(nested["distinct_count"], 1)


class ListOpsToolFlattenTest(unittest.TestCase):
    """Ground-truth cases for the flatten mode."""

    def setUp(self) -> None:
        self.tool = ListOpsTool()

    def test_flatten_full_by_default(self) -> None:
        result = self.tool.execute(mode="flatten", a=[1, [2, [3, [4]]], 5])
        self.assertEqual(
            result,
            {
                "mode": "flatten",
                "depth": None,
                "result": [1, 2, 3, 4, 5],
                "counts": {"a": 3, "result": 5},
            },
        )

    def test_flatten_depth_matrix(self) -> None:
        nested = [1, [2, [3, [4]]]]
        self.assertEqual(
            self.tool.execute(mode="flatten", a=nested, depth=0)["result"],
            [1, [2, [3, [4]]]],
        )
        self.assertEqual(
            self.tool.execute(mode="flatten", a=nested, depth=1)["result"],
            [1, 2, [3, [4]]],
        )
        self.assertEqual(
            self.tool.execute(mode="flatten", a=nested, depth=2)["result"],
            [1, 2, 3, [4]],
        )
        self.assertEqual(
            self.tool.execute(mode="flatten", a=nested, depth=3)["result"],
            [1, 2, 3, 4],
        )
        # Depth beyond the nesting flattens everything.
        self.assertEqual(
            self.tool.execute(mode="flatten", a=nested, depth=10)["result"],
            [1, 2, 3, 4],
        )

    def test_flatten_objects_are_leaves(self) -> None:
        result = self.tool.execute(
            mode="flatten", a=[[{"id": 1}], [{"id": 2}], 3]
        )
        self.assertEqual(result["result"], [{"id": 1}, {"id": 2}, 3])

    def test_flatten_empty_and_flat_lists(self) -> None:
        self.assertEqual(self.tool.execute(mode="flatten", a=[])["result"], [])
        self.assertEqual(
            self.tool.execute(mode="flatten", a=[1, 2])["result"], [1, 2]
        )
        self.assertEqual(
            self.tool.execute(mode="flatten", a=[[], [[]], [[], []]])[
                "result"
            ],
            [],
        )

    def test_flatten_json_array_string(self) -> None:
        result = self.tool.execute(mode="flatten", a='[[1, 2], [3]]')
        self.assertEqual(result["result"], [1, 2, 3])

    def test_flatten_cycle_guard(self) -> None:
        cyclic = [1, [2]]
        cyclic[1].append(cyclic)
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="flatten", a=cyclic)
        self.assertIn("cycle detected", str(ctx.exception))
        # A self-containing list deeper down is caught too.
        deeper = [[cyclic]]
        with self.assertRaises(ValueError):
            self.tool.execute(mode="flatten", a=deeper)
        # Cycle detection also applies to partial depths that reach it.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="flatten", a=cyclic, depth=1)

    def test_flatten_sibling_reuse_is_not_a_cycle(self) -> None:
        shared = [1, 2]
        result = self.tool.execute(mode="flatten", a=[shared, shared])
        self.assertEqual(result["result"], [1, 2, 1, 2])

    def test_flatten_result_cap(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="flatten", a=[[0] * 10_001])
        self.assertIn("10,000-element limit", str(ctx.exception))
        exact = self.tool.execute(mode="flatten", a=[[0] * 10_000])
        self.assertEqual(len(exact["result"]), 10_000)


class ListOpsToolValidationTest(unittest.TestCase):
    """The strict validation matrix (all raise ValueError)."""

    def setUp(self) -> None:
        self.tool = ListOpsTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="merge", a=[1])
        self.assert_invalid(mode="UNION", a=[1], b=[2])
        self.assert_invalid(mode=None, a=[1])
        self.assert_invalid(mode=123, a=[1])

    def test_invalid_a_types(self) -> None:
        for bad in (None, 5, True, "not-json", "[1, 2", '{"k": 1}', '"text"', "42"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="dedupe", a=bad)
                self.assert_invalid(mode="flatten", a=bad)

    def test_invalid_b_types(self) -> None:
        for bad in (None, 5, True, '{"k": 1}', "[1,"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="union", a=[1], b=bad)

    def test_invalid_key(self) -> None:
        for bad in (5, True, "", "a..b", ".a", "a.", None):
            with self.subTest(bad=bad):
                # None key means scalar mode, so use a bad non-None value.
                if bad is None:
                    continue
                self.assert_invalid(mode="dedupe", a=[{"id": 1}], key=bad)

    def test_invalid_top_n(self) -> None:
        for bad in (0, -1, 2.5, True, "few", 10_001):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="unique_count", a=[1], top_n=bad)

    def test_invalid_depth(self) -> None:
        for bad in (-1, 2.5, True, "deep", 101):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="flatten", a=[1], depth=bad)

    def test_invalid_mode_specific_options_in_wrong_mode(self) -> None:
        cases = [
            {"mode": "dedupe", "b": [1]},
            {"mode": "unique_count", "b": [1]},
            {"mode": "flatten", "b": [1]},
            {"mode": "flatten", "key": "id"},
            {"mode": "union", "top_n": 3},
            {"mode": "dedupe", "top_n": 3},
            {"mode": "union", "depth": 1},
            {"mode": "unique_count", "depth": 1},
        ]
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(a=[1, 2], **kwargs)
                self.assertIn("is only valid in the", str(ctx.exception))
                self.assertIn(f"with mode={kwargs['mode']!r}", str(ctx.exception))

    def test_valid_options_accepted_in_their_own_modes(self) -> None:
        # The wrong-mode rejection must not overreach.
        self.tool.execute(mode="union", a=[1], b=[2])
        self.tool.execute(mode="intersection", a=[1], b=[2])
        self.tool.execute(mode="difference", a=[1], b=[2])
        self.tool.execute(mode="symmetric_difference", a=[1], b=[2])
        self.tool.execute(mode="dedupe", a=[1])
        self.tool.execute(mode="dedupe", a=[{"id": 1}], key="id")
        self.tool.execute(
            mode="unique_count", a=[{"id": 1}], key="id", top_n=3
        )
        self.tool.execute(mode="flatten", a=[1], depth=2)

    def test_string_integer_options_accepted(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="unique_count", a=[1, 1], top_n="2")[
                "top_n"
            ],
            2,
        )
        self.assertEqual(
            self.tool.execute(mode="flatten", a=[[1]], depth="1")["depth"],
            1,
        )

    def test_input_cap_rejects_10001(self) -> None:
        oversized = ["x"] * 10_001
        self.assert_invalid(mode="dedupe", a=oversized)
        self.assert_invalid(mode="union", a=[1], b=oversized)

    def test_input_cap_accepts_exactly_10000(self) -> None:
        result = self.tool.execute(mode="unique_count", a=["x"] * 10_000)
        self.assertEqual(result["counts"]["a"], 10_000)
        self.assertEqual(result["distinct_count"], 1)

    def test_scalar_validation_covers_both_lists(self) -> None:
        # Even though only b's values matter for difference, every
        # element of both lists must be a hashable scalar.
        self.assert_invalid(mode="difference", a=[1], b=[[2]])
        self.assert_invalid(mode="intersection", a=[1], b=[{"id": 2}])

    def test_deterministic_across_calls(self) -> None:
        a = ["b", "a", "b", 1, True, "1"]
        b = ["a", 1.0, "z"]
        for mode in ("union", "intersection", "symmetric_difference"):
            first = self.tool.execute(mode=mode, a=a, b=b)
            for _ in range(5):
                self.assertEqual(first, self.tool.execute(mode=mode, a=a, b=b))


class ListOpsToolPackagingTest(unittest.TestCase):
    """Class defaults, exports and metadata."""

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectListOpsTool, ListOpsTool)
        tool = ListOpsTool()
        self.assertEqual(tool.name, "list_ops_tool")
        self.assertIn("union", tool.description)
        self.assertIn("flatten", tool.description)
        self.assertEqual(
            ListOpsTool.MODES,
            (
                "union",
                "intersection",
                "difference",
                "symmetric_difference",
                "dedupe",
                "unique_count",
                "flatten",
            ),
        )
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ListOpsTool", __all__)


if __name__ == "__main__":
    unittest.main()
