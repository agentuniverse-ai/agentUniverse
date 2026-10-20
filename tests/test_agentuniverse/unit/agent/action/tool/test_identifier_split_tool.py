#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_identifier_split_tool.py

"""Offline unit tests for IdentifierSplitTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: ``split`` words and styles are pinned against literal
ground truths spelling out the documented ruleset (acronym handling,
digit-run attachment, leading/trailing separator preservation, single
letters, all-caps words, mixed inputs), ``rejoin`` outputs are pinned
per style, the case-insensitive round-trip identity
``lower(split(rejoin(words, style))) == lower(words)`` is verified per
style over a corpus of canonical identifiers, the keyword flag list,
``is_identifier`` verdicts and the full error matrices are pinned as
well.
"""

import os
import sys
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import IdentifierSplitTool
from agentuniverse.agent.action.tool.common_tool.identifier_split_tool import (
    IdentifierSplitTool as DirectIdentifierSplitTool,
)

# --------------------------------------------------------------------- #
# Ground-truth corpora
# --------------------------------------------------------------------- #

# (identifier, words, style_detected) — every vector of the documented
# ruleset: camel humps, acronyms, digit-run attachment, separators,
# leading/trailing preservation, single letters, all-caps, mixed.
SPLIT_GROUND_TRUTHS = [
    # Acronyms kept whole before a capitalized word.
    ("HTTPServer", ["HTTP", "Server"], "pascal"),
    ("XMLHttpRequest", ["XML", "Http", "Request"], "pascal"),
    ("getHTTPResponseCode", ["get", "HTTP", "Response", "Code"], "camel"),
    ("NASAServer", ["NASA", "Server"], "pascal"),
    ("parseJSONPayload", ["parse", "JSON", "Payload"], "camel"),
    # A single uppercase letter capitalizes the following word.
    ("MyServer", ["My", "Server"], "pascal"),
    ("getWord", ["get", "Word"], "camel"),
    # Digit runs attach to the preceding letter run (lower or upper)...
    ("base64", ["base64"], "camel"),
    ("utf8", ["utf8"], "camel"),
    ("MD5", ["MD5"], "screaming_snake"),
    ("SHA256", ["SHA256"], "screaming_snake"),
    # ...but always start a new word before a following uppercase.
    ("utf8Decode", ["utf8", "Decode"], "camel"),
    ("SHA256Hash", ["SHA256", "Hash"], "pascal"),
    ("HTTP2Server", ["HTTP2", "Server"], "pascal"),
    ("base64Url", ["base64", "Url"], "camel"),
    ("get2FA", ["get2", "FA"], "camel"),
    # Lowercase continues through digits.
    ("md5sum", ["md5sum"], "camel"),
    ("base64url", ["base64url"], "camel"),
    # Separator styles.
    ("get_http_response_code", ["get", "http", "response", "code"], "snake"),
    ("MAX_RETRIES", ["MAX", "RETRIES"], "screaming_snake"),
    ("ERROR_CODE_2", ["ERROR", "CODE", "2"], "screaming_snake"),
    ("content_type2", ["content", "type2"], "snake"),
    ("content-type", ["content", "type"], "kebab"),
    ("x-content-type-options", ["x", "content", "type", "options"], "kebab"),
    # Leading / trailing separator runs are preserved on the word.
    ("_private_value", ["_private", "value"], "snake"),
    ("__init__", ["__init__"], "snake"),
    ("__MAX_SIZE", ["__MAX", "SIZE"], "screaming_snake"),
    ("value_", ["value_"], "snake"),
    ("_private", ["_private"], "snake"),
    # Single letters and short uppercase runs.
    ("a", ["a"], "camel"),
    ("A", ["A"], "pascal"),
    ("X1", ["X1"], "pascal"),
    ("aB", ["a", "B"], "camel"),
    ("IO", ["IO"], "screaming_snake"),
    ("iOS", ["i", "OS"], "camel"),
    ("ABc", ["A", "Bc"], "pascal"),
    ("ABtest", ["A", "Btest"], "pascal"),
    # All-caps words stay whole.
    ("NASA", ["NASA"], "screaming_snake"),
    ("renderNASA", ["render", "NASA"], "camel"),
    ("NASA_URL", ["NASA", "URL"], "screaming_snake"),
    # Flat and digit-leading tokens.
    ("foobar", ["foobar"], "camel"),
    ("42", ["42"], "camel"),
    ("64bit", ["64bit"], "camel"),
    ("utf8Decode2", ["utf8", "Decode2"], "camel"),
    # Doubled interior separators are plain separators.
    ("foo__bar", ["foo", "bar"], "snake"),
    # Mixed inputs are flagged mixed.
    ("get_HTTP_response", ["get", "HTTP", "response"], "mixed"),
    ("Foo_bar", ["Foo", "bar"], "mixed"),
    ("snake_Case_mix", ["snake", "Case", "mix"], "mixed"),
    ("foo-barBaz", ["foo", "bar", "Baz"], "mixed"),
    ("Foo-Bar", ["Foo", "Bar"], "mixed"),
    ("CONTENT-TYPE", ["CONTENT", "TYPE"], "mixed"),
    ("foo_bar-baz", ["foo", "bar", "baz"], "mixed"),
    ("fooBar_baz", ["foo", "Bar", "baz"], "mixed"),
]

