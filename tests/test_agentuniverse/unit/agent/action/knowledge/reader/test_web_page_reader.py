# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for WebPageReader with mocked HTTP and extraction.

After the refactor, WebPageReader uses lazy imports (import inside method bodies)
instead of module-level imports.  Therefore tests cannot patch module-level
attributes like ``web_page_reader.httpx`` — they no longer exist.  Instead we
patch ``sys.modules`` so that ``import httpx`` / ``import requests`` / etc.
resolve to our mocks (or to ``None`` to simulate a missing package).
"""

import sys
import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader
from agentuniverse.agent.action.knowledge.reader.reader_errors import ReaderLoadError, ReaderDependencyError
from agentuniverse.agent.action.knowledge.store.document import Document


class TestWebPageReader(unittest.TestCase):

    def setUp(self):
        self.reader = WebPageReader()

    def test_load_data_requires_url(self):
        """_load_data with empty url should raise ReaderLoadError."""
        with self.assertRaises(ReaderLoadError) as ctx:
            self.reader._load_data(url="")
        self.assertEqual(ctx.exception.reader_name, "WebPageReader")

    def test_load_data_with_none_url(self):
        """_load_data with None url should raise ReaderLoadError."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data(url=None)

    @patch.object(WebPageReader, '_extract_main_text')
    @patch.object(WebPageReader, '_fetch_html')
    def test_load_data_success(self, mock_fetch, mock_extract):
        """Successful load should return a Document with metadata."""
        mock_fetch.return_value = "<html><body>Hello</body></html>"
        mock_extract.return_value = ("Hello World", {"extractor": "trafilatura"})

        docs = self.reader._load_data(url="https://example.com")

        self.assertEqual(len(docs), 1)
        self.assertIsInstance(docs[0], Document)
        self.assertEqual(docs[0].text, "Hello World")
        self.assertEqual(docs[0].metadata["source"], "web")
        self.assertEqual(docs[0].metadata["url"], "https://example.com")
        self.assertEqual(docs[0].metadata["extractor"], "trafilatura")

    @patch.object(WebPageReader, '_extract_main_text')
    @patch.object(WebPageReader, '_fetch_html')
    def test_load_data_with_ext_info(self, mock_fetch, mock_extract):
        """ext_info should be merged into metadata."""
        mock_fetch.return_value = "<html><body>Test</body></html>"
        mock_extract.return_value = ("Test", {"extractor": "bs4"})

        docs = self.reader._load_data(url="https://example.com", ext_info={"custom_key": "custom_val"})

        self.assertEqual(docs[0].metadata["custom_key"], "custom_val")
        self.assertEqual(docs[0].metadata["source"], "web")

    def test_fetch_html_httpx_success(self):
        """_fetch_html should use httpx when available."""
        mock_response = MagicMock()
        mock_response.text = "<html>content</html>"
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)

        mock_httpx = MagicMock()
        mock_httpx.Client.return_value = mock_client

        # Patch sys.modules so that ``import httpx`` resolves to our mock.
        with patch.dict(sys.modules, {'httpx': mock_httpx}):
            html = self.reader._fetch_html("https://example.com")
        self.assertEqual(html, "<html>content</html>")

    def test_fetch_html_requests_fallback(self):
        """_fetch_html should fall back to requests when httpx is unavailable."""
        mock_response = MagicMock()
        mock_response.text = "<html>fallback</html>"
        mock_response.raise_for_status = MagicMock()

        mock_requests = MagicMock()
        mock_requests.get.return_value = mock_response

        # httpx=None in sys.modules makes ``import httpx`` raise ImportError,
        # triggering the requests fallback path.
        with patch.dict(sys.modules, {'httpx': None, 'requests': mock_requests}):
            html = self.reader._fetch_html("https://example.com")
        self.assertEqual(html, "<html>fallback</html>")

    def test_fetch_html_both_fail_raises_load_error(self):
        """_fetch_html should raise ReaderLoadError when both httpx and requests are unavailable."""
        # Both set to None ⇒ both imports fail ⇒ ReaderLoadError
        with patch.dict(sys.modules, {'httpx': None, 'requests': None}):
            with self.assertRaises(ReaderLoadError) as ctx:
                self.reader._fetch_html("https://example.com")
            self.assertEqual(ctx.exception.reader_name, "WebPageReader")
            self.assertEqual(ctx.exception.source, "https://example.com")

    def test_extract_main_text_trafilatura(self):
        """_extract_main_text should prefer trafilatura."""
        mock_trafilatura = MagicMock()
        mock_trafilatura.extract.return_value = "  Extracted article text  "

        with patch.dict(sys.modules, {'trafilatura': mock_trafilatura}):
            text, meta = self.reader._extract_main_text("<html>...</html>", "https://example.com")
        self.assertEqual(text, "Extracted article text")
        self.assertEqual(meta["extractor"], "trafilatura")

    def test_extract_main_text_no_library_raises_dependency_error(self):
        """_extract_main_text should raise ReaderDependencyError when no extraction library is available."""
        # Setting modules to None in sys.modules makes their imports raise ImportError.
        with patch.dict(sys.modules, {
            'trafilatura': None,
            'readability': None,
            'bs4': None,
        }):
            with self.assertRaises(ReaderDependencyError) as ctx:
                self.reader._extract_main_text("<html>...</html>", "https://example.com")
            self.assertEqual(ctx.exception.reader_name, "WebPageReader")
            self.assertIn("trafilatura", ctx.exception.dependency)


class TestWebPageReaderInheritance(unittest.TestCase):
    """Test that WebPageReader properly inherits from Reader."""

    def setUp(self):
        self.reader = WebPageReader()

    def test_inherits_reader(self):
        """WebPageReader should be a Reader subclass."""
        from agentuniverse.agent.action.knowledge.reader.reader import Reader
        self.assertIsInstance(self.reader, Reader)

    def test_has_load_data_method(self):
        """WebPageReader should have load_data from Reader base."""
        self.assertTrue(hasattr(WebPageReader, 'load_data'))

    def test_has_load_data_implementation(self):
        """WebPageReader should have _load_data implemented."""
        self.assertTrue(hasattr(WebPageReader, '_load_data'))


if __name__ == "__main__":
    unittest.main()