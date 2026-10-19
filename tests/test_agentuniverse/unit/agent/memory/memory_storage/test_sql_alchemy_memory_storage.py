# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:35
# @Author  : yuewang
# @FileName: test_sql_alchemy_memory_storage.py
"""Unit tests for SqlAlchemyMemoryStorage model/converter helpers."""

import pytest
from sqlalchemy import Integer, Text, DateTime
from sqlalchemy.orm import declarative_base

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    DefaultMemoryConverter,
    SqlAlchemyMemoryStorage,
    create_memory_model,
)
from agentuniverse.agent.memory.message import Message


class TestCreateMemoryModel:
    """Test the dynamic model created by create_memory_model."""

    def test_table_name(self):
        model = create_memory_model('my_memories', declarative_base())
        assert model.__tablename__ == 'my_memories'

    def test_columns(self):
        model = create_memory_model('t', declarative_base())
        cols = {c.name: c for c in model.__table__.columns}
        assert set(cols) == {'id', 'session_id', 'agent_id', 'source', 'message', 'gmt_created'}
        assert isinstance(cols['id'].type, Integer)
        assert isinstance(cols['message'].type, Text)
        assert isinstance(cols['gmt_created'].type, DateTime)

    def test_indexes(self):
        model = create_memory_model('t2', declarative_base())
        assert {i.name for i in model.__table__.indexes} == {
            'idx_session_id_source', 'idx_agent_id_source', 'idx_gmt_created'
        }


class TestDefaultMemoryConverter:
    """Test Message <-> SQL model conversion without a live database."""

    @pytest.fixture
    def converter(self):
        return DefaultMemoryConverter('conv_table')

    def test_get_sql_model_class(self, converter):
        assert converter.get_sql_model_class() is converter.model_class
        assert converter.model_class.__tablename__ == 'conv_table'

    def test_to_sql_model_fields(self, converter):
        msg = Message(type='human', content='hello', source='user_a', metadata={'k': 'v'})
        row = converter.to_sql_model(msg, session_id='s1', agent_id='a1', source='user_a')
        assert row.session_id == 's1'
        assert row.agent_id == 'a1'
        assert row.source == 'user_a'
        assert '"content": "hello"' in row.message

    def test_round_trip(self, converter):
        msg = Message(type='ai', content='round trip 中文', source='agent_x', metadata={'a': 1})
        row = converter.to_sql_model(msg, session_id='s', agent_id='a')
        restored = converter.from_sql_model(row)
        assert isinstance(restored, Message)
        assert restored.content == 'round trip 中文'
        assert restored.type == 'ai'
        assert restored.source == 'agent_x'
        assert restored.metadata == {'a': 1}


class TestSqlAlchemyMemoryStorageDefaults:
    """Test storage defaults and configer initialization."""

    def test_initialize_by_component_configer(self):
        storage = SqlAlchemyMemoryStorage()
        config = type('C', (), {'name': 'n', 'description': 'd',
                                'sqldb_table_name': 'tbl', 'sqldb_wrapper_name': 'w1',
                                'memory_converter': None})()
        result = storage._initialize_by_component_configer(config)
        assert result is storage
        assert storage.sqldb_table_name == 'tbl'
        assert storage.sqldb_wrapper_name == 'w1'
        assert isinstance(storage.memory_converter, DefaultMemoryConverter)
        assert storage.memory_converter.model_class.__tablename__ == 'tbl'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
