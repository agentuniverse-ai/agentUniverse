# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for FeishuReader (refactored from PublicFeishuReader)."""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock

from agentuniverse.agent.action.knowledge.reader.cloud.feishu_reader import (
    FeishuReader,
    PublicFeishuReader,
)
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class TestFeishuReaderInheritance(unittest.TestCase):
    """Test FeishuReader class hierarchy and backward compatibility."""

    def test_feishu_reader_inherits_reader(self):
        """FeishuReader should inherit from Reader base class."""
        reader = FeishuReader()
        self.assertIsInstance(reader, Reader)

    def test_public_feishu_reader_is_alias(self):
        """PublicFeishuReader should be an alias for FeishuReader."""
        self.assertIs(PublicFeishuReader, FeishuReader)

    def test_has_load_data(self):
        """FeishuReader should have load_data from Reader base."""
        reader = FeishuReader()
        self.assertTrue(hasattr(reader, 'load_data'))

    def test_has_load_data_private(self):
        """FeishuReader should implement _load_data."""
        self.assertTrue(hasattr(FeishuReader, '_load_data'))

    def test_lazy_driver_init(self):
        """WebDriver should not be created at init time."""
        reader = FeishuReader()
        self.assertIsNone(reader._driver)


class TestFeishuReaderLoadData(unittest.TestCase):

    def setUp(self):
        self.reader = FeishuReader()

    def tearDown(self):
        self.reader.close()

    def test_load_data_requires_url(self):
        """_load_data with empty url should raise ReaderLoadError."""
        with self.assertRaises(ReaderLoadError) as ctx:
            self.reader._load_data(url="")
        self.assertEqual(ctx.exception.reader_name, "FeishuReader")

    def test_load_data_with_none_url(self):
        """_load_data with None url should raise ReaderLoadError."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data(url=None)

    @patch.object(FeishuReader, '_fetch_document_content')
    def test_load_data_success(self, mock_fetch):
        """Successful load should return a Document with correct metadata."""
        mock_fetch.return_value = "Feishu document content here"

        docs = self.reader._load_data(url="https://feishu.cn/docx/abc123")

        self.assertEqual(len(docs), 1)
        self.assertIsInstance(docs[0], Document)
        self.assertEqual(docs[0].text, "Feishu document content here")
        self.assertEqual(docs[0].metadata["source"], "feishu")
        self.assertEqual(docs[0].metadata["url"], "https://feishu.cn/docx/abc123")

    @patch.object(FeishuReader, '_fetch_document_content')
    def test_load_data_empty_content(self, mock_fetch):
        """Empty content should return empty list."""
        mock_fetch.return_value = ""

        docs = self.reader._load_data(url="https://feishu.cn/docx/abc123")
        self.assertEqual(len(docs), 0)

    @patch.object(FeishuReader, '_fetch_document_content')
    def test_load_data_with_ext_info(self, mock_fetch):
        """ext_info should be merged into metadata."""
        mock_fetch.return_value = "content"

        docs = self.reader._load_data(url="https://feishu.cn/docx/abc", ext_info={"team": "dev"})

        self.assertEqual(docs[0].metadata["team"], "dev")
        self.assertEqual(docs[0].metadata["source"], "feishu")


class TestFeishuReaderDriver(unittest.TestCase):

    def test_get_driver_selenium_missing(self):
        """Missing selenium should raise ReaderDependencyError."""
        reader = FeishuReader()
        with patch.dict('sys.modules', {'selenium': None}):
            # Force re-import to fail
            with patch('builtins.__import__', side_effect=ImportError("No module named 'selenium'")):
                with self.assertRaises(ReaderDependencyError) as ctx:
                    reader._get_driver()
                self.assertEqual(ctx.exception.reader_name, "FeishuReader")
                self.assertIn("selenium", ctx.exception.dependency)

    def test_close_cleans_up_driver(self):
        """close() should set _driver to None."""
        reader = FeishuReader()
        mock_driver = MagicMock()
        reader._driver = mock_driver

        reader.close()

        mock_driver.quit.assert_called_once()
        self.assertIsNone(reader._driver)

    def test_close_idempotent(self):
        """close() should be safe to call multiple times."""
        reader = FeishuReader()
        reader.close()  # Should not raise
        reader.close()  # Should not raise


class TestFeishuReaderParseContent(unittest.TestCase):

    def setUp(self):
        self.reader = FeishuReader()

    def test_parse_content_no_body_raises_parse_error(self):
        """HTML without <body> should raise ReaderParseError."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html><head></head></html>", 'html.parser')

        with self.assertRaises(ReaderParseError) as ctx:
            self.reader._parse_content(soup)
        self.assertEqual(ctx.exception.reader_name, "FeishuReader")

    def test_parse_content_with_title(self):
        """Should extract title from h1 tag."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html><body><h1>Test Title</h1><div>Content</div></body></html>", 'html.parser')

        text = self.reader._parse_content(soup)
        self.assertIn("Title: Test Title", text)
        self.assertIn("Content", text)

    def test_parse_content_deduplication(self):
        """Should deduplicate content while preserving order."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(
            "<html><body><div>Duplicate</div><div>Duplicate</div><div>Unique</div></body></html>",
            'html.parser'
        )

        text = self.reader._parse_content(soup)
        # Count occurrences of "Duplicate"
        self.assertEqual(text.count("Duplicate"), 1)
        self.assertIn("Unique", text)


if __name__ == "__main__":
    unittest.main()