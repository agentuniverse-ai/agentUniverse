# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/06
# @FileName: test_markdown_beautify_tool.py

import os
import unittest

from agentuniverse.agent.action.tool.common_tool import markdown_beautify_tool as md_module
from agentuniverse.agent.action.tool.common_tool.markdown_beautify_tool import MarkdownBeautifyTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(md_module.__file__), "markdown_beautify_tool.yaml")


class MarkdownBeautifyToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = MarkdownBeautifyTool()

    def run_tool(self, **kwargs):
        return self.tool.execute(**kwargs)

    # ========== Validation ==========

    def test_invalid_mode_and_inputs(self):
        """Unknown modes, bad markers/delimiters/shifts and oversized or
        non-string input return structured validation errors."""
        cases = [
            dict(mode="unknown", markdown="x"),
            dict(mode="beautify", markdown=123),
            dict(mode="fix_lists", markdown="x", list_marker="=>"),
            dict(mode="fix_lists", markdown="x", ordered_delimiter="!"),
            dict(mode="normalize_headings", markdown="x", heading_shift=9),
            dict(mode="normalize_headings", markdown="x", heading_shift="1"),
        ]
        for kwargs in cases:
            result = self.run_tool(**kwargs)
            self.assertEqual(result["status"], "error", msg=kwargs)
            self.assertEqual(result["error_type"], "validation_error")

    def test_input_size_limit(self):
        """Input longer than max_input_chars is rejected."""
        tool = MarkdownBeautifyTool(max_input_chars=10)
        result = tool.execute(mode="beautify", markdown="a" * 11)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_chars", result["error"])

    def test_yaml_definition_loads(self):
        """The shipped yaml registers a TOOL pointing at this class and the
        manager instantiates it with the declared input keys."""
        config = Configer(path=os.path.abspath(YAML_PATH)).load()
        component = ComponentConfiger().load_by_configer(config)
        self.assertEqual(component.get_component_config_type(),
                         ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "MarkdownBeautifyTool")

        configer = ToolConfiger().load_by_configer(config)
        try:
            previous = ApplicationConfigManager().app_configer
        except ValueError:
            previous = None
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        try:
            tool = ToolManager().get_instance_obj(configer.name)
            self.assertIsInstance(tool, MarkdownBeautifyTool)
            self.assertEqual(tool.input_keys, ["mode", "markdown"])
        finally:
            ApplicationConfigManager().app_configer = previous

    # ========== beautify ==========

    def test_beautify_full_pipeline(self):
        """One messy document comes out with normalized headings, unified
        list markers, renumbered ordered lists, an aligned table, backtick
        fences and canonical blank lines — while code is untouched.
        Blank-line spacing is only forced around headings and code fences;
        lists and tables keep flowing inline where valid."""
        source = (
            "#  Title ##\n"
            "intro text\n"
            "* item one\n"
            "+ item two\n"
            "3. third\n"
            "9. ninth\n"
            "A|B\n"
            "--|--\n"
            "x | y\n"
            "~~~js\n"
            "var a = 1\n"
            "~~~\n"
        )
        result = self.run_tool(mode="beautify", markdown=source)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["changed"])
        self.assertEqual(
            result["markdown"],
            "# Title\n"
            "\n"
            "intro text\n"
            "- item one\n"
            "- item two\n"
            "1. third\n"
            "2. ninth\n"
            "| A   | B   |\n"
            "| --- | --- |\n"
            "| x   | y   |\n"
            "\n"
            "```js\n"
            "var a = 1\n"
            "```\n"
        )

    def test_beautify_protects_code_content(self):
        """Markup inside fenced blocks and inline code is preserved as-is."""
        source = "text `* not a list` more\n\n```md\n#   not heading\n*  raw\n```\n"
        result = self.run_tool(mode="beautify", markdown=source)
        self.assertIn("`* not a list`", result["markdown"])
        self.assertIn("#   not heading\n*  raw", result["markdown"])
        self.assertNotIn("-  raw", result["markdown"])

    def test_beautify_normalizes_blank_lines(self):
        """Runs of blank lines collapse, leading blanks vanish and the output
        ends with exactly one newline."""
        source = "\n\n# Head\n\n\n\nbody line\n\n\n"
        result = self.run_tool(mode="beautify", markdown=source)
        self.assertEqual(result["markdown"], "# Head\n\nbody line\n")

    # ========== normalize_headings ==========

    def test_normalize_headings_converts_setext(self):
        """Setext underlines become ATX headings."""
        source = "Title One\n=========\n\nTitle Two\n---------\n"
        result = self.run_tool(mode="normalize_headings", markdown=source)
        self.assertEqual(result["markdown"], "# Title One\n\n## Title Two\n")

    def test_normalize_headings_shifts_and_clamps(self):
        """heading_shift demotes/promotes and is clamped to levels 1-6."""
        source = "## H2\n#### H4\n"
        demoted = self.run_tool(mode="normalize_headings", markdown=source,
                                heading_shift=1)
        self.assertEqual(demoted["markdown"], "### H2\n##### H4\n")
        promoted = self.run_tool(mode="normalize_headings", markdown=source,
                                 heading_shift=-1)
        self.assertEqual(promoted["markdown"], "# H2\n### H4\n")
        clamped = self.run_tool(mode="normalize_headings", markdown=source,
                                heading_shift=5)
        self.assertEqual(clamped["markdown"], "###### H2\n###### H4\n")

    def test_normalize_headings_repairs_level_gaps(self):
        """A document jumping to a deep heading without parents is flattened
        to a gap-free hierarchy in the beautify path."""
        source = "# H1\n\n#### Deep\n\n#### Deep2\n"
        result = self.run_tool(mode="beautify", markdown=source)
        self.assertEqual(result["markdown"],
                         "# H1\n\n## Deep\n\n## Deep2\n")
        # The dedicated mode keeps levels as written (shift only).
        keep = self.run_tool(mode="normalize_headings", markdown=source)
        self.assertEqual(keep["markdown"], source)

    # ========== fix_lists ==========

    def test_fix_lists_unifies_markers(self):
        """Mixed unordered markers become the configured one, indent kept."""
        source = "* one\n  + two\n- three\n"
        result = self.run_tool(mode="fix_lists", markdown=source)
        self.assertEqual(result["markdown"],
                         "- one\n  - two\n- three\n")
        star = self.run_tool(mode="fix_lists", markdown=source,
                             list_marker="*")
        self.assertEqual(star["markdown"], "* one\n  * two\n* three\n")

    def test_fix_lists_renumbers_and_delimiter(self):
        """Ordered lists renumber from 1 per contiguous list, restart after
        an interruption, and honor a ')' delimiter; loose lists keep
        counting across blank lines."""
        source = (
            "3. a\n"
            "7. b\n"
            "\n"
            "8. continues\n"
            "\n"
            "paragraph\n"
            "\n"
            "4. restarts\n"
        )
        result = self.run_tool(mode="fix_lists", markdown=source)
        self.assertEqual(
            result["markdown"],
            "1. a\n2. b\n\n3. continues\n\nparagraph\n\n1. restarts\n")
        paren = self.run_tool(mode="fix_lists", markdown="2) x\n3) y\n",
                              ordered_delimiter=")")
        self.assertEqual(paren["markdown"], "1) x\n2) y\n")

    def test_fix_lists_renumber_disabled(self):
        """With renumber_ordered=False original numbers are kept."""
        source = "3. a\n7. b\n"
        result = self.run_tool(mode="fix_lists", markdown=source,
                               renumber_ordered=False)
        self.assertEqual(result["markdown"], "3. a\n7. b\n")

    # ========== fix_tables ==========

    def test_fix_tables_aligns_columns(self):
        """Cells are padded to column width (min 3) and rows rebuilt
        uniformly."""
        source = "Name|Value\n---|---\na|1\nlonger|22\n"
        result = self.run_tool(mode="fix_tables", markdown=source)
        self.assertEqual(
            result["markdown"],
            "| Name   | Value |\n"
            "| ------ | ----- |\n"
            "| a      | 1     |\n"
            "| longer | 22    |\n")

    def test_fix_tables_keeps_alignment_and_pads_rows(self):
        """Column alignment survives and short/long rows are padded or
        truncated to the header width; escaped pipes stay intact."""
        source = "| A | B | C |\n| --- | :---: | ---: |\n| 1 |\n| 1 | 2 | 3 | 4 |\n"
        result = self.run_tool(mode="fix_tables", markdown=source)
        lines = result["markdown"].split("\n")
        self.assertEqual(lines[0], "| A   |  B  |   C |")
        self.assertEqual(lines[1], "| --- | :-: | --: |")
        self.assertEqual(lines[2], "| 1   |     |     |")
        self.assertEqual(lines[3], "| 1   |  2  |   3 |")
        escaped = self.run_tool(mode="fix_tables",
                                markdown="| a\\|b |\n| --- |\n| c |\n")
        self.assertIn("a\\|b", escaped["markdown"])

    def test_fix_tables_ignores_prose_with_pipes(self):
        """Lines containing pipes without a separator row are left alone."""
        source = "either | or\nplain paragraph\n"
        result = self.run_tool(mode="fix_tables", markdown=source)
        self.assertEqual(result["markdown"], source)

    # ========== stats ==========

    def test_stats_counts_structure(self):
        """Headings (ATX and setext), lists, tables, code, links, images,
        quotes and words are all counted, code excluded from structure."""
        source = (
            "# Title\n"
            "para one\n"
            "## Section\n"
            "Setext\n"
            "======\n"
            "* bullet\n"
            "1. first\n"
            "2. second\n"
            "| A | B |\n"
            "| - | - |\n"
            "| 1 | 2 |\n"
            "```python\n"
            "# not a heading\n"
            "```\n"
            "see [link](http://x) and ![img](http://y) and `code`\n"
            "> quoted line\n"
        )
        stats = self.run_tool(mode="stats", markdown=source)["stats"]
        self.assertEqual(stats["headings"]["h1"], 2)
        self.assertEqual(stats["headings"]["h2"], 1)
        self.assertEqual(stats["heading_total"], 3)
        self.assertEqual(stats["list_items"]["unordered"], 1)
        self.assertEqual(stats["list_items"]["ordered"], 2)
        self.assertEqual(stats["tables"], 1)
        self.assertEqual(stats["code_blocks"]["fenced"], 1)
        self.assertEqual(stats["code_blocks"]["inline"], 1)
        self.assertEqual(stats["code_blocks"]["languages"], ["python"])
        self.assertEqual(stats["links"], 1)
        self.assertEqual(stats["images"], 1)
        self.assertEqual(stats["blockquote_lines"], 1)

    def test_stats_empty_and_changed_flag(self):
        """Empty input produces empty output with success; an already-clean
        document reports changed=False."""
        empty = self.run_tool(mode="beautify", markdown="")
        self.assertEqual(empty["status"], "success")
        self.assertEqual(empty["markdown"], "")
        clean = self.run_tool(mode="beautify", markdown="# H\n\ntext\n")
        self.assertFalse(clean["changed"])

    def test_crlf_normalized_and_beautify_idempotent(self):
        """Windows line endings are normalized and a second beautify pass
        changes nothing (the transform is idempotent)."""
        source = "#  Head\r\n\r\ntext\r\n"
        first = self.run_tool(mode="beautify", markdown=source)
        self.assertEqual(first["markdown"], "# Head\n\ntext\n")
        second = self.run_tool(mode="beautify", markdown=first["markdown"])
        self.assertEqual(second["markdown"], first["markdown"])
        self.assertFalse(second["changed"])


if __name__ == "__main__":
    unittest.main()
