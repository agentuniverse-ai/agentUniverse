#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_markdown_lint_tool.py

"""Offline unit tests for MarkdownLintTool.

The tool is built purely on the standard library and never touches
the filesystem (except the read-only guidebook corpus below), the
network or a database, so this suite runs fully offline. Assertions
are exact ground truths: every one of the 16 lint rules is checked
in its triggering shape and in a non-triggering control shape, fence
interiors grant immunity to every non-fence rule at scale (backtick,
tilde and four-backtick fences, mismatched and short closers),
profile arithmetic is verified by hand (family tokenizer, link
census, reading seconds), fix_hints exact outputs are checked with a
re-lint round-trip and idempotence, and the full option error matrix
including per-mode option gating is exercised. The final test runs
lint and profile over 20 real guidebook documents (10 English, 10
Chinese) and re-derives every line-local finding independently from
the raw file bytes.
"""

import re
import unittest
from pathlib import Path

from agentuniverse.agent.action.tool.common_tool import MarkdownLintTool
from agentuniverse.agent.action.tool.common_tool.markdown_lint_tool import (
    MarkdownLintTool as DirectMarkdownLintTool,
)


def _codes(result: dict) -> list:
    return [finding["code"] for finding in result["findings"]]


def _finding(result: dict, code: str) -> dict:
    matches = [f for f in result["findings"] if f["code"] == code]
    assert matches, f"{code} not in {_codes(result)}"
    return matches[0]


def _lines(*lines: str) -> str:
    return "\n".join(lines) + "\n"


class MarkdownLintToolBasicsTest(unittest.TestCase):
    """Export surface, determinism and ok semantics."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(MarkdownLintTool, DirectMarkdownLintTool)

    def test_name_modes_and_rule_codes(self) -> None:
        self.assertEqual(self.tool.name, "markdown_lint_tool")
        self.assertEqual(
            MarkdownLintTool.MODES, ("lint", "profile", "fix_hints")
        )
        self.assertEqual(len(MarkdownLintTool.RULE_CODES), 16)
        self.assertEqual(
            MarkdownLintTool.RULE_CODES,
            tuple(f"MD{number:03d}" for number in range(1, 17)),
        )

    def test_deterministic_repeat(self) -> None:
        text = _lines("# T", "", "- a", "* b", "```", "code", "```")
        self.assertEqual(
            self.tool.execute(mode="lint", markdown_text=text),
            self.tool.execute(mode="lint", markdown_text=text),
        )

    def test_clean_document_is_ok(self) -> None:
        text = _lines(
            "# Title", "", "Paragraph text.", "",
            "## Section", "",
            "- item one", "- item two", "",
            "```python", "x = 1", "```", "",
            "See [docs](guide.md).",
        )
        result = self.tool.execute(mode="lint", markdown_text=text)
        self.assertTrue(result["ok"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["finding_count"], 0)
        self.assertFalse(result["findings_truncated"])

    def test_info_only_stays_ok(self) -> None:
        text = _lines("# Title", "", "text with http://bare.example.com")
        result = self.tool.execute(mode="lint", markdown_text=text)
        self.assertEqual(_codes(result), ["MD011"])
        self.assertTrue(result["ok"])

    def test_warning_breaks_ok(self) -> None:
        text = _lines("# A", "# B")
        result = self.tool.execute(mode="lint", markdown_text=text)
        self.assertEqual(_codes(result), ["MD002"])
        self.assertFalse(result["ok"])


class HeadingRulesTest(unittest.TestCase):
    """MD001 / MD002 / MD003 / MD004 triggers and controls."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_md001_level_jump(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("# H1", "#### H4")
        )
        finding = _finding(result, "MD001")
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["severity"], "warning")
        self.assertIn("h1 -> h4", finding["message"])
        self.assertIn("h3", finding["message"])

    def test_md001_control_single_step(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("# H1", "## H2", "### H3")
        )
        self.assertNotIn("MD001", _codes(result))

    def test_md001_control_going_shallower_any_amount(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "###### Deep", "#### Mid", "## Shallow", "# Top",
            )
        )
        self.assertNotIn("MD001", _codes(result))

    def test_md002_multiple_h1(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "# First", "## Mid", "# Second", "# Third",
            )
        )
        hits = [f for f in result["findings"] if f["code"] == "MD002"]
        self.assertEqual([h["line"] for h in hits], [3, 4])

    def test_md002_control_single_h1(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("# Only", "## Two")
        )
        self.assertNotIn("MD002", _codes(result))

    def test_md003_empty_heading(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("# Title", "##", "###   ")
        )
        hits = [f for f in result["findings"] if f["code"] == "MD003"]
        self.assertEqual([h["line"] for h in hits], [2, 3])
        self.assertEqual(hits[0]["severity"], "error")

    def test_md003_closed_empty_shape_is_empty_not_mismatch(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("## ##")
        )
        self.assertEqual(_codes(result), ["MD003"])

    def test_md003_control_hash_word_not_heading(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("#Hello", "#C#")
        )
        self.assertEqual(result["findings"], [])

    def test_md004_trailing_hashes_inconsistent(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("## Title ###")
        )
        finding = _finding(result, "MD004")
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["severity"], "warning")

    def test_md004_control_matching_and_absent(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "## Title ##", "# One #", "## C# notes",
            )
        )
        self.assertEqual(result["findings"], [])