# Canonical identifiers for the round-trip identity: single interior
# separators only and no pure-digit words (a lone digit word such as
# the "2" of ERROR_CODE_2 is kept apart by separators but re-merges
# into the preceding hump under separator-less styles), and no uncased
# digit-embedded tokens (uppercasing styles inject a new digit->Upper
# hump into "md5sum" -> "MD5SUM" -> MD5|SUM) — both boundaries are
# genuinely not representable across every style.
ROUND_TRIP_CORPUS = [
    "getHTTPResponseCode",
    "HTTPServer",
    "XMLHttpRequest",
    "utf8Decode",
    "base64Url",
    "SHA256Hash",
    "get_http_response_code",
    "MAX_RETRIES",
    "content_type2",
    "content-type",
    "_private_value",
    "value_",
    "parseJSONPayload",
    "renderNASA",
    "NASAServer",
    "iOS",
    "ABc",
    "a",
]

# All 35 hard Python keywords, pinned: every one must be flagged.
ALL_KEYWORDS = [
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else",
    "except", "finally", "for", "from", "global", "if", "import", "in",
    "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
    "return", "try", "while", "with", "yield",
]

# Not keywords (case-sensitive check; soft keywords excluded).
NOT_KEYWORDS = ["Class", "false", "matches", "cases", "types", "my_var", "x"]


