# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the jsonl file utilities of the medical consultation app."""

import json

import pytest

from examples.third_party_examples.apps.medical_consultation_assistant_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonFileOps:
    def test_is_file_exist_rejects_wrong_extension(self):
        with pytest.raises(Exception, match="Unsupported file extension"):
            JsonFileOps.is_file_exist("/tmp/sample.txt")

    def test_is_file_exist_reflects_file_presence(self, tmp_path):
        path = tmp_path / "data.jsonl"
        assert JsonFileOps.is_file_exist(str(path)) is False
        path.write_text("{}\n", encoding="utf-8")
        assert JsonFileOps.is_file_exist(str(path)) is True


class TestJsonFileReader:
    def _write(self, tmp_path, lines):
        path = tmp_path / "data.jsonl"
        path.write_text("".join(lines), encoding="utf-8")
        return str(path)

    def test_read_json_obj_returns_objects_in_order(self, tmp_path):
        file_path = self._write(tmp_path, ['{"a": 1}\n', '{"b": 2}\n'])
        reader = JsonFileReader(file_path)
        assert reader.read_json_obj() == {"a": 1}
        assert reader.read_json_obj() == {"b": 2}
        assert reader.read_json_obj() is None

    def test_read_json_obj_list(self, tmp_path):
        file_path = self._write(tmp_path, ['{"a": 1}\n', '{"b": 2}\n'])
        assert JsonFileReader(file_path).read_json_obj_list() == [{"a": 1}, {"b": 2}]

    def test_corrupt_line_returns_empty_object(self, tmp_path):
        file_path = self._write(tmp_path, ["not json\n", '{"b": 2}\n'])
        reader = JsonFileReader(file_path)
        assert reader.read_json_obj() == {}
        assert reader.read_json_obj() == {"b": 2}

    def test_missing_file_raises_on_read(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / "missing.jsonl"))
        with pytest.raises(Exception, match="None json file to read"):
            reader.read_json_obj()


class TestJsonFileWriter:
    def test_write_json_obj(self, tmp_path):
        writer = JsonFileWriter("out", directory=str(tmp_path) + "/")
        writer.write_json_obj({"x": 1})
        writer.write_json_query_answer("q", "a")
        lines = (tmp_path / "out.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0]) == {"x": 1}
        assert json.loads(lines[1]) == {"query": "q", "answer": "a"}

    def test_write_json_obj_list_and_query_answer_list(self, tmp_path):
        writer = JsonFileWriter("out2", directory=str(tmp_path) + "/")
        writer.write_json_obj_list([{"i": 1}, {"i": 2}])
        writer.write_json_query_answer_list([("q1", "a1"), ("q2", "a2")])
        objs = JsonFileReader(str(tmp_path / "out2.jsonl")).read_json_obj_list()
        assert objs == [{"i": 1}, {"i": 2}, {"query": "q1", "answer": "a1"}, {"query": "q2", "answer": "a2"}]

