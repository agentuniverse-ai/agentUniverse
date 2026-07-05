# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for CloudDocReader."""

import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader import (
    CloudDocReader,
    _platform_map,
)
from agentuniverse.agent.action.knowledge.reader.reader_errors import ReaderLoadError
from agentuniverse.agent.action.knowledge.store.document import Document


class TestCloudDocReader(unittest.TestCase):
    """Test suite for CloudDocReader."""

    def setUp(self):
        self.reader = CloudDocReader()
        # Save original platform map and restore after each test
        self._original_map = dict(_platform_map)

    def tearDown(self):
        _platform_map.clear()
        _platform_map.update(self._original_map)

    def test_detect_platform_feishu(self):
        """Should detect feishu.cn from URL."""
        platform = CloudDocReader._detect_platform("https://www.feishu.cn/docx/ABC123")
        self.assertEqual(platform, "feishu.cn")

    def test_detect_platform_yuque(self):
        """Should detect yuque.com from URL."""
        platform = CloudDocReader._detect_platform("https://www.yuque.com/org/repo/doc")
        self.assertEqual(platform, "yuque.com")

    def test_detect_platform_notion(self):
        """Should detect notion.so from URL."""
        platform = CloudDocReader._detect_platform("https://www.notion.so/Page-Title-abc123")
        self.assertEqual(platform, "notion.so")

    def test_detect_platform_confluence(self):
        """Should detect confluence in domain."""
        platform = CloudDocReader._detect_platform("https://confluence.example.com/display/SPACE/Page")
        self.assertEqual(platform, "confluence")

    def test_detect_platform_google_docs(self):
        """Should detect docs.google.com from URL."""
        platform = CloudDocReader._detect_platform("https://docs.google.com/document/d/abc123/edit")
        self.assertEqual(platform, "docs.google.com")

    def test_detect_platform_unknown(self):
        """Should return empty string for unknown platform."""
        platform = CloudDocReader._detect_platform("https://example.com/doc")
        self.assertEqual(platform, "")

    def test_detect_platform_invalid_url(self):
        """Should return empty string for invalid URL."""
        platform = CloudDocReader._detect_platform("not-a-url")
        self.assertEqual(platform, "")

    def test_register_platform(self):
        """Should register a new platform."""
        CloudDocReader.register_platform("shimo.im", "default_shimo_reader")
        self.assertIn("shimo.im", _platform_map)
        self.assertEqual(_platform_map["shimo.im"], "default_shimo_reader")

    def test_unregister_platform(self):
        """Should unregister a platform."""
        CloudDocReader.register_platform("test.example.com", "test_reader")
        self.assertIn("test.example.com", _platform_map)
        CloudDocReader.unregister_platform("test.example.com")
        self.assertNotIn("test.example.com", _platform_map)

    def test_get_platform_map(self):
        """Should return a copy of the platform map."""
        pmap = CloudDocReader.get_platform_map()
        self.assertIsInstance(pmap, dict)
        self.assertIn("feishu.cn", pmap)

    def test_load_data_empty_url(self):
        """Should raise ReaderLoadError for empty URL."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data("")

    def test_load_data_none_url(self):
        """Should raise ReaderLoadError for None URL."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data(None)

    def test_load_data_unknown_platform(self):
        """Should raise ReaderLoadError for unrecognized platform."""
        with self.assertRaises(ReaderLoadError) as ctx:
            self.reader._load_data("https://unknown-platform.example.com/doc")
        self.assertIn("No cloud reader registered", str(ctx.exception))

    @patch("agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader.ReaderManager")
    def test_load_data_routes_to_platform_reader(self, mock_manager_cls):
        """Should route to the correct platform reader."""
        mock_feishu_reader = MagicMock()
        mock_doc = Document(text="feishu content", metadata={"source": "feishu"})
        mock_feishu_reader.load_data.return_value = [mock_doc]

        mock_manager = MagicMock()
        mock_manager.get_instance_obj.return_value = mock_feishu_reader
        mock_manager_cls.return_value = mock_manager

        docs = self.reader._load_data("https://www.feishu.cn/docx/TEST123")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "feishu content")
        mock_feishu_reader.load_data.assert_called_once_with(
            url="https://www.feishu.cn/docx/TEST123", ext_info=None
        )

    @patch("agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader.ReaderManager")
    def test_load_data_passes_ext_info(self, mock_manager_cls):
        """Should pass ext_info to the platform reader."""
        mock_reader = MagicMock()
        mock_reader.load_data.return_value = [Document(text="ok")]
        mock_manager = MagicMock()
        mock_manager.get_instance_obj.return_value = mock_reader
        mock_manager_cls.return_value = mock_manager

        ext_info = {"NOTION_TOKEN": "secret123"}
        self.reader._load_data("https://www.notion.so/page1", ext_info=ext_info)
        mock_reader.load_data.assert_called_once_with(
            url="https://www.notion.so/page1", ext_info=ext_info
        )

    @patch("agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader.ReaderManager")
    def test_load_data_reader_not_registered(self, mock_manager_cls):
        """Should raise ReaderLoadError when platform reader is not registered."""
        mock_manager = MagicMock()
        mock_manager.get_instance_obj.return_value = None
        mock_manager_cls.return_value = mock_manager

        with self.assertRaises(ReaderLoadError) as ctx:
            self.reader._load_data("https://www.feishu.cn/docx/TEST")
        self.assertIn("not registered in ReaderManager", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
