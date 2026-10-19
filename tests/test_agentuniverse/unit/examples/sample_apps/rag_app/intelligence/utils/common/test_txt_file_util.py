# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_txt_file_util.py

"""Unit tests for TxtFileOps and TxtFileReader."""

import os

import pytest

from examples.sample_apps.rag_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


def _write_lines(path, lines):
    with open(path, 'w', encoding='utf-8') as handler:
        handler.writelines(lines)


def test_is_file_exist_accepts_existing_txt(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.txt')
    _write_lines(data_path, ['hello\n'])
    assert TxtFileOps.is_file_exist(data_path)


def test_is_file_exist_false_for_missing_txt(tmp_path):
    data_path = os.path.join(str(tmp_path), 'missing.txt')
    assert not TxtFileOps.is_file_exist(data_path)


def test_is_file_exist_rejects_unsupported_extension(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.jsonl')
    _write_lines(data_path, ['{"a": 1}\n'])
    with pytest.raises(Exception, match='Unsupported file extension'):
        TxtFileOps.is_file_exist(data_path)


def test_reader_reads_lines_and_reaches_eof(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.txt')
    _write_lines(data_path, ['hello\n', 'world\n'])
    reader = TxtFileReader(data_path)
    assert reader.read_txt_obj() == 'hello'
    assert reader.read_txt_obj() == 'world'
    assert reader.read_txt_obj() is None


def test_reader_read_txt_obj_list_in_order(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.txt')
    _write_lines(data_path, ['first line\n', 'second line\n', 'third line\n'])
    obj_list = TxtFileReader(data_path).read_txt_obj_list()
    assert obj_list == ['first line', 'second line', 'third line']


def test_reader_returns_empty_list_for_empty_file(tmp_path):
    data_path = os.path.join(str(tmp_path), 'empty.txt')
    _write_lines(data_path, [])
    assert TxtFileReader(data_path).read_txt_obj_list() == []


def test_reader_raises_when_no_file_to_read(tmp_path):
    reader = TxtFileReader(os.path.join(str(tmp_path), 'missing.txt'))
    with pytest.raises(Exception, match='No txt file to read'):
        reader.read_txt_obj()
