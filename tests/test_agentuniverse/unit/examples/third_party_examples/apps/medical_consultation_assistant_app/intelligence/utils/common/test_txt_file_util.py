# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the txt file utilities of the medical consultation app."""

import pytest

from examples.third_party_examples.apps.medical_consultation_assistant_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileOps:
    def test_is_file_exist_rejects_wrong_extension(self):
        with pytest.raises(Exception, match="Unsupported file extension"):
            TxtFileOps.is_file_exist("/tmp/sample.jsonl")

    def test_is_file_exist_reflects_file_presence(self, tmp_path):
        path = tmp_path / "notes.txt"
        assert TxtFileOps.is_file_exist(str(path)) is False
        path.write_text("hello\n", encoding="utf-8")
        assert TxtFileOps.is_file_exist(str(path)) is True


class TestTxtFileReader:
    def _write(self, tmp_path, content):
        path = tmp_path / "notes.txt"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def test_read_txt_obj_returns_stripped_lines(self, tmp_path):
        file_path = self._write(tmp_path, "line one\nline two\n")
        reader = TxtFileReader(file_path)
        assert reader.read_txt_obj() == "line one"
        assert reader.read_txt_obj() == "line two"
        assert reader.read_txt_obj() is None

    def test_read_txt_obj_strips_whitespace(self, tmp_path):
        file_path = self._write(tmp_path, "  padded  \n")
        assert TxtFileReader(file_path).read_txt_obj() == "padded"

    def test_read_txt_obj_list(self, tmp_path):
        file_path = self._write(tmp_path, "a\nb\nc\n")
        assert TxtFileReader(file_path).read_txt_obj_list() == ["a", "b", "c"]

    def test_read_empty_file_returns_none(self, tmp_path):
        file_path = self._write(tmp_path, "")
        reader = TxtFileReader(file_path)
        assert reader.read_txt_obj() is None
        assert reader.read_txt_obj_list() == []

    def test_missing_file_raises_on_read(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / "missing.txt"))
        with pytest.raises(Exception, match="No txt file to read"):
            reader.read_txt_obj()
