#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_front_matter_tool.py

"""Offline unit tests for FrontMatterTool.

The tool is built purely on the standard library (tomllib) plus the
framework's existing PyYAML dependency and never touches the network,
so this suite runs fully offline. Every assertion is deterministic:
parse results are compared against literal expected documents for each
delimiter form, set / merge outputs against exact expected texts
(verified against yaml.safe_dump behavior with sort_keys=False), and
the error matrix covers both the ValueError parameter validation and
the structured content-level error payloads.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import FrontMatterTool
from agentuniverse.agent.action.tool.common_tool.front_matter_tool import (
    FrontMatterTool as DirectFrontMatterTool,
)

# --------------------------------------------------------------------- #
# Ground-truth documents (literal expected values, independent of the
# tool's own serialization code)
# --------------------------------------------------------------------- #

DOC_YAML = (
    "---\n"
    "title: Hello World\n"
    "draft: true\n"
    "tags:\n"
    "- alpha\n"
    "- beta\n"
    "author:\n"
    "  name: Ada\n"
    "  city: London\n"
    "---\n"
    "# Heading\n"
    "\n"
    "Body text.\n"
)
DOC_YAML_FRONT_MATTER = {
    "title": "Hello World",
    "draft": True,
    "tags": ["alpha", "beta"],
    "author": {"name": "Ada", "city": "London"},
}
DOC_YAML_BODY = "# Heading\n\nBody text.\n"

DOC_DOTS = "...\ntitle: Dots Form\nweight: 10\n...\nDots body\n"

DOC_TOML = (
    "+++\n"
    'title = "Toml Form"\n'
    "weight = 7\n"
    "[author]\n"
    'name = "Grace"\n'
    "+++\n"
    "Toml body\n"
)

DOC_TOML_INVALID = "+++\ntitle: not toml\n+++\nbody\n"

DOC_EMPTY_FRONT_MATTER = "---\n---\nbody only\n"
DOC_BLANK_FRONT_MATTER = "---\n\n---\nbody only\n"

DOC_NO_FRONT_MATTER = "# Just a doc\n\nNo front matter here.\n"
DOC_THEMATIC_BREAK = "----\n----\nfour dashes are a break\n"
DOC_RULE_NOT_FIRST_LINE = "paragraph\n---\n"

DOC_UNTERMINATED = "---\ntitle: x\n"
DOC_DOTS_UNTERMINATED = "...\ntitle: x\n"

DOC_YAML_ERROR = "---\nkey: [unclosed\nrest: 1\n---\nbody\n"
DOC_NOT_MAPPING = "---\n- just\n- a list\n---\nbody\n"

FM_PATCH = (
    "---\n"
    "# leading comment\n"
    "title: Old Title\n"
    "draft: true\n"
    "tags:\n"
    "- alpha\n"
    "- beta\n"
    "---\n"
    "body\n"
)
FM_PATCH_SET_TITLE = (
    "---\n"
    "# leading comment\n"
    "title: New Title\n"
    "draft: true\n"
    "tags:\n"
    "- alpha\n"
    "- beta\n"
    "---\n"
    "body\n"
)

FM_NESTED = (
    "---\n"
    "title: Keep Me\n"
    "author:\n"
    "  name: Ada\n"
    "  city: London\n"
    "draft: true\n"
    "---\n"
    "body text\n"
)
FM_NESTED_SET_CITY = (
    "---\n"
    "title: Keep Me\n"
    "author:\n"
    "  name: Ada\n"
    "  city: Paris\n"
    "draft: true\n"
    "---\n"
    "body text\n"
)

FM_NEWPATH = "---\ntitle: T\n---\nbody\n"
FM_NEWPATH_SET = "---\ntitle: T\nseo:\n  description: A page\n---\nbody\n"

FM_DEEPPATH_SET_ON_PLAIN_DOC = "---\na:\n  b:\n    c: 1\n---\nplain body"

FM_BLANK = (
    "---\n"
    "first: 1\n"
    "nested:\n"
    "  a: 1\n"
    "\n"
    "  b: 2\n"
    "last: 9\n"
    "---\n"
    "body\n"
)
FM_BLANK_SET = (
    "---\n"
    "first: 1\n"
    "nested:\n"
    "  a: 1\n"
    "  b: 2\n"
    "  c: 3\n"
    "last: 9\n"
    "---\n"
    "body\n"
)

FM_TOML_SET = "+++\ntitle = \"Old\"\nweight = 2\n+++\nbody\n"
FM_TOML_SET_RESULT = "---\ntitle: New\nweight: 2\n---\nbody\n"

FM_CONFLICT = "---\nauthor: plain string\n---\nbody\n"

DOC_CRLF = "---\r\ntitle: Old\r\n---\r\nbody\r\n"
DOC_CRLF_SET = "---\r\ntitle: New\r\n---\r\nbody\r\n"

MERGE_A = "---\ntitle: From A\nshared: a-version\nonly_a: from-a\n---\nbody A\n"
MERGE_B = "---\ntitle: From B\nshared: b-version\nonly_b: 42\n---\nbody B\n"
MERGE_SECOND_WINS = (
    "---\ntitle: From B\nshared: b-version\nonly_a: from-a\nonly_b: 42\n---\nbody B\n"
)
MERGE_FIRST_WINS = (
    "---\ntitle: From A\nshared: a-version\nonly_b: 42\nonly_a: from-a\n---\nbody B\n"
)

MERGE_DEEP_A = "---\nauthor:\n  name: Ada\n  home:\n    city: London\n---\nA\n"
MERGE_DEEP_B = "---\nauthor:\n  home:\n    country: UK\n  age: 36\n---\nB\n"
MERGE_DEEP_RESULT = (
    "---\n"
    "author:\n"
    "  name: Ada\n"
    "  home:\n"
    "    city: London\n"
    "    country: UK\n"
    "  age: 36\n"
    "---\n"
    "B\n"
)

MERGE_ONLY_A = "---\ntitle: Only A\n---\nbody A\n"
MERGE_ONLY_A_RESULT = "---\ntitle: Only A\n---\nJust body B\n"

MERGE_TOML_A = "+++\ntitle = \"A\"\n+++\nA\n"
MERGE_TOML_RESULT = "---\ntitle: A\nweight: 5\n---\nB\n"

MERGE_EMPTY_RESULT = "---\n---\nB body\n"


class FrontMatterToolTest(unittest.TestCase):
    """Offline deterministic test cases for FrontMatterTool."""

    def setUp(self) -> None:
        self.tool = FrontMatterTool()

    # ------------------------------------------------------------------ #
    # parse mode — delimiter forms
    # ------------------------------------------------------------------ #

    def test_parse_yaml_fence_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=DOC_YAML)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "has_front_matter": True,
                "delimiters": "---",
                "format": "yaml",
                "front_matter": DOC_YAML_FRONT_MATTER,
                "body": DOC_YAML_BODY,
            },
        )

    def test_parse_dots_fence_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=DOC_DOTS)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "has_front_matter": True,
                "delimiters": "...",
                "format": "yaml",
                "front_matter": {"title": "Dots Form", "weight": 10},
                "body": "Dots body\n",
            },
        )

    def test_parse_toml_fence_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=DOC_TOML)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "has_front_matter": True,
                "delimiters": "+++",
                "format": "toml",
                "front_matter": {
                    "title": "Toml Form",
                    "weight": 7,
                    "author": {"name": "Grace"},
                },
                "body": "Toml body\n",
            },
        )

    def test_parse_invalid_toml_reports_raw_string(self) -> None:
        result = self.tool.execute(mode="parse", text=DOC_TOML_INVALID)
        self.assertEqual(result["mode"], "parse")
        self.assertTrue(result["has_front_matter"])
        self.assertEqual(result["delimiters"], "+++")
        self.assertEqual(result["format"], "raw_string")
        self.assertIsNone(result["front_matter"])
        self.assertEqual(result["raw_string"], "title: not toml\n")
        self.assertIn("not valid TOML", result["reason"])
        self.assertEqual(result["body"], "body\n")

    def test_parse_empty_front_matter(self) -> None:
        for doc in (DOC_EMPTY_FRONT_MATTER, DOC_BLANK_FRONT_MATTER):
            result = self.tool.execute(mode="parse", text=doc)
            self.assertEqual(result["has_front_matter"], True)
            self.assertEqual(result["front_matter"], {})
            self.assertEqual(result["format"], "yaml")
            self.assertEqual(result["delimiters"], "---")
            self.assertEqual(result["body"], "body only\n")

    def test_parse_no_front_matter_passthrough(self) -> None:
        result = self.tool.execute(mode="parse", text=DOC_NO_FRONT_MATTER)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "has_front_matter": False,
                "delimiters": None,
                "format": None,
                "front_matter": {},
                "body": DOC_NO_FRONT_MATTER,
            },
        )

    def test_parse_thematic_break_is_not_front_matter(self) -> None:
        for doc in (DOC_THEMATIC_BREAK, DOC_RULE_NOT_FIRST_LINE):
            result = self.tool.execute(mode="parse", text=doc)
            self.assertFalse(result["has_front_matter"])
            self.assertIsNone(result["delimiters"])
            self.assertEqual(result["body"], doc)

    # ------------------------------------------------------------------ #
    # parse mode — structured content errors
    # ------------------------------------------------------------------ #

    def test_parse_unterminated_front_matter(self) -> None:
        for doc, delim in ((DOC_UNTERMINATED, "---"), (DOC_DOTS_UNTERMINATED, "...")):
            result = self.tool.execute(mode="parse", text=doc)
            self.assertEqual(result["mode"], "parse")
            self.assertEqual(result["delimiters"], delim)
            self.assertEqual(result["error"]["type"], "unterminated_front_matter")
            self.assertIn(delim, result["error"]["message"])

    def test_parse_yaml_error_with_line_and_column(self) -> None:
        result = self.tool.execute(mode="parse", text=DOC_YAML_ERROR)
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["delimiters"], "---")
        self.assertEqual(result["error"]["type"], "yaml_parse_error")
        self.assertEqual(result["error"]["line"], 2)
        self.assertEqual(result["error"]["column"], 5)
        self.assertIn("not valid YAML", result["error"]["message"])

    def test_parse_front_matter_not_mapping(self) -> None:
        result = self.tool.execute(mode="parse", text=DOC_NOT_MAPPING)
        self.assertEqual(result["error"]["type"], "front_matter_not_mapping")
        self.assertIn("mapping", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # strip mode
    # ------------------------------------------------------------------ #

    def test_strip_returns_body_only(self) -> None:
        result = self.tool.execute(mode="strip", text=DOC_YAML)
        self.assertEqual(
            result, {"mode": "strip", "has_front_matter": True, "result": DOC_YAML_BODY}
        )

    def test_strip_without_front_matter_passthrough(self) -> None:
        result = self.tool.execute(mode="strip", text=DOC_NO_FRONT_MATTER)
        self.assertEqual(
            result,
            {"mode": "strip", "has_front_matter": False, "result": DOC_NO_FRONT_MATTER},
        )

    def test_strip_toml_fence(self) -> None:
        result = self.tool.execute(mode="strip", text=DOC_TOML)
        self.assertEqual(result["has_front_matter"], True)
        self.assertEqual(result["result"], "Toml body\n")

    # ------------------------------------------------------------------ #
    # set mode
    # ------------------------------------------------------------------ #

    def test_set_adds_block_when_absent(self) -> None:
        result = self.tool.execute(
            mode="set", text="# Body\n", key="title", value="Hello"
        )
        self.assertEqual(result["mode"], "set")
        self.assertTrue(result["has_front_matter"])
        self.assertEqual(result["delimiters"], "---")
        self.assertFalse(result["converted_delimiters"])
        self.assertEqual(result["result"], "---\ntitle: Hello\n---\n# Body\n")

    def test_set_existing_key_line_patch_preserves_order_and_comments(self) -> None:
        result = self.tool.execute(
            mode="set", text=FM_PATCH, key="title", value="New Title"
        )
        self.assertEqual(result["result"], FM_PATCH_SET_TITLE)
        self.assertEqual(result["key"], "title")
        self.assertEqual(result["value"], "New Title")

    def test_set_nested_key_preserves_siblings(self) -> None:
        result = self.tool.execute(
            mode="set", text=FM_NESTED, key="author.city", value="Paris"
        )
        self.assertEqual(result["result"], FM_NESTED_SET_CITY)

    def test_set_dotted_key_creates_nested_path(self) -> None:
        result = self.tool.execute(
            mode="set", text=FM_NEWPATH, key="seo.description", value="A page"
        )
        self.assertEqual(result["result"], FM_NEWPATH_SET)

    def test_set_deep_dotted_key_on_plain_text(self) -> None:
        result = self.tool.execute(
            mode="set", text="plain body", key="a.b.c", value=1
        )
        self.assertEqual(result["result"], FM_DEEPPATH_SET_ON_PLAIN_DOC)

    def test_set_replaces_block_spanning_blank_lines(self) -> None:
        result = self.tool.execute(
            mode="set", text=FM_BLANK, key="nested.c", value=3
        )
        self.assertEqual(result["result"], FM_BLANK_SET)

    def test_set_value_type_round_trip(self) -> None:
        base = "---\nk0: v\n---\nb\n"
        cases = [
            ("flag", "true", "---\nk0: v\nflag: 'true'\n---\nb\n"),
            ("num", 42, "---\nk0: v\nnum: 42\n---\nb\n"),
            ("ratio", 3.5, "---\nk0: v\nratio: 3.5\n---\nb\n"),
            ("nope", False, "---\nk0: v\nnope: false\n---\nb\n"),
            ("nothing", None, "---\nk0: v\nnothing: null\n---\nb\n"),
        ]
        for key, value, expected in cases:
            result = self.tool.execute(mode="set", text=base, key=key, value=value)
            self.assertEqual(result["result"], expected, f"case {key!r}")
            reparsed = self.tool.execute(mode="parse", text=result["result"])
            self.assertEqual(reparsed["front_matter"][key], value, f"case {key!r}")

    def test_set_unicode_value_preserved(self) -> None:
        result = self.tool.execute(
            mode="set", text="body", key="city", value="Zürich 🌍"
        )
        self.assertEqual(result["result"], "---\ncity: Zürich 🌍\n---\nbody")
        reparsed = self.tool.execute(mode="parse", text=result["result"])
        self.assertEqual(reparsed["front_matter"], {"city": "Zürich 🌍"})

    def test_set_on_toml_block_converts_to_yaml(self) -> None:
        result = self.tool.execute(
            mode="set", text=FM_TOML_SET, key="title", value="New"
        )
        self.assertEqual(result["delimiters"], "---")
        self.assertTrue(result["converted_delimiters"])
        self.assertEqual(result["result"], FM_TOML_SET_RESULT)
        reparsed = self.tool.execute(mode="parse", text=result["result"])
        self.assertEqual(
            reparsed["front_matter"], {"title": "New", "weight": 2}
        )

    def test_set_on_invalid_toml_block_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="set", text=DOC_TOML_INVALID, key="title", value="New"
        )
        self.assertEqual(result["mode"], "set")
        self.assertEqual(result["error"]["type"], "invalid_toml_front_matter")
        self.assertIn("tomllib", result["error"]["message"])

    def test_set_dotted_key_conflict_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="set", text=FM_CONFLICT, key="author.name", value="Ada"
        )
        self.assertEqual(result["error"]["type"], "key_conflict")
        self.assertIn("author", result["error"]["message"])

    def test_set_propagates_unterminated_error(self) -> None:
        result = self.tool.execute(
            mode="set", text=DOC_UNTERMINATED, key="title", value="New"
        )
        self.assertEqual(result["error"]["type"], "unterminated_front_matter")

    def test_set_propagates_yaml_error(self) -> None:
        result = self.tool.execute(
            mode="set", text=DOC_YAML_ERROR, key="title", value="New"
        )
        self.assertEqual(result["error"]["type"], "yaml_parse_error")
        self.assertEqual(result["error"]["line"], 2)
        self.assertEqual(result["error"]["column"], 5)

    def test_set_preserves_crlf_newlines(self) -> None:
        result = self.tool.execute(
            mode="set", text=DOC_CRLF, key="title", value="New"
        )
        self.assertEqual(result["result"], DOC_CRLF_SET)

    def test_set_is_deterministic(self) -> None:
        for _ in range(3):
            result = self.tool.execute(
                mode="set", text=FM_NESTED, key="author.city", value="Paris"
            )
            self.assertEqual(result["result"], FM_NESTED_SET_CITY)

    def test_set_then_parse_round_trip(self) -> None:
        updated = self.tool.execute(
            mode="set", text=DOC_YAML, key="author.email", value="ada@example.com"
        )["result"]
        parsed = self.tool.execute(mode="parse", text=updated)
        expected = dict(DOC_YAML_FRONT_MATTER)
        expected["author"] = {
            "name": "Ada",
            "city": "London",
            "email": "ada@example.com",
        }
        self.assertEqual(parsed["front_matter"], expected)
        self.assertEqual(parsed["body"], DOC_YAML_BODY)

    # ------------------------------------------------------------------ #
    # merge mode
    # ------------------------------------------------------------------ #

    def test_merge_default_second_wins(self) -> None:
        result = self.tool.execute(mode="merge", text=MERGE_A, other_text=MERGE_B)
        self.assertEqual(
            result,
            {
                "mode": "merge",
                "precedence": "second",
                "has_front_matter": True,
                "delimiters": "---",
                "result": MERGE_SECOND_WINS,
            },
        )

    def test_merge_first_wins_documented_flip(self) -> None:
        result = self.tool.execute(
            mode="merge", text=MERGE_A, other_text=MERGE_B, precedence="first"
        )
        self.assertEqual(result["precedence"], "first")
        self.assertEqual(result["result"], MERGE_FIRST_WINS)

    def test_merge_deep_nested_values(self) -> None:
        result = self.tool.execute(
            mode="merge", text=MERGE_DEEP_A, other_text=MERGE_DEEP_B
        )
        self.assertEqual(result["result"], MERGE_DEEP_RESULT)

    def test_merge_body_comes_from_second(self) -> None:
        result = self.tool.execute(
            mode="merge", text=MERGE_ONLY_A, other_text="Just body B\n"
        )
        self.assertEqual(
            result,
            {
                "mode": "merge",
                "precedence": "second",
                "has_front_matter": True,
                "delimiters": "---",
                "result": MERGE_ONLY_A_RESULT,
            },
        )

    def test_merge_neither_has_front_matter(self) -> None:
        result = self.tool.execute(
            mode="merge", text="body A\n", other_text="body B\n"
        )
        self.assertEqual(
            result,
            {
                "mode": "merge",
                "precedence": "second",
                "has_front_matter": False,
                "delimiters": None,
                "result": "body B\n",
            },
        )

    def test_merge_both_empty_front_matter_keeps_empty_block(self) -> None:
        result = self.tool.execute(
            mode="merge", text="---\n---\nA body\n", other_text="---\n---\nB body\n"
        )
        self.assertTrue(result["has_front_matter"])
        self.assertEqual(result["result"], MERGE_EMPTY_RESULT)

    def test_merge_toml_first_converted_to_yaml(self) -> None:
        result = self.tool.execute(
            mode="merge",
            text=MERGE_TOML_A,
            other_text="---\nweight: 5\n---\nB\n",
        )
        self.assertEqual(result["delimiters"], "---")
        self.assertEqual(result["result"], MERGE_TOML_RESULT)

    def test_merge_propagates_content_errors(self) -> None:
        result = self.tool.execute(
            mode="merge", text=DOC_UNTERMINATED, other_text="b\n"
        )
        self.assertEqual(result["mode"], "merge")
        self.assertEqual(result["error"]["type"], "unterminated_front_matter")

        result = self.tool.execute(
            mode="merge", text=DOC_TOML_INVALID, other_text="b\n"
        )
        self.assertEqual(result["error"]["type"], "invalid_toml_front_matter")

    def test_merge_is_deterministic(self) -> None:
        for _ in range(3):
            result = self.tool.execute(
                mode="merge", text=MERGE_A, other_text=MERGE_B
            )
            self.assertEqual(result["result"], MERGE_SECOND_WINS)

    # ------------------------------------------------------------------ #
    # Parameter validation (ValueError before any computation)
    # ------------------------------------------------------------------ #

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="format", text=DOC_YAML)
        with self.assertRaises(ValueError):
            self.tool.execute(mode=None, text=DOC_YAML)

    def test_invalid_text_raises(self) -> None:
        for bad in (None, "", 123, b"bytes", ["list"]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="parse", text=bad)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="merge", text="a\n", other_text=None)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="merge", text="a\n", other_text=123)

    def test_invalid_key_raises(self) -> None:
        for bad in (None, 5, "", ".a", "a.", "a..b", "a:b", "a b", "a b.c"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="set", text=DOC_YAML, key=bad, value="v")

    def test_invalid_value_raises(self) -> None:
        for bad in ([1, 2], {"k": 1}, b"bytes", (1, 2)):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="set", text=DOC_YAML, key="k", value=bad)

    def test_invalid_precedence_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="merge", text="a\n", other_text="b\n", precedence="bogus"
            )

    def test_oversized_text_raises(self) -> None:
        huge = "x" * 100_001
        with self.assertRaises(ValueError):
            self.tool.execute(mode="parse", text=huge)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="set", text=DOC_YAML, key="k", value=huge)

    # ------------------------------------------------------------------ #
    # Import surface
    # ------------------------------------------------------------------ #

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(FrontMatterTool, DirectFrontMatterTool)
        self.assertEqual(FrontMatterTool().name, "front_matter_tool")


if __name__ == "__main__":
    unittest.main()
