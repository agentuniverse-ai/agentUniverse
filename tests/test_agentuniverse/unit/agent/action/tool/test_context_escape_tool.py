#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_context_escape_tool.py

"""Offline unit tests for ContextEscapeTool.

The tool is built purely on the standard library (json, re, string)
and never touches the network, so this suite runs fully offline. Every
assertion is deterministic: each context direction is checked against
literal ground-truth vectors (computed by hand from the relevant
specifications — GFM table cell rules, RFC 4180, POSIX single-quoting,
the HTML entity sets, JSON string literals and re.escape), and the
central property — ``unescape(escape(x)) == x`` — is swept over a
corpus of nasty inputs (quotes, newlines in every flavor, pipes,
backslash combos, escape markers themselves, CJK, emoji, control
characters) for all seven context pairs, plus per-context safety
invariants of the escaped form.
"""

import re
import string
import unittest

from agentuniverse.agent.action.tool.common_tool import ContextEscapeTool
from agentuniverse.agent.action.tool.common_tool.context_escape_tool import (
    ContextEscapeTool as DirectContextEscapeTool,
)

UNICODE_TEXT = "héllo 世界 🌍 & <stuff>"

# Every entry is non-empty (the tool rejects empty text) and exercises a
# different way to break an escaper: escape markers already present in
# the input, every newline flavor, backslash runs adjacent to pipes,
# quote idiom fragments, CSV edge shapes and multi-codepoint emoji.
NASTY_CORPUS = [
    "plain",
    "|",
    "||",
    "a|b|c",
    "\\",
    "\\\\",
    "\\|",
    "a\\|b",
    "\\\\|",
    "back\\slash |pipe",
    "\n",
    "\r",
    "\r\n",
    "a\r\nb\nc\rd",
    "\r\n\r\n",
    "<br>",
    "<cr>",
    "x<br>y<cr>z",
    "\\<br>",
    "<br/><BR>",
    "<bogus>",
    "'",
    '"',
    "it's a 'test'",
    "'\"'\"'",
    "''",
    "'''",
    '""',
    '""""',
    '","',
    'a,b"c\nd',
    ",",
    '"quoted, text"',
    '"unterminated',
    "&",
    "&amp;",
    "&lt;script&gt;",
    "&bogus;",
    "<>&\"'",
    "héllo 世界 🌍",
    "日本語＆記号「」『』〜",
    "emoji 👨‍👩‍👧‍👦 family",
    "e\u0301 combining",
    "zero​width﻿chars",
    "\t\v\f",
    "\x00\x01\x1f control",
    string.punctuation,
    "".join(chr(i) for i in range(32, 127)),
    "pipe | newline \n cr \r crlf \r\n quote \" ' backslash \\ marker <br> end",
    "word " * 1000,
]


class ContextEscapeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib ContextEscapeTool."""

    def setUp(self) -> None:
        self.tool = ContextEscapeTool()

    def escape(self, context: str, text: str, **kwargs: object) -> str:
        result = self.tool.execute(
            mode="escape", context=context, text=text, **kwargs
        )
        self.assertNotIn("error", result)
        return result["result"]

    def unescape(self, context: str, text: str) -> str:
        result = self.tool.execute(mode="unescape", context=context, text=text)
        self.assertNotIn("error", result)
        return result["result"]

    def round_trip(self, context: str, text: str) -> None:
        self.assertEqual(self.unescape(context, self.escape(context, text)), text)

    # ------------------------------------------------------------------ #
    # markdown_table context
    # ------------------------------------------------------------------ #

    def test_markdown_table_escape_ground_truths(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="escape", context="markdown_table", text="a|b"
            ),
            {"mode": "escape", "context": "markdown_table", "result": "a\\|b"},
        )
        cases = [
            ("a|b", "a\\|b"),
            ("a\nb", "a<br>b"),
            ("a\rb", "a<cr>b"),
            ("a\r\nb", "a<cr><br>b"),
            ("x<br>y", "x\\<br>y"),
            ("x<cr>y", "x\\<cr>y"),
            ("back\\slash", "back\\\\slash"),
            ("no specials", "no specials"),
            (
                "all | of \n it \r\n and \\ | <br>",
                "all \\| of <br> it <cr><br> and \\\\ \\| \\<br>",
            ),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.escape("markdown_table", text), expected)

    def test_markdown_table_unescape_ground_truths(self) -> None:
        cases = [
            ("a\\|b", "a|b"),
            ("a<br>b", "a\nb"),
            ("a<cr>b", "a\rb"),
            ("a<cr><br>b", "a\r\nb"),
            ("x\\<br>y", "x<br>y"),
            ("x\\<cr>y", "x<cr>y"),
            ("a\\\\b", "a\\b"),
            ("\\\\\\|", "\\|"),
            ("plain cell", "plain cell"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.unescape("markdown_table", text), expected)

    def test_markdown_table_escape_removes_cell_breakers(self) -> None:
        escaped = self.escape(
            "markdown_table", "a|b\nc\r\nd\\|e<br>f"
        )
        # Raw newlines are gone entirely; every pipe that remains sits
        # behind a backslash escape, so stripping each "\<char>" pair
        # must leave no pipe at all.
        stripped = re.sub(r"\\.", "", escaped)
        self.assertNotIn("|", stripped)
        self.assertNotIn("\n", escaped)
        self.assertNotIn("\r", escaped)

    def test_markdown_table_unescape_invalid_escape_payload(self) -> None:
        for bad in ("bad\\z", "ends\\", "\\<x>", "\\a"):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="unescape", context="markdown_table", text=bad
                )
                self.assertEqual(result["mode"], "unescape")
                self.assertEqual(result["context"], "markdown_table")
                self.assertEqual(result["error"]["type"], "invalid_escape_sequence")
                self.assertIn("escape", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # csv context (RFC 4180)
    # ------------------------------------------------------------------ #

    def test_csv_escape_quoting_matrix(self) -> None:
        cases = [
            ("plain", "plain"),
            (" spaced ", " spaced "),
            ("semi;colon", "semi;colon"),
            ("a,b", '"a,b"'),
            ('he said "hi"', '"he said ""hi"""'),
            ("line1\nline2", '"line1\nline2"'),
            ("a\r\nb", '"a\r\nb"'),
            ('"', '""""'),
            ("a,b\"c\nd", '"a,b""c\nd"'),
            ('"quoted, text"', '"""quoted, text"""'),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.escape("csv", text), expected)

    def test_csv_escape_result_shape(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="escape", context="csv", text="a,b"),
            {"mode": "escape", "context": "csv", "result": '"a,b"'},
        )

    def test_csv_unescape_ground_truths(self) -> None:
        cases = [
            ("plain", "plain"),
            ('"a,b"', "a,b"),
            ('"say ""hi"""', 'say "hi"'),
            ('""""', '"'),
            ('"line1\nline2"', "line1\nline2"),
            ('"trailing space "', "trailing space "),
            ('""', ""),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.unescape("csv", text), expected)

    def test_csv_unescape_invalid_field_payload(self) -> None:
        # Unterminated, misplaced quotes and quotes in unquoted fields.
        for bad in ('"unterminated', '"', '"a"b', 'a"b', '"a""b'):
            with self.subTest(bad=bad):
                result = self.tool.execute(mode="unescape", context="csv", text=bad)
                self.assertEqual(result["context"], "csv")
                self.assertEqual(result["error"]["type"], "invalid_csv_field")
                self.assertIn("quote", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # shell_single context (POSIX)
    # ------------------------------------------------------------------ #

    def test_shell_single_escape_ground_truths(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="escape", context="shell_single", text="plain arg"
            ),
            {"mode": "escape", "context": "shell_single", "result": "'plain arg'"},
        )
        cases = [
            ("plain arg", "'plain arg'"),
            ("it's a 'test'", "'it'\"'\"'s a '\"'\"'test'\"'\"''"),
            ("'", "''\"'\"''"),
            ("''", "''\"'\"''\"'\"''"),
            ('double " quotes', "'double \" quotes'"),
            ("$(rm -rf /)", "'$(rm -rf /)'"),
            ("$HOME `cmd` \\n", "'$HOME `cmd` \\n'"),
            ("héllo 🌍", "'héllo 🌍'"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.escape("shell_single", text), expected)

    def test_shell_single_unescape_ground_truths(self) -> None:
        cases = [
            ("'plain arg'", "plain arg"),
            ("''\"'\"''", "'"),
            ("'it'\"'\"'s'", "it's"),
            ("''", ""),
            ("'$(dangerous)'", "$(dangerous)"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.unescape("shell_single", text), expected)

    def test_shell_single_escape_output_always_wrapped(self) -> None:
        for text in NASTY_CORPUS:
            escaped = self.escape("shell_single", text)
            self.assertTrue(escaped.startswith("'"))
            self.assertTrue(escaped.endswith("'"))

    def test_shell_single_unescape_invalid_quoting_payload(self) -> None:
        for bad in ("no quotes", "'unterminated", "'", "'''", "'a'x'", "a'b'"):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="unescape", context="shell_single", text=bad
                )
                self.assertEqual(result["context"], "shell_single")
                self.assertEqual(result["error"]["type"], "invalid_shell_quoting")
                self.assertIn("quote", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # html_attr / html_text contexts
    # ------------------------------------------------------------------ #

    def test_html_attr_escape_full_entity_set(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="escape", context="html_attr", text='&<>"\''
            ),
            {
                "mode": "escape",
                "context": "html_attr",
                "result": "&amp;&lt;&gt;&quot;&#x27;",
            },
        )
        cases = [
            ("a & b", "a &amp; b"),
            ("&lt;script&gt;", "&amp;lt;script&amp;gt;"),
            ('key="value"', "key=&quot;value&quot;"),
            ("it's", "it&#x27;s"),
            ("café 世界", "café 世界"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.escape("html_attr", text), expected)

    def test_html_attr_unescape_ground_truths(self) -> None:
        cases = [
            ("&amp;&lt;&gt;&quot;&#x27;", '&<>"\''),
            ("&amp;lt;", "&lt;"),
            ("Tom &amp; Jerry", "Tom & Jerry"),
            ("Tom & Jerry", "Tom & Jerry"),
            ("&bogus; &copy;", "&bogus; &copy;"),
            ("plain", "plain"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.unescape("html_attr", text), expected)

    def test_html_text_escapes_only_three_chars(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="escape", context="html_text", text="&<>"),
            {"mode": "escape", "context": "html_text", "result": "&amp;&lt;&gt;"},
        )
        self.assertEqual(
            self.escape("html_text", 'she said "hi"'),
            'she said "hi"',
        )
        self.assertEqual(
            self.escape("html_text", "5 < 6 && 7 > 3"),
            "5 &lt; 6 &amp;&amp; 7 &gt; 3",
        )

    def test_html_text_unescape_ground_truths(self) -> None:
        cases = [
            ("&lt;em&gt;", "<em>"),
            ("a &amp; b", "a & b"),
            # The attribute entities are outside the html_text set and
            # pass through verbatim.
            ("&quot;", "&quot;"),
            ("&#x27;", "&#x27;"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.unescape("html_text", text), expected)

    def test_html_escape_leaves_no_raw_specials(self) -> None:
        # After escaping, every remaining '&' introduces a known entity,
        # so stripping the entities must leave none of the raw specials.
        attr_entities = re.compile("&(amp;|lt;|gt;|quot;|#x27;)")
        text_entities = re.compile("&(amp;|lt;|gt;)")
        for text in NASTY_CORPUS:
            attr = self.escape("html_attr", text)
            for char in "&<>\"'":
                self.assertNotIn(char, attr_entities.sub("", attr))
            body = self.escape("html_text", text)
            for char in "&<>":
                self.assertNotIn(char, text_entities.sub("", body))

    # ------------------------------------------------------------------ #
    # json_string context
    # ------------------------------------------------------------------ #

    def test_json_string_escape_ascii_default(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="escape", context="json_string", text="hello"),
            {
                "mode": "escape",
                "context": "json_string",
                "ensure_ascii": True,
                "result": '"hello"',
            },
        )
        self.assertEqual(
            self.escape("json_string", "héllo"),
            '"h\\u00e9llo"',
        )
        self.assertEqual(
            self.escape("json_string", 'say "hi"\n\t'),
            '"say \\"hi\\"\\n\\t"',
        )

    def test_json_string_escape_ensure_ascii_false(self) -> None:
        result = self.tool.execute(
            mode="escape",
            context="json_string",
            text="héllo 世界",
            ensure_ascii=False,
        )
        self.assertEqual(result["ensure_ascii"], False)
        self.assertEqual(result["result"], '"héllo 世界"')
        self.assertEqual(
            self.escape("json_string", "héllo", ensure_ascii=True),
            '"h\\u00e9llo"',
        )

    def test_json_string_unescape_ground_truths(self) -> None:
        cases = [
            ('"hello"', "hello"),
            ('"h\\u00e9llo"', "héllo"),
            ('"héllo"', "héllo"),
            ('"say \\"hi\\""', 'say "hi"'),
            ('"line\\nbreak"', "line\nbreak"),
            ('""', ""),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.unescape("json_string", text), expected)

    def test_json_string_unescape_invalid_payload(self) -> None:
        for bad in ("not json", "'single'", '"unterminated', "[1,2]", "null", "123"):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="unescape", context="json_string", text=bad
                )
                self.assertEqual(result["context"], "json_string")
                self.assertEqual(result["error"]["type"], "invalid_json_string")
                self.assertIn("JSON", result["error"]["message"])

    def test_json_string_ensure_ascii_both_directions_round_trip(self) -> None:
        for ensure_ascii in (True, False):
            with self.subTest(ensure_ascii=ensure_ascii):
                for text in ("héllo 世界 🌍", 'quo"te\n', UNICODE_TEXT):
                    escaped = self.escape(
                        "json_string", text, ensure_ascii=ensure_ascii
                    )
                    if ensure_ascii:
                        self.assertTrue(escaped.isascii())
                    self.assertEqual(self.unescape("json_string", escaped), text)

    # ------------------------------------------------------------------ #
    # regex context
    # ------------------------------------------------------------------ #

    def test_regex_escape_ground_truths(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="escape", context="regex", text="a.b*c"),
            {"mode": "escape", "context": "regex", "result": "a\\.b\\*c"},
        )
        cases = [
            ("a.b*c", "a\\.b\\*c"),
            ("1+1=2", "1\\+1=2"),
            ("a(b)[c]{d}|e^f$g", "a\\(b\\)\\[c\\]\\{d\\}\\|e\\^f\\$g"),
            ("hello!", "hello!"),
            ("a b", "a\\ b"),
            ("plain-text_9", "plain\\-text_9"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.escape("regex", text), expected)

    def test_regex_escape_matches_stdlib(self) -> None:
        for text in NASTY_CORPUS:
            with self.subTest(text=text[:32]):
                self.assertEqual(self.escape("regex", text), re.escape(text))

    def test_regex_unescape_ground_truths(self) -> None:
        cases = [
            ("a\\.b", "a.b"),
            ("1\\+1=2", "1+1=2"),
            ("a\\ b", "a b"),
            ("\\\\", "\\"),
            ("back\\\\slash", "back\\slash"),
            ("plain", "plain"),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(self.unescape("regex", text), expected)

    def test_regex_punctuation_sweep(self) -> None:
        for char in string.punctuation:
            with self.subTest(char=char):
                triple = char * 3
                escaped = self.escape("regex", triple)
                self.assertEqual(escaped, re.escape(triple))
                self.assertEqual(self.unescape("regex", escaped), triple)

    def test_regex_escape_produces_literal_that_matches_original(self) -> None:
        for text in NASTY_CORPUS:
            with self.subTest(text=text[:32]):
                escaped = self.escape("regex", text)
                self.assertIsNotNone(re.fullmatch(escaped, text))

    def test_regex_unescape_invalid_escape_payload(self) -> None:
        for bad in ("\\d+", "\\w", "abc\\", "\\1", "\\é"):
            with self.subTest(bad=bad):
                result = self.tool.execute(mode="unescape", context="regex", text=bad)
                self.assertEqual(result["context"], "regex")
                self.assertEqual(result["error"]["type"], "invalid_regex_escape")
                self.assertIn("backslash", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Round-trip property sweep over the nasty corpus
    # ------------------------------------------------------------------ #

    def test_round_trip_sweep_all_contexts(self) -> None:
        contexts = (
            "markdown_table",
            "csv",
            "shell_single",
            "html_attr",
            "html_text",
            "json_string",
            "regex",
        )
        for context in contexts:
            for text in NASTY_CORPUS:
                with self.subTest(context=context, text=text[:40]):
                    self.round_trip(context, text)

    def test_round_trip_is_exact_identity_not_normalization(self) -> None:
        # Newline flavors must survive verbatim instead of collapsing.
        self.round_trip("markdown_table", "crlf\r\nlf\nlone\rcr")
        self.round_trip("csv", "a\r\nb\rc\nd")
        self.round_trip("json_string", "\r\n")
        self.round_trip("regex", "\r\n")
        # Escape markers already present in the input must survive.
        self.round_trip("markdown_table", "\\<br>\\|<cr>")
        self.round_trip("shell_single", "'\"'\"'")
        self.round_trip("html_attr", "&amp;&lt;")
        self.round_trip("regex", "\\\\d")

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_deterministic_output(self) -> None:
        for context in ("markdown_table", "csv", "shell_single", "json_string"):
            with self.subTest(context=context):
                first = self.tool.execute(
                    mode="escape", context=context, text=UNICODE_TEXT
                )
                second = self.tool.execute(
                    mode="escape", context=context, text=UNICODE_TEXT
                )
                self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        for bad in ("encode", "Escape", "", None, 123, "transform"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode=bad, context="csv", text="hello"
                )

    def test_invalid_context(self) -> None:
        for bad in ("markdown", "HTML", "", None, 123, "csv ", "sql"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="escape", context=bad, text="hello"
                )

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"], {"a": 1}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="escape", context="csv", text=bad)
                self.assert_invalid(mode="unescape", context="regex", text=bad)

    def test_empty_text_rejected(self) -> None:
        for context in ("markdown_table", "csv", "shell_single", "regex"):
            with self.subTest(context=context):
                self.assert_invalid(mode="escape", context=context, text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(
            mode="escape", context="markdown_table", text=oversized
        )
        self.assert_invalid(mode="unescape", context="regex", text=oversized)
        ok = self.tool.execute(
            mode="escape", context="markdown_table", text="a" * 100_000
        )
        # 'a' has no specials, so the escaped form keeps its length; a
        # backslash-heavy input at the same limit doubles but is accepted.
        self.assertEqual(len(ok["result"]), 100_000)
        doubled = self.tool.execute(
            mode="escape", context="markdown_table", text="\\" * 50_000
        )
        self.assertEqual(len(doubled["result"]), 100_000)

    def test_invalid_ensure_ascii(self) -> None:
        for bad in (123, "yes", 1):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="escape",
                    context="json_string",
                    text="hello",
                    ensure_ascii=bad,
                )

    def test_ensure_ascii_rejected_outside_json_string(self) -> None:
        for context in ("csv", "markdown_table", "regex"):
            with self.subTest(context=context):
                self.assert_invalid(
                    mode="escape", context=context, text="hello", ensure_ascii=True
                )
        # None means "not provided" and stays legal everywhere.
        result = self.tool.execute(
            mode="escape", context="csv", text="hello", ensure_ascii=None
        )
        self.assertEqual(result["result"], "hello")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectContextEscapeTool, ContextEscapeTool)
        self.assertEqual(self.tool.name, "context_escape_tool")
        for token in ("escape", "markdown_table", "csv", "shell_single",
                      "html_attr", "json_string", "regex"):
            self.assertIn(token, self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ContextEscapeTool", __all__)


if __name__ == "__main__":
    unittest.main()
