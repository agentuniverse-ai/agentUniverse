#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_url_query_tool.py

"""Offline unit tests for UrlQueryTool.

The tool is built purely on the standard library (urllib.parse) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: each mode is checked against exact
ground-truth URLs (add / update order preservation, repeated keys
untouched by other operations, encoding of spaces / '&' / '=' / CJK /
emoji in both directions, empty values, delete-all-repeats, rename
collisions, stable sorting, dangling-'?' handling, strict mode), the
error matrix against exact error types, and round-trip properties
(idempotence per mode, set-stability, agreement of the reported
pairs with ``urllib.parse.parse_qsl`` on the produced URL) over a
corpus of tricky URLs.
"""

import unittest
import urllib.parse

from agentuniverse.agent.action.tool.common_tool import UrlQueryTool
from agentuniverse.agent.action.tool.common_tool.url_query_tool import (
    UrlQueryTool as DirectUrlQueryTool,
)

# Corpus of url-shaped strings the round-trip properties run over.
CORPUS = (
    "https://example.com/path?b=2&a=1&a=0&c=3#frag",
    "https://example.com:8443/p?a=&a",
    "https://example.com/p?=v&a=1",
    "https://example.com/p?a=1&&b=2",
    "https://example.com/p?a",
    "https://example.com/p?",
    "https://example.com/p",
    "https://example.com/p?q=hello+world&x=1",
    "https://example.com/p?q=a%20b&y=%2B2",
    "https://example.com/p?q=%E4%B8%AD%E6%96%87",
    "https://example.com/p?tag=a&tag=b#f?x=1",
    "//cdn.example.com/lib.js?v=2&v=3",
    "/rel/path?x=1",
    "?a=1&b=2",
    "ftp://files.example.com/pub?dl=1",
    "HTTP://Example.COM/p?a=1",
)


def parse_qsl_of(url: str):
    """Decode the query of ``url`` exactly like the stdlib does."""
    return [
        list(pair)
        for pair in urllib.parse.parse_qsl(
            urllib.parse.urlsplit(url).query, keep_blank_values=True
        )
    ]


class UrlQueryToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib UrlQueryTool."""

    def setUp(self) -> None:
        self.tool = UrlQueryTool()

    # ------------------------------------------------------------------ #
    # export sanity
    # ------------------------------------------------------------------ #

    def test_direct_import_matches_package_export(self) -> None:
        self.assertIs(UrlQueryTool, DirectUrlQueryTool)

    # ------------------------------------------------------------------ #
    # set mode — ground truths
    # ------------------------------------------------------------------ #

    def test_set_adds_new_keys_appended(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://e.com/s?b=2", params={"a": "1"}
        )
        self.assertEqual(
            result,
            {
                "mode": "set",
                "url": "https://e.com/s?b=2&a=1",
                "params": [["b", "2"], ["a", "1"]],
                "added": ["a"],
                "updated": [],
            },
        )

    def test_set_updates_preserve_existing_order(self) -> None:
        result = self.tool.execute(
            mode="set",
            url="https://e.com/s?b=2&a=1&c=3",
            params={"a": "9"},
        )
        self.assertEqual(result["url"], "https://e.com/s?b=2&a=9&c=3")
        self.assertEqual(result["updated"], ["a"])
        self.assertEqual(result["added"], [])
        self.assertEqual(
            result["params"], [["b", "2"], ["a", "9"], ["c", "3"]]
        )

    def test_set_updates_only_first_occurrence_of_repeated_key(
        self,
    ) -> None:
        result = self.tool.execute(
            mode="set",
            url="https://e.com/s?a=1&b=2&a=3",
            params={"a": "9"},
        )
        self.assertEqual(result["url"], "https://e.com/s?a=9&b=2&a=3")
        self.assertEqual(result["updated"], ["a"])
        self.assertEqual(
            result["params"], [["a", "9"], ["b", "2"], ["a", "3"]]
        )

    def test_set_appends_multiple_new_keys_in_dict_order(self) -> None:
        result = self.tool.execute(
            mode="set",
            url="https://e.com/s",
            params={"a": 1, "z": True, "m": 2.5},
        )
        self.assertEqual(result["url"], "https://e.com/s?a=1&z=true&m=2.5")
        self.assertEqual(result["added"], ["a", "z", "m"])

    def test_set_value_coercion_rule(self) -> None:
        result = self.tool.execute(
            mode="set",
            url="https://e.com/s",
            params={"t": True, "f": False, "i": 42, "x": 2.0, "s": "v"},
        )
        self.assertEqual(
            result["url"],
            "https://e.com/s?t=true&f=false&i=42&x=2.0&s=v",
        )
        # bool is checked before int: True is 'true', never '1'.
        self.assertEqual(
            result["params"],
            [
                ["t", "true"],
                ["f", "false"],
                ["i", "42"],
                ["x", "2.0"],
                ["s", "v"],
            ],
        )

    def test_set_empty_value_is_preserved(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://e.com/s?keep=1", params={"e": ""}
        )
        self.assertEqual(result["url"], "https://e.com/s?keep=1&e=")
        self.assertEqual(result["params"], [["keep", "1"], ["e", ""]])

    def test_set_on_dangling_question_mark(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p?", params={"a": "1"}
        )
        self.assertEqual(result["url"], "https://h/p?a=1")

    def test_set_on_url_without_query(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p#frag", params={"a": "1"}
        )
        self.assertEqual(result["url"], "https://h/p?a=1#frag")

    def test_set_repeated_keys_untouched_by_other_updates(self) -> None:
        result = self.tool.execute(
            mode="set",
            url="https://h/p?t=a&t=b&x=1&t=c",
            params={"x": "9"},
        )
        self.assertEqual(result["url"], "https://h/p?t=a&t=b&x=9&t=c")

    # ------------------------------------------------------------------ #
    # encoding — both directions
    # ------------------------------------------------------------------ #

    def test_set_encodes_space_as_plus(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p", params={"q": "hello world"}
        )
        self.assertEqual(result["url"], "https://h/p?q=hello+world")
        self.assertEqual(result["params"], [["q", "hello world"]])

    def test_set_encodes_ampersand_and_equals_in_values(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p", params={"t": "a&b=c"}
        )
        self.assertEqual(result["url"], "https://h/p?t=a%26b%3Dc")
        self.assertEqual(result["params"], [["t", "a&b=c"]])

    def test_set_encodes_cjk_and_emoji(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p", params={"k": "中文🚀"}
        )
        self.assertEqual(
            result["url"], "https://h/p?k=%E4%B8%AD%E6%96%87%F0%9F%9A%80"
        )
        # ... and decodes back to the same characters.
        self.assertEqual(result["params"], [["k", "中文🚀"]])

    def test_set_treats_percent_literals_as_data(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p", params={"p": "a%20b"}
        )
        self.assertEqual(result["url"], "https://h/p?p=a%2520b")
        self.assertEqual(result["params"], [["p", "a%20b"]])

    def test_set_raw_mode_passes_pre_encoded_values_through(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p", params={"p": "a%20b"},
            encode=False,
        )
        self.assertEqual(result["url"], "https://h/p?p=a%20b")
        # The report reflects what the URL actually decodes to.
        self.assertEqual(result["params"], [["p", "a b"]])

    def test_delete_decodes_and_reencodes_plus_literals(self) -> None:
        result = self.tool.execute(
            mode="delete", url="https://h/p?q=%2B2&x=1", keys=["x"]
        )
        self.assertEqual(result["url"], "https://h/p?q=%2B2")
        self.assertEqual(result["params"], [["q", "+2"]])

    def test_untouched_pairs_canonicalize_encoding(self) -> None:
        # %20 and + both mean space; canonical re-encoding uses '+'.
        result = self.tool.execute(
            mode="delete", url="https://h/p?q=a%20b&x=1", keys=["x"]
        )
        self.assertEqual(result["url"], "https://h/p?q=a+b")
        self.assertEqual(result["params"], [["q", "a b"]])

    def test_untouched_pairs_kept_byte_for_byte_in_raw_mode(self) -> None:
        result = self.tool.execute(
            mode="delete", url="https://h/p?q=a%20b&x=1", keys=["x"],
            encode=False,
        )
        self.assertEqual(result["url"], "https://h/p?q=a%20b")

    def test_rename_keeps_raw_value_bytes_in_raw_mode(self) -> None:
        result = self.tool.execute(
            mode="rename", url="https://h/p?a=x%20y&b=2",
            mapping={"a": "c"}, encode=False,
        )
        self.assertEqual(result["url"], "https://h/p?c=x%20y&b=2")

    # ------------------------------------------------------------------ #
    # delete mode — ground truths
    # ------------------------------------------------------------------ #

    def test_delete_removes_every_occurrence_and_reports_missing(self) -> None:
        result = self.tool.execute(
            mode="delete", url="https://h/p?a=1&b=2&a=3&c=4",
            keys=["a", "c", "zz"],
        )
        self.assertEqual(
            result,
            {
                "mode": "delete",
                "url": "https://h/p?b=2",
                "params": [["b", "2"]],
                "deleted": ["a", "c"],
                "missing": ["zz"],
                "removed": 3,
            },
        )

    def test_delete_to_empty_query_drops_question_mark(self) -> None:
        result = self.tool.execute(
            mode="delete", url="https://h/p?a=1&b=2", keys=["a", "b"]
        )
        self.assertEqual(result["url"], "https://h/p")
        self.assertEqual(result["params"], [])

    def test_delete_all_repeats_of_empty_values(self) -> None:
        result = self.tool.execute(
            mode="delete", url="https://h/p?a=&a&keep=1", keys=["a"]
        )
        self.assertEqual(result["url"], "https://h/p?keep=1")
        self.assertEqual(result["removed"], 2)

    def test_delete_missing_key_leaves_url_byte_identical(self) -> None:
        url = "HTTP://Example.COM:8080/p?a=1"
        result = self.tool.execute(mode="delete", url=url, keys=["zz"])
        self.assertEqual(result["url"], url)

    def test_delete_deduplicates_reported_keys(self) -> None:
        result = self.tool.execute(
            mode="delete", url="https://h/p?a=1&b=2", keys=["a", "a"]
        )
        self.assertEqual(result["deleted"], ["a"])
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["removed"], 1)

    # ------------------------------------------------------------------ #
    # rename mode — ground truths
    # ------------------------------------------------------------------ #

    def test_rename_in_place_keeps_order(self) -> None:
        result = self.tool.execute(
            mode="rename", url="https://h/p?old=1&b=2",
            mapping={"old": "new"},
        )
        self.assertEqual(
            result,
            {
                "mode": "rename",
                "url": "https://h/p?new=1&b=2",
                "params": [["new", "1"], ["b", "2"]],
                "renamed": {"old": "new"},
                "missing": [],
                "renamed_count": 1,
            },
        )

    def test_rename_collision_coexists_as_repeats(self) -> None:
        result = self.tool.execute(
            mode="rename", url="https://h/p?b=1&a=2", mapping={"a": "b"}
        )
        self.assertEqual(result["url"], "https://h/p?b=1&b=2")
        self.assertEqual(result["params"], [["b", "1"], ["b", "2"]])

    def test_rename_applies_against_original_keys_no_cascade(self) -> None:
        result = self.tool.execute(
            mode="rename", url="https://h/p?a=1&b=2",
            mapping={"a": "b", "b": "c"},
        )
        self.assertEqual(result["url"], "https://h/p?b=1&c=2")
        self.assertEqual(
            result["renamed"], {"a": "b", "b": "c"}
        )
        self.assertEqual(result["renamed_count"], 2)

    def test_rename_repeated_keys_all_occurrences(self) -> None:
        result = self.tool.execute(
            mode="rename", url="https://h/p?a=1&x=2&a=3", mapping={"a": "z"}
        )
        self.assertEqual(result["url"], "https://h/p?z=1&x=2&z=3")
        self.assertEqual(result["renamed_count"], 2)

    def test_rename_missing_keys_reported(self) -> None:
        result = self.tool.execute(
            mode="rename", url="https://h/p?a=1", mapping={"nope": "x"}
        )
        self.assertEqual(result["url"], "https://h/p?a=1")
        self.assertEqual(result["missing"], ["nope"])
        self.assertEqual(result["renamed"], {})

    # ------------------------------------------------------------------ #
    # clear mode — ground truths
    # ------------------------------------------------------------------ #

    def test_clear_removes_query_keeps_fragment(self) -> None:
        result = self.tool.execute(
            mode="clear", url="https://h/p?a=1&b=2#frag"
        )
        self.assertEqual(
            result,
            {
                "mode": "clear",
                "url": "https://h/p#frag",
                "params": [],
                "removed_params": 2,
                "had_query": True,
            },
        )

    def test_clear_drops_dangling_question_mark(self) -> None:
        result = self.tool.execute(mode="clear", url="https://h/p?")
        self.assertEqual(result["url"], "https://h/p")
        self.assertTrue(result["had_query"])
        self.assertEqual(result["removed_params"], 0)

    def test_clear_keeps_fragment_containing_question_mark(self) -> None:
        result = self.tool.execute(
            mode="clear", url="https://h/p?a=1#f?x=2"
        )
        self.assertEqual(result["url"], "https://h/p#f?x=2")

    def test_clear_without_query_is_noop(self) -> None:
        result = self.tool.execute(mode="clear", url="https://h/p#f")
        self.assertEqual(result["url"], "https://h/p#f")
        self.assertFalse(result["had_query"])

    # ------------------------------------------------------------------ #
    # sort mode — ground truths
    # ------------------------------------------------------------------ #

    def test_sort_orders_keys_stably_for_repeats(self) -> None:
        result = self.tool.execute(
            mode="sort", url="https://h/p?b=2&a=1&a=0&c=3"
        )
        self.assertEqual(
            result,
            {
                "mode": "sort",
                "url": "https://h/p?a=1&a=0&b=2&c=3",
                "params": [["a", "1"], ["a", "0"], ["b", "2"], ["c", "3"]],
                "sorted": True,
            },
        )

    def test_sort_already_sorted_reports_false(self) -> None:
        result = self.tool.execute(
            mode="sort", url="https://h/p?a=1&b=2"
        )
        self.assertEqual(result["url"], "https://h/p?a=1&b=2")
        self.assertFalse(result["sorted"])

    def test_sort_preserves_repeated_key_relative_order(self) -> None:
        result = self.tool.execute(
            mode="sort", url="https://h/p?z=1&a=2&a=1"
        )
        self.assertEqual(result["url"], "https://h/p?a=2&a=1&z=1")

    def test_sort_raw_mode_reorders_verbatim_segments(self) -> None:
        result = self.tool.execute(
            mode="sort", url="https://h/p?b=2&a=+x", encode=False
        )
        self.assertEqual(result["url"], "https://h/p?a=+x&b=2")

    # ------------------------------------------------------------------ #
    # toggle_bool mode — ground truths
    # ------------------------------------------------------------------ #

    def test_toggle_true_to_false(self) -> None:
        result = self.tool.execute(
            mode="toggle_bool", url="https://h/p?flag=true&x=1", key="flag"
        )
        self.assertEqual(
            result,
            {
                "mode": "toggle_bool",
                "key": "flag",
                "url": "https://h/p?flag=false&x=1",
                "params": [["flag", "false"], ["x", "1"]],
                "action": "flipped",
                "from": "true",
                "to": "false",
            },
        )

    def test_toggle_false_to_true(self) -> None:
        result = self.tool.execute(
            mode="toggle_bool", url="https://h/p?f=false", key="f"
        )
        self.assertEqual(result["url"], "https://h/p?f=true")
        self.assertEqual(
            (result["action"], result["from"], result["to"]),
            ("flipped", "false", "true"),
        )

    def test_toggle_matches_case_insensitively(self) -> None:
        result = self.tool.execute(
            mode="toggle_bool", url="https://h/p?f=TRUE", key="f"
        )
        self.assertEqual(result["url"], "https://h/p?f=false")
        self.assertEqual(result["from"], "true")

    def test_toggle_absent_key_adds_true(self) -> None:
        result = self.tool.execute(
            mode="toggle_bool", url="https://h/p?x=1", key="f"
        )
        self.assertEqual(result["url"], "https://h/p?x=1&f=true")
        self.assertEqual(result["action"], "added")
        self.assertIsNone(result["from"])
        self.assertEqual(result["to"], "true")

    def test_toggle_flips_only_first_occurrence(self) -> None:
        result = self.tool.execute(
            mode="toggle_bool", url="https://h/p?f=true&f=false", key="f"
        )
        self.assertEqual(result["url"], "https://h/p?f=false&f=false")

    def test_toggle_rejects_non_boolean_values(self) -> None:
        result = self.tool.execute(
            mode="toggle_bool", url="https://h/p?f=maybe", key="f"
        )
        self.assertEqual(result["error"]["type"], "invalid_value")
        self.assertNotIn("url", result)

    # ------------------------------------------------------------------ #
    # url shape — leniency, byte fidelity, fragments
    # ------------------------------------------------------------------ #

    def test_scheme_relative_url_accepted(self) -> None:
        result = self.tool.execute(
            mode="set", url="//cdn.e.com/lib.js?v=2", params={"v": "3"}
        )
        self.assertEqual(result["url"], "//cdn.e.com/lib.js?v=3")

    def test_non_http_scheme_accepted(self) -> None:
        result = self.tool.execute(
            mode="delete", url="ftp://files.e.com/pub?dl=1", keys=["dl"]
        )
        self.assertEqual(result["url"], "ftp://files.e.com/pub")

    def test_path_only_and_query_only_strings(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="set", url="/search", params={"q": "x"}
            )["url"],
            "/search?q=x",
        )
        self.assertEqual(
            self.tool.execute(
                mode="toggle_bool", url="?a=true", key="a"
            )["url"],
            "?a=false",
        )

    def test_prefix_and_fragment_stay_byte_identical(self) -> None:
        url = "HTTP://Example.COM:8080/p?a=1#frag"
        result = self.tool.execute(
            mode="set", url=url, params={"a": "2"}
        )
        self.assertEqual(result["url"], "HTTP://Example.COM:8080/p?a=2#frag")

    def test_fragment_with_question_mark_untouched(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p?a=1#f?x=2", params={"a": "9"}
        )
        self.assertEqual(result["url"], "https://h/p?a=9#f?x=2")

    def test_strict_mode_requires_scheme(self) -> None:
        result = self.tool.execute(
            mode="set", url="/search?q=1", params={"a": "1"}, strict=True
        )
        self.assertEqual(result["error"]["type"], "missing_scheme")
        # The same input passes with the default lenient mode.
        ok = self.tool.execute(
            mode="set", url="/search?q=1", params={"a": "1"}
        )
        self.assertEqual(ok["url"], "/search?q=1&a=1")

    def test_strict_mode_accepts_schemed_urls(self) -> None:
        result = self.tool.execute(
            mode="set", url="https://h/p", params={"a": "1"}, strict=True
        )
        self.assertEqual(result["url"], "https://h/p?a=1")

    # ------------------------------------------------------------------ #
    # structured content errors
    # ------------------------------------------------------------------ #

    def test_malformed_url_with_space(self) -> None:
        result = self.tool.execute(
            mode="sort", url="https://h/p?a=1 b"
        )
        self.assertEqual(result["error"]["type"], "malformed_url")

    def test_malformed_url_unmatched_ipv6_bracket(self) -> None:
        result = self.tool.execute(mode="sort", url="http://[::1/p?a=1")
        self.assertEqual(result["error"]["type"], "malformed_url")

    def test_raw_mode_rejects_structure_breaking_characters(self) -> None:
        for params in ({"a": "b c"}, {"a": "b&c"}, {"a": "b#c"}, {"a&b": "c"}):
            result = self.tool.execute(
                mode="set", url="https://h/p", params=params, encode=False
            )
            self.assertEqual(
                result["error"]["type"], "invalid_value", params
            )
        # '=' is allowed in raw values (base64 padding round-trips).
        ok = self.tool.execute(
            mode="set", url="https://h/p", params={"t": "abc=="},
            encode=False,
        )
        self.assertEqual(ok["url"], "https://h/p?t=abc==")

    # ------------------------------------------------------------------ #
    # error matrix — parameter-level ValueErrors
    # ------------------------------------------------------------------ #

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="edit", url="https://h/p?a=1")

    def test_missing_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode=None, url="https://h/p?a=1")

    def test_bad_url_raises(self) -> None:
        for url in (None, 5, True, "", " " * 100_001):
            with self.assertRaises(ValueError, msg=repr(url)):
                self.tool.execute(mode="sort", url=url)

    def test_bad_params_raise(self) -> None:
        bad = (
            None, "a=1", [], {}, {5: "v"}, {"": "v"}, {True: "v"},
            {"a": None}, {"a": ["x"]}, {"a": {"b": 1}}, {"a": (1,)},
        )
        for params in bad:
            with self.assertRaises(ValueError, msg=repr(params)):
                self.tool.execute(
                    mode="set", url="https://h/p", params=params
                )

    def test_bad_keys_raise(self) -> None:
        bad = (None, "a", [], [1], [""], [True], [[]])
        for keys in bad:
            with self.assertRaises(ValueError, msg=repr(keys)):
                self.tool.execute(
                    mode="delete", url="https://h/p?a=1", keys=keys
                )

    def test_bad_mapping_raises(self) -> None:
        bad = (None, [], {}, {"a": 5}, {5: "b"}, {"a": None}, {"a": "a"})
        for mapping in bad:
            with self.assertRaises(ValueError, msg=repr(mapping)):
                self.tool.execute(
                    mode="rename", url="https://h/p?a=1", mapping=mapping
                )

    def test_bad_toggle_key_raises(self) -> None:
        for key in (None, 5, True, ""):
            with self.assertRaises(ValueError, msg=repr(key)):
                self.tool.execute(
                    mode="toggle_bool", url="https://h/p?f=true", key=key
                )

    def test_bad_flags_raise(self) -> None:
        for kwargs in ({"encode": "yes"}, {"encode": 1}, {"strict": 0},
                       {"strict": None or "no"}):
            with self.assertRaises(ValueError, msg=repr(kwargs)):
                self.tool.execute(mode="sort", url="https://h/p?a=1", **kwargs)

    # ------------------------------------------------------------------ #
    # round-trip properties over the corpus
    # ------------------------------------------------------------------ #

    def test_set_is_stable_after_first_application(self) -> None:
        for url in CORPUS:
            with self.subTest(url=url):
                first = self.tool.execute(
                    mode="set", url=url, params={"zz": "new", "a": "upd"}
                )
                second = self.tool.execute(
                    mode="set",
                    url=first["url"],
                    params={"zz": "new", "a": "upd"},
                )
                self.assertEqual(first["url"], second["url"])

    def test_delete_is_stable_after_first_application(self) -> None:
        for url in CORPUS:
            with self.subTest(url=url):
                first = self.tool.execute(
                    mode="delete", url=url, keys=["zz"]
                )
                second = self.tool.execute(
                    mode="delete", url=first["url"], keys=["zz"]
                )
                self.assertEqual(first["url"], second["url"])

    def test_sort_is_idempotent(self) -> None:
        for url in CORPUS:
            with self.subTest(url=url):
                first = self.tool.execute(mode="sort", url=url)
                second = self.tool.execute(mode="sort", url=first["url"])
                self.assertEqual(first["url"], second["url"])
                self.assertFalse(second["sorted"])

    def test_clear_is_idempotent(self) -> None:
        for url in CORPUS:
            with self.subTest(url=url):
                first = self.tool.execute(mode="clear", url=url)
                if first["url"] == "":
                    # Clearing a query-only URL yields the empty
                    # string, which is not a valid further input.
                    self.assertEqual(url, "?a=1&b=2")
                    continue
                second = self.tool.execute(mode="clear", url=first["url"])
                self.assertEqual(first["url"], second["url"])

    def test_rename_second_pass_reports_missing_and_is_stable(
        self,
    ) -> None:
        for url in CORPUS:
            with self.subTest(url=url):
                first = self.tool.execute(
                    mode="rename", url=url, mapping={"a": "zz"}
                )
                second = self.tool.execute(
                    mode="rename", url=first["url"], mapping={"a": "zz"}
                )
                self.assertEqual(first["url"], second["url"])
                self.assertEqual(second["missing"], ["a"])

    def test_toggle_twice_round_trips_boolean_values(self) -> None:
        for url in (
            "https://h/p?f=true&x=1",
            "https://h/p?f=false",
            "https://h/p?x=1&f=false",
        ):
            with self.subTest(url=url):
                first = self.tool.execute(
                    mode="toggle_bool", url=url, key="f"
                )
                second = self.tool.execute(
                    mode="toggle_bool", url=first["url"], key="f"
                )
                self.assertEqual(second["url"], url)

    def test_reported_params_always_match_parse_qsl_of_output(self) -> None:
        calls = []
        for url in CORPUS:
            calls.append(("set", self.tool.execute(
                mode="set", url=url, params={"q": "a b", "n": 1})))
            calls.append(("set-raw", self.tool.execute(
                mode="set", url=url, params={"q": "a%20b"}, encode=False)))
            calls.append(("delete", self.tool.execute(
                mode="delete", url=url, keys=["a", "zz"])))
            calls.append(("rename", self.tool.execute(
                mode="rename", url=url, mapping={"a": "zz", "b": "yy"})))
            calls.append(("sort", self.tool.execute(mode="sort", url=url)))
            calls.append(("sort-raw", self.tool.execute(
                mode="sort", url=url, encode=False)))
            calls.append(("toggle", self.tool.execute(
                mode="toggle_bool", url=url, key="zz")))
        for label, result in calls:
            with self.subTest(label=label, url=result.get("url")):
                if "error" in result:
                    continue
                self.assertEqual(
                    result["params"], parse_qsl_of(result["url"])
                )

    def test_fragment_survives_every_mode_byte_identically(self) -> None:
        fragment = "#frag?x=1&y=2"
        url = "https://h/p?a=true&b=2" + fragment
        results = (
            self.tool.execute(mode="set", url=url, params={"c": "3"}),
            self.tool.execute(mode="delete", url=url, keys=["a"]),
            self.tool.execute(mode="rename", url=url, mapping={"a": "z"}),
            self.tool.execute(mode="clear", url=url),
            self.tool.execute(mode="sort", url=url),
            self.tool.execute(mode="toggle_bool", url=url, key="a"),
        )
        for result in results:
            self.assertTrue(result["url"].endswith(fragment))

    def test_empty_segments_and_bare_keys_normalized_away(self) -> None:
        result = self.tool.execute(
            mode="delete", url="https://h/p?a=1&&b=2", keys=["zz"]
        )
        self.assertEqual(result["url"], "https://h/p?a=1&b=2")
        bare = self.tool.execute(mode="delete", url="https://h/p?a", keys=["zz"])
        self.assertEqual(bare["url"], "https://h/p?a=")


if __name__ == "__main__":
    unittest.main()