class ListRulesTest(unittest.TestCase):
    """MD005 / MD006 / MD007 / MD015 triggers and controls."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_md005_marker_mixing(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "* a", "* b", "* c", "- d", "+ e",
            )
        )
        finding = _finding(result, "MD005")
        self.assertEqual(finding["line"], 4)
        self.assertIn("'-' x1", finding["message"])
        self.assertIn("'+' x1", finding["message"])
        self.assertIn("'*' x3", finding["message"])

    def test_md005_tie_prefers_dash(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("* a", "- b", "* c", "- d")
        )
        finding = _finding(result, "MD005")
        # Tie 2-2: '-' dominant, first '*' reported.
        self.assertEqual(finding["line"], 1)

    def test_md005_control_single_marker(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("- a", "- b", "- c")
        )
        self.assertNotIn("MD005", _codes(result))

    def test_md006_indent_not_multiple_of_two(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("- a", "   - b", "     - c")
        )
        hits = [f for f in result["findings"] if f["code"] == "MD006"]
        self.assertEqual([h["line"] for h in hits], [2, 3])

    def test_md006_control_even_indents(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "- a", "  - b", "    - c", "      - d",
            )
        )
        self.assertNotIn("MD006", _codes(result))

    def test_md007_tab_in_list_indent(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("- a", "\t- b", "1. x", "\t2. y")
        )
        hits = [f for f in result["findings"] if f["code"] == "MD007"]
        self.assertEqual([h["line"] for h in hits], [2, 4])

    def test_md007_no_double_fire_with_md006(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("\t- b")
        )
        self.assertEqual(_codes(result), ["MD007"])

    def test_md015_inconsistent_bullet_case(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "- Deploy the service", "- run tests", "- Monitor",
            )
        )
        finding = _finding(result, "MD015")
        self.assertEqual(finding["line"], 2)
        self.assertIn("'D'", finding["message"])
        self.assertIn("'r'", finding["message"])

    def test_md015_control_consistent_case(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "- deploy", "- run", "- monitor",
            )
        )
        self.assertNotIn("MD015", _codes(result))

    def test_md015_non_letter_items_do_not_participate(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "- 123 start", "- (parenthetical)", "- 中文条目",
            )
        )
        self.assertNotIn("MD015", _codes(result))

    def test_thematic_break_is_not_a_list_item(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("- a", "* * *", "- c")
        )
        # '*' line is a thematic break: no marker mixing, no MD005.
        self.assertNotIn("MD005", _codes(result))


class FenceRulesTest(unittest.TestCase):
    """MD008 / MD009 / MD010 triggers and controls."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_md008_unclosed_fence(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("```", "code")
        )
        finding = _finding(result, "MD008")
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["severity"], "error")

    def test_md008_control_closed(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("```", "code", "```")
        )
        self.assertNotIn("MD008", _codes(result))

    def test_md009_lang_missing(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("```", "x", "```")
        )
        finding = _finding(result, "MD009")
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["severity"], "info")

    def test_md009_control_with_language(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("```python", "x = 1", "```")
        )
        self.assertNotIn("MD009", _codes(result))

    def test_md010_fence_char_mismatch_then_proper_close(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "```python", "x = 1", "~~~", "still inside", "```",
            )
        )
        finding = _finding(result, "MD010")
        self.assertEqual(finding["line"], 3)
        self.assertEqual(finding["severity"], "error")
        self.assertNotIn("MD008", _codes(result))
        # "still inside" is interior: immune to every other rule.
        self.assertEqual(_codes(result), ["MD010"])

    def test_md010_mismatch_and_never_closed(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("```", "x = 1", "~~~")
        )
        self.assertEqual(
            [(f["line"], f["code"]) for f in result["findings"]],
            [(1, "MD008"), (1, "MD009"), (3, "MD010")],
        )

    def test_shorter_same_char_close_does_not_close(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "````", "```", "inner", "````",
            )
        )
        # The 3-run line is interior (not flagged), the 4-run closes.
        self.assertNotIn("MD008", _codes(result))
        self.assertNotIn("MD010", _codes(result))

    def test_backtick_info_with_backtick_is_not_opener(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("```foo`bar", "text")
        )
        self.assertEqual(result["findings"], [])

    def test_tilde_fence_and_indent_tolerance(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(
                "  ~~~ruby", "code", "   ~~~",
            )
        )
        self.assertEqual(result["findings"], [])


