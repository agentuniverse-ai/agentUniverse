# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_txt_file_util.py
"""Unit tests for examples txt file utilities (TxtFileOps / TxtFileReader)."""

import os

import pytest

from examples.sample_apps.workflow_agent_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileOps:
    """Tests for TxtFileOps.is_file_exist extension validation."""

    def test_unsupported_extension_raises(self):
        with pytest.raises(Exception) as exc_info:
            TxtFileOps.is_file_exist('/tmp/sample.json')
        assert 'Unsupported file extension' in str(exc_info.value)

    def test_missing_txt_file_returns_false(self, tmp_path):
        assert TxtFileOps.is_file_exist(str(tmp_path / 'not_there.txt')) is False

    def test_existing_txt_file_returns_true(self, tmp_path):
        file_path = tmp_path / 'sample.txt'
        file_path.write_text('hello\n', encoding='utf-8')
        assert TxtFileOps.is_file_exist(str(file_path)) is True


class TestTxtFileReader:
    """Tests for TxtFileReader read behavior."""

    def test_read_txt_obj_strips_line(self, tmp_path):
        file_path = tmp_path / 'sample.txt'
        file_path.write_text('  hello world  \n', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() == 'hello world'

    def test_read_txt_obj_returns_none_on_eof(self, tmp_path):
        file_path = tmp_path / 'sample.txt'
        file_path.write_text('line1\nline2\n', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() == 'line1'
        assert reader.read_txt_obj() == 'line2'
        assert reader.read_txt_obj() is None

    def test_read_txt_obj_list_returns_all_lines(self, tmp_path):
        file_path = tmp_path / 'sample.txt'
        file_path.write_text('alpha\nbeta\ngamma\n', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj_list() == ['alpha', 'beta', 'gamma']

    def test_read_txt_obj_list_skips_blank_lines(self, tmp_path):
        file_path = tmp_path / 'sample.txt'
        file_path.write_text('alpha\n\nbeta\n', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj_list() == ['alpha', '', 'beta']

    def test_read_missing_file_raises(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / 'missing.txt'))
        with pytest.raises(Exception) as exc_info:
            reader.read_txt_obj()
        assert 'No txt file to read' in str(exc_info.value)

    def test_empty_file_reads_none(self, tmp_path):
        file_path = tmp_path / 'empty.txt'
        file_path.write_text('', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() is None
        assert reader.read_txt_obj_list() == []
