# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_txt_file_util.py

"""Unit tests for the TxtFileOps and TxtFileReader utilities."""

import pytest

from examples.sample_apps.discussion_group_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileOps:
    """Tests for the TxtFileOps helper class."""

    def test_is_file_exist_true_for_existing_txt(self, tmp_path):
        file_path = tmp_path / 'sample.txt'
        file_path.write_text('hello\n', encoding='utf-8')
        assert TxtFileOps.is_file_exist(str(file_path)) is True

    def test_is_file_exist_false_for_missing_txt(self, tmp_path):
        assert TxtFileOps.is_file_exist(str(tmp_path / 'missing.txt')) is False

    def test_is_file_exist_rejects_non_txt_extension(self, tmp_path):
        file_path = tmp_path / 'sample.jsonl'
        file_path.write_text('{"a": 1}\n', encoding='utf-8')
        with pytest.raises(Exception, match='Unsupported file extension'):
            TxtFileOps.is_file_exist(str(file_path))


class TestTxtFileReader:
    """Tests for the TxtFileReader class."""

    def test_read_txt_obj_strips_the_line(self, tmp_path):
        file_path = tmp_path / 'line.txt'
        file_path.write_text('  hello world  \n', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() == 'hello world'

    def test_read_txt_obj_list_reads_all_lines(self, tmp_path):
        file_path = tmp_path / 'multi.txt'
        file_path.write_text('alpha\nbeta\n', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj_list() == ['alpha', 'beta']

    def test_read_txt_obj_returns_none_at_eof(self, tmp_path):
        file_path = tmp_path / 'empty.txt'
        file_path.write_text('', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj() is None

    def test_read_without_existing_file_raises(self, tmp_path):
        reader = TxtFileReader(str(tmp_path / 'missing.txt'))
        with pytest.raises(Exception, match='No txt file to read'):
            reader.read_txt_obj()

    def test_read_txt_obj_list_skips_trailing_empty_line(self, tmp_path):
        file_path = tmp_path / 'tail.txt'
        file_path.write_text('alpha\n', encoding='utf-8')
        reader = TxtFileReader(str(file_path))
        assert reader.read_txt_obj_list() == ['alpha']
