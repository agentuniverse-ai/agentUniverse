# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 12:00
# @Author  : Yue Wang
# @FileName: test_txt_file_util.py
"""Unit tests for txt_file_util."""

import pytest

from examples.sample_apps.peer_agent_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileOps:
    """Test TxtFileOps helpers."""

    def test_is_file_exist_missing(self, tmp_path):
        assert TxtFileOps.is_file_exist(str(tmp_path / "missing.txt")) is False

    def test_is_file_exist_present(self, tmp_path):
        target = tmp_path / "present.txt"
        target.write_text("hello\n", encoding="utf-8")
        assert TxtFileOps.is_file_exist(str(target)) is True

    def test_is_file_exist_wrong_extension(self, tmp_path):
        with pytest.raises(Exception, match="Unsupported file extension"):
            TxtFileOps.is_file_exist(str(tmp_path / "data.jsonl"))


class TestTxtFileReader:
    """Test TxtFileReader behaviors."""

    def test_read_txt_obj(self, tmp_path):
        target = tmp_path / "lines.txt"
        target.write_text("line one\nline two\n", encoding="utf-8")
        reader = TxtFileReader(str(target))
        assert reader.read_txt_obj() == "line one"
        assert reader.read_txt_obj() == "line two"
        assert reader.read_txt_obj() is None

    def test_read_txt_obj_strips_blank_line(self, tmp_path):
        target = tmp_path / "blank.txt"
        target.write_text("first\n\n", encoding="utf-8")
        reader = TxtFileReader(str(target))
        assert reader.read_txt_obj() == "first"
        assert reader.read_txt_obj() == ""
        assert reader.read_txt_obj() is None

    def test_read_txt_obj_list(self, tmp_path):
        target = tmp_path / "lines.txt"
        target.write_text("a\nb\nc\n", encoding="utf-8")
        assert TxtFileReader(str(target)).read_txt_obj_list() == ["a", "b", "c"]

    def test_read_missing_file_raises(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / "none.txt"))
        with pytest.raises(Exception, match="No txt file to read"):
            reader.read_txt_obj()
