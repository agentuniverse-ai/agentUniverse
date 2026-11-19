#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_bullets_to_prose_tool.py

"""Offline unit tests for BulletsToProseTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every assertion is
deterministic: converted text is checked against hand-computed ground
truths including simple bullet blocks, all four numbered families,
single-item / two-item connector special cases, nesting flattening,
checkbox semantics, byte-exact preservation of surrounding text, code
fence immunity, custom connectors, the lead connector flag and the
idempotent second-pass guard (including the backslash-escape edge
cases). The preview and stats payloads are compared against exact
expected dicts, and a full error matrix covers the strict input
validation.
"""

import os
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import (
    BulletsToProseTool,
    bullets_to_prose_tool as bullets_to_prose_module,
)
from agentuniverse.agent.action.tool.common_tool.bullets_to_prose_tool import (
    BulletsToProseTool as DirectBulletsToProseTool,
)

YAML_PATH = os.path.join(
    os.path.dirname(os.path.abspath(bullets_to_prose_module.__file__)),
    "bullets_to_prose_tool.yaml",
)


class BulletsToProseToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib BulletsToProseTool."""

    def setUp(self) -> None:
        self.tool = BulletsToProseTool()

    # ------------------------------------------------------------------ #
    # convert mode — ground truths
    # ------------------------------------------------------------------ #

    def test_convert_simple_bullet_block_full_payload(self) -> None:
        result = self.tool.execute(
            mode="convert",
            text="Intro line.\n- alpha\n- beta\n- gamma\nOutro line.",
        )
        self.assertEqual(
            result,
            {
                "mode": "convert",
                "result": (
                    "Intro line.\n"
                    "alpha, and then beta, and finally gamma\n"
                    "Outro line."
                ),
                "blocks": [
                    {
                        "kind": "bullet",
                        "family": "-",
                        "start_line": 2,
                        "end_line": 4,
                        "item_count": 3,
                        "top_level_item_count": 3,
                        "nesting_depth": 1,
                    }
                ],
                "block_count": 1,
                "item_count": 3,
                "top_level_item_count": 3,
                "max_nesting_depth": 1,
                "checkbox_counts": {"completed": 0, "pending": 0},
                "escaped_paragraph_count": 0,
            },
        )

    def test_convert_numbered_families(self) -> None:
        # arabic-dot
        result = self.tool.execute(
            mode="convert", text="1. first\n2. second\n3. third"
        )
        self.assertEqual(
            result["result"], "first, and then second, and finally third"
        )
        self.assertEqual(result["blocks"][0]["kind"], "numbered")
        self.assertEqual(result["blocks"][0]["family"], "arabic-dot")
        # arabic-paren
        result = self.tool.execute(mode="convert", text="1) a\n2) b")
        self.assertEqual(result["result"], "a, and finally b")
        self.assertEqual(result["blocks"][0]["family"], "arabic-paren")
        # letter-paren, any case, sequence not enforced
        result = self.tool.execute(
            mode="convert", text="(A) x\n(b) y\n(c) z"
        )
        self.assertEqual(result["result"], "x, and then y, and finally z")
        self.assertEqual(result["blocks"][0]["family"], "letter-paren")
        # cjk-paren
        result = self.tool.execute(
            mode="convert", text="(一) east\n(二) west"
        )
        self.assertEqual(result["result"], "east, and finally west")
        self.assertEqual(result["blocks"][0]["family"], "cjk-paren")
        # sequence continuity is not enforced for digits either
        result = self.tool.execute(mode="convert", text="1. a\n9. b")
        self.assertEqual(result["result"], "a, and finally b")
        self.assertEqual(result["block_count"], 1)

    def test_convert_single_item_block_no_connectors(self) -> None:
        result = self.tool.execute(mode="convert", text="- only")
        self.assertEqual(result["result"], "only")
        self.assertEqual(result["item_count"], 1)
        # The lead connector is also suppressed for a lone item.
        result = self.tool.execute(
            mode="convert", text="- only", lead_connector=True
        )
        self.assertEqual(result["result"], "only")

    def test_convert_two_item_block_only_last_connector(self) -> None:
        result = self.tool.execute(mode="convert", text="- one\n- two")
        self.assertEqual(result["result"], "one, and finally two")
        # With the lead flag both roles appear.
        result = self.tool.execute(
            mode="convert", text="- one\n- two", lead_connector=True
        )
        self.assertEqual(result["result"], "First, one, and finally two")

    def test_convert_nested_flattening(self) -> None:
        result = self.tool.execute(
            mode="convert",
            text="- fruits\n  - apple\n  - banana\n- vegetables",
        )
        self.assertEqual(
            result["result"],
            "fruits (namely: apple; banana), and finally vegetables",
        )
        self.assertEqual(result["blocks"][0]["top_level_item_count"], 2)
        self.assertEqual(result["blocks"][0]["nesting_depth"], 2)
        # Recursion: a child with its own sub-list gains its own
        # parenthetical.
        result = self.tool.execute(
            mode="convert", text="- a\n  - b\n    - c"
        )
        self.assertEqual(result["result"], "a (namely: b (namely: c))")
        self.assertEqual(result["blocks"][0]["nesting_depth"], 3)
        # One tab or every two spaces is one level; depth clamps at 4.
        result = self.tool.execute(mode="convert", text="- a\n\t- b")
        self.assertEqual(result["result"], "a (namely: b)")
        result = self.tool.execute(
            mode="convert", text="- a\n" + " " * 10 + "- b"
        )
        self.assertEqual(result["result"], "a (namely: b)")
        # A single stray space stays level 0 (no nesting), and the
        # block's first-item indentation is preserved on the paragraph.
        result = self.tool.execute(mode="convert", text=" - a\n - b")
        self.assertEqual(result["result"], " a, and finally b")

    def test_convert_checkbox_semantics(self) -> None:
        result = self.tool.execute(
            mode="convert", text="- [x] write tests\n- [ ] ship release"
        )
        self.assertEqual(
            result["result"],
            "write tests (completed), and finally ship release (pending)",
        )
        self.assertEqual(
            result["checkbox_counts"], {"completed": 1, "pending": 1}
        )
        # Uppercase X also means checked; bare boxes work too.
        result = self.tool.execute(mode="convert", text="- [X] Done")
        self.assertEqual(result["result"], "Done (completed)")
        result = self.tool.execute(mode="convert", text="[x] solo")
        self.assertEqual(result["result"], "solo (completed)")
        self.assertEqual(result["blocks"][0]["kind"], "checkbox")
        # An empty checkbox keeps its bare semantics.
        result = self.tool.execute(mode="convert", text="- [x]")
        self.assertEqual(result["result"], "(completed)")
        # Checkbox children under a checkbox parent flatten inline
        # (kind and family stay identical, so the block holds together).
        result = self.tool.execute(
            mode="convert",
            text="- [x] parent\n  - [ ] child\n  - [x] other",
        )
        self.assertEqual(
            result["result"],
            "parent (completed) (namely: child (pending); "
            "other (completed))",
        )

    def test_convert_mixed_doc_preserves_non_list_text_byte_exact(self) -> None:
        text = (
            "# Release notes\n"
            "\n"
            "Highlights below.  \n"
            "\n"
            "- fast parsing\n"
            "* small footprint\n"
            "- zero dependencies\n"
            "\n"
            "Trivia: 2023 was a year.\n"
            "\n"
            "    indented prose keeps its bytes\n"
        )
        result = self.tool.execute(mode="convert", text=text)
        self.assertEqual(
            result["result"],
            "# Release notes\n"
            "\n"
            "Highlights below.  \n"
            "\n"
            "fast parsing\n"
            "small footprint\n"
            "zero dependencies\n"
            "\n"
            "Trivia: 2023 was a year.\n"
            "\n"
            "    indented prose keeps its bytes\n",
        )
        # A marker style change splits blocks: three one-item blocks.
        self.assertEqual(result["block_count"], 3)
        self.assertEqual(
            [block["family"] for block in result["blocks"]],
            ["-", "*", "-"],
        )
        # No trailing newline is preserved as-is.
        result = self.tool.execute(mode="convert", text="- a\n- b")
        self.assertEqual(result["result"], "a, and finally b")
        # A marker must be followed by a separating whitespace run, so
        # flags, bold spans and rules stay prose.
        result = self.tool.execute(
            mode="convert", text="--force and **bold** and --- rule"
        )
        self.assertEqual(
            result["result"], "--force and **bold** and --- rule"
        )
        self.assertEqual(result["block_count"], 0)
        # Oversized digit runs inside prose are not enumerations.
        result = self.tool.execute(
            mode="convert", text="1234567890. hello"
        )
        self.assertEqual(result["result"], "1234567890. hello")
        self.assertEqual(result["block_count"], 0)

    def test_convert_style_change_splits_blocks(self) -> None:
        result = self.tool.execute(mode="convert", text="- a\n* b")
        self.assertEqual(result["result"], "a\nb")
        self.assertEqual(result["block_count"], 2)
        result = self.tool.execute(mode="convert", text="1. a\n1) b")
        self.assertEqual(result["result"], "a\nb")
        self.assertEqual(result["block_count"], 2)

    def test_code_fence_immunity(self) -> None:
        text = (
            "Example:\n"
            "\n"
            "```python\n"
            "- not converted\n"
            "* also kept\n"
            "```\n"
            "\n"
            "- real list\n"
        )
        result = self.tool.execute(mode="convert", text=text)
        self.assertEqual(
            result["result"],
            "Example:\n\n```python\n- not converted\n* also kept\n```\n\n"
            "real list\n",
        )
        self.assertEqual(result["block_count"], 1)
        # Tilde fences are honored too.
        result = self.tool.execute(mode="convert", text="~~~\n- kept\n")
        self.assertEqual(result["result"], "~~~\n- kept\n")
        self.assertEqual(result["block_count"], 0)
        # An unclosed fence immunizes everything to the end of input.
        result = self.tool.execute(mode="convert", text="```\n- kept\n- also")
        self.assertEqual(result["result"], "```\n- kept\n- also")
        # A fence line inside a list closes the block; list lines
        # between the fence pair survive.
        result = self.tool.execute(
            mode="convert", text="- a\n```\n- b\n```\n- c"
        )
        self.assertEqual(result["result"], "a\n```\n- b\n```\nc")

    def test_custom_connectors(self) -> None:
        # Full set, honored exactly.
        result = self.tool.execute(
            mode="convert",
            text="- a\n- b\n- c",
            connectors={
                "first": "To start, ",
                "middle": " plus ",
                "last": " and at last ",
            },
        )
        self.assertEqual(
            result["result"], "To start, a plus b and at last c"
        )
        # Partial subset: missing roles fall back to the defaults.
        result = self.tool.execute(
            mode="convert", text="- a\n- b\n- c", connectors={"last": " & "}
        )
        self.assertEqual(result["result"], "a, and then b & c")
        # Exact honoring — no case munging, no stripping.
        result = self.tool.execute(
            mode="convert",
            text="- a\n- b\n- c",
            connectors={"middle": " — "},
        )
        self.assertEqual(result["result"], "a — b, and finally c")
        # An explicit first connector wins over the lead flag.
        result = self.tool.execute(
            mode="convert",
            text="- a\n- b",
            lead_connector=True,
            connectors={"first": "Begin: "},
        )
        self.assertEqual(result["result"], "Begin: a, and finally b")
        # Single-item blocks ignore custom connectors entirely.
        result = self.tool.execute(
            mode="convert", text="- solo", connectors={"last": " & "}
        )
        self.assertEqual(result["result"], "solo")

    def test_lead_connector_flag(self) -> None:
        result = self.tool.execute(
            mode="convert", text="- a\n- b\n- c", lead_connector=True
        )
        self.assertEqual(
            result["result"], "First, a, and then b, and finally c"
        )
        # Default off.
        result = self.tool.execute(mode="convert", text="- a\n- b\n- c")
        self.assertEqual(result["result"], "a, and then b, and finally c")

    def test_idempotent_second_pass(self) -> None:
        samples = [
            "Intro line.\n- alpha\n- beta\n- gamma\nOutro line.",
            "1. first\n2. second\n3. third",
            "- fruits\n  - apple\n  - banana\n- vegetables",
            "- [x] write tests\n- [ ] ship release",
            "- a\n```\n- b\n```\n- c",
            "- only",
            "plain prose without any list",
        ]
        for sample in samples:
            with self.subTest(sample=sample[:40]):
                first = self.tool.execute(mode="convert", text=sample)
                second = self.tool.execute(
                    mode="convert", text=first["result"]
                )
                self.assertEqual(first["result"], second["result"])
                self.assertEqual(second["block_count"], 0)

    def test_idempotence_escape_guard(self) -> None:
        # A first item whose own text looks like a bare ordered line
        # gets a backslash escape so the second pass also finds no list.
        result = self.tool.execute(mode="convert", text="- 1. looks ordered")
        self.assertEqual(result["result"], "1\\. looks ordered")
        self.assertEqual(result["escaped_paragraph_count"], 1)
        second = self.tool.execute(mode="convert", text=result["result"])
        self.assertEqual(second["result"], result["result"])
        self.assertEqual(second["block_count"], 0)
        # Bullet-looking item text escapes the marker itself.
        result = self.tool.execute(mode="convert", text="- - nested-looking")
        self.assertEqual(result["result"], "\\- nested-looking")
        self.assertEqual(result["escaped_paragraph_count"], 1)
        second = self.tool.execute(mode="convert", text=result["result"])
        self.assertEqual(second["result"], result["result"])
        # Paren-style ordered escape targets the opening bracket.
        result = self.tool.execute(mode="convert", text="- (a) lettered")
        self.assertEqual(result["result"], "\\(a) lettered")
        second = self.tool.execute(mode="convert", text=result["result"])
        self.assertEqual(second["result"], result["result"])
        self.assertEqual(second["block_count"], 0)

    def test_convert_empty_items_are_preserved(self) -> None:
        # A marker standing alone yields an empty item; empty items
        # are never dropped, so the connectors still fire.
        result = self.tool.execute(mode="convert", text="-\n- b")
        self.assertEqual(result["result"], ", and finally b")
        self.assertEqual(result["item_count"], 2)

    def test_convert_crlf_input(self) -> None:
        # Item text is stripped of the carriage return; converted
        # paragraphs use plain line endings while non-list lines (here
        # the trailing empty line) keep their bytes.
        result = self.tool.execute(mode="convert", text="- a\r\n- b\r\n")
        self.assertEqual(result["result"], "a, and finally b\n")

    def test_convert_no_blocks_returns_text_unchanged(self) -> None:
        result = self.tool.execute(mode="convert", text="just prose\n")
        self.assertEqual(result["result"], "just prose\n")
        self.assertEqual(result["block_count"], 0)
        self.assertEqual(result["max_nesting_depth"], 0)

    # ------------------------------------------------------------------ #
    # paragraphs_only mode (preview)
    # ------------------------------------------------------------------ #

    def test_paragraphs_only_reports_line_ranges(self) -> None:
        result = self.tool.execute(
            mode="paragraphs_only",
            text="Intro\n- a\n  - b\n- c\nOutro\n",
        )
        self.assertEqual(
            result,
            {
                "mode": "paragraphs_only",
                "result": [
                    {
                        "kind": "bullet",
                        "family": "-",
                        "start_line": 2,
                        "end_line": 4,
                        "item_count": 3,
                        "top_level_item_count": 2,
                        "nesting_depth": 2,
                    }
                ],
                "block_count": 1,
                "item_count": 3,
                "max_nesting_depth": 2,
            },
        )

    def test_paragraphs_only_does_not_rewrite(self) -> None:
        text = "keep me\n- a\n- b\n"
        result = self.tool.execute(mode="paragraphs_only", text=text)
        # The preview payload carries only metadata, never a rewritten
        # copy of the text.
        self.assertNotIn("text", result)
        self.assertIsInstance(result["result"], list)
        self.assertEqual(result["block_count"], 1)
        self.assertEqual(result["result"][0]["start_line"], 2)
        self.assertEqual(result["result"][0]["end_line"], 3)

    # ------------------------------------------------------------------ #
    # stats mode
    # ------------------------------------------------------------------ #

    def test_stats_full_payload(self) -> None:
        result = self.tool.execute(
            mode="stats",
            text="- a\n  - [x] b\n- c\n\ntext\n\n1. d\n",
        )
        self.assertEqual(
            result,
            {
                "mode": "stats",
                "result": {
                    "blocks": 4,
                    "items": 4,
                    "top_level_items": 4,
                    "nesting_levels": [1],
                    "max_nesting_depth": 1,
                    "checkbox_counts": {"completed": 1, "pending": 0},
                },
                "block_count": 4,
                "item_count": 4,
                "max_nesting_depth": 1,
            },
        )

    def test_stats_agrees_with_convert_and_preview(self) -> None:
        text = (
            "Para.\n- x\n- y\n  - z\n\n(a) one\n(b) two\n\n"
            "- [ ] todo\n"
        )
        stats = self.tool.execute(mode="stats", text=text)
        preview = self.tool.execute(mode="paragraphs_only", text=text)
        converted = self.tool.execute(mode="convert", text=text)
        self.assertEqual(stats["block_count"], preview["block_count"])
        self.assertEqual(stats["block_count"], converted["block_count"])
        self.assertEqual(stats["item_count"], preview["item_count"])
        self.assertEqual(stats["item_count"], converted["item_count"])
        self.assertEqual(
            stats["result"]["checkbox_counts"],
            converted["checkbox_counts"],
        )
        self.assertEqual(stats["result"]["nesting_levels"], [1, 2])
        # The rewritten text holds no list marker lines any more.
        for line in converted["result"].split("\n"):
            self.assertIsNone(
                bullets_to_prose_module._parse_line(line),
                msg=f"line still parses as a list item: {line!r}",
            )

    # ------------------------------------------------------------------ #
    # Input validation — error matrix
    # ------------------------------------------------------------------ #

    def test_error_matrix(self) -> None:
        cases = [
            {"mode": "rewrite", "text": "- a"},                       # bad mode
            {"mode": "convert", "text": None},                        # no text
            {"mode": "convert", "text": ""},                          # empty
            {"mode": "convert", "text": 12},                          # non-str
            {"mode": "convert", "text": True},                        # bool
            {"mode": "convert", "text": "x" * 100_001},               # oversized
            {"mode": "convert", "text": "- a", "lead_connector": 1},  # non-bool
            {"mode": "convert", "text": "- a", "lead_connector": "yes"},
            {"mode": "convert", "text": "- a", "connectors": "x"},    # non-dict
            {"mode": "convert", "text": "- a", "connectors": ["m"]},
            {"mode": "convert", "text": "- a", "connectors": True},
            {"mode": "convert", "text": "- a", "connectors": {"top": "x"}},
            {"mode": "convert", "text": "- a", "connectors": {"middle": 42}},
            {"mode": "convert", "text": "- a", "connectors": {"middle": None}},
            {"mode": "convert", "text": "- a", "connectors": {"middle": ""}},
            {"mode": "convert",
             "text": "- a", "connectors": {"middle": "x" * 65}},
            # Validation is strict in every mode, not just convert.
            {"mode": "stats", "text": None},
            {"mode": "paragraphs_only", "text": "- a", "connectors": {1: "x"}},
        ]
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    self.tool.execute(**case)

    def test_validation_boundaries_accepted(self) -> None:
        # 64-character connector and a text at the size cap pass.
        result = self.tool.execute(
            mode="convert",
            text="- a\n- b\n- c",
            connectors={"middle": "x" * 64},
        )
        self.assertEqual(
            result["result"], "a" + "x" * 64 + "b, and finally c"
        )
        result = self.tool.execute(
            mode="convert", text="x" * (100_000 - 8) + "\n- a\n- b"
        )
        self.assertTrue(result["result"].endswith("a, and finally b"))
        # None lead_connector and None connectors are the defaults.
        result = self.tool.execute(
            mode="convert", text="- a\n- b",
            lead_connector=None, connectors=None,
        )
        self.assertEqual(result["result"], "a, and finally b")

    # ------------------------------------------------------------------ #
    # Class defaults / packaging
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectBulletsToProseTool, BulletsToProseTool)
        self.assertEqual(self.tool.name, "bullets_to_prose_tool")
        self.assertIn("convert", self.tool.description)
        self.assertIn("paragraphs_only", self.tool.description)
        self.assertEqual(self.tool.MODES, ("convert", "paragraphs_only", "stats"))
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("BulletsToProseTool", __all__)

    def test_yaml_registration_file(self) -> None:
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "bullets_to_prose_tool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(config["metadata"]["type"], "TOOL")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.bullets_to_prose_tool",
        )
        self.assertEqual(config["metadata"]["class"], "BulletsToProseTool")
        self.assertEqual(config["input_keys"], ["mode"])
        self.assertEqual(
            config["args_model_schema"]["properties"]["mode"]["enum"],
            ["convert", "paragraphs_only", "stats"],
        )
        self.assertEqual(
            config["args_model_schema"]["required"], ["mode"]
        )


if __name__ == "__main__":
    unittest.main()
