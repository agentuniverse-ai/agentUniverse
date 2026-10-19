#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_markdown_toc_tool.py

"""Offline unit tests for MarkdownTocTool.

The tool is built purely on the standard library (``re`` and line
scanning) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic and pinned to ground truths:

* heading slugs follow the pinned github-slugger examples
  (``"Heading with spaces"`` -> ``heading-with-spaces``,
  ``"C++ & C#"`` -> ``c--c``, duplicates -> ``-1`` / ``-2``, CJK kept
  verbatim, underscores kept, punctuation stripped);
* generated TOCs are compared against literal expected documents
  (indentation by level, in-place replacement, append semantics);
* fenced-code immunity, level filtering, anchors/check modes and the
  validation error matrix are each covered by exact expectations.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import MarkdownTocTool
from agentuniverse.agent.action.tool.common_tool.markdown_toc_tool import (
    MarkdownTocTool as DirectMarkdownTocTool,
)

# --------------------------------------------------------------------- #
# Ground-truth documents
# --------------------------------------------------------------------- #

DOC = (
    "# Project Title\n"
    "\n"
    "## Getting Started\n"
    "\n"
    "Intro text.\n"
    "\n"
    "### Install\n"
    "\n"
    "Run `pip install`.\n"
    "\n"
    "### Usage\n"
    "\n"
    "See the [guide](#guide) below.\n"
    "\n"
    "## Getting Started\n"
    "\n"
    "Duplicate heading.\n"
)

TOC_DEFAULT = (
    "- [Getting Started](#getting-started)\n"
    "  - [Install](#install)\n"
    "  - [Usage](#usage)\n"
    "- [Getting Started](#getting-started-1)"
)

DOC_APPENDED = (
    DOC.rstrip("\n") + "\n\n" + TOC_DEFAULT + "\n"
)

DOC_WITH_TOC = (
    "# Title\n"
    "\n"
    "- [Old](#old)\n"
    "  * [Sub](#sub)\n"
    "\n"
    "## Alpha\n"
    "\n"
    "### Beta\n"
    "\n"
    "Body.\n"
)

DOC_WITH_TOC_REPLACED = (
    "# Title\n"
    "\n"
    "- [Alpha](#alpha)\n"
    "  - [Beta](#beta)\n"
    "\n"
    "## Alpha\n"
    "\n"
    "### Beta\n"
    "\n"
    "Body.\n"
)

DOC_FENCED = (
    "## Real\n"
    "\n"
    "```markdown\n"
    "## Fake\n"
    "\n"
    "* [Ghost](#ghost)\n"
    "```\n"
    "\n"
    "### Nested\n"
    "\n"
    "~~~\n"
    "## Tilde Fake\n"
    "~~~\n"
    "\n"
    "Done.\n"
)

DOC_FENCED_APPENDED = (
    DOC_FENCED.rstrip("\n") + "\n\n"
    "- [Real](#real)\n"
    "  - [Nested](#nested)\n"
)

SLUG_DOC = (
    "## C++ & C#\n"
    "## 中文 标题\n"
    "## Hello, World! (v2) — 2026\n"
    "## snake_case_name\n"
    "## dup\n"
    "## dup\n"
    "## dup\n"
    "## [Foo](https://example.com)\n"
    "## Heading with spaces\n"
)

CHECK_DOC = (
    "## Setup\n"
    "\n"
    "See [setup](#setup), [missing](#nope) and [c++](#c--c).\n"
    "Inline `[code](#ignored)` spans are skipped.\n"
    "\n"
    "```markdown\n"
    "[fenced](#also-ignored)\n"
    "```\n"
    "\n"
    "## C++ & C#\n"
)


class MarkdownTocToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib MarkdownTocTool."""

    def setUp(self) -> None:
        self.tool = MarkdownTocTool()

    # ------------------------------------------------------------------ #
    # generate mode
    # ------------------------------------------------------------------ #

    def test_generate_appends_when_no_toc_exists(self) -> None:
        result = self.tool.execute(mode="generate", markdown=DOC)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "generate")
        self.assertEqual(result["action"], "appended")
        self.assertFalse(result["existing_toc_found"])
        self.assertTrue(result["changed"])
        self.assertEqual(result["entries"], 4)
        self.assertEqual(result["toc"], TOC_DEFAULT)
        self.assertEqual(result["markdown"], DOC_APPENDED)
        self.assertEqual(result["min_level"], 2)
        self.assertEqual(result["max_level"], 3)

    def test_generate_replaces_existing_toc_in_place(self) -> None:
        result = self.tool.execute(mode="generate", markdown=DOC_WITH_TOC)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "replaced")
        self.assertTrue(result["existing_toc_found"])
        self.assertTrue(result["changed"])
        # The fresh TOC occupies exactly the old block's position.
        self.assertEqual(result["markdown"], DOC_WITH_TOC_REPLACED)
        self.assertEqual(
            result["markdown"].split("\n")[:4],
            ["# Title", "", "- [Alpha](#alpha)", "  - [Beta](#beta)"],
        )

    def test_generate_is_idempotent(self) -> None:
        first = self.tool.execute(mode="generate", markdown=DOC_WITH_TOC)
        second = self.tool.execute(mode="generate", markdown=first["markdown"])
        self.assertEqual(second["action"], "unchanged")
        self.assertFalse(second["changed"])
        self.assertTrue(second["existing_toc_found"])
        self.assertEqual(second["markdown"], first["markdown"])

    def test_generate_appends_when_replace_false(self) -> None:
        result = self.tool.execute(
            mode="generate", markdown=DOC_WITH_TOC, replace=False
        )
        self.assertEqual(result["action"], "appended")
        self.assertTrue(result["existing_toc_found"])
        # Old TOC untouched, new TOC appended at the end.
        self.assertIn("- [Old](#old)\n  * [Sub](#sub)", result["markdown"])
        self.assertTrue(result["markdown"].endswith("\n\n- [Alpha](#alpha)\n  - [Beta](#beta)\n"))

    def test_generate_level_bounds_filter_headings(self) -> None:
        doc = "# H1\n## H2\n### H3\n#### H4\n"
        full = self.tool.execute(
            mode="generate", markdown=doc, min_level=1, max_level=6
        )
        self.assertEqual(
            full["toc"],
            "- [H1](#h1)\n  - [H2](#h2)\n    - [H3](#h3)\n      - [H4](#h4)",
        )
        from_two = self.tool.execute(
            mode="generate", markdown=doc, min_level=2, max_level=6
        )
        self.assertEqual(
            from_two["toc"],
            "- [H2](#h2)\n  - [H3](#h3)\n    - [H4](#h4)",
        )
        only_two = self.tool.execute(
            mode="generate", markdown=doc, min_level=2, max_level=2
        )
        self.assertEqual(only_two["toc"], "- [H2](#h2)")

    def test_generate_duplicate_slugs_count_across_filtered_levels(self) -> None:
        # The h1 "Guide" occupies the slug before the h2 with the same
        # text — GitHub numbers anchors in document order over all
        # headings, even ones a level filter drops.
        doc = "# Guide\n\n## Guide\n\nBody.\n"
        result = self.tool.execute(mode="generate", markdown=doc)
        self.assertEqual(result["toc"], "- [Guide](#guide-1)")

    def test_generate_fenced_code_is_immune(self) -> None:
        result = self.tool.execute(mode="generate", markdown=DOC_FENCED)
        self.assertEqual(result["action"], "appended")
        self.assertEqual(result["entries"], 2)
        self.assertEqual(result["markdown"], DOC_FENCED_APPENDED)
        anchors = self.tool.execute(mode="anchors", markdown=DOC_FENCED)
        self.assertEqual(
            [h["slug"] for h in anchors["headings"]], ["real", "nested"]
        )

    def test_generate_bullet_block_with_non_anchor_item_is_not_a_toc(self) -> None:
        doc = "- [A](#a)\n- plain bullet\n\n## A\n"
        result = self.tool.execute(mode="generate", markdown=doc)
        self.assertEqual(result["action"], "appended")
        self.assertFalse(result["existing_toc_found"])
        # The ordinary bullet list is left untouched.
        self.assertIn("- [A](#a)\n- plain bullet\n\n", result["markdown"])

    def test_generate_escapes_brackets_in_entry_text(self) -> None:
        doc = "## [Brackets] everywhere\n"
        result = self.tool.execute(mode="generate", markdown=doc)
        self.assertEqual(
            result["toc"], "- [\\[Brackets\\] everywhere](#brackets-everywhere)"
        )

    def test_generate_no_headings_returns_structured_error(self) -> None:
        result = self.tool.execute(mode="generate", markdown="just text\n")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "no_headings_in_range")
        self.assertIn("[2, 3]", result["error"])

    def test_generate_headings_outside_range_returns_structured_error(self) -> None:
        result = self.tool.execute(mode="generate", markdown="# only h1\n")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "no_headings_in_range")
        widened = self.tool.execute(
            mode="generate", markdown="# only h1\n", min_level=1
        )
        self.assertEqual(widened["status"], "success")
        self.assertEqual(widened["toc"], "- [only h1](#only-h1)")

    # ------------------------------------------------------------------ #
    # anchors mode (slug rules pinned to github-slugger examples)
    # ------------------------------------------------------------------ #

    def test_anchors_pinned_slug_examples(self) -> None:
        result = self.tool.execute(mode="anchors", markdown=SLUG_DOC)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "anchors")
        self.assertEqual(result["count"], 9)
        self.assertEqual(
            [h["slug"] for h in result["headings"]],
            [
                "c--c",                       # C++ & C#
                "中文-标题",                    # CJK kept verbatim, space -> hyphen
                "hello-world-v2--2026",       # punctuation stripped, em dash gone
                "snake_case_name",            # underscores survive
                "dup",
                "dup-1",                      # second occurrence
                "dup-2",                      # third occurrence
                "foo",                        # link text used for the slug
                "heading-with-spaces",        # spaces -> hyphens
            ],
        )

    def test_anchors_reports_duplicate_suffix_evidence(self) -> None:
        result = self.tool.execute(mode="anchors", markdown=SLUG_DOC)
        first = result["headings"][4]
        self.assertEqual(first["text"], "dup")
        self.assertEqual(first["slug"], "dup")
        self.assertEqual(first["occurrence"], 1)
        self.assertFalse(first["duplicate_suffix"])
        self.assertEqual(first["line"], 5)
        second = result["headings"][5]
        self.assertEqual(second["slug"], "dup-1")
        self.assertEqual(second["occurrence"], 2)
        self.assertTrue(second["duplicate_suffix"])
        self.assertEqual(second["line"], 6)
        third = result["headings"][6]
        self.assertEqual(third["slug"], "dup-2")
        self.assertEqual(third["occurrence"], 3)
        self.assertTrue(third["duplicate_suffix"])

    def test_anchors_keeps_link_text_verbatim_but_slugs_it_unwrapped(self) -> None:
        result = self.tool.execute(mode="anchors", markdown=SLUG_DOC)
        linked = result["headings"][7]
        self.assertEqual(linked["text"], "[Foo](https://example.com)")
        self.assertEqual(linked["slug"], "foo")

    def test_anchors_reports_levels_and_lines(self) -> None:
        result = self.tool.execute(mode="anchors", markdown=DOC)
        self.assertEqual(
            [(h["level"], h["line"]) for h in result["headings"]],
            [(1, 1), (2, 3), (3, 7), (3, 11), (2, 15)],
        )

    def test_anchors_lists_all_headings_regardless_of_level_options(self) -> None:
        result = self.tool.execute(
            mode="anchors", markdown="# H1\n## H2\n", min_level=2, max_level=3
        )
        self.assertEqual(result["count"], 2)

    def test_anchors_empty_document(self) -> None:
        result = self.tool.execute(mode="anchors", markdown="")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["headings"], [])

    def test_anchors_strips_closing_hash_sequence(self) -> None:
        result = self.tool.execute(mode="anchors", markdown="## Foo ###\n")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["headings"][0]["text"], "Foo")
        self.assertEqual(result["headings"][0]["slug"], "foo")

    # ------------------------------------------------------------------ #
    # check mode
    # ------------------------------------------------------------------ #

    def test_check_reports_broken_local_links(self) -> None:
        result = self.tool.execute(mode="check", markdown=CHECK_DOC)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "check")
        self.assertEqual(result["links_checked"], 3)
        self.assertFalse(result["ok"])
        self.assertEqual(result["broken_count"], 1)
        self.assertEqual(
            result["broken_links"],
            [{"text": "missing", "anchor": "#nope", "line": 3}],
        )

    def test_check_ok_document(self) -> None:
        doc = "## A\n\n[a](#a) and [a again](#a)\n"
        result = self.tool.execute(mode="check", markdown=doc)
        self.assertTrue(result["ok"])
        self.assertEqual(result["broken_links"], [])
        self.assertEqual(result["links_checked"], 2)

    def test_check_matches_are_case_sensitive(self) -> None:
        doc = "## Setup\n\nSee [setup](#Setup).\n"
        result = self.tool.execute(mode="check", markdown=doc)
        self.assertFalse(result["ok"])
        self.assertEqual(result["broken_links"][0]["anchor"], "#Setup")

    def test_check_flags_stale_toc_entries(self) -> None:
        result = self.tool.execute(mode="check", markdown=DOC_WITH_TOC)
        self.assertFalse(result["ok"])
        self.assertEqual(
            [(b["anchor"], b["line"]) for b in result["broken_links"]],
            [("#old", 3), ("#sub", 4)],
        )

    def test_check_no_links_is_ok(self) -> None:
        result = self.tool.execute(mode="check", markdown="plain text\n")
        self.assertTrue(result["ok"])
        self.assertEqual(result["links_checked"], 0)

    def test_check_resolves_duplicate_suffix_anchors(self) -> None:
        doc = "# Guide\n\n## Guide\n\n[second](#guide-1) works.\n"
        result = self.tool.execute(mode="check", markdown=doc)
        self.assertTrue(result["ok"])

    # ------------------------------------------------------------------ #
    # Validation error matrix (strict, before any computation)
    # ------------------------------------------------------------------ #

    def test_invalid_mode_rejected(self) -> None:
        for mode in ("tocify", "", None, 123, True):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, markdown="## A\n")

    def test_non_string_markdown_rejected(self) -> None:
        for markdown in (None, 123, True, ["## A"]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="generate", markdown=markdown)

    def test_invalid_levels_rejected(self) -> None:
        bad_levels = (0, 7, -1, True, 2.5, "abc", "seven")
        for level in bad_levels:
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="generate", markdown="## A\n", min_level=level
                )
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="generate", markdown="## A\n", max_level=level
                )

    def test_min_level_above_max_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="generate", markdown="## A\n", min_level=4, max_level=2
            )

    def test_digit_string_levels_accepted(self) -> None:
        result = self.tool.execute(
            mode="generate", markdown="## A\n", min_level="2", max_level="3"
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["min_level"], 2)
        self.assertEqual(result["max_level"], 3)

    def test_non_boolean_replace_rejected(self) -> None:
        for replace in ("yes", 1, None.__class__, []):
            with self.assertRaises(ValueError):
                self.tool.execute(
                    mode="generate", markdown="## A\n", replace=replace
                )

    def test_oversized_markdown_rejected(self) -> None:
        huge = "## a\n" + "x" * 1_000_000
        with self.assertRaises(ValueError):
            self.tool.execute(mode="generate", markdown=huge)

    def test_levels_validated_even_when_unused(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="check", markdown="## A\n", min_level=9)

    # ------------------------------------------------------------------ #
    # Direct import / registration
    # ------------------------------------------------------------------ #

    def test_direct_module_import(self) -> None:
        self.assertIs(DirectMarkdownTocTool, MarkdownTocTool)

    def test_tool_metadata(self) -> None:
        self.assertEqual(self.tool.name, "markdown_toc_tool")
        self.assertIn("table-of-contents", self.tool.description)
        self.assertEqual(
            MarkdownTocTool.MODES, ("generate", "anchors", "check")
        )


if __name__ == "__main__":
    unittest.main()
