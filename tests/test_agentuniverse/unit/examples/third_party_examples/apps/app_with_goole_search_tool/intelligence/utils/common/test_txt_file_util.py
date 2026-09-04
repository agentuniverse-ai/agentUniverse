# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_txt_file_util.py

"""Unit tests for the TxtFileOps / TxtFileReader helpers."""

import pytest

from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


def write_txt_file(tmp_path, lines):
    """Create a .txt file containing the given lines and return its path."""
    path = tmp_path / "records.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


class TestTxtFileOps:
    def test_is_file_exist_rejects_non_txt_extension(self):
        with pytest.raises(Exception, match="Unsupported file extension"):
            TxtFileOps.is_file_exist("records.jsonl")

    def test_is_file_exist_false_for_missing_txt(self, tmp_path):
        assert TxtFileOps.is_file_exist(str(tmp_path / "missing.txt")) is False

    def test_is_file_exist_true_for_existing_txt(self, tmp_path):
        assert TxtFileOps.is_file_exist(write_txt_file(tmp_path, ["hello"])) is True


class TestTxtFileReader:
    def test_reader_raises_when_file_missing(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / "nope.txt"))
        with pytest.raises(Exception, match="No txt file to read"):
            reader.read_txt_obj()

    def test_read_txt_obj_strips_line(self, tmp_path):
        reader = TxtFileReader(write_txt_file(tmp_path, ["line one", "  line two  "]))
        assert reader.read_txt_obj() == "line one"
        assert reader.read_txt_obj() == "line two"

    def test_read_txt_obj_returns_none_at_eof(self, tmp_path):
        reader = TxtFileReader(write_txt_file(tmp_path, ["only line"]))
        reader.read_txt_obj()
        assert reader.read_txt_obj() is None

    def test_read_txt_obj_list_collects_all(self, tmp_path):
        lines = ["first", "second", "third"]
        reader = TxtFileReader(write_txt_file(tmp_path, lines))
        assert reader.read_txt_obj_list() == lines
