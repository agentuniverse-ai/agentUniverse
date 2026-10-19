# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/1 16:05
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_txt_file_util.py

"""Unit tests for TxtFileOps/TxtFileReader.

All tests use temporary files only; no network or external services.
"""
import pytest

from examples.sample_apps.multimodal_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileOps:
    """Tests for TxtFileOps.is_file_exist."""

    def test_is_file_exist_true(self, tmp_path):
        file_path = tmp_path / "notes.txt"
        file_path.write_text("hello", encoding="utf-8")
        assert TxtFileOps.is_file_exist(str(file_path)) is True

    def test_is_file_exist_false_when_missing(self, tmp_path):
        assert TxtFileOps.is_file_exist(str(tmp_path / "missing.txt")) is False

    def test_is_file_exist_rejects_other_extensions(self, tmp_path):
        file_path = tmp_path / "notes.json"
        file_path.write_text("{}", encoding="utf-8")
        with pytest.raises(Exception, match="Unsupported file extension"):
            TxtFileOps.is_file_exist(str(file_path))


class TestTxtFileReader:
    """Tests for TxtFileReader."""

    def test_read_txt_obj_strips_line(self, tmp_path):
        file_path = tmp_path / "notes.txt"
        file_path.write_text("  hello world  \n", encoding="utf-8")
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() == "hello world"

    def test_read_txt_obj_returns_none_at_eof(self, tmp_path):
        file_path = tmp_path / "empty.txt"
        file_path.write_text("", encoding="utf-8")
        assert TxtFileReader(str(file_path)).read_txt_obj() is None

    def test_read_txt_obj_list_returns_all_lines(self, tmp_path):
        file_path = tmp_path / "notes.txt"
        file_path.write_text("line one\nline two\n", encoding="utf-8")
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj_list() == ["line one", "line two"]

    def test_read_txt_obj_raises_without_file_handler(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / "not_created.txt"))
        with pytest.raises(Exception, match="No txt file to read"):
            reader.read_txt_obj()
