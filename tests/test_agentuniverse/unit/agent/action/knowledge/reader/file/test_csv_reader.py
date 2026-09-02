# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 14:00
# @Author  : Yue Wang
# @FileName: test_csv_reader.py
"""Unit tests for CSVReader."""

import io
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.reader.file.csv_reader import CSVReader


@pytest.fixture
def reader():
    """Create a CSVReader instance."""
    return CSVReader()


class TestCSVReader:
    """Test CSVReader parsing behavior."""

    def test_load_data_from_text_file_object(self, reader):
        """A str file-like object is parsed into a single Document."""
        result = reader.load_data(io.StringIO("name,age\nbob,30\n"))
        assert len(result) == 1
        assert result[0].text == "name, age\nbob, 30"
        assert result[0].metadata == {"file_name": "unknown"}

    def test_load_data_from_path_file(self, reader, tmp_path):
        """A local file path is parsed and its file name is recorded."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("a,b\n1,2\n", encoding="utf-8")
        result = reader.load_data(str(csv_file))
        assert result[0].text == "a, b\n1, 2"
        assert result[0].metadata["file_name"] == "data.csv"

    def test_custom_delimiter(self, reader):
        """A custom delimiter is normalized to commas in the output."""
        result = reader.load_data(io.StringIO("a;1\nb;2\n"), delimiter=";")
        assert result[0].text == "a, 1\nb, 2"

    def test_trailing_empty_cells_removed(self, reader):
        """Trailing empty cells are stripped from each row."""
        result = reader.load_data(io.StringIO("a,,\n"))
        assert result[0].text == "a"

    def test_blank_rows_skipped(self, reader):
        """Completely blank rows are dropped from the output."""
        result = reader.load_data(io.StringIO("a\n\nb\n"))
        assert result[0].text == "a\nb"

    def test_ext_info_merged_into_metadata(self, reader):
        """ext_info entries are merged into the document metadata."""
        result = reader.load_data(io.StringIO("x\n1\n"),
                                  ext_info={"source": "unit_test"})
        assert result[0].metadata == {"file_name": "unknown",
                                      "source": "unit_test"}

    def test_missing_path_raises_value_error(self, reader, tmp_path):
        """A nonexistent path raises ValueError with a readable message."""
        with pytest.raises(ValueError, match="Failed to read CSV file"):
            reader.load_data(str(tmp_path / "missing.csv"))
