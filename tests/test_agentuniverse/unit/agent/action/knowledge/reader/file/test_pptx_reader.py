# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_pptx_reader.py
"""Unit tests for PptxReader."""

import sys
import types
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.file.pptx_reader import PptxReader


class _FakeShape:
    """A slide shape carrying a text attribute."""

    def __init__(self, text):
        self.text = text


class _FakePicture:
    """A slide shape without any text attribute."""


class _FakeSlide:
    def __init__(self, shapes):
        self.shapes = shapes


class _FakePresentation:
    """A fake python-pptx presentation recording the opened file."""

    seen_files = []

    def __init__(self, file):
        _FakePresentation.seen_files.append(file)
        self.slides = [
            _FakeSlide([_FakeShape("first"), _FakePicture()]),
            _FakeSlide([_FakeShape("second")]),
        ]


@pytest.fixture
def fake_pptx(monkeypatch):
    """Install a fake pptx module returning _FakePresentation."""
    _FakePresentation.seen_files = []
    module = types.ModuleType("pptx")
    module.Presentation = _FakePresentation
    monkeypatch.setitem(sys.modules, "pptx", module)
    return module


class TestPptxReader:
    """Test the pure loading logic of PptxReader with a fake pptx."""

    def test_missing_pptx_raises_import_error(self, monkeypatch):
        """A clear ImportError is raised when python-pptx is unavailable."""
        monkeypatch.setitem(sys.modules, "pptx", None)
        with pytest.raises(ImportError, match="python-pptx is required"):
            PptxReader()._load_data("deck.pptx")

    def test_text_shapes_become_documents(self, fake_pptx):
        """Each text shape on every slide produces one Document."""
        documents = PptxReader()._load_data(Path("deck.pptx"))
        assert [document.text for document in documents] == ["first", "second"]

    def test_non_text_shapes_are_skipped(self, fake_pptx):
        """Shapes without a text attribute are ignored."""
        documents = PptxReader()._load_data(Path("deck.pptx"))
        assert len(documents) == 2
        assert all("picture" not in document.text for document in documents)

    def test_slide_number_and_file_name_metadata(self, fake_pptx):
        """Metadata records the 1-based slide number and file name."""
        documents = PptxReader()._load_data(Path("deck.pptx"))
        assert [d.metadata["slide_number"] for d in documents] == [1, 2]
        assert all(d.metadata["file_name"] == "deck.pptx" for d in documents)

    def test_str_path_is_converted_to_path(self, fake_pptx):
        """A str input is converted into a pathlib.Path before parsing."""
        PptxReader()._load_data("docs/deck.pptx")
        assert isinstance(_FakePresentation.seen_files[0], Path)
        assert _FakePresentation.seen_files[0].name == "deck.pptx"

    def test_ext_info_merged_into_metadata(self, fake_pptx):
        """ext_info entries are merged into every document metadata."""
        documents = PptxReader()._load_data(
            Path("deck.pptx"), ext_info={"source": "suite"}
        )
        assert all(d.metadata["source"] == "suite" for d in documents)
        assert all(d.metadata["file_name"] == "deck.pptx" for d in documents)
