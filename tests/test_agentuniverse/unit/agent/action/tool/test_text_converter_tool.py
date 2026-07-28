#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for TextConverterTool."""

import unittest

from agentuniverse.agent.action.tool.common_tool.text_converter_tool \
    import TextConverterTool


class TestMarkdownToHTML(unittest.TestCase):

    def test_heading(self):
        tool = TextConverterTool()
        result = tool.execute(mode="markdown_to_html", text="# Title")
        self.assertIn("<h1>Title</h1>", result["converted"])

    def test_bold_and_italic(self):
        tool = TextConverterTool()
        result = tool.execute(mode="markdown_to_html",
                               text="**bold** and *italic*")
        self.assertIn("<strong>bold</strong>", result["converted"])
        self.assertIn("<em>italic</em>", result["converted"])

    def test_code_block(self):
        tool = TextConverterTool()
        result = tool.execute(mode="markdown_to_html",
                               text="```python\nprint(1)\n```")
        self.assertIn("<pre><code>", result["converted"])
        self.assertIn("print(1)", result["converted"])

    def test_unordered_list(self):
        tool = TextConverterTool()
        result = tool.execute(mode="markdown_to_html",
                               text="- Item 1\n- Item 2")
        self.assertIn("<ul>", result["converted"])
        self.assertIn("<li>Item 1</li>", result["converted"])

    def test_link(self):
        tool = TextConverterTool()
        result = tool.execute(mode="markdown_to_html",
                               text="[Click](https://example.com)")
        self.assertIn('<a href="https://example.com">Click</a>',
                      result["converted"])


class TestHTMLToText(unittest.TestCase):

    def test_basic_extraction(self):
        tool = TextConverterTool()
        result = tool.execute(mode="html_to_text",
                               text="<p>Hello <strong>World</strong></p>")
        self.assertIn("Hello", result["converted"])
        self.assertIn("World", result["converted"])
        self.assertNotIn("<", result["converted"])

    def test_skips_script_and_style(self):
        tool = TextConverterTool()
        result = tool.execute(mode="html_to_text",
                               text="<script>alert(1)</script>"
                                    "<style>a{}</style>"
                                    "<p>visible</p>")
        self.assertNotIn("alert", result["converted"])
        self.assertIn("visible", result["converted"])


class TestMarkdownToText(unittest.TestCase):

    def test_strips_all_markup(self):
        tool = TextConverterTool()
        result = tool.execute(mode="markdown_to_text",
                               text="# Title\n\n**bold** text")
        self.assertNotIn("#", result["converted"])
        self.assertNotIn("*", result["converted"])
        self.assertIn("Title", result["converted"])
        self.assertIn("bold", result["converted"])


class TestValidation(unittest.TestCase):

    def test_empty_text(self):
        tool = TextConverterTool()
        result = tool.execute(mode="markdown_to_html", text="")
        self.assertEqual(result["status"], "error")

    def test_unknown_mode(self):
        tool = TextConverterTool()
        result = tool.execute(mode="invalid", text="x")
        self.assertEqual(result["status"], "error")

    def test_max_input_chars(self):
        tool = TextConverterTool(max_input_chars=10)
        result = tool.execute(mode="markdown_to_html",
                               text="x" * 100)
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
