# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_txt_file_util.py
import os
import shutil
import tempfile
import unittest

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TxtFileOpsTest(unittest.TestCase):
    """Test cases for the TxtFileOps helper class."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.txt_path = os.path.join(self.tmp_dir, 'sample.txt')
        with open(self.txt_path, 'w', encoding='utf-8') as f:
            f.write('hello\n')

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_is_file_exist_true(self):
        self.assertTrue(TxtFileOps.is_file_exist(self.txt_path))

    def test_is_file_exist_false_for_missing_file(self):
        missing = os.path.join(self.tmp_dir, 'missing.txt')
        self.assertFalse(TxtFileOps.is_file_exist(missing))

    def test_is_file_exist_rejects_other_extensions(self):
        jsonl_path = os.path.join(self.tmp_dir, 'sample.jsonl')
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            f.write('{}')
        with self.assertRaises(Exception):
            TxtFileOps.is_file_exist(jsonl_path)


class TxtFileReaderTest(unittest.TestCase):
    """Test cases for the TxtFileReader class."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.txt_path = os.path.join(self.tmp_dir, 'data.txt')
        with open(self.txt_path, 'w', encoding='utf-8') as f:
            f.write('first line\nsecond line\n')

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_read_txt_obj_returns_first_line(self):
        reader = TxtFileReader(self.txt_path)
        self.assertEqual(reader.read_txt_obj(), 'first line')

    def test_read_txt_obj_strips_line_separator(self):
        reader = TxtFileReader(self.txt_path)
        reader.read_txt_obj()
        self.assertEqual(reader.read_txt_obj(), 'second line')

    def test_read_txt_obj_list_reads_all_lines(self):
        reader = TxtFileReader(self.txt_path)
        self.assertEqual(reader.read_txt_obj_list(),
                         ['first line', 'second line'])

    def test_read_txt_obj_returns_none_after_eof(self):
        reader = TxtFileReader(self.txt_path)
        reader.read_txt_obj_list()
        self.assertIsNone(reader.read_txt_obj())

    def test_read_without_existing_file_raises(self):
        reader = TxtFileReader(os.path.join(self.tmp_dir, 'none.txt'))
        self.assertIsNone(reader.file_handler)
        with self.assertRaises(Exception):
            reader.read_txt_obj()