class IdentifierSplitToolTest(unittest.TestCase):
    """Offline deterministic test cases for IdentifierSplitTool."""

    def setUp(self) -> None:
        self.tool = IdentifierSplitTool()

    # ------------------------------------------------------------------ #
    # Registration and metadata
    # ------------------------------------------------------------------ #

    def test_package_export_and_defaults(self) -> None:
        self.assertIs(DirectIdentifierSplitTool, IdentifierSplitTool)
        self.assertEqual(self.tool.name, "identifier_split_tool")
        self.assertEqual(
            DirectIdentifierSplitTool.MODES,
            ("split", "rejoin", "is_identifier", "batch_split"),
        )
        self.assertEqual(
            sorted(DirectIdentifierSplitTool.REJOIN_STYLES),
            ["camel", "constant", "kebab", "pascal", "screaming", "snake"],
        )
        self.assertIn("acronyms preserved", self.tool.description)

    def test_yaml_config_matches_module(self) -> None:
        module = sys.modules[DirectIdentifierSplitTool.__module__]
        path = os.path.join(
            os.path.dirname(module.__file__), "identifier_split_tool.yaml"
        )
        with open(path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "identifier_split_tool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool."
            "identifier_split_tool",
        )
        self.assertEqual(config["metadata"]["class"], "IdentifierSplitTool")
        self.assertEqual(config["input_keys"], ["mode"])
        schema = config["args_model_schema"]["properties"]["mode"]
        self.assertEqual(
            sorted(schema["enum"]),
            sorted(DirectIdentifierSplitTool.MODES),
        )
        style_schema = config["args_model_schema"]["properties"]["style"]
        self.assertEqual(
            sorted(style_schema["enum"]),
            sorted(DirectIdentifierSplitTool.REJOIN_STYLES),
        )
        self.assertEqual(
            config["args_model_schema"]["required"], ["mode"]
        )

    def test_deterministic_repeatability(self) -> None:
        first = self.tool.execute(mode="split", identifier="getHTTPResponseCode")
        for _ in range(3):
            self.assertEqual(
                self.tool.execute(mode="split", identifier="getHTTPResponseCode"),
                first,
            )

    # ------------------------------------------------------------------ #
    # split mode — documented ruleset ground truths
    # ------------------------------------------------------------------ #

    def test_split_ground_truths(self) -> None:
        for identifier, words, style in SPLIT_GROUND_TRUTHS:
            with self.subTest(identifier=identifier):
                result = self.tool.execute(mode="split", identifier=identifier)
                self.assertEqual(
                    result,
                    {
                        "mode": "split",
                        "identifier": identifier,
                        "words": words,
                        "word_count": len(words),
                        "style_detected": style,
                    },
                )

    def test_split_joining_words_reproduces_identifier(self) -> None:
        # Words (minus preserved separator attachments) never lose
        # information: stripping separators and case, then removing the
        # run splits, reconstitutes the exact character multiset order.
        for identifier, words, _style in SPLIT_GROUND_TRUTHS:
            with self.subTest(identifier=identifier):
                joined = "".join(
                    word.strip("_-") for word in words
                )
                expected = identifier.replace("_", "").replace("-", "")
                self.assertEqual(joined.lower(), expected.lower())

    # ------------------------------------------------------------------ #
    # rejoin mode — per-style ground truths
    # ------------------------------------------------------------------ #

    def test_rejoin_ground_truths_per_style(self) -> None:
        words = ["HTTP", "Server"]
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=words, style="snake"),
            {"mode": "rejoin", "style": "snake", "result": "http_server"},
        )
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=words, style="kebab"),
            {"mode": "rejoin", "style": "kebab", "result": "http-server"},
        )
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=words, style="camel"),
            {"mode": "rejoin", "style": "camel", "result": "httpServer"},
        )
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=words, style="pascal"),
            {"mode": "rejoin", "style": "pascal", "result": "HttpServer"},
        )
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=words, style="constant"),
            {"mode": "rejoin", "style": "constant", "result": "HTTP_SERVER"},
        )
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=words, style="screaming"),
            {"mode": "rejoin", "style": "screaming", "result": "HTTP_SERVER"},
        )

    def test_rejoin_acronym_words(self) -> None:
        result = self.tool.execute(
            mode="rejoin", words=["XML", "Http", "Request"], style="camel"
        )
        self.assertEqual(result["result"], "xmlHttpRequest")
        result = self.tool.execute(
            mode="rejoin", words=["get", "HTTP", "Response", "Code"], style="pascal"
        )
        self.assertEqual(result["result"], "GetHttpResponseCode")

    def test_rejoin_preserves_leading_and_trailing_separators(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="rejoin", words=["_private", "value"], style="snake"
            )["result"],
            "_private_value",
        )
        self.assertEqual(
            self.tool.execute(
                mode="rejoin", words=["_private", "value"], style="camel"
            )["result"],
            "_privateValue",
        )
        self.assertEqual(
            self.tool.execute(
                mode="rejoin", words=["value_"], style="snake"
            )["result"],
            "value_",
        )

    def test_rejoin_single_and_digit_words(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=["a"], style="snake")["result"],
            "a",
        )
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=["a"], style="pascal")["result"],
            "A",
        )
        self.assertEqual(
            self.tool.execute(mode="rejoin", words=["base64", "Url"], style="kebab")[
                "result"
            ],
            "base64-url",
        )

    # ------------------------------------------------------------------ #
    # Round-trip identity: split -> rejoin -> split per style
    # ------------------------------------------------------------------ #

    def test_round_trip_identity_per_style(self) -> None:
        for style in DirectIdentifierSplitTool.REJOIN_STYLES:
            for identifier in ROUND_TRIP_CORPUS:
                with self.subTest(style=style, identifier=identifier):
                    words = self.tool.execute(
                        mode="split", identifier=identifier
                    )["words"]
                    reassembled = self.tool.execute(
                        mode="rejoin", words=words, style=style
                    )["result"]
                    words_again = self.tool.execute(
                        mode="split", identifier=reassembled
                    )["words"]
                    self.assertEqual(
                        [word.lower() for word in words_again],
                        [word.lower() for word in words],
                    )

    def test_round_trip_exact_when_style_matches_detected_style(self) -> None:
        # Rejoining with the style the identifier already has
        # reproduces it exactly — for identifiers without acronyms,
        # since rejoin lowercases words into the join (the documented
        # CaseConverterTool-compatible behaviour).
        canonical = {
            "getWord": "camel",
            "MyServer": "pascal",
            "get_http_response_code": "snake",
            "MAX_RETRIES": "constant",
            "content-type": "kebab",
            "_private_value": "snake",
        }
        for identifier, style in canonical.items():
            with self.subTest(identifier=identifier):
                words = self.tool.execute(mode="split", identifier=identifier)[
                    "words"
                ]
                reassembled = self.tool.execute(
                    mode="rejoin", words=words, style=style
                )["result"]
                self.assertEqual(reassembled, identifier)

    # ------------------------------------------------------------------ #
    # is_identifier mode
    # ------------------------------------------------------------------ #

    def test_is_identifier_valid_non_keywords(self) -> None:
        for text in ["value", "_private", "get_http_response_code", "_", "x1"]:
            with self.subTest(text=text):
                result = self.tool.execute(mode="is_identifier", text=text)
                self.assertTrue(result["valid"])
                self.assertFalse(result["is_keyword"])
                self.assertIsNone(result["invalid_reason"])
        self.assertEqual(
            self.tool.execute(mode="is_identifier", text="get_http_response_code")[
                "style_detected"
            ],
            "snake",
        )

    def test_is_identifier_all_35_python_keywords(self) -> None:
        self.assertEqual(len(ALL_KEYWORDS), 35)
        for keyword in ALL_KEYWORDS:
            with self.subTest(keyword=keyword):
                result = self.tool.execute(mode="is_identifier", text=keyword)
                self.assertTrue(result["valid"])
                self.assertTrue(result["is_keyword"])
                self.assertIsNone(result["invalid_reason"])

    def test_is_identifier_not_keywords(self) -> None:
        for text in NOT_KEYWORDS:
            with self.subTest(text=text):
                result = self.tool.execute(mode="is_identifier", text=text)
                self.assertTrue(result["valid"])
                self.assertFalse(result["is_keyword"])
        # Keywords are case-sensitive.
        self.assertFalse(
            self.tool.execute(mode="is_identifier", text="False_")["is_keyword"]
        )

    def test_is_identifier_invalid_inputs(self) -> None:
        cases = {
            "": "empty string",
            "2fast": "starts with",
            "my-var": "'-'",
            "my var": "' '",
            "foo.bar": "'.'",
            "a$b": "'$'",
            "café": "position",
        }
        for text, fragment in cases.items():
            with self.subTest(text=text):
                result = self.tool.execute(mode="is_identifier", text=text)
                self.assertFalse(result["valid"])
                self.assertIn(fragment, result["invalid_reason"])
                self.assertFalse(result["is_keyword"])

    # ------------------------------------------------------------------ #
    # batch_split mode
    # ------------------------------------------------------------------ #

    def test_batch_split_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="batch_split",
            identifiers=["HTTPServer", "http_server_status"],
        )
        self.assertEqual(result["mode"], "batch_split")
        self.assertEqual(result["count"], 2)
        self.assertEqual(
            result["results"],
            [
                {
                    "identifier": "HTTPServer",
                    "words": ["HTTP", "Server"],
                    "word_count": 2,
                    "style_detected": "pascal",
                },
                {
                    "identifier": "http_server_status",
                    "words": ["http", "server", "status"],
                    "word_count": 3,
                    "style_detected": "snake",
                },
            ],
        )
        # Case-insensitive vocabulary: http/server counted across both.
        self.assertEqual(
            result["vocabulary"], {"http": 2, "server": 2, "status": 1}
        )
        self.assertEqual(result["vocabulary_size"], 3)

    def test_batch_split_vocabulary_first_appearance_order(self) -> None:
        result = self.tool.execute(
            mode="batch_split",
            identifiers=["zoo_keeper", "zoo", "alpha_one", "alpha", "zoo"],
        )
        self.assertEqual(
            list(result["vocabulary"]),
            ["zoo", "keeper", "alpha", "one"],
        )
        self.assertEqual(
            result["vocabulary"], {"zoo": 3, "keeper": 1, "alpha": 2, "one": 1}
        )

    def test_batch_split_empty_list(self) -> None:
        result = self.tool.execute(mode="batch_split", identifiers=[])
        self.assertEqual(
            result,
            {
                "mode": "batch_split",
                "count": 0,
                "results": [],
                "vocabulary": {},
                "vocabulary_size": 0,
            },
        )

    def test_batch_split_per_item_errors_do_not_abort(self) -> None:
        result = self.tool.execute(
            mode="batch_split",
            identifiers=["valid_name", "has space", "", "also_valid"],
        )
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["results"][0]["words"], ["valid", "name"])
        for broken in (1, 2):
            self.assertIn("error", result["results"][broken])
            self.assertEqual(
                result["results"][broken]["error"]["type"],
                "invalid_identifier",
            )
        self.assertEqual(result["results"][3]["words"], ["also", "valid"])
        self.assertEqual(result["vocabulary"], {"valid": 2, "name": 1, "also": 1})

    def test_batch_split_larger_symbol_list(self) -> None:
        result = self.tool.execute(
            mode="batch_split",
            identifiers=[
                "getHTTPResponseCode",
                "http_response_code",
                "HTTPResponseCode",
                "responseTimeMs",
            ],
        )
        self.assertEqual(result["count"], 4)
        expected = {
            "get": 1,
            "http": 3,
            "response": 4,
            "code": 3,
            "time": 1,
            "ms": 1,
        }
        self.assertEqual(result["vocabulary"], expected)
        self.assertEqual(result["vocabulary_size"], 6)

    # ------------------------------------------------------------------ #
    # Error matrix — parameter validation
    # ------------------------------------------------------------------ #

    def test_error_unknown_mode(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="analyze", identifier="foo")
        self.assertIn("mode must be one of", str(ctx.exception))
        for bad in (None, "", 1, True):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=bad, identifier="foo")

    def test_error_split_input_matrix(self) -> None:
        bad_inputs = [
            None,                       # missing
            42,                         # wrong type
            True,                       # bool is not a string
            ["foo"],                    # wrong type
            "",                         # empty
            "has space",                # charset
            "foo.bar",                  # charset
            "a+b",                      # charset
            "café",                     # non-ASCII
            "x" * 10_001,               # size cap
        ]
        for bad in bad_inputs:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode="split", identifier=bad)
                self.assertIn("identifier_split_tool:", str(ctx.exception))

    def test_error_rejoin_words_matrix(self) -> None:
        bad_words = [
            None,                       # missing
            "foo",                      # bare string, not a list
            True,                       # bool
            [],                         # empty list
            ["ok", 42],                 # non-string item
            ["ok", True],               # bool item
            ["ok", ""],                 # empty item
            ["ok", "has space"],        # charset item
            ["ok", "a.b"],              # charset item
            ["x"] * 10_001,             # item cap
            ["y" * 900] * 300,          # total-char cap (270k > 200k)
        ]
        for bad in bad_words:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode="rejoin", words=bad, style="snake")
                self.assertIn("identifier_split_tool:", str(ctx.exception))

    def test_error_rejoin_style_matrix(self) -> None:
        for bad in [None, 5, True, "title", "upper", "slug", "SCREAMING", "snake_case"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode="rejoin", words=["a"], style=bad)
                self.assertIn("style must be", str(ctx.exception))

    def test_error_is_identifier_input_matrix(self) -> None:
        # Any string is acceptable (verdicts, not exceptions); only the
        # type and the size cap raise.
        for bad in [None, 42, True, ["x"]]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="is_identifier", text=bad)
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="is_identifier", text="x" * 10_001)
        self.assertIn("exceeds the 10,000-character limit", str(ctx.exception))
        # The empty string is a valid *input* with a False verdict.
        self.assertFalse(
            self.tool.execute(mode="is_identifier", text="")["valid"]
        )

    def test_error_batch_identifiers_matrix(self) -> None:
        bad_lists = [
            None,                       # missing
            "foo",                      # bare string
            True,                       # bool
            ["ok", 42],                 # non-string item
            ["ok", True],               # bool item
            ["x"] * 10_001,             # item cap
            ["y" * 900] * 300,          # total-char cap
        ]
        for bad in bad_lists:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode="batch_split", identifiers=bad)
                self.assertIn("identifier_split_tool:", str(ctx.exception))
        # Charset violations inside the list are per-item errors, not
        # exceptions (covered in test_batch_split_per_item_errors_do_not_abort).

    def test_error_required_parameter_missing_per_mode(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="split")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="rejoin", style="snake")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="rejoin", words=["a"])
        with self.assertRaises(ValueError):
            self.tool.execute(mode="is_identifier")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="batch_split")


if __name__ == "__main__":
    unittest.main()
