# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08 10:00
# @Author  : test
# @FileName: test_sqlite_conversation_memory_storage.py
"""Unit tests for sqlite_conversation_memory_storage using a real sqlite file."""

import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.memory_storage.sqlite_conversation_memory_storage import (
    DefaultMemoryConverter,
    SqliteMemoryStorage,
    create_memory_model,
)


class TestSqliteConversationMemoryStorage:
    """Tests for sqlite memory model, converter and storage."""

    @pytest.fixture
    def converter(self):
        return DefaultMemoryConverter("test_memory")

    def test_create_memory_model(self):
        model = create_memory_model("test_memory", declarative_base())
        assert model.__tablename__ == "test_memory"
        assert list(model.__table__.primary_key.columns.keys()) == ["id"]
        expected = {"id", "session_id", "content", "trace_id", "source", "source_type",
                    "target", "target_type", "type", "prefix", "timestamp", "params",
                    "pair_id", "message_id", "additional_args"}
        assert set(model.__table__.columns.keys()) == expected
        assert len(model.__table__.indexes) == 4

    def test_converter_model_class(self, converter):
        model = converter.get_sql_model_class()
        assert model.__tablename__ == "test_memory"
        assert "message_id" in model.__table__.columns and "content" in model.__table__.columns

    def test_to_sql_model(self, converter):
        msg = ConversationMessage(id="mid-2", type="input", source="u", source_type="user",
                                  target="a", target_type="agent", content="hello",
                                  trace_id="t2", metadata={"prefix": "p2", "pair_id": "pp"})
        row = converter.to_sql_model(msg, session_id="s2")
        assert row.message_id == "mid-2" and row.session_id == "s2"
        assert row.content == "hello" and row.type == "input" and row.trace_id == "t2"
        assert row.source_type == "user" and row.target_type == "agent"
        assert row.prefix == "p2" and row.pair_id == "pp" and row.additional_args == "{}"

    def test_storage_defaults(self):
        storage = SqliteMemoryStorage()
        assert storage.sqldb_table_name == "memory"
        assert storage.sqldb_path is None and storage.memory_converter is None
        assert storage.engine is None and storage.session is None

    def test_storage_add_get_delete_roundtrip(self, tmp_path):
        storage = SqliteMemoryStorage(sqldb_path=f"sqlite:///{tmp_path}/mem.db",
                                      sqldb_table_name="memory")
        storage.memory_converter = DefaultMemoryConverter("memory")
        storage._new_client()
        msgs = [ConversationMessage(id="m1", type="output", source="agent_a",
                                    source_type="agent", target="agent_b", target_type="agent",
                                    content="hi", metadata={"timestamp": datetime.datetime(2024, 1, 1, 12, 0)}),
                ConversationMessage(id="m2", type="input", source="user", source_type="user",
                                    target="agent_a", target_type="agent", content="q",
                                    metadata={"timestamp": datetime.datetime(2024, 1, 1, 13, 0)})]
        storage.add(msgs, session_id="s1")
        got = storage.get(session_id="s1")
        assert len(got) == 2 and {m.id for m in got} == {"m1", "m2"}
        assert {m.conversation_id for m in got} == {"s1"} and got[0].content == "hi"
        assert len(storage.get(session_id="s1", type="output")) == 1
        storage.delete(session_id="s1")
        assert storage.get(session_id="s1") == []
