# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/5
# @FileName: test_reader_exception_paths.py
"""Integration tests verifying that Reader subclasses raise the correct
semantic exceptions from the reader_errors hierarchy.

Each test targets a specific error path (missing file, bad config,
missing dependency, parse failure) and asserts the exact exception
type and key attributes.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderError,
    ReaderLoadError,
    ReaderDependencyError,
    ReaderParseError,
    ReaderConfigError,
)
from agentuniverse.agent.action.knowledge.reader.file.json_reader import JsonReader
from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader
from agentuniverse.agent.action.knowledge.reader.web.rendered_web_page_reader import RenderedWebPageReader


class TestJsonReaderExceptions(unittest.TestCase):
    """Exception-path tests for JsonReader."""

    def setUp(self):
        self.reader = JsonReader()

    def test_missing_file_raises_reader_load_error(self):
        with self.assertRaises(ReaderLoadError) as ctx:
            self.reader._load_data("/nonexistent/path/data.json")
        self.assertIn("JsonReader", str(ctx.exception))
        self.assertEqual(ctx.exception.reader_name, "JsonReader")
        self.assertIn("/nonexistent/path/data.json", ctx.exception.source)

    def test_missing_file_load_error_is_reader_error(self):
        """ReaderLoadError should be catchable as ReaderError."""
        with self.assertRaises(ReaderError):
            self.reader._load_data("/no/such/file.json")

    def test_invalid_json_raises_reader_parse_error(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{invalid json content!!!")
            tmp_path = f.name
        try:
            with self.assertRaises(ReaderParseError) as ctx:
                self.reader._load_data(tmp_path)
            self.assertEqual(ctx.exception.reader_name, "JsonReader")
            self.assertIn("Invalid JSON", str(ctx.exception))
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_valid_json_succeeds(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({"key": "value"}, f)
            tmp_path = f.name
        try:
            docs = self.reader._load_data(tmp_path)
            self.assertEqual(len(docs), 1)
            self.assertIn("key", docs[0].text)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestCSVReaderExceptions(unittest.TestCase):
    """Exception-path tests for CSVReader."""

    def setUp(self):
        self.reader = CSVReader()

    def test_missing_file_raises_reader_load_error(self):
        with self.assertRaises(ReaderLoadError) as ctx:
            self.reader._load_data("/nonexistent/path/data.csv")
        self.assertEqual(ctx.exception.reader_name, "CSVReader")
        self.assertIn("/nonexistent/path/data.csv", ctx.exception.source)

    def test_invalid_file_type_raises_reader_config_error(self):
        with self.assertRaises(ReaderConfigError) as ctx:
            self.reader._load_data(12345)  # type: ignore
        self.assertEqual(ctx.exception.reader_name, "CSVReader")

    def test_missing_file_load_error_catchable_as_reader_error(self):
        with self.assertRaises(ReaderError):
            self.reader._load_data("/no/such/file.csv")


class TestWebPageReaderExceptions(unittest.TestCase):
    """Exception-path tests for WebPageReader."""

    def setUp(self):
        self.reader = WebPageReader()

    def test_empty_url_raises_reader_config_error(self):
        with self.assertRaises(ReaderConfigError) as ctx:
            self.reader._load_data("")
        self.assertEqual(ctx.exception.reader_name, "WebPageReader")

    def test_none_url_raises_reader_config_error(self):
        with self.assertRaises(ReaderConfigError):
            self.reader._load_data(None)  # type: ignore

    def test_non_string_url_raises_reader_config_error(self):
        with self.assertRaises(ReaderConfigError):
            self.reader._load_data(12345)  # type: ignore

    def test_config_error_catchable_as_reader_error(self):
        with self.assertRaises(ReaderError):
            self.reader._load_data("")


class TestRenderedWebPageReaderExceptions(unittest.TestCase):
    """Exception-path tests for RenderedWebPageReader."""

    def setUp(self):
        self.reader = RenderedWebPageReader()

    def test_empty_url_raises_reader_config_error(self):
        with self.assertRaises(ReaderConfigError) as ctx:
            self.reader._load_data("")
        self.assertEqual(ctx.exception.reader_name, "RenderedWebPageReader")

    def test_missing_playwright_raises_reader_dependency_error(self):
        """When playwright is not installed, ReaderDependencyError should be raised."""
        with patch.dict("sys.modules", {"playwright": None, "playwright.sync_api": None}):
            with self.assertRaises(ReaderDependencyError) as ctx:
                self.reader._render_and_get_html("https://example.com")
            self.assertEqual(ctx.exception.reader_name, "RenderedWebPageReader")
            self.assertEqual(ctx.exception.dependency, "playwright")

    def test_dependency_error_catchable_as_reader_error(self):
        with patch.dict("sys.modules", {"playwright": None, "playwright.sync_api": None}):
            with self.assertRaises(ReaderError):
                self.reader._render_and_get_html("https://example.com")


class TestPdfReaderExceptions(unittest.TestCase):
    """Exception-path tests for PdfReader (dependency path only)."""

    def test_missing_pypdf_raises_reader_dependency_error(self):
        from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
        reader = PdfReader()
        with patch.dict("sys.modules", {"pypdf": None}):
            with self.assertRaises(ReaderDependencyError) as ctx:
                reader._load_data("/some/file.pdf")
            self.assertEqual(ctx.exception.reader_name, "PdfReader")
            self.assertEqual(ctx.exception.dependency, "pypdf")
            self.assertIn("pip install pypdf", ctx.exception.install_hint)

    def test_missing_file_raises_reader_load_error(self):
        """File-not-found should raise ReaderLoadError when pypdf IS available."""
        from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
        reader = PdfReader()
        # If pypdf is not installed, skip this test
        try:
            import pypdf  # noqa: F401
        except ImportError:
            self.skipTest("pypdf not installed")
        with self.assertRaises(ReaderLoadError) as ctx:
            reader._load_data("/nonexistent/file.pdf")
        self.assertEqual(ctx.exception.reader_name, "PdfReader")


class TestDocxReaderExceptions(unittest.TestCase):
    """Exception-path tests for DocxReader (dependency path)."""

    def test_missing_docx_dep_raises_reader_dependency_error(self):
        from agentuniverse.agent.action.knowledge.reader.file.docx_reader import DocxReader
        reader = DocxReader()
        with patch.dict("sys.modules", {"docx": None}):
            with self.assertRaises(ReaderDependencyError) as ctx:
                reader._load_data("/some/file.docx")
            self.assertEqual(ctx.exception.reader_name, "DocxReader")
            self.assertEqual(ctx.exception.dependency, "python-docx")


if __name__ == "__main__":
    unittest.main()