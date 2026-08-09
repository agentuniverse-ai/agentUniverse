#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for four tool/reader bug fixes.

1. LangChainTool.init_langchain_tool None.get crash on missing config.
2. CodeReader hardcoded utf-8 encoding.
3. GoogleSearchTool missing API key produces cryptic langchain error.
4. ArxivTool temp file leak + no size cap + corrupt PDF crash.
"""

import unittest
from unittest.mock import MagicMock, patch


class TestLangChainToolNoneGuard(unittest.TestCase):

    def test_missing_langchain_config_raises_clear_error(self):
        from agentuniverse.agent.action.tool.common_tool.langchain_tool \
            import LangChainTool
        tool = LangChainTool()
        configer = MagicMock()
        configer.configer.value = {}  # no 'langchain' key
        with self.assertRaises(ValueError) as ctx:
            tool.init_langchain_tool(configer)
        self.assertIn("langchain", str(ctx.exception).lower())


class TestCodeReaderEncoding(unittest.TestCase):

    def test_source_uses_detect_file_encoding(self):
        import inspect
        from agentuniverse.agent.action.knowledge.reader.file.code_reader \
            import CodeReader
        src = inspect.getsource(CodeReader._load_data)
        self.assertIn("detect_file_encoding", src,
                      "CodeReader must use detect_file_encoding, not hardcoded utf-8")
        self.assertNotIn('encoding="utf-8"', src)


class TestGoogleSearchToolAPIKeyGuard(unittest.TestCase):

    def test_missing_api_key_raises_clear_error(self):
        from agentuniverse.agent.action.tool.common_tool.google_search_tool \
            import GoogleSearchTool
        tool = GoogleSearchTool()
        tool.serper_api_key = None
        with self.assertRaises(ValueError) as ctx:
            tool.execute("test query")
        self.assertIn("SERPER_API_KEY", str(ctx.exception))

    def test_present_api_key_proceeds_to_search(self):
        from agentuniverse.agent.action.tool.common_tool.google_search_tool \
            import GoogleSearchTool
        tool = GoogleSearchTool()
        tool.serper_api_key = "fake-key"
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "google_search_tool.GoogleSerperAPIWrapper") as wrapper_cls:
            wrapper = MagicMock()
            wrapper.run.return_value = "search results"
            wrapper_cls.return_value = wrapper
            result = tool.execute("test query")
        self.assertEqual(result, "search results")


class TestArxivToolTempFileAndSizeGuard(unittest.TestCase):

    def test_source_uses_tempfile_not_fixed_filename(self):
        import inspect
        from agentuniverse.agent.action.tool.common_tool.arxiv_tool \
            import ArxivTool
        src = inspect.getsource(ArxivTool.retrieve_full_paper_text)
        self.assertIn("tempfile", src,
                      "ArxivTool must use tempfile, not a fixed CWD filename")
        self.assertNotIn('"downloaded-paper.pdf"', src)

    def test_source_has_finally_cleanup(self):
        import inspect
        from agentuniverse.agent.action.tool.common_tool.arxiv_tool \
            import ArxivTool
        src = inspect.getsource(ArxivTool.retrieve_full_paper_text)
        self.assertIn("finally:", src,
                      "ArxivTool must clean up the temp file in a finally block")

    def test_source_checks_max_pdf_size(self):
        import inspect
        from agentuniverse.agent.action.tool.common_tool.arxiv_tool \
            import ArxivTool
        src = inspect.getsource(ArxivTool.retrieve_full_paper_text)
        self.assertIn("max_pdf_size_bytes", src,
                      "ArxivTool must check PDF size against max_pdf_size_bytes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
