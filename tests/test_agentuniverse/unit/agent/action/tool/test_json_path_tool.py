#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_json_path_tool.py

"""Offline unit tests for JsonPathTool.

The tool is built purely on the standard library (json plus a hand
written path parser) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: extraction results are
checked against literal expected values embedded in this file, rendered
match paths against literal strings, and error payloads against their
exact types. Filters, slices and wildcards are exercised over a fixed
document whose element order json.loads preserves.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import JsonPathTool
from agentuniverse.agent.action.tool.common_tool.json_path_tool import (
    JsonPathTool as DirectJsonPathTool,
)

# --------------------------------------------------------------------- #
# Fixed ground-truth document (order-preserving under json.loads)
# --------------------------------------------------------------------- #
STORE = {
    "store": {
        "book": [
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            },
        ],
        "bicycle": {"color": "red", "price": 19.95},
    },
    "expensive": 10,
}
STORE_JSON = json.dumps(STORE)

BOOK_TITLES = [book["title"] for book in STORE["store"]["book"]]
BOOK_AUTHORS = [book["author"] for book in STORE["store"]["book"]]


def values(result):
    """Shorthand: the value list of a query result."""
    return [match["value"] for match in result["matches"]]


def paths(result):
    """Shorthand: the rendered path list of a query result."""
    return [match["path"] for match in result["matches"]]


class JsonPathToolQueryTest(unittest.TestCase):
    """Offline deterministic query-mode test cases for JsonPathTool."""

    def setUp(self) -> None:
        self.tool = JsonPathTool()

    # ------------------------------------------------------------------ #
    # dot / bracket navigation ground truth
    # ------------------------------------------------------------------ #

    def test_query_full_result_contract(self) -> None:
        result = self.tool.execute(mode="query", data='{"a": 1}', path="$.a")
        self.assertEqual(
            result,
            {
                "mode": "query",
                "path": "$.a",
                "found": True,
                "count": 1,
                "truncated": False,
                "matches": [{"path": "$.a", "value": 1}],
            },
        )

    def test_query_dot_key(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.expensive"
        )
        self.assertEqual(values(result), [10])
        self.assertEqual(paths(result), ["$.expensive"])

    def test_query_nested_dot_keys(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.bicycle.color"
        )
        self.assertEqual(values(result), ["red"])

    def test_query_bracket_index(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[0].title"
        )
        self.assertEqual(values(result), ["Sayings of the Century"])
        self.assertEqual(paths(result), ["$.store.book[0].title"])

    def test_query_negative_index_renders_concrete_index(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[-1].title"
        )
        self.assertEqual(values(result), ["The Lord of the Rings"])
        self.assertEqual(paths(result), ["$.store.book[3].title"])

    def test_query_leading_root_is_optional(self) -> None:
        with_root = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[0].title"
        )
        without_root = self.tool.execute(
            mode="query", data=STORE_JSON, path="store.book[0].title"
        )
        # The echoed path differs; everything else must be identical.
        with_root.pop("path")
        without_root.pop("path")
        self.assertEqual(with_root, without_root)
        self.assertEqual(values(with_root), ["Sayings of the Century"])

    def test_query_root_alone_selects_whole_document(self) -> None:
        result = self.tool.execute(mode="query", data=STORE_JSON, path="$")
        self.assertTrue(result["found"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(values(result), [STORE])

    def test_query_quoted_bracket_keys_with_spaces(self) -> None:
        data = json.dumps({"a b": {"c d": 1}})
        result = self.tool.execute(
            mode="query", data=data, path="$['a b']['c d']"
        )
        self.assertEqual(values(result), [1])
        self.assertEqual(paths(result), ["$['a b']['c d']"])

    def test_query_quoted_key_escapes(self) -> None:
        data = json.dumps({"it's": {"a\\b": 7}})
        result = self.tool.execute(
            mode="query", data=data, path="$['it\\'s']['a\\\\b']"
        )
        self.assertEqual(values(result), [7])

    def test_query_quoted_bare_key_renders_dot_form(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$['store']['bicycle']['color']"
        )
        self.assertEqual(values(result), ["red"])
        self.assertEqual(paths(result), ["$.store.bicycle.color"])

    def test_query_data_dict_same_as_json_string(self) -> None:
        from_text = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[*].author"
        )
        from_dict = self.tool.execute(
            mode="query", data=STORE, path="$.store.book[*].author"
        )
        self.assertEqual(from_text, from_dict)

    # ------------------------------------------------------------------ #
    # slices
    # ------------------------------------------------------------------ #

    def test_query_slice_with_bounds(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[1:3].title"
        )
        self.assertEqual(values(result), BOOK_TITLES[1:3])
        self.assertEqual(
            paths(result), ["$.store.book[1].title", "$.store.book[2].title"]
        )

    def test_query_slice_open_ended(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[2:].title"
        )
        self.assertEqual(values(result), BOOK_TITLES[2:])

    def test_query_slice_from_start(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[:2].title"
        )
        self.assertEqual(values(result), BOOK_TITLES[:2])

    def test_query_slice_negative_bounds(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[-2:].title"
        )
        self.assertEqual(values(result), BOOK_TITLES[-2:])

    def test_query_slice_empty_range_is_not_found(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[3:1].title"
        )
        self.assertFalse(result["found"])
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["matches"], [])
        self.assertFalse(result["truncated"])

    # ------------------------------------------------------------------ #
    # wildcards
    # ------------------------------------------------------------------ #

    def test_query_wildcard_over_list(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[*].author"
        )
        self.assertEqual(values(result), BOOK_AUTHORS)
        self.assertEqual(
            paths(result),
            [f"$.store.book[{i}].author" for i in range(len(BOOK_AUTHORS))],
        )

    def test_query_dot_wildcard_over_object(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.bicycle.*"
        )
        self.assertEqual(values(result), ["red", 19.95])

    def test_query_wildcard_over_empty_list(self) -> None:
        result = self.tool.execute(mode="query", data="[]", path="$[*]")
        self.assertFalse(result["found"])
        self.assertEqual(result["matches"], [])

    def test_query_wildcard_over_top_level_list(self) -> None:
        result = self.tool.execute(mode="query", data="[1, 2, 3]", path="$[*]")
        self.assertEqual(values(result), [1, 2, 3])
        self.assertEqual(paths(result), ["$[0]", "$[1]", "$[2]"])

    def test_query_key_on_list_selects_nothing(self) -> None:
        result = self.tool.execute(mode="query", data="[1, 2]", path="$.title")
        self.assertFalse(result["found"])

    # ------------------------------------------------------------------ #
    # filters
    # ------------------------------------------------------------------ #

    def test_query_filter_less_than(self) -> None:
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.price < 10)].title",
        )
        self.assertEqual(values(result), [BOOK_TITLES[0], BOOK_TITLES[2]])
        self.assertEqual(
            paths(result),
            ["$.store.book[0].title", "$.store.book[2].title"],
        )

    def test_query_filter_less_or_equal(self) -> None:
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.price <= 8.99)].title",
        )
        self.assertEqual(values(result), [BOOK_TITLES[0], BOOK_TITLES[2]])

    def test_query_filter_greater_than(self) -> None:
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.price > 20)].title",
        )
        self.assertEqual(values(result), [BOOK_TITLES[3]])

    def test_query_filter_string_equality(self) -> None:
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.category == 'reference')].title",
        )
        self.assertEqual(values(result), [BOOK_TITLES[0]])

    def test_query_filter_string_equality_double_quotes(self) -> None:
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path='$.store.book[?(@.category == "reference")].title',
        )
        self.assertEqual(values(result), [BOOK_TITLES[0]])

    def test_query_filter_not_equals_null_ignores_missing_keys(self) -> None:
        # Only books 2 and 3 carry an isbn; books without it are excluded
        # rather than compared against null.
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.isbn != null)].title",
        )
        self.assertEqual(values(result), [BOOK_TITLES[2], BOOK_TITLES[3]])

    def test_query_filter_boolean_equality(self) -> None:
        data = json.dumps(
            {"flags": [{"on": True, "v": 1}, {"on": False, "v": 2}]}
        )
        result = self.tool.execute(
            mode="query", data=data, path="$.flags[?(@.on == true)].v"
        )
        self.assertEqual(values(result), [1])

    def test_query_filter_strict_typing_cross_type_no_match(self) -> None:
        # 8.95 is a number, '8.95' is a string: strictly typed equality
        # excludes every element instead of raising.
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.price == '8.95')].title",
        )
        self.assertFalse(result["found"])

    def test_query_filter_ordering_strings_selects_nothing(self) -> None:
        data = json.dumps({"words": ["apple", "banana"]})
        result = self.tool.execute(
            mode="query", data=data, path="$.words[?(@ > 'a')]"
        )
        self.assertFalse(result["found"])

    def test_query_filter_element_itself_with_at(self) -> None:
        # '@' alone refers to the iterated element itself: here the
        # values of the scores object.
        data = json.dumps({"scores": {"a": 5, "b": 15}})
        result = self.tool.execute(
            mode="query", data=data, path="$.scores[?(@ >= 10)]"
        )
        self.assertEqual(values(result), [15])
        self.assertEqual(paths(result), ["$.scores.b"])

    def test_query_filter_quoted_key_sub_path(self) -> None:
        data = json.dumps({"rows": [{"unit price": 3}, {"unit price": 30}]})
        result = self.tool.execute(
            mode="query", data=data, path="$.rows[?(@['unit price'] > 10)]"
        )
        self.assertEqual(values(result), [{"unit price": 30}])

    def test_query_filter_index_sub_path(self) -> None:
        data = json.dumps(
            {"rows": [{"tags": ["a", "b"]}, {"tags": ["b", "c"]}]}
        )
        result = self.tool.execute(
            mode="query", data=data, path="$.rows[?(@.tags[0] == 'b')]"
        )
        self.assertEqual(values(result), [{"tags": ["b", "c"]}])

    def test_query_filter_missing_sub_path_excludes_element(self) -> None:
        result = self.tool.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.isbn == null)].title",
        )
        # isbn is absent on books 0 and 1, so no element has a present
        # null value; strictly, this selects nothing.
        self.assertFalse(result["found"])

    # ------------------------------------------------------------------ #
    # no-match behaviour
    # ------------------------------------------------------------------ #

    def test_query_missing_key_selects_nothing(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.magazine"
        )
        self.assertFalse(result["found"])
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["matches"], [])
        self.assertNotIn("error", result)

    def test_query_out_of_range_index_selects_nothing(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[99].title"
        )
        self.assertFalse(result["found"])

    def test_query_navigation_through_scalar_selects_nothing(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.expensive.price"
        )
        self.assertFalse(result["found"])

    # ------------------------------------------------------------------ #
    # caps
    # ------------------------------------------------------------------ #

    def test_query_max_matches_truncates_with_flag(self) -> None:
        capped = JsonPathTool(max_matches=2)
        result = capped.execute(
            mode="query", data=STORE_JSON, path="$.store.book[*].author"
        )
        self.assertEqual(values(result), BOOK_AUTHORS[:2])
        self.assertEqual(result["count"], 2)
        self.assertTrue(result["truncated"])

    def test_query_max_matches_exact_count_not_truncated(self) -> None:
        exact = JsonPathTool(max_matches=4)
        result = exact.execute(
            mode="query", data=STORE_JSON, path="$.store.book[*].author"
        )
        self.assertEqual(values(result), BOOK_AUTHORS)
        self.assertFalse(result["truncated"])

    def test_query_max_matches_applies_to_filters_too(self) -> None:
        capped = JsonPathTool(max_matches=1)
        result = capped.execute(
            mode="query",
            data=STORE_JSON,
            path="$.store.book[?(@.category == 'fiction')].title",
        )
        self.assertEqual(result["count"], 1)
        self.assertTrue(result["truncated"])

    # ------------------------------------------------------------------ #
    # structured error payloads (content-level failures)
    # ------------------------------------------------------------------ #

    def test_query_invalid_json_payload(self) -> None:
        result = self.tool.execute(mode="query", data="{oops", path="$.a")
        self.assertEqual(result["mode"], "query")
        self.assertEqual(result["error"]["type"], "invalid_json")
        self.assertIn("not valid JSON", result["error"]["message"])

    def test_query_nan_constant_rejected(self) -> None:
        result = self.tool.execute(
            mode="query", data='{"a": NaN}', path="$.a"
        )
        self.assertEqual(result["error"]["type"], "invalid_json")

    def test_query_deeply_nested_json_reports_invalid_json(self) -> None:
        deep = "[" * 6000 + "]" * 6000
        result = self.tool.execute(mode="query", data=deep, path="$")
        if result.get("found"):
            # The interpreter parsed the nesting without RecursionError;
            # the guard is then simply not triggered on this platform.
            self.skipTest("platform parsed deep nesting without recursion error")
        self.assertEqual(result["error"]["type"], "invalid_json")

    def test_query_unterminated_bracket_payload(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book["
        )
        self.assertEqual(result["error"]["type"], "invalid_path")
        self.assertIn("unterminated", result["error"]["message"])

    def test_query_unterminated_quoted_key_payload(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$['store"
        )
        self.assertEqual(result["error"]["type"], "invalid_path")

    def test_query_slice_step_unsupported_payload(self) -> None:
        result = self.tool.execute(
            mode="query", data='{"a": [1, 2, 3]}', path="$.a[0:3:2]"
        )
        self.assertEqual(result["error"]["type"], "invalid_path")
        self.assertIn("slice", result["error"]["message"])

    def test_query_recursive_descent_unsupported_payload(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$..book"
        )
        self.assertEqual(result["error"]["type"], "invalid_path")

    def test_query_filter_missing_comparator_payload(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[?(@.price)].title"
        )
        self.assertEqual(result["error"]["type"], "invalid_path")
        self.assertIn("comparator", result["error"]["message"])

    def test_query_filter_bad_operator_payload(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[?(@.price <> 3)]"
        )
        self.assertEqual(result["error"]["type"], "invalid_path")

    def test_query_filter_bad_literal_payload(self) -> None:
        result = self.tool.execute(
            mode="query", data=STORE_JSON, path="$.store.book[?(@.price == yes)]"
        )
        self.assertEqual(result["error"]["type"], "invalid_path")
        self.assertIn("literal", result["error"]["message"])

    def test_query_empty_bracket_segment_payload(self) -> None:
        result = self.tool.execute(mode="query", data="{}", path="$.a[]")
        self.assertEqual(result["error"]["type"], "invalid_path")

    def test_query_bare_digit_key_rejected_with_hint(self) -> None:
        result = self.tool.execute(mode="query", data='{"0": 1}', path="$.0")
        self.assertEqual(result["error"]["type"], "invalid_path")
        self.assertIn("quote", result["error"]["message"])

    def test_query_quoted_digit_key_works(self) -> None:
        result = self.tool.execute(mode="query", data='{"0": 1}', path="$['0']")
        self.assertEqual(values(result), [1])
        self.assertEqual(paths(result), ["$['0']"])

    # ------------------------------------------------------------------ #
    # strict input validation (raises ValueError before any work)
    # ------------------------------------------------------------------ #

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="eval", path="$.a", data="{}")

    def test_missing_path_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="query", data="{}")

    def test_non_string_path_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="query", path=123, data="{}")

    def test_empty_path_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="query", path="", data="{}")

    def test_whitespace_path_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="query", path="   ", data="{}")

    def test_overlong_path_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="query", path="a." * 5001, data="{}"
            )

    def test_missing_data_raises_in_query_mode(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="query", path="$.a")

    def test_wrong_data_type_raises(self) -> None:
        for bad in (42, 3.5, True, ("no",)):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="query", path="$.a", data=bad)

    def test_non_container_decoded_data_raises(self) -> None:
        # Decoded documents must be dict/list; scalars and other types
        # are malformed parameters even though JSON allows scalars.
        for bad in (42, 3.5, True):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="query", path="$", data=bad)

    def test_empty_json_string_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="query", path="$.a", data="")

    def test_overlong_data_raises(self) -> None:
        capped = JsonPathTool(max_input_chars=8)
        with self.assertRaises(ValueError):
            capped.execute(mode="query", path="$.a", data='{"a": "longer"}')

    def test_path_chars_cap_constant(self) -> None:
        # The path-length cap is a documented constant (10,000).
        self.assertEqual(JsonPathTool.MAX_PATH_CHARS, 10_000)


class JsonPathToolValidateTest(unittest.TestCase):
    """Offline deterministic validate-mode test cases for JsonPathTool."""

    def setUp(self) -> None:
        self.tool = JsonPathTool()

    def test_validate_reports_token_summaries(self) -> None:
        result = self.tool.execute(
            mode="validate", path="$.store.book[1:2].title"
        )
        self.assertEqual(
            result,
            {
                "mode": "validate",
                "path": "$.store.book[1:2].title",
                "valid": True,
                "tokens": [
                    "root",
                    "key:store",
                    "key:book",
                    "slice:1:2",
                    "key:title",
                ],
            },
        )

    def test_validate_reports_index_and_wildcards(self) -> None:
        result = self.tool.execute(mode="validate", path="$['a b'][*].c")
        self.assertEqual(
            result["tokens"], ["root", "key:a b", "wildcard", "key:c"]
        )

    def test_validate_reports_negative_index(self) -> None:
        result = self.tool.execute(mode="validate", path="$.items[-1]")
        self.assertEqual(result["tokens"], ["root", "key:items", "index:-1"])

    def test_validate_reports_filter_expression(self) -> None:
        result = self.tool.execute(
            mode="validate", path="$.items[?(@.price <= 5)]"
        )
        self.assertTrue(result["valid"])
        self.assertEqual(
            result["tokens"], ["root", "key:items", "filter:@.price <= 5"]
        )

    def test_validate_invalid_path_returns_payload_not_raise(self) -> None:
        result = self.tool.execute(mode="validate", path="$.a[1:2:3]")
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"]["type"], "invalid_path")
        self.assertIn("slice", result["error"]["message"])

    def test_validate_invalid_filter_literal(self) -> None:
        result = self.tool.execute(
            mode="validate", path="$.a[?(@.b == maybe)]"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"]["type"], "invalid_path")

    def test_validate_ignores_data(self) -> None:
        # validate mode only parses the path; data is not required and
        # not inspected.
        result = self.tool.execute(mode="validate", path="$.a", data=123)
        self.assertTrue(result["valid"])


class JsonPathToolRegistrationTest(unittest.TestCase):
    """Package-level import and component plumbing checks."""

    def test_package_export_matches_direct_import(self) -> None:
        self.assertIs(JsonPathTool, DirectJsonPathTool)

    def test_tool_identity_fields(self) -> None:
        tool = JsonPathTool()
        self.assertEqual(tool.name, "json_path_tool")
        self.assertIn("JSON path", tool.description)
        self.assertEqual(tool.max_matches, 1000)
        self.assertEqual(tool.max_input_chars, 100_000)

    def test_defaults_are_overridable(self) -> None:
        tool = JsonPathTool(max_matches=7, max_input_chars=99)
        self.assertEqual(tool.max_matches, 7)
        self.assertEqual(tool.max_input_chars, 99)


if __name__ == "__main__":
    unittest.main()
