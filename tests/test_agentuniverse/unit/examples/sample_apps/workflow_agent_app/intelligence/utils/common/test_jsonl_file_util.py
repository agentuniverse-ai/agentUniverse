# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_jsonl_file_util.py
"""Unit tests for examples jsonl file utilities (JsonFileOps / JsonFileReader / JsonFileWriter)."""

import json
import os

import pytest

from examples.sample_apps.workflow_agent_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonFileOps:
    """Tests for JsonFileOps.is_file_exist extension validation."""

    def test_unsupported_extension_raises(self):
        with pytest.raises(Exception) as exc_info:
            JsonFileOps.is_file_exist('/tmp/sample.txt')
        assert 'Unsupported file extension' in str(exc_info.value)

    def test_missing_jsonl_file_returns_false(self, tmp_path):
        assert JsonFileOps.is_file_exist(str(tmp_path / 'not_there.jsonl')) is False

    def test_existing_jsonl_file_returns_true(self, tmp_path):
        file_path = tmp_path / 'sample.jsonl'
        file_path.write_text('{"k": "v"}\n', encoding='utf-8')
        assert JsonFileOps.is_file_exist(str(file_path)) is True


class TestJsonFileReader:
    """Tests for JsonFileReader read behavior."""

    def test_read_json_obj_returns_none_on_eof(self, tmp_path):
        file_path = tmp_path / 'sample.jsonl'
        file_path.write_text('{"a": 1}\n', encoding='utf-8')
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj() == {'a': 1}
        assert reader.read_json_obj() is None

    def test_read_json_obj_list_returns_all_objects(self, tmp_path):
        file_path = tmp_path / 'sample.jsonl'
        file_path.write_text('{"a": 1}\n{"b": 2}\n', encoding='utf-8')
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj_list() == [{'a': 1}, {'b': 2}]

    def test_malformed_line_returns_empty_dict(self, tmp_path):
        file_path = tmp_path / 'sample.jsonl'
        file_path.write_text('not-a-json\n', encoding='utf-8')
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj() == {}

    def test_read_missing_file_raises(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / 'missing.jsonl'))
        with pytest.raises(Exception) as exc_info:
            reader.read_json_obj()
        assert 'None json file to read' in str(exc_info.value)


class TestJsonFileWriter:
    """Tests for JsonFileWriter write and round-trip behavior."""

    @pytest.fixture
    def out_dir(self, tmp_path):
        return str(tmp_path) + os.sep

    def test_write_and_read_back(self, out_dir):
        writer = JsonFileWriter('demo', directory=out_dir)
        writer.write_json_obj({'query': 'q1', 'answer': 'a1'})
        reader = JsonFileReader(out_dir + 'demo.jsonl')
        assert reader.read_json_obj() == {'query': 'q1', 'answer': 'a1'}

    def test_write_json_query_answer(self, out_dir):
        writer = JsonFileWriter('demo', directory=out_dir)
        writer.write_json_query_answer('who', 'alice')
        with open(out_dir + 'demo.jsonl', encoding='utf-8') as f:
            assert json.loads(f.readline()) == {'query': 'who', 'answer': 'alice'}
