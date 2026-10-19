# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_jsonl_file_util.py

"""Unit tests for the jsonl_file_util example helpers."""

import os
import shutil
import tempfile
import unittest

from examples.startup_app.demo_startup_app_with_single_agent.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps, JsonFileReader, JsonFileWriter)


class TestJsonlFileUtil(unittest.TestCase):
    """Pure file-handling behaviors of the jsonl utilities."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _path(self, name):
        return os.path.join(self.tmp_dir, name)

    def test_is_file_exist_accepts_jsonl(self):
        path = self._path('sample.jsonl')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{}\n')
        self.assertTrue(JsonFileOps.is_file_exist(path))
        self.assertFalse(JsonFileOps.is_file_exist(self._path('missing.jsonl')))

    def test_is_file_exist_rejects_other_extensions(self):
        with self.assertRaises(Exception):
            JsonFileOps.is_file_exist(self._path('sample.txt'))

    def test_reader_missing_file_raises(self):
        with self.assertRaises(Exception):
            JsonFileReader(self._path('none.jsonl')).read_json_obj()

    def test_reader_parses_json_line(self):
        path = self._path('sample.jsonl')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{"query": "q1", "answer": "a1"}\n')
        self.assertEqual(JsonFileReader(path).read_json_obj(),
                         {"query": "q1", "answer": "a1"})

    def test_reader_returns_none_at_eof(self):
        path = self._path('sample.jsonl')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{"a": 1}\n')
        reader = JsonFileReader(path)
        self.assertIsNotNone(reader.read_json_obj())
        self.assertIsNone(reader.read_json_obj())

    def test_reader_invalid_line_yields_empty_dict(self):
        path = self._path('bad.jsonl')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('not a json line\n')
        self.assertEqual(JsonFileReader(path).read_json_obj(), {})

    def test_reader_read_obj_list(self):
        path = self._path('sample.jsonl')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{"a": 1}\n{"b": 2}\n')
        self.assertEqual(JsonFileReader(path).read_json_obj_list(),
                         [{"a": 1}, {"b": 2}])

    def test_writer_round_trip(self):
        output = self._path('out')
        JsonFileWriter(output_file_name='out', extension='jsonl',
                       directory=self.tmp_dir + '/').write_json_query_answer('q', 'a')
        reader = JsonFileReader(output + '.jsonl')
        self.assertEqual(reader.read_json_obj(), {"query": "q", "answer": "a"})


if __name__ == '__main__':
    unittest.main()
