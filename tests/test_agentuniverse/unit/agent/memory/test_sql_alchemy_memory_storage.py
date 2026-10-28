# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Regression tests for type filtering in ``SqlAlchemyMemoryStorage``.

The default converter used to persist the message type only inside the JSON
payload while ``get(type=...)`` tried to read a ``type`` column that did not
exist.  These tests exercise the SQLite-backed storage directly, including the
legacy-table upgrade path and the normal ``Memory`` summarization entry point.
"""

import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from unittest.mock import MagicMock, patch

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, inspect
from sqlalchemy.orm import declarative_base

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import MemoryStorageManager
from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    BaseMemoryConverter, SqlAlchemyMemoryStorage,
)
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper


class SqlAlchemyMemoryStorageTest(unittest.TestCase):
    """Verify that the persisted type column drives SQL-side filtering."""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self._db_path = os.path.join(self._temp_dir.name, 'memory.db')
        self._db_uri = 'sqlite:///' + self._db_path.replace(os.sep, '/')
        self._wrappers = []
        self.storage = self._build_storage()

    def tearDown(self) -> None:
        for wrapper in self._wrappers:
            wrapper.sql_database._engine.dispose()
        self._temp_dir.cleanup()

    def _new_wrapper(self) -> SQLDBWrapper:
        wrapper_configer = SQLDBWrapperConfiger()
        wrapper_configer.db_uri = self._db_uri
        wrapper = SQLDBWrapper(
            name=f'test_wrapper_{len(self._wrappers)}',
            db_wrapper_configer=wrapper_configer,
        )
        self._wrappers.append(wrapper)
        return wrapper

    def _build_storage(self, wrapper: SQLDBWrapper = None, initialize: bool = True) -> SqlAlchemyMemoryStorage:
        storage = SqlAlchemyMemoryStorage(name='sql_memory_storage')
        configer = ComponentConfiger()
        configer.sqldb_table_name = 'memory'
        configer.sqldb_wrapper_name = 'test_wrapper'
        storage.initialize_by_component_configer(configer)
        storage._sqldb_wrapper = wrapper or self._new_wrapper()
        if initialize:
            storage._create_table_if_not_exists()
        return storage

    def _add_sample_messages(self, storage: SqlAlchemyMemoryStorage = None) -> None:
        storage = storage or self.storage
        storage.add(
            [
                Message(id='1', type='human', content='hello', source='agent_a'),
                Message(id='2', type='summarize', content='first summary', source='agent_a'),
                Message(id='3', type='ai', content='hi there', source='agent_a'),
                Message(id='4', type='summarize', content='second summary', source='agent_a'),
            ],
            session_id='session-1',
            agent_id='agent_a',
        )

    def _assign_created_at_offsets(self) -> None:
        """Give the sample rows distinct timestamps so ordering is explicit.

        SQLite evaluates ``CURRENT_TIMESTAMP`` with second precision, which can
        leave all rows with the same value when they are inserted in one
        transaction.  The storage orders by that column, so the tests assign
        deterministic timestamps before asserting top-k behaviour.
        """
        model_class = self.storage.memory_converter.get_sql_model_class()
        base = datetime(2024, 1, 1, 0, 0, 0)
        with self.storage._sqldb_wrapper.get_session()() as session:
            rows = session.query(model_class).order_by(model_class.id.asc()).all()
            for offset, row in enumerate(rows):
                row.gmt_created = base + timedelta(seconds=offset)
            session.commit()

    def test_default_model_persists_type_column_and_composite_index(self) -> None:
        model_class = self.storage.memory_converter.get_sql_model_class()
        table = model_class.__table__

        self.assertIn('type', table.columns)
        self.assertEqual(table.columns['type'].type.length, 50)

        indexes = {
            index.name: [column.name for column in index.columns]
            for index in table.indexes
        }
        self.assertEqual(
            indexes['idx_session_id_agent_id_type'],
            ['session_id', 'agent_id', 'type'],
        )

        with self.storage._sqldb_wrapper.sql_database._engine.connect() as conn:
            database_columns = {column['name'] for column in inspect(conn).get_columns('memory')}
            database_indexes = {index['name'] for index in inspect(conn).get_indexes('memory')}
        self.assertIn('type', database_columns)
        self.assertIn('idx_session_id_agent_id_type', database_indexes)

    def test_converter_round_trip_keeps_type(self) -> None:
        converter = self.storage.memory_converter
        message = Message(
            id='message-1',
            type='summarize',
            content='a compact summary',
            source='agent_a',
            metadata={'turn': 3},
        )

        row = converter.to_sql_model(
            message, session_id='session-1', agent_id='agent_a', source='agent_a',
        )
        row.id = 7
        self.assertEqual(row.type, 'summarize')

        restored = converter.from_sql_model(row)
        self.assertEqual(restored.id, 7)
        self.assertEqual(restored.type, 'summarize')
        self.assertEqual(restored.content, 'a compact summary')
        self.assertEqual(restored.source, 'agent_a')
        self.assertEqual(restored.metadata, {'turn': 3})

        # Rows written before the column was introduced only contain the type
        # inside the serialized message, so reads must fall back to the JSON.
        payload = json.loads(row.message)
        payload['type'] = 'human'
        row.message = json.dumps(payload)
        self.assertEqual(converter.from_sql_model(row).type, 'summarize')

        row.type = None
        self.assertEqual(converter.from_sql_model(row).type, 'human')
        row.type = ''
        self.assertEqual(converter.from_sql_model(row).type, 'human')

    def test_add_persists_type_in_the_database_column(self) -> None:
        self._add_sample_messages()
        table = self.storage.memory_converter.get_sql_model_class().__table__
        with self.storage._sqldb_wrapper.sql_database._engine.connect() as conn:
            rows = conn.execute(table.select().order_by(table.c.id)).all()
        self.assertEqual([row.type for row in rows], ['human', 'summarize', 'ai', 'summarize'])

    def test_get_with_scalar_type_returns_only_matching_messages(self) -> None:
        self._add_sample_messages()

        summaries = self.storage.get(session_id='session-1', agent_id='agent_a', type='summarize')
        self.assertCountEqual(
            [message.content for message in summaries],
            ['first summary', 'second summary'],
        )
        self.assertTrue(all(message.type == 'summarize' for message in summaries))

        humans = self.storage.get(session_id='session-1', agent_id='agent_a', type='human')
        self.assertEqual([message.content for message in humans], ['hello'])

        # Blank filters keep the previous "no type filter" behaviour.
        self.assertEqual(
            len(self.storage.get(session_id='session-1', agent_id='agent_a', type='')),
            4,
        )

    def test_get_with_sequence_type_returns_all_matching_messages(self) -> None:
        self._add_sample_messages()

        messages = self.storage.get(
            session_id='session-1', agent_id='agent_a', type=['human', 'ai'],
        )
        self.assertCountEqual([message.type for message in messages], ['human', 'ai'])

        summaries = self.storage.get(
            session_id='session-1', agent_id='agent_a', type=('summarize',),
        )
        self.assertEqual(len(summaries), 2)

        self.assertEqual(
            len(self.storage.get(session_id='session-1', agent_id='agent_a', type=[])),
            4,
        )

    def test_get_without_type_returns_every_message(self) -> None:
        self._add_sample_messages()

        messages = self.storage.get(session_id='session-1', agent_id='agent_a')
        self.assertCountEqual(
            [message.type for message in messages],
            ['human', 'summarize', 'ai', 'summarize'],
        )

    def test_get_with_unknown_type_returns_an_empty_list(self) -> None:
        self._add_sample_messages()

        self.assertEqual(
            self.storage.get(session_id='session-1', agent_id='agent_a', type='unknown'),
            [],
        )
        self.assertEqual(
            self.storage.get(session_id='session-1', agent_id='agent_a', type=['unknown', 'missing']),
            [],
        )

    def test_get_applies_top_k_after_type_filter(self) -> None:
        self._add_sample_messages()
        self._assign_created_at_offsets()

        # Filtering before top_k matters here: the newest row overall is a
        # summary, so slicing first would leave nothing for the human filter.
        humans = self.storage.get(
            session_id='session-1', agent_id='agent_a', type='human', top_k=1,
        )
        self.assertEqual([message.content for message in humans], ['hello'])

        summaries = self.storage.get(
            session_id='session-1', agent_id='agent_a', type='summarize', top_k=1,
        )
        self.assertEqual([message.content for message in summaries], ['second summary'])

        mixed = self.storage.get(
            session_id='session-1', agent_id='agent_a',
            type=['human', 'summarize'], top_k=2,
        )
        self.assertEqual(
            [message.content for message in mixed],
            ['first summary', 'second summary'],
        )

    def test_normalize_memory_types_handles_scalar_and_sequence_contract(self) -> None:
        normalize = SqlAlchemyMemoryStorage._normalize_memory_types

        self.assertEqual(normalize(None), [])
        self.assertEqual(normalize(''), [])
        self.assertEqual(normalize('summarize'), ['summarize'])
        self.assertEqual(normalize(['human', '', None, 'ai']), ['human', 'ai'])
        self.assertEqual(normalize(('summarize',)), ['summarize'])
        self.assertCountEqual(normalize({'human', 'ai'}), ['human', 'ai'])

        with self.assertRaises(ValueError):
            normalize(42)
        with self.assertRaises(ValueError):
            normalize({'human': True})

    def test_existing_table_without_type_is_upgraded_and_backfilled(self) -> None:
        wrapper = self._new_wrapper()
        engine = wrapper.sql_database._engine

        legacy_metadata = MetaData()
        legacy_table = Table(
            'memory',
            legacy_metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('session_id', String(100), default=''),
            Column('agent_id', String(100), default=''),
            Column('source', String(500), default=''),
            Column('message', Text),
            Column('gmt_created', DateTime),
        )
        legacy_metadata.drop_all(engine, checkfirst=True)
        legacy_metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(
                legacy_table.insert(),
                [
                    {
                        'session_id': 'session-1',
                        'agent_id': 'agent_a',
                        'source': 'agent_a',
                        'message': json.dumps({'type': 'human', 'content': 'old hello'}),
                        'gmt_created': datetime.now(),
                    },
                    {
                        'session_id': 'session-1',
                        'agent_id': 'agent_a',
                        'source': 'agent_a',
                        'message': json.dumps({'type': 'summarize', 'content': 'old summary'}),
                        'gmt_created': datetime.now(),
                    },
                ],
            )

        storage = self._build_storage(wrapper=wrapper, initialize=False)
        storage._create_table_if_not_exists()

        with engine.connect() as conn:
            database_columns = {column['name'] for column in inspect(conn).get_columns('memory')}
            database_indexes = {index['name'] for index in inspect(conn).get_indexes('memory')}
        self.assertIn('type', database_columns)
        self.assertIn('idx_session_id_agent_id_type', database_indexes)

        # The legacy summary must remain retrievable after the upgrade.
        summaries = storage.get(session_id='session-1', agent_id='agent_a', type='summarize')
        self.assertEqual([message.content for message in summaries], ['old summary'])

        storage.add(
            [Message(type='ai', content='new reply')],
            session_id='session-1',
            agent_id='agent_a',
        )
        self.assertCountEqual(
            [message.type for message in storage.get(session_id='session-1', agent_id='agent_a')],
            ['human', 'summarize', 'ai'],
        )

        # Initialization runs on every process start, so a second pass must be
        # a harmless no-op rather than a duplicate-column/index error.
        storage._create_table_if_not_exists()

    def test_concurrent_legacy_initialization_uses_one_sqlite_migration(self) -> None:
        metadata = MetaData()
        legacy_table = Table(
            'memory', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('session_id', String(100)),
            Column('agent_id', String(100)),
            Column('source', String(500)),
            Column('message', Text),
            Column('gmt_created', DateTime),
        )
        engine = self.storage._sqldb_wrapper.sql_database._engine
        metadata.drop_all(engine, checkfirst=True)
        metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(legacy_table.insert().values(
                session_id='session-1', agent_id='agent_a', source='agent_a',
                message=json.dumps({'type': 'summarize', 'content': 'old summary'}),
                gmt_created=datetime.now(),
            ))

        storages = [self._build_storage(wrapper=self._new_wrapper(), initialize=False)
                    for _ in range(2)]
        start = Barrier(2)

        def initialize(storage):
            start.wait(timeout=10)
            storage._create_table_if_not_exists()

        with ThreadPoolExecutor(max_workers=2) as pool:
            tasks = [pool.submit(initialize, storage) for storage in storages]
            for task in tasks:
                task.result(timeout=20)

        with engine.connect() as conn:
            self.assertIn('type', {column['name'] for column in inspect(conn).get_columns('memory')})
            self.assertIn('idx_session_id_agent_id_type',
                          {index['name'] for index in inspect(conn).get_indexes('memory')})
        self.assertEqual(storages[0].get(type='summarize')[0].content, 'old summary')

    def test_legacy_custom_converter_without_type_column_still_works(self) -> None:
        base = declarative_base()

        class LegacyModel(base):
            __tablename__ = 'custom_memory'
            id = Column(Integer, primary_key=True, autoincrement=True)
            session_id = Column(String(100))
            agent_id = Column(String(100))
            source = Column(String(500))
            message = Column(Text)
            gmt_created = Column(DateTime)

        class LegacyConverter(BaseMemoryConverter):
            def __init__(self):
                super().__init__()
                self.model_class = LegacyModel

            def get_sql_model_class(self):
                return self.model_class

            def to_sql_model(self, message, session_id=None, agent_id=None, source=None):
                return self.model_class(
                    session_id=session_id, agent_id=agent_id, source=source,
                    message=json.dumps(message.to_dict()), gmt_created=datetime.now(),
                )

            def from_sql_model(self, row):
                return Message.from_dict({'id': row.id, **json.loads(row.message)})

        engine = self.storage._sqldb_wrapper.sql_database._engine
        base.metadata.create_all(engine)
        storage = self._build_storage(initialize=False)
        storage.sqldb_table_name = 'custom_memory'
        storage.memory_converter = LegacyConverter()
        storage._create_table_if_not_exists()
        storage.add([Message(type='human', content='hello')], session_id='session-1')
        self.assertEqual(storage.get(session_id='session-1')[0].content, 'hello')
        with engine.connect() as conn:
            self.assertNotIn('type', {column['name'] for column in inspect(conn).get_columns('custom_memory')})

    def test_memory_api_saves_and_loads_summary_with_type_filter(self) -> None:
        memory = Memory(
            name='sql_memory',
            memory_storages=['sql_memory_storage'],
            memory_retrieval_storage='sql_memory_storage',
        )
        storage_manager = MemoryStorageManager()

        with patch.object(storage_manager, 'get_instance_obj', return_value=self.storage):
            memory.add(
                [
                    Message(type='human', content='hello'),
                    Message(type='summarize', content='previous summary'),
                ],
                session_id='session-1',
                agent_id='agent_a',
            )

            summaries = memory.get(session_id='session-1', agent_id='agent_a', type='summarize')
            self.assertEqual([message.content for message in summaries], ['previous summary'])

            fake_agent = MagicMock()
            fake_agent.run.return_value = OutputObject({'output': 'fresh summary'})
            with patch.object(AgentManager(), 'get_instance_obj', return_value=fake_agent):
                result = memory.summarize_memory(session_id='session-1', agent_id='agent_a')

        self.assertEqual(result, 'fresh summary')
        fake_agent.run.assert_called_once()
        self.assertEqual(
            fake_agent.run.call_args.kwargs['summarize_content'],
            'previous summary',
        )


if __name__ == '__main__':
    unittest.main()
