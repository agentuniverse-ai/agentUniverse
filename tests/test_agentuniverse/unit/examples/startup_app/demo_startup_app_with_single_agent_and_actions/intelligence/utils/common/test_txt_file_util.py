# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_txt_file_util.py
"""Unit tests for the TXT file utilities in the startup demo example."""

import pytest

from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileOps:
    """Test the TxtFileOps class."""

    def test_rejects_non_txt_extension(self, tmp_path):
        path = tmp_path / 'data.json'
        path.write_text('{}', encoding='utf-8')
        with pytest.raises(Exception, match='Unsupported file extension'):
            TxtFileOps.is_file_exist(str(path))

    def test_existing_txt_file_is_found(self, tmp_path):
        path = tmp_path / 'notes.txt'
        path.write_text('hello\n', encoding='utf-8')
        assert TxtFileOps.is_file_exist(str(path)) is True

    def test_missing_txt_file_is_not_found(self, tmp_path):
        assert TxtFileOps.is_file_exist(str(tmp_path / 'absent.txt')) is False


class TestTxtFileReader:
    """Test the TxtFileReader class."""

    def test_read_single_line_strips_whitespace(self, tmp_path):
        path = tmp_path / 'one.txt'
        path.write_text('  hello world  \n', encoding='utf-8')
        reader = TxtFileReader(str(path))
        assert reader.read_txt_obj() == 'hello world'
        assert reader.read_txt_obj() is None

    def test_read_txt_obj_list(self, tmp_path):
        path = tmp_path / 'many.txt'
        path.write_text('line one\nline two\n', encoding='utf-8')
        assert TxtFileReader(str(path)).read_txt_obj_list() == ['line one', 'line two']

    def test_read_without_file_raises(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / 'absent.txt'))
        with pytest.raises(Exception, match='No txt file to read'):
            reader.read_txt_obj()

    def test_read_empty_file_yields_none(self, tmp_path):
        path = tmp_path / 'empty.txt'
        path.write_text('', encoding='utf-8')
        reader = TxtFileReader(str(path))
        assert reader.read_txt_obj() is None
        assert reader.read_txt_obj_list() == []
