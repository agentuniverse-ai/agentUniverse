# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/1 21:09
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_jsonl_file_util.py

"""Unit tests for JsonFileOps/JsonFileReader/JsonFileWriter.

All tests use temporary files only; no network or external services.
"""
import os

import pytest

from examples.sample_apps.multimodal_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonFileOps:
    """Tests for JsonFileOps.is_file_exist."""

    def test_is_file_exist_true(self, tmp_path):
        file_path = tmp_path / "records.jsonl"
        file_path.write_text('{"a": 1}\n', encoding="utf-8")
        assert JsonFileOps.is_file_exist(str(file_path)) is True

    def test_is_file_exist_false_when_missing(self, tmp_path):
        assert JsonFileOps.is_file_exist(str(tmp_path / "missing.jsonl")) is False

    def test_is_file_exist_rejects_other_extensions(self, tmp_path):
        file_path = tmp_path / "records.txt"
        file_path.write_text("hello", encoding="utf-8")
        with pytest.raises(Exception, match="Unsupported file extension"):
            JsonFileOps.is_file_exist(str(file_path))


class TestJsonFileReader:
    """Tests for JsonFileReader."""

    def test_read_json_obj_returns_none_at_eof(self, tmp_path):
        file_path = tmp_path / "empty.jsonl"
        file_path.write_text("", encoding="utf-8")
        assert JsonFileReader(str(file_path)).read_json_obj() is None

    def test_read_json_obj_list_returns_all_objects(self, tmp_path):
        lines = ['{"query": "q1", "answer": "a1"}', '{"query": "q2", "answer": "a2"}']
        file_path = tmp_path / "records.jsonl"
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj_list() == [
            {"query": "q1", "answer": "a1"},
            {"query": "q2", "answer": "a2"},
        ]

    def test_read_json_obj_raises_without_file_handler(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / "not_created.jsonl"))
        with pytest.raises(Exception, match="None json file to read"):
            reader.read_json_obj()


class TestJsonFileWriter:
    """Tests for JsonFileWriter."""

    def test_write_json_obj_produces_one_line(self, tmp_path):
        writer = JsonFileWriter("records", directory=str(tmp_path) + os.sep)
        writer.write_json_obj({"query": "q1", "answer": "a1"})
        writer.outfile_handler.close()
        content = (tmp_path / "records.jsonl").read_text(encoding="utf-8")
        assert content == '{"query": "q1", "answer": "a1"}\n'

    def test_write_json_query_answer_list_roundtrip(self, tmp_path):
        writer = JsonFileWriter("records", directory=str(tmp_path) + os.sep)
        writer.write_json_query_answer_list([("q1", "a1"), ("q2", "a2")])
        writer.outfile_handler.close()
        reader = JsonFileReader(str(tmp_path / "records.jsonl"))
        assert reader.read_json_obj_list() == [
            {"query": "q1", "answer": "a1"},
            {"query": "q2", "answer": "a2"},
        ]
