# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_markdown_reader.py
"""Unit tests for MarkdownReader."""

import sys
from pathlib import Path

import pytest
from langchain_community import document_loaders as lc_document_loaders

from agentuniverse.agent.action.knowledge.reader.file.markdown_reader import (
    MarkdownReader,
)
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_base import ComponentEnum


class _StubLoader:
    """Stand-in that mimics UnstructuredMarkdownLoader behaviour."""
    content = ""
    last_path = None

    def __init__(self, file_path):
        type(self).last_path = file_path

    def load(self):
        return [type("_StubDoc", (), {"page_content": self.content})()]


def _patch_loader(monkeypatch, content):
    """Replace UnstructuredMarkdownLoader with a stub returning content."""
    _StubLoader.content = content
    monkeypatch.setattr(lc_document_loaders, "UnstructuredMarkdownLoader",
                        _StubLoader)


class TestMarkdownReader:
    """Test the MarkdownReader implementation."""

    @pytest.fixture
    def reader(self):
        return MarkdownReader()

    @pytest.fixture
    def md_file(self, tmp_path):
        path = tmp_path / "note.md"
        path.write_text("# Title\n\nbody text", encoding="utf-8")
        return path

    def test_component_defaults(self, reader):
        assert isinstance(reader, Reader)
        assert reader.component_type == ComponentEnum.READER
        assert reader.name is None and reader.description is None

    def test_missing_loader_raises_import_error(self, reader, md_file,
                                                monkeypatch):
        monkeypatch.setitem(sys.modules, "langchain_community.document_loaders",
                            None)
        with pytest.raises(ImportError, match="unstructured is required"):
            reader._load_data(md_file)

    def test_load_data_builds_document(self, reader, md_file, monkeypatch):
        _patch_loader(monkeypatch, "# Title\n\nHello markdown.")
        docs = reader._load_data(md_file)
        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert docs[0].text == "# Title\n\nHello markdown."
        assert docs[0].metadata == {"file_name": "note.md"}

    def test_string_path_is_converted_to_pathlib(self, reader, md_file,
                                                 monkeypatch):
        _patch_loader(monkeypatch, "content")
        reader._load_data(str(md_file))
        assert isinstance(_StubLoader.last_path, Path)
        assert _StubLoader.last_path == md_file

    def test_ext_info_is_merged_and_overrides(self, reader, md_file,
                                              monkeypatch):
        _patch_loader(monkeypatch, "content")
        docs = reader._load_data(md_file, ext_info={"section": 2})
        assert docs[0].metadata["section"] == 2
        assert docs[0].metadata["file_name"] == "note.md"

        docs = reader._load_data(md_file, ext_info={"file_name": "renamed.md"})
        assert docs[0].metadata["file_name"] == "renamed.md"
