# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the JSONL file utility helpers.

Covers extension validation in ``JsonFileOps``, the line-by-line decoding of
``JsonFileReader`` (including malformed lines and EOF) and the write/read
round-trip behaviour of ``JsonFileWriter``.  All tests use temp directories.
"""

import json
import os

import pytest

from examples.sample_standard_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonFileOps:
    def test_rejects_non_jsonl_extension(self):
        with pytest.raises(Exception, match="Unsupported file extension"):
            JsonFileOps.is_file_exist("data.txt")

    def test_existence_depends_on_file_on_disk(self, tmp_path):
        missing = tmp_path / "missing.jsonl"
        assert not JsonFileOps.is_file_exist(str(missing))
        missing.write_text("", encoding="utf-8")
        assert JsonFileOps.is_file_exist(str(missing))


class TestJsonFileReader:
    def test_missing_file_raises_on_read(self, tmp_path):
        reader = JsonFileReader(str(tmp_path / "missing.jsonl"))
        with pytest.raises(Exception, match="None json file to read"):
            reader.read_json_obj()

    def test_reads_json_objects_until_eof(self, tmp_path):
        file_path = tmp_path / "data.jsonl"
        file_path.write_text('{"a": 1}\n{"b": 2}\n{"c": 3}\n', encoding="utf-8")
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj_list() == [{"a": 1}, {"b": 2}, {"c": 3}]
        assert reader.read_json_obj() is None

    def test_malformed_line_falls_back_to_empty_object(self, tmp_path):
        file_path = tmp_path / "data.jsonl"
        file_path.write_text("not-a-json-line\n", encoding="utf-8")
        reader = JsonFileReader(str(file_path))
        assert reader.read_json_obj() == {}


class TestJsonFileWriter:
    def test_write_and_read_round_trip(self, tmp_path):
        writer = JsonFileWriter("output", directory=str(tmp_path) + os.sep)
        writer.write_json_obj({"query": "q1", "answer": "a1"})
        writer.write_json_obj({"query": "q2", "answer": "a2"})
        writer.outfile_handler.close()

        reader = JsonFileReader(str(tmp_path / "output.jsonl"))
        assert reader.read_json_obj_list() == [
            {"query": "q1", "answer": "a1"},
            {"query": "q2", "answer": "a2"},
        ]

    def test_write_query_answer_uses_expected_shape(self, tmp_path):
        writer = JsonFileWriter("qa", directory=str(tmp_path) + os.sep)
        writer.write_json_query_answer("question", "answer")
        writer.outfile_handler.close()

        raw = (tmp_path / "qa.jsonl").read_text(encoding="utf-8")
        assert json.loads(raw) == {"query": "question", "answer": "answer"}

    def test_write_json_obj_list_and_nested_dirs(self, tmp_path):
        nested = tmp_path / "nested" / "dir"
        writer = JsonFileWriter("list", directory=str(nested) + os.sep)
        writer.write_json_obj_list([{"i": 1}, {"i": 2}])
        writer.outfile_handler.close()

        assert (nested / "list.jsonl").exists()
        lines = (nested / "list.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[1]) == {"i": 2}
