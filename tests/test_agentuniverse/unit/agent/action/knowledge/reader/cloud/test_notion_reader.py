# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for NotionReader."""

import sys
import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.knowledge.reader.cloud.notion_reader import NotionReader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
    ReaderConfigError,
)
from agentuniverse.agent.action.knowledge.store.document import Document


class TestNotionReader(unittest.TestCase):
    """Test suite for NotionReader."""

    def setUp(self):
        self.reader = NotionReader()

    def test_inherits_from_reader(self):
        """Should inherit from Reader base class."""
        from agentuniverse.agent.action.knowledge.reader.reader import Reader
        self.assertIsInstance(self.reader, Reader)

    def test_load_data_empty_id(self):
        """Should raise ReaderLoadError for empty page/db id."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data("")

    def test_load_data_none_id(self):
        """Should raise ReaderLoadError for None page/db id."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data(None)

    def test_load_data_missing_token(self):
        """Should raise ReaderConfigError when NOTION_TOKEN is not set."""
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ReaderConfigError) as ctx:
                self.reader._load_data("page123")
            self.assertEqual(ctx.exception.config_key, "NOTION_TOKEN")

    def test_load_data_missing_notion_client(self):
        """Should raise ReaderDependencyError when notion-client is not installed."""
        saved = sys.modules.get("notion_client")
        sys.modules["notion_client"] = None
        try:
            with patch.dict("os.environ", {"NOTION_TOKEN": "test-token"}):
                with self.assertRaises(ReaderDependencyError) as ctx:
                    self.reader._load_data("page123")
                self.assertEqual(ctx.exception.dependency, "notion-client")
        finally:
            if saved is None:
                sys.modules.pop("notion_client", None)
            else:
                sys.modules["notion_client"] = saved

    def _install_mock_notion_client(self):
        """Create a mock notion_client module in sys.modules."""
        mock_module = MagicMock()
        mock_module.Client = MagicMock()
        sys.modules["notion_client"] = mock_module
        return mock_module

    def _uninstall_mock_notion_client(self):
        sys.modules.pop("notion_client", None)

    def test_load_data_token_from_ext_info(self):
        """Should use token from ext_info."""
        mock_notion = self._install_mock_notion_client()
        try:
            mock_client = MagicMock()
            mock_page = {"id": "page123", "object": "page"}
            mock_client.pages.retrieve.return_value = mock_page

            mock_blocks = MagicMock()
            mock_blocks.get.return_value = {"results": [], "has_more": False}
            mock_client.blocks.children.list.return_value = mock_blocks
            mock_notion.Client.return_value = mock_client

            docs = self.reader._load_data("page123", ext_info={"NOTION_TOKEN": "test-token"})
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0].metadata["source"], "notion")
            mock_notion.Client.assert_called_once_with(auth="test-token")
        finally:
            self._uninstall_mock_notion_client()

    def test_load_data_token_from_env(self):
        """Should use token from environment variable."""
        mock_notion = self._install_mock_notion_client()
        try:
            with patch.dict("os.environ", {"NOTION_TOKEN": "env-token"}):
                mock_client = MagicMock()
                mock_page = {"id": "page123", "object": "page"}
                mock_client.pages.retrieve.return_value = mock_page

                mock_blocks = MagicMock()
                mock_blocks.get.return_value = {"results": [], "has_more": False}
                mock_client.blocks.children.list.return_value = mock_blocks
                mock_notion.Client.return_value = mock_client

                docs = self.reader._load_data("page123")
                self.assertEqual(len(docs), 1)
                mock_notion.Client.assert_called_once_with(auth="env-token")
        finally:
            self._uninstall_mock_notion_client()

    def test_block_to_text_paragraph(self):
        """Should extract text from paragraph blocks."""
        block = {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Hello"}]}}
        result = self.reader._block_to_text(block)
        self.assertEqual(result, "Hello")

    def test_block_to_text_heading(self):
        """Should extract text from heading blocks."""
        block = {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "Title"}]}}
        result = self.reader._block_to_text(block)
        self.assertEqual(result, "Title")

    def test_block_to_text_image(self):
        """Should return placeholder for image blocks."""
        block = {"type": "image", "image": {}}
        result = self.reader._block_to_text(block)
        self.assertEqual(result, "[image]")

    def test_block_to_text_table(self):
        """Should return placeholder for table blocks."""
        block = {"type": "table", "table": {}}
        result = self.reader._block_to_text(block)
        self.assertEqual(result, "[table omitted]")


if __name__ == "__main__":
    unittest.main()
