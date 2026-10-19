# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the txt file utility helpers.

Covers the extension validation in ``TxtFileOps`` and the line-by-line reading
behaviour of ``TxtFileReader`` (stripping, blank lines and EOF).  All tests use
temporary directories.
"""

import pytest

from examples.sample_standard_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileOps:
    def test_rejects_non_txt_extension(self):
        with pytest.raises(Exception, match="Unsupported file extension"):
            TxtFileOps.is_file_exist("data.json")

    def test_existence_depends_on_file_on_disk(self, tmp_path):
        missing = tmp_path / "missing.txt"
        assert not TxtFileOps.is_file_exist(str(missing))
        missing.write_text("hello", encoding="utf-8")
        assert TxtFileOps.is_file_exist(str(missing))


class TestTxtFileReader:
    def test_missing_file_raises_on_read(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / "missing.txt"))
        with pytest.raises(Exception, match="No txt file to read"):
            reader.read_txt_obj()

    def test_reads_lines_until_eof(self, tmp_path):
        file_path = tmp_path / "data.txt"
        file_path.write_text("first line\nsecond line\n", encoding="utf-8")
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() == "first line"
        assert reader.read_txt_obj() == "second line"
        assert reader.read_txt_obj() is None

    def test_read_txt_obj_list_returns_all_lines(self, tmp_path):
        file_path = tmp_path / "data.txt"
        file_path.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj_list() == ["alpha", "beta", "gamma"]

    def test_lines_are_stripped_of_whitespace(self, tmp_path):
        file_path = tmp_path / "data.txt"
        file_path.write_text("  padded  \n\tindented\n", encoding="utf-8")
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() == "padded"
        assert reader.read_txt_obj() == "indented"

    def test_blank_line_is_read_as_empty_string(self, tmp_path):
        file_path = tmp_path / "data.txt"
        file_path.write_text("first\n\nthird\n", encoding="utf-8")
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj_list() == ["first", "", "third"]
