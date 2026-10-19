# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the example-app TxtFile utilities (file based)."""

import pytest

from examples.sample_apps.toolkit_demo_app.intelligence.utils.common.txt_file_util import TxtFileOps, TxtFileReader


class TestTxtFileOps:
    """Test extension validation and existence checks."""

    def test_unsupported_extension_raises(self, tmp_path):
        path = tmp_path / "notes.jsonl"
        path.write_text("x")
        with pytest.raises(Exception, match="Unsupported file extension"):
            TxtFileOps.is_file_exist(str(path))

    def test_missing_txt_file_returns_false(self):
        assert TxtFileOps.is_file_exist("/tmp/missing_b6.txt") is False

    def test_existing_txt_file_returns_true(self, tmp_path):
        path = tmp_path / "data.txt"
        path.write_text("hi", encoding="utf-8")
        assert TxtFileOps.is_file_exist(str(path)) is True


class TestTxtFileReader:
    """Test reading txt lines."""

    def test_read_txt_obj_lines(self, tmp_path):
        path = tmp_path / "data.txt"
        path.write_text("line one\nline two\n", encoding="utf-8")
        reader = TxtFileReader(str(path))
        assert reader.read_txt_obj() == "line one"
        assert reader.read_txt_obj() == "line two"
        assert reader.read_txt_obj() is None

    def test_missing_file_raises(self):
        reader = TxtFileReader("/tmp/no_such_b6.txt")
        assert reader.file_handler is None
        with pytest.raises(Exception, match="No txt file to read"):
            reader.read_txt_obj()

    def test_read_txt_obj_list(self, tmp_path):
        path = tmp_path / "data.txt"
        path.write_text("a\nb\nc\n", encoding="utf-8")
        assert TxtFileReader(str(path)).read_txt_obj_list() == ["a", "b", "c"]
