# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_csv_reader.py
"""Unit tests for CSVReader."""

import io
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader

CSV_TEXT = "name,age\nAlice,30\n\nBob,\n"
PARSED_TEXT = "name, age\nAlice, 30\nBob"


class TestCSVReader:
    """Test CSV parsing from real files and file-like objects."""

    @pytest.fixture
    def reader(self):
        return CSVReader()

    @pytest.fixture
    def csv_file(self, tmp_path):
        path = tmp_path / "people.csv"
        path.write_text(CSV_TEXT, encoding="utf-8")
        return path

    def test_parse_path_file(self, reader, csv_file):
        """Rows join with ', '; blank rows and trailing empty cells drop."""
        documents = reader._load_data(csv_file)
        assert len(documents) == 1
        assert documents[0].text == PARSED_TEXT
        assert documents[0].metadata["file_name"] == "people.csv"

    def test_str_path_equals_path_input(self, reader, csv_file):
        """String paths and Path objects parse identically."""
        from_str = reader._load_data(str(csv_file))
        from_path = reader._load_data(csv_file)
        assert len(from_str) == 1
        assert from_str[0].text == from_path[0].text
        assert from_str[0].metadata == from_path[0].metadata

    def test_read_from_stringio(self, reader):
        """A str stream is parsed without a file name attribute."""
        documents = reader._load_data(io.StringIO(CSV_TEXT))
        assert len(documents) == 1
        assert documents[0].text == PARSED_TEXT
        assert documents[0].metadata["file_name"] == "unknown"

    def test_read_from_bytesio(self, reader):
        """A bytes stream is decoded before parsing."""
        documents = reader._load_data(io.BytesIO(CSV_TEXT.encode("utf-8")))
        assert len(documents) == 1
        assert documents[0].text == PARSED_TEXT
        assert documents[0].metadata["file_name"] == "unknown"

    def test_custom_delimiter(self, reader):
        """A non-default delimiter is honored."""
        documents = reader._load_data(io.StringIO("a;b\n1;2"), delimiter=";")
        assert documents[0].text == "a, b\n1, 2"

    def test_ext_info_merged_into_metadata(self, reader, csv_file):
        """ext_info entries are merged into the document metadata."""
        documents = reader._load_data(csv_file, ext_info={"source": "tests"})
        metadata = documents[0].metadata
        assert metadata["file_name"] == "people.csv"
        assert metadata["source"] == "tests"

    def test_missing_file_raises_value_error(self, reader, tmp_path):
        """A missing path is reported as a wrapped ValueError."""
        with pytest.raises(ValueError, match="File not found"):
            reader._load_data(tmp_path / "missing.csv")

    def test_gbk_encoded_file_is_decoded(self, reader, tmp_path):
        """Non-UTF-8 encodings are detected and decoded correctly."""
        path = tmp_path / "people_gbk.csv"
        path.write_bytes("名字,年龄\n张三,30".encode("gbk"))
        documents = reader._load_data(path)
        assert "名字" in documents[0].text
        assert "张三, 30" in documents[0].text
