#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.base.context.context_archive_utils import (
    get_current_context_archive,
    update_context_archive,
)
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


class TestContextArchivePersistence(unittest.TestCase):
    def setUp(self) -> None:
        FrameworkContextManager().clear_all_contexts()

    def tearDown(self) -> None:
        FrameworkContextManager().clear_all_contexts()

    def test_update_context_archive_persists_across_calls(self) -> None:
        update_context_archive('retrieval', {'docs': 3}, 'top-3 docs for query')
        archive = get_current_context_archive()
        self.assertIn('retrieval', archive)
        self.assertEqual(archive['retrieval']['data'], {'docs': 3})
        self.assertEqual(archive['retrieval']['description'], 'top-3 docs for query')

    def test_archive_object_is_shared_not_recreated(self) -> None:
        first = get_current_context_archive()
        first['hand_written'] = {'data': 'x', 'description': 'd'}
        second = get_current_context_archive()
        self.assertIn('hand_written', second)


if __name__ == '__main__':
    unittest.main()
