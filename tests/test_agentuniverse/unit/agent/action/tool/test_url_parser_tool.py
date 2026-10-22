#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_url_parser_tool.py

"""Offline unit tests for URLParserTool.

The tool is built purely on the standard library (urllib.parse) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: parses are checked against ground-truth
components (RFC 3986 examples, IPv6 literals, userinfo, ports,
multi-value parameters), query operations and builds against exact
expected URLs, normalization against known transformations plus
idempotence, and the error matrix against exact error types.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import URLParserTool
from agentuniverse.agent.action.tool.common_tool.url_parser_tool import (
    URLParserTool as DirectURLParserTool,
)

# RFC 3986 section 1.1.2 example URL.
RFC3986_EXAMPLE = "foo://example.com:8042/over/there?name=ferret#nose"

RICH_URL = "https://user:pass@example.com:8443/docs/a?b=2&a=1&a=1&c#frag"


class URLParserToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib URLParserTool."""

    def setUp(self) -> None:
        self.tool = URLParserTool()

    # ------------------------------------------------------------------ #
    # parse mode — ground truths
    # ------------------------------------------------------------------ #

    def test_direct_import_matches_package_export(self) -> None:
        self.assertIs(URLParserTool, DirectURLParserTool)

    def test_parse_rfc3986_example(self) -> None:
        result = self.tool.execute(mode="parse", url=RFC3986_EXAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "url": RFC3986_EXAMPLE,
                "scheme": "foo",
                "netloc": "example.com:8042",
                "hostname": "example.com",
                "port": 8042,
                "explicit_port": 8042,
                "default_port": None,
                "path": "/over/there",
                "query": "name=ferret",
                "params": [["name", "ferret"]],
                "fragment": "nose",
                "has_user_info": False,
                "username": None,
                "password": None,
                "is_http_scheme": False,
            },
        )

    def test_parse_rich_url_userinfo_ports_multi_value(self) -> None:
        result = self.tool.execute(mode="parse", url=RICH_URL)
        self.assertEqual(result["scheme"], "https")
        self.assertEqual(result["netloc"], "user:pass@example.com:8443")
        self.assertEqual(result["hostname"], "example.com")
        self.assertEqual(result["explicit_port"], 8443)
        self.assertEqual(result["default_port"], 443)
        self.assertEqual(result["port"], 8443)
        self.assertEqual(result["path"], "/docs/a")
        self.assertEqual(result["query"], "b=2&a=1&a=1&c")
        self.assertEqual(
            result["params"],
            [["b", "2"], ["a", "1"], ["a", "1"], ["c", ""]],
        )
        self.assertEqual(result["fragment"], "frag")
        self.assertTrue(result["has_user_info"])
        self.assertEqual(result["username"], "user")
        self.assertEqual(result["password"], "pass")
        self.assertTrue(result["is_http_scheme"])

    def test_parse_resolves_scheme_default_ports(self) -> None:
        for url, expected in (
            ("http://example.com/", 80),
            ("https://example.com/", 443),
            ("ws://example.com/", 80),
            ("wss://example.com/", 443),
            ("ftp://example.com/", 21),
        ):
            result = self.tool.execute(mode="parse", url=url)
            self.assertEqual(result["port"], expected, url)
            self.assertIsNone(result["explicit_port"], url)
            self.assertEqual(result["default_port"], expected, url)

    def test_parse_ipv6_bracketed_host(self) -> None:
        result = self.tool.execute(
            mode="parse", url="http://[2001:db8::1]:8080/x?y=1"
        )
        self.assertEqual(result["netloc"], "[2001:db8::1]:8080")
        self.assertEqual(result["hostname"], "2001:db8::1")
        self.assertEqual(result["explicit_port"], 8080)
        self.assertEqual(result["port"], 8080)
        self.assertEqual(result["params"], [["y", "1"]])
        # Zone ids are preserved raw (the '%25' escape is untouched).
        result = self.tool.execute(
            mode="parse", url="http://[fe80::1%25eth0]/p"
        )
        self.assertEqual(result["hostname"], "fe80::1%25eth0")

    def test_parse_lowercase_hostname_and_scheme(self) -> None:
        result = self.tool.execute(mode="parse", url="HTTP://Ex.Ample.COM/p")
        self.assertEqual(result["scheme"], "http")
        self.assertEqual(result["hostname"], "ex.ample.com")
        self.assertEqual(result["netloc"], "Ex.Ample.COM")

    def test_parse_raw_percent_encoded_userinfo(self) -> None:
        result = self.tool.execute(
            mode="parse", url="http://user%3Aword@h.example/x"
        )
        self.assertTrue(result["has_user_info"])
        self.assertEqual(result["username"], "user%3Aword")
        self.assertIsNone(result["password"])

    def test_parse_percent_encoded_query_decodes(self) -> None:
        result = self.tool.execute(
            mode="parse", url="https://e.example/s?q=hello+world&n=v%2B1"
        )
        self.assertEqual(result["query"], "q=hello+world&n=v%2B1")
        self.assertEqual(
            result["params"], [["q", "hello world"], ["n", "v+1"]]
        )

    def test_parse_no_netloc_and_no_query(self) -> None:
        result = self.tool.execute(mode="parse", url="mailto:someone@example.com")
        self.assertEqual(result["scheme"], "mailto")
        self.assertEqual(result["netloc"], "")
        self.assertIsNone(result["hostname"])
        self.assertEqual(result["params"], [])
        self.assertFalse(result["is_http_scheme"])
        result = self.tool.execute(mode="parse", url="http:///just/a/path")
        self.assertEqual(result["netloc"], "")
        self.assertIsNone(result["hostname"])
        self.assertEqual(result["path"], "/just/a/path")

    def test_parse_empty_port_is_none(self) -> None:
        result = self.tool.execute(mode="parse", url="http://h.example:/p")
        self.assertIsNone(result["explicit_port"])
        self.assertEqual(result["port"], 80)

    # ------------------------------------------------------------------ #
    # query mode
    # ------------------------------------------------------------------ #

    def test_query_get_multi_value(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="get",
            url="https://e.example/s?tag=a&other=1&tag=b",
            key="tag",
        )
        self.assertEqual(
            result,
            {
                "mode": "query",
                "operation": "get",
                "url": "https://e.example/s?tag=a&other=1&tag=b",
                "key": "tag",
                "values": ["a", "b"],
                "count": 2,
            },
        )

    def test_query_get_missing_key_returns_empty(self) -> None:
        result = self.tool.execute(
            mode="query", operation="get", url="https://e.example/s?a=1", key="zz"
        )
        self.assertEqual(result["values"], [])
        self.assertEqual(result["count"], 0)

    def test_query_get_all_pairs_without_key(self) -> None:
        result = self.tool.execute(
            mode="query", operation="get", url="https://e.example/s?b=2&a=1&a=1&c"
        )
        self.assertEqual(
            result["params"], [["b", "2"], ["a", "1"], ["a", "1"], ["c", ""]]
        )

    def test_query_get_on_url_without_query(self) -> None:
        result = self.tool.execute(
            mode="query", operation="get", url="https://e.example/s", key="a"
        )
        self.assertEqual(result["values"], [])
        result = self.tool.execute(
            mode="query", operation="get", url="https://e.example/s"
        )
        self.assertEqual(result["params"], [])

    def test_query_set_replaces_first_occurrence_and_keeps_order(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="set",
            url="https://e.example/s?b=2&a=1",
            key="a",
            value="9",
        )
        self.assertEqual(result["url"], "https://e.example/s?b=2&a=9")
        self.assertTrue(result["replaced"])
        self.assertEqual(result["params"], [["b", "2"], ["a", "9"]])

    def test_query_set_appends_new_key_at_end(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="set",
            url="https://e.example/s?b=2",
            key="a",
            value="1",
        )
        self.assertEqual(result["url"], "https://e.example/s?b=2&a=1")
        self.assertFalse(result["replaced"])

    def test_query_set_collapses_multi_value_with_list(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="set",
            url="https://e.example/s?tag=a&x=1&tag=b",
            key="tag",
            value=["c", "d"],
        )
        self.assertEqual(result["url"], "https://e.example/s?tag=c&tag=d&x=1")
        self.assertTrue(result["replaced"])
        self.assertEqual(result["params"], [["tag", "c"], ["tag", "d"], ["x", "1"]])

    def test_query_set_empty_value_is_kept(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="set",
            url="https://e.example/s?a=1",
            key="b",
            value="",
        )
        self.assertEqual(result["url"], "https://e.example/s?a=1&b=")

    def test_query_set_on_url_without_query(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="set",
            url="https://e.example/s#frag",
            key="a",
            value="1",
        )
        self.assertEqual(result["url"], "https://e.example/s?a=1#frag")

    def test_query_delete_removes_all_occurrences(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="delete",
            url="https://e.example/s?tag=a&x=1&tag=b",
            key="tag",
        )
        self.assertEqual(
            result,
            {
                "mode": "query",
                "operation": "delete",
                "url": "https://e.example/s?x=1",
                "key": "tag",
                "params": [["x", "1"]],
                "removed": 2,
            },
        )

    def test_query_delete_missing_key_is_noop(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="delete",
            url="https://e.example/s?x=1",
            key="tag",
        )
        self.assertEqual(result["url"], "https://e.example/s?x=1")
        self.assertEqual(result["removed"], 0)

    def test_query_delete_last_param_drops_question_mark(self) -> None:
        result = self.tool.execute(
            mode="query",
            operation="delete",
            url="https://e.example/s?a=1#f",
            key="a",
        )
        self.assertEqual(result["url"], "https://e.example/s#f")

    def test_query_percent_encoding_round_trips(self) -> None:
        url = "https://e.example/s?q=a%2Bb%20c&n=1"
        parsed = self.tool.execute(mode="parse", url=url)
        result = self.tool.execute(
            mode="query", operation="set", url=url, key="n", value="2"
        )
        # The rebuilt query re-encodes with conventional separators, but
        # must decode back to the very same parameter pairs.
        reparsed = self.tool.execute(mode="parse", url=result["url"])
        self.assertEqual(reparsed["params"][0], parsed["params"][0])
        self.assertEqual(reparsed["params"][1], ["n", "2"])
        self.assertEqual(result["url"], "https://e.example/s?q=a%2Bb+c&n=2")

    def test_query_byte_stable_for_conventional_encoding(self) -> None:
        url = "https://e.example/s?q=hello+world&l=zh-CN&x=1"
        result = self.tool.execute(
            mode="query", operation="delete", url=url, key="x"
        )
        self.assertEqual(result["url"], "https://e.example/s?q=hello+world&l=zh-CN")

    def test_query_works_on_scheme_less_references(self) -> None:
        result = self.tool.execute(
            mode="query", operation="get", url="?a=1&b", key="b"
        )
        self.assertEqual(result["values"], [""])

    # ------------------------------------------------------------------ #
    # build mode
    # ------------------------------------------------------------------ #

    def test_build_basic_parts(self) -> None:
        result = self.tool.execute(
            mode="build",
            scheme="https",
            host="example.com",
            path="/a/b",
            query="x=1",
            fragment="frag",
        )
        self.assertEqual(result["url"], "https://example.com/a/b?x=1#frag")
        self.assertEqual(result["netloc"], "example.com")
        self.assertEqual(result["query"], "x=1")

    def test_build_with_port_and_no_path(self) -> None:
        result = self.tool.execute(
            mode="build", scheme="http", host="h.example", port=8080
        )
        self.assertEqual(result["url"], "http://h.example:8080")

    def test_build_ipv6_host_is_kept_bracketed(self) -> None:
        result = self.tool.execute(
            mode="build",
            scheme="http",
            host="[2001:db8::1]",
            port=80,
            path="/x",
        )
        self.assertEqual(result["url"], "http://[2001:db8::1]:80/x")

    def test_build_userinfo_is_percent_encoded(self) -> None:
        result = self.tool.execute(
            mode="build",
            scheme="https",
            host="e.example",
            username="user@example.com",
            password="p@ss:word",
            path="/x",
        )
        self.assertEqual(
            result["url"],
            "https://user%40example.com:p%40ss%3Aword@e.example/x",
        )

    def test_build_query_from_pairs_and_dict(self) -> None:
        result = self.tool.execute(
            mode="build",
            scheme="https",
            host="e.example",
            query=[["a", "1"], ["a", "2"]],
        )
        self.assertEqual(result["url"], "https://e.example?a=1&a=2")
        result = self.tool.execute(
            mode="build",
            scheme="https",
            host="e.example",
            query={"a": ["1", "2"], "b": "3"},
        )
        self.assertEqual(result["url"], "https://e.example?a=1&a=2&b=3")

    def test_build_from_raw_netloc(self) -> None:
        result = self.tool.execute(
            mode="build",
            scheme="http",
            netloc="user@h.example:8080",
            path="/p",
        )
        self.assertEqual(result["url"], "http://user@h.example:8080/p")

    def test_build_scheme_less_when_explicitly_allowed(self) -> None:
        result = self.tool.execute(
            mode="build",
            allow_scheme_relative=True,
            host="e.example",
            path="/x",
            query="a=1",
        )
        self.assertEqual(result["url"], "//e.example/x?a=1")
        result = self.tool.execute(
            mode="build",
            allow_scheme_relative=True,
            path="/x",
            query="a=1",
        )
        self.assertEqual(result["url"], "/x?a=1")

    def test_build_parse_round_trip(self) -> None:
        url = "https://example.com:8443/docs/a?b=2&a=1#frag"
        parsed = self.tool.execute(mode="parse", url=url)
        rebuilt = self.tool.execute(
            mode="build",
            scheme=parsed["scheme"],
            netloc=parsed["netloc"],
            path=parsed["path"],
            query=parsed["query"],
            fragment=parsed["fragment"],
        )
        self.assertEqual(rebuilt["url"], url)
        reparsed = self.tool.execute(mode="parse", url=rebuilt["url"])
        self.assertEqual(reparsed["params"], parsed["params"])
        self.assertEqual(reparsed["port"], parsed["port"])

    def test_build_ipv6_round_trip(self) -> None:
        url = "http://[2001:db8::1]:8080/x?y=1"
        parsed = self.tool.execute(mode="parse", url=url)
        rebuilt = self.tool.execute(
            mode="build",
            scheme=parsed["scheme"],
            host="[" + parsed["hostname"] + "]",
            port=parsed["explicit_port"],
            path=parsed["path"],
            query=parsed["query"],
        )
        self.assertEqual(rebuilt["url"], url)

    # ------------------------------------------------------------------ #
    # normalize mode — known transformations
    # ------------------------------------------------------------------ #

    def test_normalize_full_transformation(self) -> None:
        result = self.tool.execute(
            mode="normalize", url="HTTP://Example.COM.:80/a?b=2&a=1#"
        )
        self.assertEqual(result["url"], "http://example.com/a?a=1&b=2")
        self.assertEqual(
            result["changed"],
            [
                "lowercased_scheme",
                "lowercased_host",
                "resolved_trailing_dot_host",
                "removed_default_port",
                "sorted_query_keys",
                "removed_empty_fragment",
            ],
        )
        self.assertEqual(result["changed_count"], 6)

    def test_normalize_keeps_non_default_port_and_path(self) -> None:
        result = self.tool.execute(
            mode="normalize", url="http://Example.com:8080/A/B"
        )
        self.assertEqual(result["url"], "http://example.com:8080/A/B")
        self.assertEqual(result["changed"], ["lowercased_host"])

    def test_normalize_https_and_ws_default_ports(self) -> None:
        for url, expected in (
            ("https://e.example:443/x", "https://e.example/x"),
            ("ws://e.example:80/x", "ws://e.example/x"),
            ("wss://e.example:443/x", "wss://e.example/x"),
            ("ftp://e.example:21/x", "ftp://e.example/x"),
        ):
            result = self.tool.execute(mode="normalize", url=url)
            self.assertEqual(result["url"], expected, url)
            self.assertIn("removed_default_port", result["changed"], url)

    def test_normalize_ipv6_and_multiple_trailing_dots(self) -> None:
        result = self.tool.execute(
            mode="normalize", url="HTTP://[2001:DB8::1]:80/path"
        )
        self.assertEqual(result["url"], "http://[2001:db8::1]/path")
        self.assertEqual(
            result["changed"],
            ["lowercased_scheme", "lowercased_host", "removed_default_port"],
        )
        result = self.tool.execute(mode="normalize", url="http://h.example..:80/x")
        self.assertEqual(result["url"], "http://h.example/x")
        self.assertIn("resolved_trailing_dot_host", result["changed"])

    def test_normalize_userinfo_stays_byte_identical(self) -> None:
        result = self.tool.execute(
            mode="normalize", url="HTTP://User:P%40ss@Example.COM:80/"
        )
        self.assertEqual(result["url"], "http://User:P%40ss@example.com/")
        self.assertEqual(
            result["changed"],
            ["lowercased_scheme", "lowercased_host", "removed_default_port"],
        )

    def test_normalize_sorts_query_keys_stably(self) -> None:
        result = self.tool.execute(
            mode="normalize", url="http://e.example/p?b=1&a=x&a=y"
        )
        self.assertEqual(result["url"], "http://e.example/p?a=x&a=y&b=1")

    def test_normalize_preserves_query_bytes_when_already_sorted(self) -> None:
        result = self.tool.execute(mode="normalize", url="http://e.example/p?a=%2F&b=2")
        self.assertEqual(result["url"], "http://e.example/p?a=%2F&b=2")
        self.assertEqual(result["changed"], [])

    def test_normalize_drops_empty_markers(self) -> None:
        result = self.tool.execute(mode="normalize", url="http://e.example/p?#")
        self.assertEqual(result["url"], "http://e.example/p")
        self.assertEqual(
            result["changed"], ["removed_empty_query", "removed_empty_fragment"]
        )
        result = self.tool.execute(mode="normalize", url="http://e.example:/p")
        self.assertEqual(result["url"], "http://e.example/p")
        self.assertIn("removed_empty_port", result["changed"])

    def test_normalize_is_idempotent(self) -> None:
        urls = [
            "HTTP://Example.COM.:80/a?b=2&a=1&b=0#",
            "https://e.example:443/x?q=a+b%20c&z=1",
            "HTTP://[2001:DB8::1]:80/path?b=1&a=2&a=1",
            "http://e.example/p?#",
            "http://e.example:/p?",
            "ftp://h.example..:21/x?a=%2F",
            "//relative.example/p?b=2&a=1",
            "urn:isbn:0451450523",
        ]
        for url in urls:
            first = self.tool.execute(mode="normalize", url=url)
            second = self.tool.execute(mode="normalize", url=first["url"])
            self.assertEqual(second["url"], first["url"], url)
            self.assertEqual(second["changed"], [], url)
            self.assertEqual(second["changed_count"], 0, url)

    def test_normalize_already_canonical_url_is_unchanged(self) -> None:
        url = "https://example.com/docs/a?a=1&b=2#frag"
        result = self.tool.execute(mode="normalize", url=url)
        self.assertEqual(result["url"], url)
        self.assertEqual(result["changed"], [])
        self.assertEqual(result["changed_count"], 0)

    def test_normalize_works_on_scheme_less_references(self) -> None:
        result = self.tool.execute(mode="normalize", url="//H.example/p?b=2&a=1")
        self.assertEqual(result["url"], "//h.example/p?a=1&b=2")
        self.assertIn("lowercased_host", result["changed"])

    # ------------------------------------------------------------------ #
    # Error matrix — content-level structured payloads
    # ------------------------------------------------------------------ #

    def test_parse_missing_scheme_structured_error(self) -> None:
        result = self.tool.execute(mode="parse", url="example.com/path")
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["error"]["type"], "missing_scheme")
        self.assertIn("allow_scheme_relative", result["error"]["message"])

    def test_parse_scheme_relative_allowed(self) -> None:
        result = self.tool.execute(
            mode="parse", url="//example.com/path", allow_scheme_relative=True
        )
        self.assertEqual(result["scheme"], "")
        self.assertEqual(result["netloc"], "example.com")
        self.assertEqual(result["path"], "/path")

    def test_parse_malformed_url_whitespace(self) -> None:
        result = self.tool.execute(mode="parse", url="http://exa mple.com/")
        self.assertEqual(result["error"]["type"], "malformed_url")

    def test_parse_malformed_url_control_character(self) -> None:
        result = self.tool.execute(mode="parse", url="http://a/\tx")
        self.assertEqual(result["error"]["type"], "malformed_url")

    def test_parse_malformed_url_unmatched_bracket(self) -> None:
        result = self.tool.execute(mode="parse", url="http://[2001:db8::1/p")
        self.assertEqual(result["error"]["type"], "malformed_url")
        self.assertIn("IPv6", result["error"]["message"])

    def test_parse_invalid_port_non_integer(self) -> None:
        result = self.tool.execute(mode="parse", url="http://example.com:abc/")
        self.assertEqual(result["error"]["type"], "invalid_port")

    def test_parse_invalid_port_out_of_range(self) -> None:
        result = self.tool.execute(mode="parse", url="http://example.com:99999/")
        self.assertEqual(result["error"]["type"], "invalid_port")

    def test_query_bad_url_returns_structured_error(self) -> None:
        result = self.tool.execute(
            mode="query", operation="get", url="http://a:zz/", key="a"
        )
        self.assertEqual(result["error"]["type"], "invalid_port")
        self.assertEqual(result["operation"], "get")

    def test_normalize_bad_url_returns_structured_error(self) -> None:
        result = self.tool.execute(mode="normalize", url="http://a:99999/")
        self.assertEqual(result["mode"], "normalize")
        self.assertEqual(result["error"]["type"], "invalid_port")

    def test_build_error_matrix(self) -> None:
        cases = [
            ({"host": "e.example"}, "missing_scheme"),
            (
                {"scheme": "1http", "host": "e.example"},
                "invalid_scheme",
            ),
            (
                {"scheme": "http", "host": "2001:db8::1"},
                "invalid_host",
            ),
            (
                {"scheme": "http", "host": "e.example", "port": 0},
                "invalid_port",
            ),
            (
                {"scheme": "http", "host": "e.example", "port": 70000},
                "invalid_port",
            ),
            (
                {"scheme": "http", "host": "e.example", "path": "abc"},
                "invalid_path",
            ),
            (
                {
                    "scheme": "http",
                    "allow_scheme_relative": True,
                    "path": "//x",
                },
                "invalid_path",
            ),
            (
                {"scheme": "http", "host": "e.example", "query": "?x=1"},
                "invalid_query",
            ),
            (
                {"scheme": "http", "host": "e.example", "query": "a=1#f"},
                "invalid_query",
            ),
            (
                {"scheme": "http", "host": "e.example", "fragment": "#f"},
                "invalid_fragment",
            ),
            (
                {"scheme": "http", "host": "e.example", "fragment": "a#b"},
                "invalid_fragment",
            ),
            (
                {"scheme": "http", "netloc": "h.example/a"},
                "invalid_netloc",
            ),
        ]
        for kwargs, error_type in cases:
            result = self.tool.execute(mode="build", **kwargs)
            self.assertEqual(result.get("error", {}).get("type"), error_type, kwargs)
            self.assertEqual(result["mode"], "build")

    def test_build_unclosed_ipv6_bracket_is_invalid_host(self) -> None:
        result = self.tool.execute(
            mode="build", scheme="http", host="[2001:db8::1"
        )
        self.assertEqual(result["error"]["type"], "invalid_host")

    # ------------------------------------------------------------------ #
    # Error matrix — parameter-level ValueError
    # ------------------------------------------------------------------ #

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="bogus", url="http://a/")

    def test_invalid_operation_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="query", operation="push", url="http://a/")

    def test_missing_url_raises(self) -> None:
        for mode in ("parse", "query", "normalize"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode)
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, url="")
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, url=123)

    def test_missing_key_for_query_set_and_delete_raises(self) -> None:
        for operation in ("set", "delete"):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="query", operation=operation, url="http://a/?x=1"
                )
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="query",
                    operation=operation,
                    url="http://a/?x=1",
                    key="",
                )

    def test_invalid_set_value_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="query",
                operation="set",
                url="http://a/?x=1",
                key="x",
                value=42,
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="query",
                operation="set",
                url="http://a/?x=1",
                key="x",
                value=[],
            )

    def test_invalid_allow_scheme_relative_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="parse", url="http://a/", allow_scheme_relative="yes"
            )

    def test_invalid_build_parameter_types_raise(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="build", scheme="http", host="a", port="80")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="build", scheme="http", host="a", port=True)
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="build", scheme="http", host="a", netloc="b", port=1
            )
        with self.assertRaises(ValueError):
            self.tool.execute(mode="build", scheme="http", host="a", query=123)
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="build", scheme="http", host="a", query=[["a", 1]]
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="build", scheme="http", host="a", query={"a": 1}
            )
        with self.assertRaises(ValueError):
            self.tool.execute(mode="build", scheme="http", username="u")
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="build", scheme="http", host="a", password="p"
            )

    def test_oversized_url_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="parse", url="http://a/" + "x" * 100_001)


if __name__ == "__main__":
    unittest.main()
