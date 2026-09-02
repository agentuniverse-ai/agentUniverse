# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_file_reader.py
"""Unit tests for FileReader."""

from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader
from agentuniverse.agent.action.knowledge.reader.file.file_reader import (
    DEFAULT_FILE_READERS,
    FileReader,
)
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document

CSV_TEXT = "name,age\nAlice,30\n\nBob,\n"


class _CapturingReader(Reader):
    """Fake reader recording every dispatched file and ext_info."""

    def _load_data(self, file, ext_info=None):
        return [Document(text="dispatched:" + Path(file).name,
                         metadata={"file_name": Path(file).name, "ext": ext_info})]


class TestFileReader:
    """Test the suffix-to-reader mapping and file dispatch logic."""

    @pytest.fixture
    def reader(self):
        return FileReader()

    @pytest.fixture
    def csv_file(self, tmp_path):
        path = tmp_path / "people.csv"
        path.write_text(CSV_TEXT, encoding="utf-8")
        return path

    def test_default_file_readers_cover_expected_suffixes(self):
        """DEFAULT_FILE_READERS maps common suffixes to Reader subclasses."""
        for suffix in (".txt", ".md", ".markdown", ".csv", ".docx", ".pptx"):
            assert suffix in DEFAULT_FILE_READERS
        assert all(issubclass(cls, Reader) for cls in DEFAULT_FILE_READERS.values())

    def test_default_file_readers_values(self):
        """Specific suffixes are bound to the expected reader classes."""
        assert DEFAULT_FILE_READERS[".txt"] is TxtReader
        assert DEFAULT_FILE_READERS[".csv"] is CSVReader
        assert DEFAULT_FILE_READERS[".md"] is DEFAULT_FILE_READERS[".markdown"]

    def test_file_readers_attribute_equals_default_mapping(self, reader):
        """An instance maps the same suffixes as the module default."""
        assert reader.file_readers == DEFAULT_FILE_READERS

    def test_load_supported_csv_file(self, reader, csv_file):
        """A registered suffix yields the reader's documents."""
        documents = reader._load_data([csv_file])
        assert len(documents) == 1
        assert documents[0].text == "name, age\nAlice, 30\nBob"
        assert documents[0].metadata["file_name"] == "people.csv"

    def test_uppercase_suffix_is_lowercased(self, reader, tmp_path):
        """Suffix matching is case-insensitive through .lower()."""
        path = tmp_path / "DATA.CSV"
        path.write_text("a,b\n1,2", encoding="utf-8")
        documents = reader._load_data([path])
        assert len(documents) == 1
        assert documents[0].metadata["file_name"] == "DATA.CSV"

    def test_unknown_suffix_is_skipped(self, reader, tmp_path):
        """Files with an unregistered suffix produce no documents."""
        path = tmp_path / "notes.unknown"
        path.write_text("ignored", encoding="utf-8")
        assert reader._load_data([path]) == []
        assert reader._load_data([]) == []

    def test_ext_info_forwarded_and_merged(self, reader, csv_file):
        """ext_info is passed down and merged into document metadata."""
        documents = reader._load_data([csv_file], ext_info={"source": "tests"})
        assert documents[0].metadata["source"] == "tests"
        assert documents[0].metadata["file_name"] == "people.csv"

    def test_custom_file_readers_dispatch(self):
        """Only registered suffixes dispatch, receiving file and ext_info."""
        custom = FileReader(file_readers={".cap": _CapturingReader})
        documents = custom._load_data([Path("a.cap"), Path("b.zzz")],
                                      ext_info={"k": "v"})
        assert len(documents) == 1
        assert documents[0].text == "dispatched:a.cap"
        assert documents[0].metadata["ext"] == {"k": "v"}
