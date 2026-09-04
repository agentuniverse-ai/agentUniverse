# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_jsonl_file_util.py

"""Unit tests for JsonFileOps, JsonFileReader and JsonFileWriter."""

import json
import os

import pytest

from examples.sample_apps.rag_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


def _write_lines(path, lines):
    with open(path, 'w', encoding='utf-8') as handler:
        handler.writelines(lines)


def test_is_file_exist_accepts_existing_jsonl(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.jsonl')
    _write_lines(data_path, ['{"a": 1}\n'])
    assert JsonFileOps.is_file_exist(data_path)


def test_is_file_exist_false_for_missing_jsonl(tmp_path):
    data_path = os.path.join(str(tmp_path), 'missing.jsonl')
    assert not JsonFileOps.is_file_exist(data_path)


def test_is_file_exist_rejects_unsupported_extension(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.txt')
    _write_lines(data_path, ['plain text'])
    with pytest.raises(Exception, match='Unsupported file extension'):
        JsonFileOps.is_file_exist(data_path)


def test_reader_reads_json_objects_until_eof(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.jsonl')
    _write_lines(data_path, ['{"a": 1}\n', '{"b": 2}\n'])
    reader = JsonFileReader(data_path)
    assert reader.read_json_obj() == {'a': 1}
    assert reader.read_json_obj() == {'b': 2}
    assert reader.read_json_obj() is None


def test_reader_read_json_obj_list_in_order(tmp_path):
    data_path = os.path.join(str(tmp_path), 'sample.jsonl')
    _write_lines(data_path, ['{"a": 1}\n', '{"b": 2}\n'])
    obj_list = JsonFileReader(data_path).read_json_obj_list()
    assert obj_list == [{'a': 1}, {'b': 2}]


def test_reader_raises_when_no_file_to_read(tmp_path):
    reader = JsonFileReader(os.path.join(str(tmp_path), 'missing.jsonl'))
    with pytest.raises(Exception, match='None json file to read'):
        reader.read_json_obj()


def test_writer_write_and_reader_roundtrip(tmp_path):
    output_path = os.path.join(str(tmp_path), 'records.jsonl')
    writer = JsonFileWriter('records', directory=str(tmp_path) + os.sep)
    writer.write_json_obj({'name': '张三', 'age': 30})
    writer.write_json_obj_list([{'name': '李四', 'age': 25}])
    with open(output_path, encoding='utf-8') as handler:
        lines = [json.loads(line) for line in handler]
    assert lines == [{'name': '张三', 'age': 30}, {'name': '李四', 'age': 25}]


def test_writer_write_query_answer_helpers(tmp_path):
    output_path = os.path.join(str(tmp_path), 'qa.jsonl')
    writer = JsonFileWriter('qa', directory=str(tmp_path) + os.sep)
    writer.write_json_query_answer('q1', 'a1')
    writer.write_json_query_answer_list([('q2', 'a2'), ('q3', 'a3')])
    with open(output_path, encoding='utf-8') as handler:
        lines = [json.loads(line) for line in handler]
    assert lines == [
        {'query': 'q1', 'answer': 'a1'},
        {'query': 'q2', 'answer': 'a2'},
        {'query': 'q3', 'answer': 'a3'},
    ]