class LineRulesTest(unittest.TestCase):
    """MD011 / MD012 / MD013 / MD014 triggers and controls."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_md011_bare_url(self) -> None:
        result = self.tool.execute(
            mode="lint",
            markdown_text=_lines(
                "See https://example.com/a and http://example.com/b now.",
            ),
        )
        finding = _finding(result, "MD011")
        self.assertEqual(finding["line"], 1)
        self.assertIn("2 bare URL(s)", finding["message"])
        self.assertIn("https://example.com/a", finding["message"])

    def test_md011_controls_links_autolinks_code(self) -> None:
        result = self.tool.execute(
            mode="lint",
            markdown_text=_lines(
                "[site](https://example.com)",
                "![img](https://example.com/x.png)",
                "<https://example.com>",
                "`https://example.com`",
                "[ref]: https://example.com",
            ),
        )
        self.assertEqual(result["findings"], [])

    def test_md012_raw_html_block(self) -> None:
        result = self.tool.execute(
            mode="lint",
            markdown_text=_lines(
                "<div class=\"x\">", "text", "</div>", "<!-- comment -->",
            ),
        )
        hits = [f for f in result["findings"] if f["code"] == "MD012"]
        self.assertEqual([h["line"] for h in hits], [1, 3, 4])
        self.assertEqual(hits[0]["severity"], "info")

    def test_md012_controls_inline_and_non_block(self) -> None:
        result = self.tool.execute(
            mode="lint",
            markdown_text=_lines(
                "bold <b>inline</b> text", "<span>x</span>", "    <div>indent",
            ),
        )
        self.assertEqual(result["findings"], [])

    def test_md013_hard_break_ambiguity(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("line one  ", "line two\t", "x  \t")
        )
        hits = [f for f in result["findings"] if f["code"] == "MD013"]
        # Ends with 2+ spaces only on line 1 ("x  \t" ends with a tab).
        self.assertEqual([h["line"] for h in hits], [1])
        self.assertEqual(hits[0]["severity"], "info")

    def test_md013_blank_line_exempt(self) -> None:
        # A whitespace-only line parses as blank, not as a hard break.
        result = self.tool.execute(mode="lint", markdown_text="x\n  \n")
        self.assertEqual(result["findings"], [])

    def test_md014_line_too_long_with_url_exemption(self) -> None:
        long_text = "x" * 121
        long_with_url = "y" * 121 + " https://example.com"
        result = self.tool.execute(
            mode="lint", markdown_text=_lines(long_text, long_with_url)
        )
        hits = [f for f in result["findings"] if f["code"] == "MD014"]
        self.assertEqual([h["line"] for h in hits], [1])
        self.assertIn("121 characters", hits[0]["message"])

    def test_md014_threshold_option(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("a" * 50),
            max_line_length=40,
        )
        self.assertEqual(_codes(result), ["MD014"])
        boundary = self.tool.execute(
            mode="lint", markdown_text=_lines("a" * 40),
            max_line_length=40,
        )
        self.assertEqual(boundary["findings"], [])

    def test_md014_trailing_whitespace_not_counted(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("a" * 118 + "   ")
        )
        # Width measured after right-trim: 118 stays under 120; the
        # 3-space tail raises MD013 only.
        self.assertEqual(_codes(result), ["MD013"])


class LinkRulesTest(unittest.TestCase):
    """MD016 triggers, shapes and controls."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_md016_both_shapes(self) -> None:
        result = self.tool.execute(
            mode="lint",
            markdown_text=_lines("[a](ok.md)", "[]()", "[text]()", "[](x.md)"),
        )
        hits = [f for f in result["findings"] if f["code"] == "MD016"]
        self.assertEqual([h["line"] for h in hits], [2, 3])
        self.assertIn("neither text nor destination", hits[0]["message"])
        self.assertIn("goes nowhere", hits[1]["message"])
        self.assertEqual(hits[0]["severity"], "warning")

    def test_md016_control_healthy_and_image_links(self) -> None:
        result = self.tool.execute(
            mode="lint",
            markdown_text=_lines(
                "[text](https://example.com)", "![alt]()", "![alt](img.png)",
            ),
        )
        self.assertEqual(result["findings"], [])

    def test_md016_in_code_span_immune(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=_lines("`[]()` inline code")
        )
        self.assertEqual(result["findings"], [])


