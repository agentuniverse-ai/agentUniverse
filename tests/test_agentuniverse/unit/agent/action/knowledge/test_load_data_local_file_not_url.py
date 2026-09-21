# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/21
# @FileName: test_load_data_local_file_not_url.py
import os
import tempfile
import unittest
from unittest import mock

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.reader.reader import Reader


class RecordingReader(Reader):
    """Reader stub that records the path it was asked to load."""

    loaded_paths: list = []

    def _load_data(self, source_path: str, **kwargs):
        return []

    def load_data(self, source_path: str, **kwargs):
        RecordingReader.loaded_paths.append(source_path)
        return []


class TestLoadDataSourceDispatch(unittest.TestCase):
    """A local file whose name looks like a bare domain (name.ext) must be
    read from disk, not dispatched to the web page reader."""

    def setUp(self):
        self.knowledge = Knowledge()
        self.recorder = RecordingReader()
        RecordingReader.loaded_paths = []
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.report = os.path.join(self.tempdir.name, 'report.pdf')
        with open(self.report, 'w') as f:
            f.write('local content')
        self._old_cwd = os.getcwd()
        os.chdir(self.tempdir.name)
        self.addCleanup(os.chdir, self._old_cwd)

    def test_existing_file_with_url_like_name_uses_file_reader(self):
        self.knowledge.readers = {'pdf': 'recorded_reader'}
        with mock.patch(
                'agentuniverse.agent.action.knowledge.knowledge.ReaderManager'
        ) as reader_manager:
            reader_manager.return_value.get_instance_obj.return_value = self.recorder
            self.knowledge._load_data(source_path='report.pdf')
        self.assertEqual(['report.pdf'], RecordingReader.loaded_paths)

    def test_url_still_dispatches_to_url_reader(self):
        self.knowledge.readers = {'url': 'recorded_reader'}
        with mock.patch(
                'agentuniverse.agent.action.knowledge.knowledge.ReaderManager'
        ) as reader_manager:
            reader_manager.return_value.get_instance_obj.return_value = self.recorder
            self.knowledge._load_data(source_path='https://example.com/page')
        self.assertEqual(['https://example.com/page'], RecordingReader.loaded_paths)

    def test_missing_file_without_url_shape_raises(self):
        with mock.patch(
                'agentuniverse.agent.action.knowledge.knowledge.ReaderManager'
        ):
            with self.assertRaisesRegex(Exception, 'Unknown source type'):
                self.knowledge._load_data(source_path='/no/such/thing.xyz')


if __name__ == '__main__':
    unittest.main()
