# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:00
# @Author  : agentuniverse
# @FileName: test_sql_alchemy_memory_storage.py
"""Unit tests for the memory model factory and the default memory converter."""

import json

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.pool import StaticPool

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    DefaultMemoryConverter,
    create_memory_model,
)
from agentuniverse.agent.memory.message import Message


@pytest.fixture
def converter():
    return DefaultMemoryConverter('memory_table')


@pytest.fixture
def engine():
    return create_engine('sqlite://', connect_args={'check_same_thread': False},
                         poolclass=StaticPool)


class TestCreateMemoryModel:
    """Test the create_memory_model factory."""

    def test_model_columns_and_table_name(self):
        model = create_memory_model('memory_table', declarative_base())
        assert model.__tablename__ == 'memory_table'
        columns = {column.name for column in model.__table__.columns}
        assert {'id', 'session_id', 'agent_id', 'source', 'message',
                'gmt_created'} <= columns

    def test_model_indexes(self):
        model = create_memory_model('memory_table', declarative_base())
        index_names = {index.name for index in model.__table__.indexes}
        assert {'idx_session_id_source', 'idx_agent_id_source',
                'idx_gmt_created'} <= index_names

    def test_distinct_models_for_distinct_table_names(self):
        model_a = create_memory_model('memory_a', declarative_base())
        model_b = create_memory_model('memory_b', declarative_base())
        assert model_a is not model_b
        assert model_a.__tablename__ != model_b.__tablename__


class TestDefaultMemoryConverter:
    """Test the DefaultMemoryConverter mapping between Message and sql rows."""

    def test_initialization(self, converter):
        model_class = converter.get_sql_model_class()
        assert model_class is converter.model_class
        assert model_class.__tablename__ == 'memory_table'

    def test_to_sql_model_serializes_message(self, converter):
        message = Message(type='human', content='你好，世界',
                          source='user', metadata={'lang': 'zh'})
        sql_model = converter.to_sql_model(message=message, session_id='s1',
                                           agent_id='a1', source='user')
        assert sql_model.session_id == 's1'
        assert sql_model.agent_id == 'a1'
        assert sql_model.source == 'user'
        assert json.loads(sql_model.message) == message.to_dict()

    def test_sql_roundtrip(self, converter, engine):
        converter.get_sql_model_class().__table__.create(engine)
        message = Message(type='ai', content='roundtrip 内容',
                          source='agent', metadata={'n': 1})
        with Session(engine) as session:
            session.add(converter.to_sql_model(message=message, session_id='s1',
                                               agent_id='a1', source='agent'))
            session.commit()
            rows = session.execute(select(converter.model_class)).scalars().all()
        assert len(rows) == 1
        restored = converter.from_sql_model(rows[0])
        assert restored.id == rows[0].id
        assert restored.type == message.type
        assert restored.content == message.content
        assert restored.metadata == message.metadata