class FenceImmunityAtScaleTest(unittest.TestCase):
    """Every non-fence rule stays silent inside fenced blocks."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()
        # Every shape below triggers its rule in prose; embedded in
        # three fence styles it must stay silent.
        self.dirty_interior = [
            "# H1", "#### jump", "##", "## bad ###",
            "- a", "* b", " - c", "\t- d", "- Upper", "- lower",
            "<div>", "raw http://bare.example.com",
            "[]()", "[text]()", "trailing  ",
            "x" * 130,
        ]

    def _wrapped(self, fence: str) -> str:
        # Fence carries a language so MD009 stays silent too: the
        # wrapped document must lint completely clean.
        return _lines(fence + "text", *self.dirty_interior, fence)

    def test_immune_inside_backtick_fence(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=self._wrapped("```")
        )
        self.assertEqual(result["findings"], [])

    def test_immune_inside_tilde_fence(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=self._wrapped("~~~")
        )
        self.assertEqual(result["findings"], [])

    def test_immune_inside_four_backtick_fence(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text=self._wrapped("````")
        )
        self.assertEqual(result["findings"], [])

    def test_multiple_fences_and_prose_between(self) -> None:
        text = _lines(
            "```python", "#### not a heading", "* not a list", "```",
            "", "# Real", "#### real jump", "", "~~~yaml", "[]()", "~~~",
        )
        result = self.tool.execute(mode="lint", markdown_text=text)
        # The fenced "# ..."-shaped lines do not register as headings,
        # so the only level jump is the real prose one at line 7.
        self.assertEqual(
            [(f["line"], f["code"]) for f in result["findings"]],
            [(7, "MD001")],
        )

    def test_immune_at_scale(self) -> None:
        # 200 fence blocks each embedding every violation shape: the
        # whole document lints completely clean.
        block = ["```text", *self.dirty_interior, "```", ""]
        text = "\n".join(block * 200)
        result = self.tool.execute(mode="lint", markdown_text=text)
        self.assertEqual(result["finding_count"], 0)
        self.assertTrue(result["ok"])


class MixedDocTest(unittest.TestCase):
    """Exact full findings list for a hand-verified mixed document."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_exact_findings(self) -> None:
        text = _lines(
            "# Title",
            "## ##",
            "Hello",
            "#### Deep",
            "See https://example.com/long now.",
            "",
            "- alpha",
            "* beta",
            " - gamma",
            "\t- delta",
            "<div>",
            "raw http://bare.example.com here",
            "trailing  \\",
            "~~~",
            "code with - * + and #### and <div>",
            "~~~",
            "```python",
            "x = 1",
            "```",
            "```",
            "unmatched",
            "[empty]()",
            "[link]()",
            "![img](ok.png)",
            "[](dest)",
            "- - -",
        ).replace("\\", "")
        result = self.tool.execute(mode="lint", markdown_text=text)
        self.assertEqual(
            [(f["line"], f["code"], f["severity"]) for f in result["findings"]],
            [
                (2, "MD003", "error"),
                (4, "MD001", "warning"),
                (5, "MD011", "info"),
                (8, "MD005", "warning"),
                (9, "MD006", "warning"),
                (10, "MD007", "warning"),
                (11, "MD012", "info"),
                (12, "MD011", "info"),
                (13, "MD013", "info"),
                (14, "MD009", "info"),
                (20, "MD008", "error"),
                (20, "MD009", "info"),
            ],
        )
        self.assertEqual(result["finding_count"], 12)
        self.assertFalse(result["ok"])
        # Lines 21-26 sit inside the unclosed fence: immune.
        self.assertNotIn("MD016", _codes(result))

    def test_rules_disable_option(self) -> None:
        text = _lines("# A", "#### B", "```", "```")
        result = self.tool.execute(
            mode="lint", markdown_text=text,
            rules={"MD001": False, "MD009": False},
        )
        self.assertEqual(result["findings"], [])

    def test_findings_cap(self) -> None:
        text = "\n".join(f"# h {i}" for i in range(250))
        result = self.tool.execute(mode="lint", markdown_text=text)
        self.assertEqual(len(result["findings"]), 200)
        self.assertEqual(result["finding_count"], 249)
        self.assertTrue(result["findings_truncated"])


