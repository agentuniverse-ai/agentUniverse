# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_image_ocr_reader.py
"""Unit tests for ImageOCRReader (offline: OCR engines are faked or absent)."""

import sys
import types
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.image.image_ocr_reader import ImageOCRReader
from agentuniverse.agent.action.knowledge.store.document import Document


class TestImageOCRReader:
    """Test ImageOCRReader guards, metadata shaping and engine fallback order."""

    @pytest.fixture
    def reader(self):
        """Create an ImageOCRReader instance for testing."""
        return ImageOCRReader()

    @pytest.fixture
    def image_file(self, tmp_path):
        """Create a placeholder image file that merely exists on disk."""
        path = tmp_path / "page.png"
        path.write_bytes(b"\x89PNG\r\n\x1a\nplaceholder")
        return path

    @pytest.mark.parametrize("file_input", [None, 123, "/no/such/file.png"])
    def test_load_data_requires_existing_file(self, reader, file_input):
        """Missing or non-path inputs raise FileNotFoundError before any OCR runs."""
        with pytest.raises(FileNotFoundError, match="ImageOCRReader file not found"):
            reader._load_data(file_input)

    def test_load_data_shapes_image_metadata(self, reader, image_file):
        """A Document is returned with source/file_name/engine metadata."""
        reader._ocr = lambda file: ("recognized line", "pytesseract")
        docs = reader._load_data(str(image_file))
        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert docs[0].text == "recognized line"
        assert docs[0].metadata == {
            "source": "image",
            "file_name": "page.png",
            "engine": "pytesseract",
        }

    def test_load_data_merges_ext_info_into_metadata(self, reader, image_file):
        """ext_info entries are merged and can override default metadata keys."""
        reader._ocr = lambda file: ("text", "easyocr")
        docs = reader._load_data(image_file, ext_info={"engine": "custom", "page": 3})
        assert docs[0].metadata["engine"] == "custom"
        assert docs[0].metadata["page"] == 3
        assert docs[0].metadata["source"] == "image"

    def test_load_data_converts_str_path_to_path_object(self, reader, image_file):
        """A string input is converted to Path before being handed to _ocr."""
        seen = {}
        reader._ocr = lambda file: seen.update(file=file) or ("text", "pytesseract")
        reader._load_data(str(image_file))
        assert isinstance(seen["file"], Path)
        assert seen["file"].name == "page.png"

    def test_ocr_raises_import_error_without_any_engine(self, reader, monkeypatch):
        """With every OCR engine unavailable an ImportError guides installation."""
        for module_name in ("paddleocr", "PIL", "pytesseract", "easyocr"):
            monkeypatch.setitem(sys.modules, module_name, None)
        with pytest.raises(ImportError, match="No OCR engine available"):
            reader._ocr(Path("/tmp/irrelevant.png"))

    def test_ocr_falls_back_to_easyocr(self, reader, monkeypatch):
        """When only easyocr is importable its output is joined with newlines."""
        for module_name in ("paddleocr", "PIL", "pytesseract"):
            monkeypatch.setitem(sys.modules, module_name, None)
        fake_easyocr = types.ModuleType("easyocr")

        class _FakeEasyOcrReader:
            def __init__(self, languages):
                self.languages = languages

            def readtext(self, img_path, detail=0):
                return ["hello", "world"]

        fake_easyocr.Reader = _FakeEasyOcrReader
        monkeypatch.setitem(sys.modules, "easyocr", fake_easyocr)

        text, engine = reader._ocr(Path("/tmp/irrelevant.png"))
        assert engine == "easyocr"
        assert text == "hello\nworld"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
