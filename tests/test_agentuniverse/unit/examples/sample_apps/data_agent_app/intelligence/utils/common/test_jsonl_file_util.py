# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the example-app JsonFile utilities (file based)."""

import json
import os
import pytest

from examples.sample_apps.data_agent_app.intelligence.utils.common.jsonl_file_util import JsonFileOps, JsonFileReader, JsonFileWriter


class TestJsonFileOps:
    """Test extension validation and existence checks."""

    def test_unsupported_extension_raises(self, tmp_path):
        path = tmp_path / "notes.txt"
        path.write_text("x")
        with pytest.raises(Exception, match="Unsupported file extension"):
            JsonFileOps.is_file_exist(str(path))

    def test_missing_jsonl_file_returns_false(self):
        assert JsonFileOps.is_file_exist("/tmp/missing_b6.jsonl") is False

    def test_existing_jsonl_file_returns_true(self, tmp_path):
        path = tmp_path / "data.jsonl"
        path.write_text("{}\n", encoding="utf-8")
        assert JsonFileOps.is_file_exist(str(path)) is True


class TestJsonFileReader:
    """Test reading jsonl objects."""

    def test_read_json_obj_and_end(self, tmp_path):
        path = tmp_path / "data.jsonl"
        path.write_text(json.dumps({"a": 1}) + "\n" +
                        json.dumps({"a": 2}) + "\n", encoding="utf-8")
        reader = JsonFileReader(str(path))
        assert reader.read_json_obj() == {"a": 1}
        assert reader.read_json_obj() == {"a": 2}
        assert reader.read_json_obj() is None

    def test_missing_file_raises(self):
        reader = JsonFileReader("/tmp/no_such_b6.jsonl")
        assert reader.file_handler is None
        with pytest.raises(Exception, match="None json file to read"):
            reader.read_json_obj()

    def test_read_json_obj_list(self, tmp_path):
        path = tmp_path / "data.jsonl"
        path.write_text(json.dumps({"q": "hi"}) + "\n" +
                        json.dumps({"q": "bye"}) + "\n", encoding="utf-8")
        assert JsonFileReader(str(path)).read_json_obj_list() == [
            {"q": "hi"}, {"q": "bye"}]


class TestJsonFileWriter:
    """Test writing jsonl objects."""

    def test_write_and_readback(self, tmp_path):
        writer = JsonFileWriter(output_file_name="out",
                                extension="jsonl",
                                directory=str(tmp_path) + os.sep)
        writer.write_json_obj({"k": 1})
        writer.write_json_obj({"k": 2})
        writer.outfile_handler.close()
        out_path = os.path.join(str(tmp_path), "out.jsonl")
        assert JsonFileReader(out_path).read_json_obj_list() == [
            {"k": 1}, {"k": 2}]

    def test_write_json_obj_list(self, tmp_path):
        writer = JsonFileWriter(output_file_name="list",
                                extension="jsonl",
                                directory=str(tmp_path) + os.sep)
        writer.write_json_obj_list([{"n": 1}, {"n": 2}, {"n": 3}])
        writer.outfile_handler.close()
        out_path = os.path.join(str(tmp_path), "list.jsonl")
        assert JsonFileReader(out_path).read_json_obj_list() == [
            {"n": 1}, {"n": 2}, {"n": 3}]
