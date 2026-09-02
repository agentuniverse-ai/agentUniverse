# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_pdf_reader.py
"""Unit tests for PdfReader."""

import sys
import types

import pytest
from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_base import ComponentEnum


class _FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text

def _install_fake_pypdf(monkeypatch, texts, labels):
    """Install a fake pypdf module so no real PDF parsing happens."""
    module = types.ModuleType("pypdf")

    class FakePdfReader:
        def __init__(self, stream):
            self.stream = stream
            self.pages = [_FakePage(text) for text in texts]
            self.page_labels = list(labels)

    module.PdfReader = FakePdfReader
    monkeypatch.setitem(sys.modules, "pypdf", module)

class TestPdfReader:
    """Test the PdfReader implementation."""

    @pytest.fixture
    def reader(self):
        return PdfReader()

    @pytest.fixture
    def pdf_file(self, tmp_path):
        path = tmp_path / "sample.pdf"
        path.write_bytes(b"%PDF-1.4\n%%EOF\n")
        return path

    def test_component_defaults(self, reader):
        assert isinstance(reader, Reader)
        assert reader.component_type == ComponentEnum.READER
        assert reader.name is None and reader.description is None

    def test_missing_pypdf_raises_import_error(self, reader, pdf_file,
                                               monkeypatch):
        monkeypatch.setitem(sys.modules, "pypdf", None)
        with pytest.raises(ImportError, match="pypdf is required"):
            reader._load_data(pdf_file)

    def test_load_data_builds_documents_with_metadata(self, reader, pdf_file,
                                                      monkeypatch):
        _install_fake_pypdf(monkeypatch, ["page one text", "page two text"],
                            ["1", "2"])
        docs = reader._load_data(pdf_file)
        assert len(docs) == 2
        assert [doc.text for doc in docs] == ["page one text", "page two text"]
        assert all(isinstance(doc, Document) for doc in docs)
        assert docs[0].metadata == {"page_label": "1",
                                    "file_name": "sample.pdf"}

    def test_ext_info_is_merged_and_overrides(self, reader, pdf_file,
                                              monkeypatch):
        _install_fake_pypdf(monkeypatch, ["content"], ["1"])
        docs = reader._load_data(pdf_file, ext_info={"chapter": 3})
        assert docs[0].metadata["chapter"] == 3
        assert docs[0].metadata["file_name"] == "sample.pdf"

        docs = reader._load_data(pdf_file, ext_info={"file_name": "renamed.pdf",
                                                     "page_label": "override"})
        assert docs[0].metadata["file_name"] == "renamed.pdf"
        assert docs[0].metadata["page_label"] == "override"

    def test_accepts_str_path_and_empty_pdf(self, reader, pdf_file,
                                            monkeypatch):
        _install_fake_pypdf(monkeypatch, ["content"], ["1"])
        docs = reader._load_data(str(pdf_file))
        assert docs[0].metadata["file_name"] == "sample.pdf"

        _install_fake_pypdf(monkeypatch, [], [])
        assert reader._load_data(pdf_file) == []
