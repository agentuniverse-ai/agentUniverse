# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_jsonl_file_util.py
"""Unit tests for the JSONL file utilities in the startup demo example."""

import os

import pytest

from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonFileOps:
    """Test the JsonFileOps class."""

    def test_rejects_non_jsonl_extension(self, tmp_path):
        path = tmp_path / 'data.txt'
        path.write_text('{}', encoding='utf-8')
        with pytest.raises(Exception, match='Unsupported file extension'):
            JsonFileOps.is_file_exist(str(path))

    def test_existing_jsonl_file_is_found(self, tmp_path):
        path = tmp_path / 'records.jsonl'
        path.write_text('{"a": 1}\n', encoding='utf-8')
        assert JsonFileOps.is_file_exist(str(path)) is True


class TestJsonFileReader:
    """Test the JsonFileReader class."""

    def test_read_single_json_object(self, tmp_path):
        path = tmp_path / 'one.jsonl'
        path.write_text('{"query": "q", "answer": "a"}\n', encoding='utf-8')
        reader = JsonFileReader(str(path))
        assert reader.read_json_obj() == {"query": "q", "answer": "a"}
        assert reader.read_json_obj() is None

    def test_read_json_object_list(self, tmp_path):
        path = tmp_path / 'many.jsonl'
        path.write_text('{"id": 1}\n{"id": 2}\n', encoding='utf-8')
        assert JsonFileReader(str(path)).read_json_obj_list() == [{"id": 1}, {"id": 2}]

    def test_read_without_file_raises(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / 'absent.jsonl'))
        with pytest.raises(Exception, match='None json file to read'):
            reader.read_json_obj()

    def test_malformed_line_yields_empty_dict(self, tmp_path):
        path = tmp_path / 'bad.jsonl'
        path.write_text('not-json\n', encoding='utf-8')
        assert JsonFileReader(str(path)).read_json_obj() == {}


class TestJsonFileWriter:
    """Test the JsonFileWriter class."""

    def test_write_json_object_and_read_back(self, tmp_path):
        directory = str(tmp_path) + os.sep
        writer = JsonFileWriter('output', extension='jsonl', directory=directory)
        writer.write_json_obj({"query": "q", "answer": "a"})
        writer.outfile_handler.close()
        reader = JsonFileReader(str(tmp_path / 'output.jsonl'))
        assert reader.read_json_obj() == {"query": "q", "answer": "a"}

    def test_write_json_query_answer_list(self, tmp_path):
        directory = str(tmp_path) + os.sep
        writer = JsonFileWriter('output', extension='jsonl', directory=directory)
        writer.write_json_query_answer_list([["q1", "a1"], ["q2", "a2"]])
        writer.outfile_handler.close()
        reader = JsonFileReader(str(tmp_path / 'output.jsonl'))
        assert reader.read_json_obj_list() == [
            {"query": "q1", "answer": "a1"},
            {"query": "q2", "answer": "a2"},
        ]
