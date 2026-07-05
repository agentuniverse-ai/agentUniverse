# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for RenderedWebPageReader."""

import sys
import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.knowledge.reader.web.rendered_web_page_reader import RenderedWebPageReader
from agentuniverse.agent.action.knowledge.reader.reader_errors import ReaderLoadError, ReaderDependencyError
from agentuniverse.agent.action.knowledge.store.document import Document


class TestRenderedWebPageReader(unittest.TestCase):
    """Test suite for RenderedWebPageReader."""

    def setUp(self):
        self.reader = RenderedWebPageReader()

    def test_load_data_empty_url(self):
        """Should raise ReaderLoadError for empty URL."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data("")

    def test_load_data_none_url(self):
        """Should raise ReaderLoadError for None URL."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data(None)

    def test_load_data_non_string_url(self):
        """Should raise ReaderLoadError for non-string URL."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data(123)

    def _install_mock_playwright(self):
        """Create a mock playwright module in sys.modules."""
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_page.content.return_value = "<html><body><p>Hello World</p></body></html>"
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context

        mock_sync_playwright = MagicMock()
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright_instance

        mock_playwright = MagicMock()
        mock_playwright.sync_api.sync_playwright = mock_sync_playwright
        sys.modules["playwright"] = mock_playwright
        sys.modules["playwright.sync_api"] = MagicMock()
        return mock_playwright

    def _uninstall_mock_playwright(self):
        sys.modules.pop("playwright", None)
        sys.modules.pop("playwright.sync_api", None)

    @patch("agentuniverse.agent.action.knowledge.reader.web.web_page_reader.WebPageReader")
    def test_load_data_success(self, mock_wp):
        """Should successfully render and extract a web page."""
        self._install_mock_playwright()
        try:
            mock_wp_instance = MagicMock()
            mock_wp_instance._extract_main_text.return_value = ("Hello World", {"extractor": "trafilatura"})
            mock_wp.return_value = mock_wp_instance

            docs = self.reader._load_data("https://example.com")
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0].text, "Hello World")
            self.assertEqual(docs[0].metadata["source"], "web")
            self.assertTrue(docs[0].metadata["rendered"])
        finally:
            self._uninstall_mock_playwright()

    @patch("agentuniverse.agent.action.knowledge.reader.web.web_page_reader.WebPageReader")
    def test_load_data_with_ext_info(self, mock_wp):
        """Should include ext_info in document metadata."""
        self._install_mock_playwright()
        try:
            mock_wp_instance = MagicMock()
            mock_wp_instance._extract_main_text.return_value = ("Test", {})
            mock_wp.return_value = mock_wp_instance

            docs = self.reader._load_data("https://example.com", ext_info={"custom": "value"})
            self.assertEqual(docs[0].metadata["custom"], "value")
        finally:
            self._uninstall_mock_playwright()

    def test_render_and_get_html_missing_playwright(self):
        """Should raise ReaderDependencyError when playwright is not installed."""
        saved = sys.modules.get("playwright")
        sys.modules["playwright"] = None
        try:
            with self.assertRaises(ReaderDependencyError) as ctx:
                self.reader._render_and_get_html("https://example.com")
            self.assertEqual(ctx.exception.dependency, "playwright")
        finally:
            if saved is None:
                sys.modules.pop("playwright", None)
            else:
                sys.modules["playwright"] = saved

    def test_inherits_from_reader(self):
        """Should inherit from Reader base class."""
        from agentuniverse.agent.action.knowledge.reader.reader import Reader
        self.assertIsInstance(self.reader, Reader)


if __name__ == "__main__":
    unittest.main()
