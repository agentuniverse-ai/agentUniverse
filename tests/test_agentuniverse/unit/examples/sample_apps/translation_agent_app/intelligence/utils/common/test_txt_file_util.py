# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_txt_file_util.py

"""Unit tests for the TxtFileOps / TxtFileReader example utilities."""

import os
import shutil
import tempfile
import unittest

from examples.sample_apps.translation_agent_app.intelligence.utils.common.txt_file_util import (
    TxtFileOps,
    TxtFileReader,
)


class TestTxtFileUtil(unittest.TestCase):
    """Test deterministic txt file operations using temporary directories."""

    def setUp(self):
        """Create a temporary working directory per test."""
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))

    def _write_txt(self, content):
        path = os.path.join(self.tmpdir, 'sample.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_is_file_exist_rejects_non_txt(self):
        """A non .txt extension should raise an exception."""
        with self.assertRaises(Exception):
            TxtFileOps.is_file_exist('notes.md')

    def test_is_file_exist_missing_file_returns_false(self):
        """A missing .txt path should report False."""
        self.assertFalse(TxtFileOps.is_file_exist(os.path.join(self.tmpdir, 'missing.txt')))

    def test_is_file_exist_existing_file_returns_true(self):
        """An existing .txt file should report True."""
        path = self._write_txt('hello\n')
        self.assertTrue(TxtFileOps.is_file_exist(path))

    def test_reader_returns_stripped_lines_then_none(self):
        """read_txt_obj should strip each line then return None at EOF."""
        path = self._write_txt('line one\n  padded line  \nlast')
        reader = TxtFileReader(path)
        self.assertEqual(reader.read_txt_obj(), 'line one')
        self.assertEqual(reader.read_txt_obj(), 'padded line')
        self.assertEqual(reader.read_txt_obj(), 'last')
        self.assertIsNone(reader.read_txt_obj())

    def test_reader_read_txt_obj_list(self):
        """read_txt_obj_list should return all lines in order."""
        path = self._write_txt('alpha\nbeta\ngamma\n')
        self.assertEqual(TxtFileReader(path).read_txt_obj_list(), ['alpha', 'beta', 'gamma'])

    def test_reader_keeps_blank_lines(self):
        """Blank lines should be read as empty strings, not None."""
        path = self._write_txt('head\n\nfoot\n')
        reader = TxtFileReader(path)
        self.assertEqual(reader.read_txt_obj_list(), ['head', '', 'foot'])

    def test_reader_missing_file_raises(self):
        """Reading a file that never opened should raise an exception."""
        reader = TxtFileReader(os.path.join(self.tmpdir, 'missing.txt'))
        with self.assertRaises(Exception):
            reader.read_txt_obj()

    def test_reader_roundtrip_multiline(self):
        """A multi-paragraph txt file should round-trip through the reader."""
        content = '第一段\nsecond paragraph\n第三段\n'
        path = self._write_txt(content)
        self.assertEqual(TxtFileReader(path).read_txt_obj_list(),
                         ['第一段', 'second paragraph', '第三段'])


if __name__ == '__main__':
    unittest.main()
