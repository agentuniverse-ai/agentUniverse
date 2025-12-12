#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/12 14:25
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_langchain_bridge_reader.py
"""
Unit tests for LangchainBridgeReader
"""

import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.reader.langchain_bridge.langchain_bridge_reader import LangchainBridgeReader
from agentuniverse.agent.action.knowledge.store.document import Document


class TestLangchainBridgeReader(unittest.TestCase):
    """Unit tests for LangchainBridgeReader"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_langchain_doc = Mock()
        self.mock_langchain_doc.page_content = "Test content"
        self.mock_langchain_doc.metadata = {"source": "test"}

    @patch('importlib.import_module')
    @patch('agentuniverse.agent.action.knowledge.reader.langchain_bridge.langchain_bridge_reader.Document.from_langchain_list')
    def test_load_data_success(self, mock_from_langchain, mock_import_module):
        """Test successful data loading"""
        # Mock the loader class
        mock_loader_cls = Mock()
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [self.mock_langchain_doc]
        mock_loader_cls.return_value = mock_loader_instance
        
        mock_module = Mock()
        mock_module.TextLoader = mock_loader_cls
        mock_import_module.return_value = mock_module
        
        # Mock the conversion
        mock_from_langchain.return_value = [Document(text="Test content", metadata={"source": "test"})]
        
        # Test
        reader = LangchainBridgeReader(
            loader_class="TextLoader",
            loader_module="langchain_community.document_loaders.text",
            loader_params={
                "file_path": "test.txt"
            }
        )
        result = reader.load_data()
        
        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Test content")
        mock_loader_cls.assert_called_once_with(file_path="test.txt")

    @patch('importlib.import_module')
    @patch('agentuniverse.agent.action.knowledge.reader.langchain_bridge.langchain_bridge_reader.Document.from_langchain_list')
    def test_load_data_with_kwargs(self, mock_from_langchain, mock_import_module):
        """Test data loading with additional keyword arguments"""
        # Mock the loader class
        mock_loader_cls = Mock()
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [self.mock_langchain_doc]
        mock_loader_cls.return_value = mock_loader_instance
        
        mock_module = Mock()
        mock_module.TextLoader = mock_loader_cls
        mock_import_module.return_value = mock_module
        
        # Mock the conversion
        mock_from_langchain.return_value = [Document(text="Test content", metadata={"source": "test"})]
        
        # Test with additional kwargs
        reader = LangchainBridgeReader(
            loader_class="TextLoader",
            loader_module="langchain_community.document_loaders.text",
            loader_params={
                "file_path": "test.txt"
            }
        )
        result = reader.load_data(encoding="utf-8", autodetect_encoding=True)
        
        # Assertions
        self.assertEqual(len(result), 1)
        mock_loader_cls.assert_called_once_with(file_path="test.txt", encoding="utf-8", autodetect_encoding=True)

    def test_missing_loader_configuration(self):
        """Test error handling for missing loader configuration"""
        reader = LangchainBridgeReader()
        
        with self.assertRaises(ValueError) as context:
            reader.load_data()
        
        self.assertIn("LangchainReader requires loader_class and loader_module configuration", str(context.exception))

    @patch('importlib.import_module')
    def test_import_error(self, mock_import_module):
        """Test error handling for import failures"""
        mock_import_module.side_effect = ImportError("Module not found")
        
        reader = LangchainBridgeReader(
            loader_class="NonExistentLoader",
            loader_module="non_existent.module"
        )
        
        with self.assertRaises(ImportError) as context:
            reader.load_data()
        
        self.assertIn("Failed to import loader NonExistentLoader", str(context.exception))

    @patch('importlib.import_module')
    def test_runtime_error(self, mock_import_module):
        """Test error handling for runtime failures"""
        mock_loader_cls = Mock()
        mock_loader_instance = Mock()
        mock_loader_instance.load.side_effect = Exception("Loader error")
        mock_loader_cls.return_value = mock_loader_instance
        
        mock_module = Mock()
        mock_module.TestLoader = mock_loader_cls
        mock_import_module.return_value = mock_module
        
        reader = LangchainBridgeReader(
            loader_class="TestLoader",
            loader_module="test.module"
        )
        
        with self.assertRaises(RuntimeError) as context:
            reader.load_data()
        
        self.assertIn("Error loading documents with TestLoader", str(context.exception))

    def test_initialization_with_data(self):
        """Test initialization with data parameters"""
        reader = LangchainBridgeReader(
            loader_class="TextLoader",
            loader_module="langchain_community.document_loaders.text",
            loader_params={"file_path": "test.txt"}
        )
        
        self.assertEqual(reader.loader_class, "TextLoader")
        self.assertEqual(reader.loader_module, "langchain_community.document_loaders.text")
        self.assertEqual(reader.loader_params["file_path"], "test.txt")

    @patch('importlib.import_module')
    @patch('agentuniverse.agent.action.knowledge.reader.langchain_bridge.langchain_bridge_reader.Document.from_langchain_list')
    def test_empty_document_list(self, mock_from_langchain, mock_import_module):
        """Test handling of empty document list"""
        # Mock the loader class
        mock_loader_cls = Mock()
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = []  # Empty list
        mock_loader_cls.return_value = mock_loader_instance
        
        mock_module = Mock()
        mock_module.TextLoader = mock_loader_cls
        mock_import_module.return_value = mock_module
        
        # Mock the conversion
        mock_from_langchain.return_value = []
        
        # Test
        reader = LangchainBridgeReader(
            loader_class="TextLoader",
            loader_module="langchain_community.document_loaders.text",
            loader_params={"file_path": "empty.txt"}
        )
        result = reader.load_data()
        
        # Assertions
        self.assertEqual(len(result), 0)
        mock_loader_cls.assert_called_once_with(file_path="empty.txt")


if __name__ == "__main__":
    unittest.main()
