# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_docx_reader.py
"""Unit tests for DocxReader."""

import sys
import types
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.file.docx_reader import DocxReader


class TestDocxReader:
    """Test the pure loading logic of DocxReader with a fake docx2txt."""

    @pytest.fixture
    def fake_docx2txt(self, monkeypatch):
        """Install a fake docx2txt module capturing the parsed file."""
        module = types.ModuleType("docx2txt")
        captured = {}

        def process(file):
            captured["file"] = file
            return "parsed docx text"

        module.process = process
        monkeypatch.setitem(sys.modules, "docx2txt", module)
        return captured

    def test_missing_docx2txt_raises_import_error(self, monkeypatch):
        """A clear ImportError is raised when docx2txt is unavailable."""
        monkeypatch.setitem(sys.modules, "docx2txt", None)
        with pytest.raises(ImportError, match="docx2txt is required"):
            DocxReader()._load_data("sample.docx")

    def test_load_data_returns_single_document(self, fake_docx2txt):
        """The parsed text is wrapped into exactly one Document."""
        documents = DocxReader()._load_data(Path("sample.docx"))
        assert len(documents) == 1
        assert documents[0].text == "parsed docx text"

    def test_str_path_is_converted_to_path(self, fake_docx2txt):
        """A str input is converted into a pathlib.Path before parsing."""
        DocxReader()._load_data("docs/report.docx")
        assert isinstance(fake_docx2txt["file"], Path)
        assert fake_docx2txt["file"].name == "report.docx"

    def test_metadata_contains_file_name(self, fake_docx2txt):
        """Document metadata records the docx file name."""
        documents = DocxReader()._load_data("docs/report.docx")
        assert documents[0].metadata == {"file_name": "report.docx"}

    def test_ext_info_merged_into_metadata(self, fake_docx2txt):
        """ext_info entries are merged into the document metadata."""
        documents = DocxReader()._load_data(
            Path("sample.docx"), ext_info={"source": "suite", "priority": "high"}
        )
        metadata = documents[0].metadata
        assert metadata["file_name"] == "sample.docx"
        assert metadata["source"] == "suite"
        assert metadata["priority"] == "high"
