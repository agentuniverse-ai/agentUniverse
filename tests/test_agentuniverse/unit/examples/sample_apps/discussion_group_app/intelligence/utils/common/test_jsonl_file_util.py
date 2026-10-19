# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_jsonl_file_util.py

"""Unit tests for the JsonFileOps / JsonFileReader / JsonFileWriter utilities."""

import os

import pytest

from examples.sample_apps.discussion_group_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonFileOps:
    """Tests for the JsonFileOps helper class."""

    def test_is_file_exist_true_for_existing_jsonl(self, tmp_path):
        file_path = tmp_path / 'sample.jsonl'
        file_path.write_text('{"a": 1}\n', encoding='utf-8')
        assert JsonFileOps.is_file_exist(str(file_path)) is True

    def test_is_file_exist_false_for_missing_jsonl(self, tmp_path):
        assert JsonFileOps.is_file_exist(str(tmp_path / 'missing.jsonl')) is False

    def test_is_file_exist_rejects_non_jsonl_extension(self, tmp_path):
        file_path = tmp_path / 'sample.txt'
        file_path.write_text('hello', encoding='utf-8')
        with pytest.raises(Exception, match='Unsupported file extension'):
            JsonFileOps.is_file_exist(str(file_path))


class TestJsonFileReader:
    """Tests for the JsonFileReader class."""

    def test_read_json_obj_returns_single_object(self, tmp_path):
        file_path = tmp_path / 'single.jsonl'
        file_path.write_text('{"query": "q1", "answer": "a1"}\n', encoding='utf-8')
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj() == {"query": "q1", "answer": "a1"}

    def test_read_json_obj_list_reads_all_lines(self, tmp_path):
        file_path = tmp_path / 'multi.jsonl'
        file_path.write_text('{"i": 1}\n{"i": 2}\n', encoding='utf-8')
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj_list() == [{"i": 1}, {"i": 2}]

    def test_read_without_existing_file_raises(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / 'missing.jsonl'))
        with pytest.raises(Exception, match='None json file to read'):
            reader.read_json_obj()


class TestJsonFileWriter:
    """Tests for the JsonFileWriter class."""

    def test_write_and_read_back_round_trip(self, tmp_path):
        directory = str(tmp_path) + os.sep
        writer = JsonFileWriter('output', extension='jsonl', directory=directory)
        writer.write_json_obj({"query": "q1", "answer": "a1"})
        writer.write_json_obj({"query": "q2", "answer": "a2"})

        out_path = os.path.join(str(tmp_path), 'output.jsonl')
        reader = JsonFileReader(out_path)
        assert reader.read_json_obj_list() == [{"query": "q1", "answer": "a1"},
                                               {"query": "q2", "answer": "a2"}]

    def test_write_json_query_answer_writes_query_answer_pair(self, tmp_path):
        directory = str(tmp_path) + os.sep
        writer = JsonFileWriter('qa', extension='jsonl', directory=directory)
        writer.write_json_query_answer('question', 'answer')

        out_path = os.path.join(str(tmp_path), 'qa.jsonl')
        reader = JsonFileReader(out_path)
        assert reader.read_json_obj() == {"query": "question", "answer": "answer"}
