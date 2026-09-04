# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_jsonl_file_util.py

"""Unit tests for the JsonFileOps / JsonFileReader / JsonFileWriter helpers."""

import json
import os

import pytest

from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


def write_jsonl_file(tmp_path, rows):
    """Create a .jsonl file containing the given dict rows and return its path."""
    path = tmp_path / "records.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return str(path)


class TestJsonFileOps:
    def test_is_file_exist_rejects_non_jsonl_extension(self):
        with pytest.raises(Exception, match="Unsupported file extension"):
            JsonFileOps.is_file_exist("records.txt")

    def test_is_file_exist_false_for_missing_jsonl(self, tmp_path):
        assert JsonFileOps.is_file_exist(str(tmp_path / "missing.jsonl")) is False

    def test_is_file_exist_true_for_existing_jsonl(self, tmp_path):
        assert JsonFileOps.is_file_exist(write_jsonl_file(tmp_path, [{"a": 1}])) is True


class TestJsonFileReader:
    def test_reader_raises_when_file_missing(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / "nope.jsonl"))
        with pytest.raises(Exception, match="None json file to read"):
            reader.read_json_obj()

    def test_read_json_obj_parses_line(self, tmp_path):
        reader = JsonFileReader(write_jsonl_file(tmp_path, [{"a": 1}, {"b": 2}]))
        assert reader.read_json_obj() == {"a": 1}
        assert reader.read_json_obj() == {"b": 2}

    def test_read_json_obj_returns_none_at_eof(self, tmp_path):
        reader = JsonFileReader(write_jsonl_file(tmp_path, [{"a": 1}]))
        reader.read_json_obj()
        assert reader.read_json_obj() is None

    def test_read_json_obj_list_collects_all(self, tmp_path):
        rows = [{"a": 1}, {"b": 2}, {"c": 3}]
        reader = JsonFileReader(write_jsonl_file(tmp_path, rows))
        assert reader.read_json_obj_list() == rows


class TestJsonFileWriter:
    def _writer(self, tmp_path, name="out"):
        return JsonFileWriter(name, directory=str(tmp_path) + os.sep)

    def test_write_json_obj_writes_one_line(self, tmp_path):
        writer = self._writer(tmp_path)
        writer.write_json_obj({"a": 1})
        writer.outfile_handler.close()
        content = (tmp_path / "out.jsonl").read_text(encoding="utf-8")
        assert content.splitlines() == ['{"a": 1}']

    def test_write_json_query_answer(self, tmp_path):
        writer = self._writer(tmp_path)
        writer.write_json_query_answer("what", "42")
        writer.outfile_handler.close()
        content = (tmp_path / "out.jsonl").read_text(encoding="utf-8")
        assert json.loads(content) == {"query": "what", "answer": "42"}

    def test_write_json_query_answer_list(self, tmp_path):
        writer = self._writer(tmp_path)
        writer.write_json_query_answer_list([("q1", "a1"), ("q2", "a2")])
        writer.outfile_handler.close()
        content = (tmp_path / "out.jsonl").read_text(encoding="utf-8")
        assert len(content.splitlines()) == 2
        assert json.loads(content.splitlines()[1]) == {"query": "q2", "answer": "a2"}
