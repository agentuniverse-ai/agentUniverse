# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Regression tests for the ``type`` filter of ``SqlAlchemyMemoryStorage.get``.

``Agent.get_memory_params`` puts ``type=['input', 'output']`` into the memory
retrieval parameters whenever an agent declares ``conversation_memory`` without
a ``name``, and ``Agent.load_summarize_memory`` asks for ``type='summarize'``.
``SqlAlchemyMemoryStorage`` is one of the built-in memory storages documented in
``docs/guidebook/*/In-Depth_Guides/Tutorials/Memory/MemoryStorage.md``, so the
filter has to work for it.
"""

import os
import tempfile
import unittest

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    SqlAlchemyMemoryStorage,
)
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.configer import Configer
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

APP_NAME = 'memory_type_filter_test_app'
WRAPPER_NAME = 'memory_sqldb_wrapper'


class SqlAlchemyMemoryTypeFilterTest(unittest.TestCase):
    """``get(type=...)`` must filter by message type and must not raise."""

    @classmethod
    def setUpClass(cls):
        cls._tmp_dir = tempfile.TemporaryDirectory()
        db_uri = 'sqlite:///' + os.path.join(cls._tmp_dir.name, 'memory.db')

        try:
            cls._previous_app_configer = ApplicationConfigManager().app_configer
        except ValueError:
            cls._previous_app_configer = None
        app_configer = AppConfiger()
        app_configer._AppConfiger__base_info_appname = APP_NAME
        ApplicationConfigManager().app_configer = app_configer

        wrapper_configer = Configer()
        wrapper_configer.value = {
            'name': WRAPPER_NAME,
            'description': 'sqlite wrapper for the memory type filter test',
            'db_uri': db_uri,
            'sql_database_args': {},
            'engine_args': {},
        }
        wrapper = SQLDBWrapper()
        wrapper.initialize_by_component_configer(
            ComponentConfiger().load_by_configer(wrapper_configer))
        SQLDBWrapperManager().register(wrapper.get_instance_code(), wrapper)

        storage_configer = Configer()
        storage_configer.value = {
            'name': 'sql_alchemy_memory_storage',
            'description': 'sqlalchemy memory storage for the type filter test',
            'sqldb_table_name': 'memory',
            'sqldb_wrapper_name': WRAPPER_NAME,
        }
        storage = SqlAlchemyMemoryStorage()
        storage.initialize_by_component_configer(
            ComponentConfiger().load_by_configer(storage_configer))
        cls._storage = storage

    @classmethod
    def tearDownClass(cls):
        if cls._previous_app_configer is not None:
            ApplicationConfigManager().app_configer = cls._previous_app_configer
        cls._tmp_dir.cleanup()

    def setUp(self):
        self._storage.delete(session_id='session')

    def _add_messages(self):
        self._storage.add(
            [
                Message(type='input', content='first question', source='agent_a'),
                Message(type='output', content='first answer', source='agent_a'),
                Message(type='summarize', content='summary of turn one',
                        source='agent_a'),
            ],
            session_id='session',
            agent_id='agent_a',
        )

    def test_type_filter_as_list_used_by_agent_load_memory(self):
        """The params Agent.get_memory_params builds must return the pair."""
        self._add_messages()

        messages = self._storage.get(session_id='session', agent_id='agent_a',
                                     top_k=20, type=['input', 'output'])

        self.assertEqual([message.type for message in messages], ['input', 'output'])

    def test_type_filter_as_string_used_by_summarize_memory(self):
        self._add_messages()

        messages = self._storage.get(session_id='session', agent_id='agent_a',
                                     top_k=20, type='summarize')

        self.assertEqual([message.type for message in messages], ['summarize'])
        self.assertEqual(messages[0].content, 'summary of turn one')

    def test_no_type_filter_returns_every_message(self):
        self._add_messages()

        messages = self._storage.get(session_id='session', agent_id='agent_a', top_k=20)

        self.assertEqual([message.type for message in messages],
                         ['input', 'output', 'summarize'])

    def test_type_filter_keeps_the_most_recent_messages(self):
        self._add_messages()
        for index in range(5):
            self._storage.add([Message(type='input', content=f'question {index}',
                                       source='agent_a')],
                              session_id='session', agent_id='agent_a')

        messages = self._storage.get(session_id='session', agent_id='agent_a',
                                     top_k=2, type=['input'])

        self.assertEqual([message.content for message in messages],
                         ['question 3', 'question 4'])

    def test_type_filter_matching_nothing_returns_empty(self):
        self._add_messages()

        messages = self._storage.get(session_id='session', agent_id='agent_a',
                                     top_k=20, type='unknown-type')

        self.assertEqual(messages, [])


if __name__ == '__main__':
    unittest.main()
