# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for ScannedPdfOCRReader."""

import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.image.scanned_pdf_ocr_reader import ScannedPdfOCRReader
from agentuniverse.agent.action.knowledge.reader.reader_errors import ReaderLoadError, ReaderDependencyError
from agentuniverse.agent.action.knowledge.store.document import Document


class TestScannedPdfOCRReader(unittest.TestCase):
    """Test suite for ScannedPdfOCRReader."""

    def setUp(self):
        self.reader = ScannedPdfOCRReader()

    def test_inherits_from_reader(self):
        """Should inherit from Reader base class."""
        from agentuniverse.agent.action.knowledge.reader.reader import Reader
        self.assertIsInstance(self.reader, Reader)

    def test_load_data_nonexistent_file(self):
        """Should raise ReaderLoadError for non-existent file."""
        with self.assertRaises(ReaderLoadError):
            self.reader._load_data(Path("/nonexistent/path/file.pdf"))

    def test_max_pages_default_none(self):
        """Should default max_pages to None (unlimited)."""
        self.assertIsNone(self.reader.max_pages)

    def test_max_pages_settable(self):
        """Should allow setting max_pages."""
        reader = ScannedPdfOCRReader(max_pages=5)
        self.assertEqual(reader.max_pages, 5)

    def test_ocr_pdf_page_missing_pdf2image(self):
        """Should raise ReaderDependencyError when pdf2image is not installed."""
        saved = sys.modules.get("pdf2image")
        sys.modules["pdf2image"] = None
        try:
            with self.assertRaises(ReaderDependencyError) as ctx:
                self.reader._ocr_pdf_page(Path("/fake/file.pdf"), 0)
            self.assertEqual(ctx.exception.dependency, "pdf2image")
        finally:
            if saved is None:
                sys.modules.pop("pdf2image", None)
            else:
                sys.modules["pdf2image"] = saved

    def test_load_data_with_pypdf_success(self):
        """Should extract text with pypdf when text is available."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page content"
        mock_pdf.pages = [mock_page]

        # Mock pypdf module since it may not be installed
        mock_pypdf = MagicMock()
        mock_pypdf.PdfReader.return_value = mock_pdf
        saved = sys.modules.get("pypdf")
        sys.modules["pypdf"] = mock_pypdf
        try:
            with patch("builtins.open", mock_open()):
                with patch.object(Path, "exists", return_value=True):
                    docs = self.reader._load_data(Path("/fake/file.pdf"))
                    self.assertEqual(len(docs), 1)
                    self.assertEqual(docs[0].text, "Page content")
                    self.assertIn("pypdf", docs[0].metadata["engine"])
        finally:
            if saved is None:
                sys.modules.pop("pypdf", None)
            else:
                sys.modules["pypdf"] = saved

    def test_document_structure(self):
        """Should return valid Document objects."""
        doc = Document(text="test", metadata={"key": "value"})
        self.assertEqual(doc.text, "test")
        self.assertEqual(doc.metadata["key"], "value")


if __name__ == "__main__":
    unittest.main()
