# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_jsonl_file_util.py

"""Unit tests for the JsonFileOps / JsonFileReader / JsonFileWriter example utilities."""

import os
import tempfile
import unittest

from examples.sample_apps.translation_agent_app.intelligence.utils.common.jsonl_file_util import (
    JsonFileOps,
    JsonFileReader,
    JsonFileWriter,
)


class TestJsonlFileUtil(unittest.TestCase):
    """Test deterministic jsonl file operations using temporary directories."""

    def setUp(self):
        """Create a temporary working directory per test."""
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(self._remove_tmpdir)

    def _remove_tmpdir(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_jsonl(self, lines):
        path = os.path.join(self.tmpdir, 'sample.jsonl')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return path

    def test_is_file_exist_rejects_non_jsonl(self):
        """A non .jsonl extension should raise an exception."""
        with self.assertRaises(Exception):
            JsonFileOps.is_file_exist('notes.json')

    def test_is_file_exist_missing_file_returns_false(self):
        """A missing .jsonl path should report False."""
        self.assertFalse(JsonFileOps.is_file_exist(os.path.join(self.tmpdir, 'missing.jsonl')))

    def test_is_file_exist_existing_file_returns_true(self):
        """An existing .jsonl file should report True."""
        path = self._write_jsonl(['{"a": 1}'])
        self.assertTrue(JsonFileOps.is_file_exist(path))

    def test_reader_returns_objects_then_none(self):
        """read_json_obj should return each object then None at EOF."""
        path = self._write_jsonl(['{"a": 1}', '{"b": 2}'])
        reader = JsonFileReader(path)
        self.assertEqual(reader.read_json_obj(), {'a': 1})
        self.assertEqual(reader.read_json_obj(), {'b': 2})
        self.assertIsNone(reader.read_json_obj())

    def test_reader_read_json_obj_list(self):
        """read_json_obj_list should return all objects in order."""
        path = self._write_jsonl(['{"a": 1}', '{"b": 2}'])
        reader = JsonFileReader(path)
        self.assertEqual(reader.read_json_obj_list(), [{'a': 1}, {'b': 2}])

    def test_reader_missing_file_raises(self):
        """Reading a file that never opened should raise an exception."""
        reader = JsonFileReader(os.path.join(self.tmpdir, 'missing.jsonl'))
        with self.assertRaises(Exception):
            reader.read_json_obj()

    def test_reader_invalid_line_returns_empty_dict(self):
        """A malformed json line should degrade to an empty dict."""
        path = self._write_jsonl(['not json', '{"ok": 1}'])
        reader = JsonFileReader(path)
        self.assertEqual(reader.read_json_obj(), {})
        self.assertEqual(reader.read_json_obj(), {'ok': 1})

    def test_writer_roundtrip(self):
        """Objects written by JsonFileWriter should be readable back."""
        directory = os.path.join(self.tmpdir, 'nested') + os.sep
        writer = JsonFileWriter('out', directory=directory)
        writer.write_json_obj({'x': 1})
        writer.write_json_obj_list([{'y': 2}, {'z': 3}])
        writer.write_json_query_answer('q', 'a')
        writer.write_json_query_answer_list([('q1', 'a1'), ('q2', 'a2')])
        path = os.path.join(directory, 'out.jsonl')
        self.assertTrue(os.path.exists(path))
        self.assertEqual(JsonFileReader(path).read_json_obj_list(),
                         [{'x': 1}, {'y': 2}, {'z': 3},
                          {'query': 'q', 'answer': 'a'},
                          {'query': 'q1', 'answer': 'a1'},
                          {'query': 'q2', 'answer': 'a2'}])


if __name__ == '__main__':
    unittest.main()
