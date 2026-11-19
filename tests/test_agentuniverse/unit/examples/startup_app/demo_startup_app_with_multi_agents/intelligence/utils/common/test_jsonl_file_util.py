# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_jsonl_file_util.py
import json
import os
import shutil
import tempfile
import unittest

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class JsonFileOpsTest(unittest.TestCase):
    """Test cases for the JsonFileOps helper class."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.jsonl_path = os.path.join(self.tmp_dir, 'sample.jsonl')
        with open(self.jsonl_path, 'w', encoding='utf-8') as f:
            f.write('{"a": 1}\n')

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_is_file_exist_true(self):
        self.assertTrue(JsonFileOps.is_file_exist(self.jsonl_path))

    def test_is_file_exist_false_for_missing_file(self):
        missing = os.path.join(self.tmp_dir, 'missing.jsonl')
        self.assertFalse(JsonFileOps.is_file_exist(missing))

    def test_is_file_exist_rejects_other_extensions(self):
        txt_path = os.path.join(self.tmp_dir, 'sample.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('hello')
        with self.assertRaises(Exception):
            JsonFileOps.is_file_exist(txt_path)


class JsonFileReaderTest(unittest.TestCase):
    """Test cases for the JsonFileReader class."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.jsonl_path = os.path.join(self.tmp_dir, 'data.jsonl')
        with open(self.jsonl_path, 'w', encoding='utf-8') as f:
            f.write('{"name": "a"}\n{"name": "b"}\n')

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_read_json_obj_returns_first_object(self):
        reader = JsonFileReader(self.jsonl_path)
        self.assertEqual(reader.read_json_obj(), {"name": "a"})

    def test_read_json_obj_list_reads_all_objects(self):
        reader = JsonFileReader(self.jsonl_path)
        self.assertEqual(reader.read_json_obj_list(),
                         [{"name": "a"}, {"name": "b"}])

    def test_read_without_existing_file_raises(self):
        reader = JsonFileReader(os.path.join(self.tmp_dir, 'none.jsonl'))
        self.assertIsNone(reader.file_handler)
        with self.assertRaises(Exception):
            reader.read_json_obj()


class JsonFileWriterTest(unittest.TestCase):
    """Test cases for the JsonFileWriter class."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp() + os.sep

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_write_json_obj_then_read_back(self):
        writer = JsonFileWriter('out', directory=self.tmp_dir)
        writer.write_json_obj({"key": "value"})
        reader = JsonFileReader(os.path.join(self.tmp_dir, 'out.jsonl'))
        self.assertEqual(reader.read_json_obj(), {"key": "value"})

    def test_write_json_query_answer(self):
        writer = JsonFileWriter('qa', directory=self.tmp_dir)
        writer.write_json_query_answer('what?', 'answer!')
        reader = JsonFileReader(os.path.join(self.tmp_dir, 'qa.jsonl'))
        self.assertEqual(reader.read_json_obj(),
                         {"query": "what?", "answer": "answer!"})

    def test_file_content_is_valid_json_lines(self):
        writer = JsonFileWriter('lines', directory=self.tmp_dir)
        writer.write_json_obj({"a": 1, "b": 2})
        with open(os.path.join(self.tmp_dir, 'lines.jsonl'), encoding='utf-8') as f:
            line = f.readline()
        self.assertEqual(json.loads(line), {"a": 1, "b": 2})