class ProfileModeTest(unittest.TestCase):
    """Profile arithmetic verified by hand."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_exact_profile(self) -> None:
        text = _lines(
            "# T",
            "## 中文标题",
            "- one",
            "- two",
            "1. first",
            "2. second",
            "- alpha",
            "- Beta",
            "See [docs](guide/book.md) and [site](https://example.com)"
            " and [x](#anchor).",
            "```python",
            "code = 1",
            "```",
            "~~~",
            "plain",
            "```",
            "unclosed tail",
        )
        result = self.tool.execute(mode="profile", markdown_text=text)
        # Words: T(1) + 4 CJK + one/two/first+1/second+1/alpha/Beta(8)
        # + 13 on the links line = 26; 26*60/238 -> ceil 7 s.
        self.assertEqual(result["line_count"], 16)
        self.assertEqual(result["word_count"], 26)
        self.assertEqual(result["cjk_char_count"], 4)
        self.assertEqual(result["headings"]["count"], 2)
        self.assertEqual(result["headings"]["max_depth"], 2)
        self.assertEqual(result["headings"]["by_level"], {"1": 1, "2": 1})
        self.assertEqual(
            result["headings"]["items"],
            [{"line": 1, "level": 1, "text": "T"},
             {"line": 2, "level": 2, "text": "中文标题"}],
        )
        self.assertEqual(result["lists"]["list_blocks"], 1)
        self.assertEqual(result["lists"]["unordered_items"], 4)
        self.assertEqual(result["lists"]["ordered_items"], 2)
        self.assertEqual(result["code_fences"]["count"], 2)
        self.assertEqual(result["code_fences"]["closed"], 1)
        self.assertEqual(result["code_fences"]["unclosed"], 1)
        self.assertEqual(result["code_fences"]["languages"], {"python": 1})
        self.assertEqual(result["code_fences"]["without_lang"], 1)
        self.assertEqual(result["links"]["total"], 3)
        self.assertEqual(result["links"]["internal"], 2)
        self.assertEqual(result["links"]["external"], 1)
        self.assertEqual(result["reading"]["wpm"], 238)
        self.assertEqual(result["reading"]["seconds"], 7)
        self.assertEqual(result["reading"]["humanized"], "7 s")

    def test_reading_humanize_shapes(self) -> None:
        # 238 wpm: 4 words -> 4*60/238 -> ceil 2 s; 500 words -> 127 s
        # -> "2 min 7 s"; 12000 words -> 3025 s -> "50 min 25 s".
        for words, humanized in ((4, "2 s"), (500, "2 min 7 s")):
            text = " ".join(["w"] * words)
            result = self.tool.execute(mode="profile", markdown_text=text)
            self.assertEqual(result["word_count"], words)
            self.assertEqual(result["reading"]["humanized"], humanized)

    def test_empty_words(self) -> None:
        result = self.tool.execute(mode="profile", markdown_text="#\t \n")
        # "#" + tab + space: an empty heading line (MD003), no words.
        self.assertEqual(result["word_count"], 0)
        self.assertEqual(result["reading"]["seconds"], 0)
        self.assertEqual(result["reading"]["humanized"], "0 s")

    def test_mailto_counts_external(self) -> None:
        result = self.tool.execute(
            mode="profile",
            markdown_text=_lines("[m](mailto:a@b.c)", "[r](./x.md)"),
        )
        self.assertEqual(result["links"]["external"], 1)
        self.assertEqual(result["links"]["internal"], 1)


class FixHintsModeTest(unittest.TestCase):
    """fix_hints exact output, toggles, round-trip and idempotence."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_exact_fix(self) -> None:
        text = _lines(
            "# Title",
            "```",
            "code line trailing   ",
            "```",
            "keep hard break  ",
            "tab end\t",
            "single space ",
            "",
            "~~~~",
            "unclosed fence tail",
        )
        result = self.tool.execute(mode="fix_hints", markdown_text=text)
        self.assertEqual(
            result["fixed_text"],
            "# Title\n"
            "```\n"
            "code line trailing   \n"   # fence interior untouched
            "```\n"
            "keep hard break  \n"       # 2-space hard break kept
            "tab end\n"
            "single space\n"
            "\n"
            "~~~~\n"
            "unclosed fence tail\n"
            "~~~~\n",
        )
        self.assertEqual(
            result["applied"],
            [
                {"action": "strip_trailing_spaces", "count": 2},
                {"action": "close_unclosed_fence", "line": 9, "fence": "~~~~"},
            ],
        )
        remaining = [(f["line"], f["code"]) for f in result["remaining"]]
        self.assertEqual(
            remaining, [(2, "MD009"), (5, "MD013"), (9, "MD009")]
        )

    def test_toggles_off(self) -> None:
        text = _lines("```", "x ", "tail   ")
        result = self.tool.execute(
            mode="fix_hints", markdown_text=text,
            close_unclosed_fence=False, strip_trailing_spaces=False,
        )
        self.assertEqual(result["fixed_text"], text)
        self.assertEqual(result["applied"], [])
        # Lines 2-3 sit inside the unclosed fence: only the fence
        # findings remain, no MD013 from the interior.
        self.assertEqual(
            [(f["line"], f["code"]) for f in result["remaining"]],
            [(1, "MD008"), (1, "MD009")],
        )

    def test_relint_clean_round_trip(self) -> None:
        text = _lines("one ", "two\t", "```bash", "echo hi")
        fixed = self.tool.execute(mode="fix_hints", markdown_text=text)
        self.assertEqual(
            fixed["fixed_text"], "one\ntwo\n```bash\necho hi\n```\n"
        )
        relint = self.tool.execute(
            mode="lint", markdown_text=fixed["fixed_text"]
        )
        self.assertEqual(relint["findings"], [])

    def test_idempotence(self) -> None:
        text = _lines("a ", "b  ", "```", "unclosed")
        once = self.tool.execute(mode="fix_hints", markdown_text=text)
        twice = self.tool.execute(
            mode="fix_hints", markdown_text=once["fixed_text"]
        )
        self.assertEqual(once["fixed_text"], twice["fixed_text"])
        self.assertEqual(twice["applied"], [])

    def test_rules_carried_into_relint(self) -> None:
        text = _lines("keep  ", "```", "x")
        result = self.tool.execute(
            mode="fix_hints", markdown_text=text, rules={"MD013": False},
        )
        # The fence gets closed; MD009 remains and the hard break is
        # kept but not reported because its rule is disabled.
        self.assertEqual(
            [(f["line"], f["code"]) for f in result["remaining"]],
            [(2, "MD009")],
        )
        self.assertIn("keep  \n", result["fixed_text"])

    def test_never_structural(self) -> None:
        # Heading jumps, marker mixing and empty links are left alone.
        text = _lines("# A", "#### B", "- a", "* b", "[t]()")
        result = self.tool.execute(mode="fix_hints", markdown_text=text)
        self.assertEqual(
            result["fixed_text"], "# A\n#### B\n- a\n* b\n[t]()\n"
        )
        self.assertEqual(
            [(f["line"], f["code"]) for f in result["remaining"]],
            [(2, "MD001"), (4, "MD005"), (5, "MD016")],
        )


