# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 12:00
# @Author  : Yue Wang
# @FileName: test_jsonl_file_util.py
"""Unit tests for jsonl_file_util."""

import json
import os

import pytest

from examples.sample_apps.peer_agent_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonFileOps:
    """Test JsonFileOps helpers."""

    def test_is_file_exist_missing(self, tmp_path):
        assert JsonFileOps.is_file_exist(str(tmp_path / "missing.jsonl")) is False

    def test_is_file_exist_present(self, tmp_path):
        target = tmp_path / "present.jsonl"
        target.write_text("{}\n", encoding="utf-8")
        assert JsonFileOps.is_file_exist(str(target)) is True

    def test_is_file_exist_wrong_extension(self, tmp_path):
        with pytest.raises(Exception, match="Unsupported file extension"):
            JsonFileOps.is_file_exist(str(tmp_path / "data.txt"))


class TestJsonFileReader:
    """Test JsonFileReader behaviors."""

    def test_read_json_obj(self, tmp_path):
        target = tmp_path / "objs.jsonl"
        target.write_text('{"a": 1}\n{"b": 2}\n', encoding="utf-8")
        reader = JsonFileReader(str(target))
        assert reader.read_json_obj() == {"a": 1}
        assert reader.read_json_obj() == {"b": 2}
        assert reader.read_json_obj() is None

    def test_read_json_obj_list(self, tmp_path):
        target = tmp_path / "objs.jsonl"
        target.write_text('{"a": 1}\n{"b": 2}\n', encoding="utf-8")
        assert JsonFileReader(str(target)).read_json_obj_list() == [{"a": 1}, {"b": 2}]

    def test_read_bad_json_line_returns_empty(self, tmp_path):
        target = tmp_path / "bad.jsonl"
        target.write_text("not-json\n", encoding="utf-8")
        assert JsonFileReader(str(target)).read_json_obj() == {}

    def test_read_missing_file_raises(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / "none.jsonl"))
        with pytest.raises(Exception, match="None json file to read"):
            reader.read_json_obj()


class TestJsonFileWriter:
    """Test JsonFileWriter round-trips through JsonFileReader."""

    def test_write_and_read_round_trip(self, tmp_path):
        writer = JsonFileWriter("roundtrip", directory=str(tmp_path) + os.sep)
        writer.write_json_obj({"a": 1})
        writer.write_json_query_answer("q1", "a1")
        writer.write_json_query_answer_list([["q2", "a2"]])
        writer.outfile_handler.close()

        written = JsonFileReader(str(tmp_path / "roundtrip.jsonl")).read_json_obj_list()
        assert written == [
            {"a": 1},
            {"query": "q1", "answer": "a1"},
            {"query": "q2", "answer": "a2"},
        ]

    def test_write_json_obj_list(self, tmp_path):
        writer = JsonFileWriter("list", directory=str(tmp_path) + os.sep)
        writer.write_json_obj_list([{"x": 1}, {"y": 2}])
        writer.outfile_handler.close()
        content = (tmp_path / "list.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert [json.loads(line) for line in content] == [{"x": 1}, {"y": 2}]
