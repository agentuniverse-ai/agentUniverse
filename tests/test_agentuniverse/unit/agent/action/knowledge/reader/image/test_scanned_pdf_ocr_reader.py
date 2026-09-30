# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_scanned_pdf_ocr_reader.py
"""Unit tests for ScannedPdfOCRReader (offline, no real OCR)."""

import sys
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.image.scanned_pdf_ocr_reader import \
    ScannedPdfOCRReader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum


class TestScannedPdfOCRReader:
    """Test the pure logic of ScannedPdfOCRReader without OCR engines."""

    @pytest.fixture
    def reader(self):
        """Create a ScannedPdfOCRReader instance."""
        return ScannedPdfOCRReader()

    @pytest.fixture
    def junk_pdf(self, tmp_path):
        """Create a file that is not a real PDF (never OCR'ed)."""
        pdf = tmp_path / "sample.pdf"
        pdf.write_bytes(b"this file is not a valid pdf document at all")
        return pdf

    def test_reader_class_defaults(self, reader):
        """Reader defaults: subclass of Reader and READER component type."""
        assert isinstance(reader, Reader)
        assert reader.component_type == ComponentEnum.READER
        assert reader.name is None
        assert reader.description is None

    def test_load_data_missing_file_raises(self, reader):
        """Loading a nonexistent file raises FileNotFoundError (str and Path)."""
        with pytest.raises(FileNotFoundError, match="file not found"):
            reader.load_data("/no/such/scanned.pdf")
        with pytest.raises(FileNotFoundError, match="file not found"):
            reader.load_data(Path("/no/such/scanned.pdf"))

    def test_count_pdf_pages_invalid_file_returns_zero(self, reader, junk_pdf):
        """An unreadable/non-PDF file counts as zero pages."""
        assert reader._count_pdf_pages(junk_pdf) == 0

    def test_ocr_page_without_pdf2image_raises(self, reader, junk_pdf,
                                               monkeypatch):
        """OCR page requires pdf2image; its absence raises ImportError."""
        monkeypatch.setitem(sys.modules, "pdf2image", None)
        with pytest.raises(ImportError, match="pdf2image is required"):
            reader._ocr_pdf_page(junk_pdf, 0)

    def test_load_data_builds_document_with_mocked_ocr(self, reader, junk_pdf,
                                                       monkeypatch):
        """Page texts are joined and metadata is summarized when OCR is stubbed."""
        def fake_count(file):
            return 2

        def fake_ocr(file, page_index):
            return [("first page text", "paddleocr"),
                    ("second page text", "pytesseract")][page_index]

        monkeypatch.setattr(reader, "_count_pdf_pages", fake_count)
        monkeypatch.setattr(reader, "_ocr_pdf_page", fake_ocr)

        docs = reader.load_data(str(junk_pdf), ext_info={"chapter": "intro"})

        assert len(docs) == 1
        doc = docs[0]
        assert isinstance(doc, Document)
        assert doc.text == "first page text\n\nsecond page text"
        assert doc.metadata["source"] == "pdf"
        assert doc.metadata["file_name"] == junk_pdf.name
        assert doc.metadata["engine"] == "paddleocr,pytesseract"
        assert doc.metadata["chapter"] == "intro"

    def test_load_data_unparseable_pdf_returns_empty_unknown(self, reader,
                                                             junk_pdf):
        """When no extraction engine works the reader yields empty/unknown."""
        docs = reader.load_data(junk_pdf)

        assert len(docs) == 1
        assert docs[0].text == ""
        assert docs[0].metadata["source"] == "pdf"
        assert docs[0].metadata["engine"] == "unknown"