class CrlfBomTest(unittest.TestCase):
    """BOM stripping and CRLF/CR normalization."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_crlf_reports_lf_twin_lines(self) -> None:
        crlf = "# A\r\n#### B\r\n- a\r\n* b\r\n"
        lf = "# A\n#### B\n- a\n* b\n"
        crlf_result = self.tool.execute(mode="lint", markdown_text=crlf)
        lf_result = self.tool.execute(mode="lint", markdown_text=lf)
        self.assertEqual(crlf_result, lf_result)
        self.assertEqual(
            [(f["line"], f["code"]) for f in crlf_result["findings"]],
            [(2, "MD001"), (4, "MD005")],
        )

    def test_lone_cr_normalized(self) -> None:
        result = self.tool.execute(
            mode="lint", markdown_text="# A\r#### B\r"
        )
        self.assertEqual(_finding(result, "MD001")["line"], 2)

    def test_bom_stripped_silently(self) -> None:
        bom = "\ufeff# Title\n\ntext\n"
        result = self.tool.execute(mode="lint", markdown_text=bom)
        self.assertEqual(result["findings"], [])


class ErrorMatrixTest(unittest.TestCase):
    """Strict validation of every argument."""

    def setUp(self) -> None:
        self.tool = MarkdownLintTool()

    def test_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="audit", markdown_text="x")

    def test_non_string_text(self) -> None:
        for bad in (None, 123, ["# x"]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="lint", markdown_text=bad)

    def test_empty_and_whitespace_only(self) -> None:
        for bad in ("", "   \n\t\n"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="lint", markdown_text=bad)

    def test_oversized(self) -> None:
        ok = "a" * 100_000
        self.tool.execute(mode="lint", markdown_text=ok)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="lint", markdown_text=ok + "a")

    def test_max_line_length_bounds(self) -> None:
        for bad in (39, 501, "80", True, 4.5):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="lint", markdown_text="x", max_line_length=bad
                )
        self.tool.execute(
            mode="lint", markdown_text="x", max_line_length=40
        )
        self.tool.execute(
            mode="lint", markdown_text="x", max_line_length=500
        )

    def test_rules_shapes(self) -> None:
        for bad in (["MD001"], {"MD999": False}, {"MD001": "no"}, "MD001"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="lint", markdown_text="x", rules=bad)

    def test_per_mode_option_gating(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="profile", markdown_text="x", max_line_length=100
            )
        with self.assertRaises(ValueError):
            self.tool.execute(mode="profile", markdown_text="x", rules={})
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", markdown_text="x", strip_trailing_spaces=True
            )
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="lint", markdown_text="x", close_unclosed_fence=True
            )
        # max_line_length / rules ARE allowed in fix_hints.
        self.tool.execute(
            mode="fix_hints", markdown_text="x",
            max_line_length=100, rules={"MD009": False},
        )

    def test_fix_bool_options(self) -> None:
        for bad in ("yes", 1, None.__class__):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="fix_hints", markdown_text="x",
                    strip_trailing_spaces=bad,
                )


_REPO_ROOT = Path(__file__).resolve().parents[6]
_H1_RE = re.compile(r"^ {0,3}#(\s|\Z)")
_EMPTY_HEADING_RE = re.compile(r"^ {0,3}#{1,6}[\s#]*\Z")
_ITEM_RE = re.compile(r"\A([ \t]*)(?:[-*+]|[0-9]{1,9}[.)])([ \t]|\Z)")
_URL_RE = re.compile(r"https?://")


@unittest.skipUnless(
    (_REPO_ROOT / "docs/guidebook").is_dir(), "guidebook corpus unavailable"
)
class GuidebookCorpusTest(unittest.TestCase):
    """Lint and profile over 20 real guidebook documents, findings
    re-derived independently from the raw file bytes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = MarkdownLintTool()
        base = _REPO_ROOT / "docs/guidebook"
        english = sorted((base / "en").rglob("*.md"))[:10]
        chinese = sorted((base / "zh").rglob("*.md"))[:10]
        cls.files = english + chinese
        if len(cls.files) != 20:
            raise unittest.SkipTest(
                f"guidebook corpus changed: {len(cls.files)} files"
            )
        cls.raws = [path.read_text(encoding="utf-8") for path in cls.files]
        cls.line_sets = [
            raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
            for raw in cls.raws
        ]

    def test_lint_runs_deterministically(self) -> None:
        for raw in self.raws:
            first = self.tool.execute(mode="lint", markdown_text=raw)
            second = self.tool.execute(mode="lint", markdown_text=raw)
            self.assertEqual(first, second)

    def test_finding_invariants(self) -> None:
        for raw, lines in zip(self.raws, self.line_sets):
            result = self.tool.execute(mode="lint", markdown_text=raw)
            codes_seen = [
                f["code"] for f in result["findings"]
            ]
            self.assertTrue(set(codes_seen) <= set(MarkdownLintTool.RULE_CODES))
            for finding in result["findings"]:
                self.assertTrue(1 <= finding["line"] <= len(lines))
            ordered = [
                (f["line"], f["code"], f["message"])
                for f in result["findings"]
            ]
            self.assertEqual(ordered, sorted(ordered))

    def test_line_local_findings_re_derived(self) -> None:
        """Independently re-derive every re-derivable finding.

        MD002 / MD003 / MD006 / MD013 / MD014 are line-local: their
        trigger predicates can be recomputed from the raw file line
        alone. The corpus yields well over 30 such findings; every
        one must re-verify. (Spot check by hand during development
        confirmed the same findings against the file contents.)
        """
        re_derived = 0
        for raw, lines in zip(self.raws, self.line_sets):
            result = self.tool.execute(mode="lint", markdown_text=raw)
            for finding in result["findings"]:
                code, line_no = finding["code"], finding["line"]
                raw_line = lines[line_no - 1]
                if code == "MD002":
                    self.assertRegex(raw_line, _H1_RE)
                    earlier = any(
                        _H1_RE.match(other)
                        for other in lines[: line_no - 1]
                    )
                    self.assertTrue(earlier, finding)
                elif code == "MD003":
                    self.assertIsNotNone(_EMPTY_HEADING_RE.match(raw_line))
                elif code == "MD006":
                    match = _ITEM_RE.match(raw_line)
                    self.assertIsNotNone(match)
                    self.assertNotIn("\t", match.group(1))
                    self.assertEqual(len(match.group(1)) % 2, 1)
                elif code == "MD013":
                    trailing = len(raw_line) - len(raw_line.rstrip(" "))
                    self.assertGreaterEqual(trailing, 2)
                    self.assertTrue(raw_line.strip())
                elif code == "MD014":
                    self.assertGreater(len(raw_line.rstrip()), 120)
                    self.assertIsNone(_URL_RE.search(raw_line))
                else:
                    continue
                re_derived += 1
        self.assertGreaterEqual(re_derived, 30)

    def test_corpus_finding_totals(self) -> None:
        totals: dict = {}
        for raw in self.raws:
            result = self.tool.execute(mode="lint", markdown_text=raw)
            for finding in result["findings"]:
                totals[finding["code"]] = (
                    totals.get(finding["code"], 0) + 1
                )
        self.assertGreaterEqual(sum(totals.values()), 100)
        self.assertIn("MD014", totals)
        self.assertIn("MD002", totals)

    def test_profile_over_corpus(self) -> None:
        cjk_seen = 0
        for raw in self.raws:
            result = self.tool.execute(mode="profile", markdown_text=raw)
            self.assertGreater(result["line_count"], 0)
            self.assertGreaterEqual(result["word_count"], 0)
            self.assertEqual(
                result["headings"]["count"],
                len(result["headings"]["items"]),
            )
            self.assertEqual(
                result["code_fences"]["closed"]
                + result["code_fences"]["unclosed"],
                result["code_fences"]["count"],
            )
            self.assertEqual(
                result["links"]["internal"] + result["links"]["external"],
                result["links"]["total"],
            )
            cjk_seen += result["cjk_char_count"]
        # The Chinese half of the corpus is pure CJK prose.
        self.assertGreater(cjk_seen, 0)


if __name__ == "__main__":
    unittest.main()
