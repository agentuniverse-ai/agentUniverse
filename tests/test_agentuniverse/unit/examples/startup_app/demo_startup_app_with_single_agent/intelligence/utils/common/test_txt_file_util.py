# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_txt_file_util.py

"""Unit tests for the txt_file_util example helpers."""

import os
import shutil
import tempfile
import unittest

from examples.startup_app.demo_startup_app_with_single_agent.intelligence.utils.common.txt_file_util import (
    TxtFileOps, TxtFileReader)


class TestTxtFileUtil(unittest.TestCase):
    """Pure file-handling behaviors of the txt utilities."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _path(self, name):
        return os.path.join(self.tmp_dir, name)

    def test_is_file_exist_accepts_txt(self):
        path = self._path('sample.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('line\n')
        self.assertTrue(TxtFileOps.is_file_exist(path))
        self.assertFalse(TxtFileOps.is_file_exist(self._path('missing.txt')))

    def test_is_file_exist_rejects_other_extensions(self):
        with self.assertRaises(Exception):
            TxtFileOps.is_file_exist(self._path('sample.json'))

    def test_reader_missing_file_raises(self):
        with self.assertRaises(Exception):
            TxtFileReader(self._path('none.txt')).read_txt_obj()

    def test_reader_reads_stripped_line(self):
        path = self._path('sample.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('  hello world  \n')
        self.assertEqual(TxtFileReader(path).read_txt_obj(), 'hello world')

    def test_reader_returns_none_at_eof(self):
        path = self._path('sample.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('only line\n')
        reader = TxtFileReader(path)
        self.assertEqual(reader.read_txt_obj(), 'only line')
        self.assertIsNone(reader.read_txt_obj())

    def test_reader_read_obj_list(self):
        path = self._path('sample.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('alpha\n beta \n')
        self.assertEqual(TxtFileReader(path).read_txt_obj_list(), ['alpha', 'beta'])

    def test_reader_empty_file_returns_none(self):
        path = self._path('empty.txt')
        with open(path, 'w', encoding='utf-8'):
            pass
        self.assertIsNone(TxtFileReader(path).read_txt_obj())


if __name__ == '__main__':
    unittest.main()
