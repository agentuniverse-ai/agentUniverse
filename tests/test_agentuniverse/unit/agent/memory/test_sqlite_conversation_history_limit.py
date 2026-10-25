"""Limit ORM materialization while returning recent conversation history."""

import json
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import Column, DateTime, String, event, insert
from sqlalchemy.orm import declarative_base

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.memory_storage.sqlite_conversation_memory_storage import (
    DefaultMemoryConverter,
    BaseMemoryConverter,
    SqliteMemoryStorage,
)


@pytest.fixture
def storage():
    """Initialize the real storage and SQLAlchemy converter against SQLite."""
    instance = SqliteMemoryStorage(
        sqldb_path="sqlite://",
        memory_converter=DefaultMemoryConverter("conversation_history"),
    )
    instance._new_client()
    try:
        yield instance
    finally:
        instance.engine.dispose()


def seed(storage, overrides):
    """Insert realistic serialized rows without populating an ORM identity map."""
    start = datetime(2026, 1, 1)
    rows = []
    for index, override in enumerate(overrides):
        row = {
            "session_id": "wanted",
            "message_id": f"id-{index}",
            "content": f"message-{index}",
            "source": "user",
            "source_type": "user",
            "target": "assistant",
            "target_type": "agent",
            "type": "input",
            "trace_id": "trace-wanted",
            "timestamp": start + timedelta(seconds=index),
            "params": "{}",
            "additional_args": json.dumps({"position": index}),
        }
        row.update(override)
        rows.append(row)
    model = storage.memory_converter.get_sql_model_class()
    with storage.engine.begin() as connection:
        connection.execute(insert(model), rows)


@contextmanager
def materialized_rows(storage):
    """Observe actual SQLAlchemy ORM loads; do not replace the query or cursor."""
    loaded = []
    model = storage.memory_converter.get_sql_model_class()

    def on_load(instance, context):
        loaded.append(instance.message_id)

    event.listen(model, "load", on_load)
    try:
        yield loaded
    finally:
        event.remove(model, "load", on_load)


@pytest.mark.parametrize("top_k", [1, 3, 20, 1500, 10**30])
def test_positive_limit_bounds_loaded_rows_and_keeps_chronology(storage, top_k):
    seed(storage, [{} for _ in range(1000)])
    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted", top_k=top_k)

    count = min(top_k, 1000)
    assert [message.id for message in messages] == [
        f"id-{index}" for index in range(1000 - count, 1000)
    ]
    assert len(loaded) == count


def test_default_limit_materializes_only_twenty_messages(storage):
    seed(storage, [{} for _ in range(75)])
    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted")

    assert [message.content for message in messages] == [
        f"message-{index}" for index in range(55, 75)
    ]
    assert len(loaded) == 20


def test_timestamp_ties_use_database_insertion_order(storage):
    start = datetime(2026, 1, 1)
    seed(storage, [{"timestamp": start + timedelta(days=day)}
                   for day in [3, 1, 2, 2, 1]])

    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted", top_k=3)

    assert [message.id for message in messages] == ["id-2", "id-3", "id-0"]
    assert len(loaded) == 3


def test_null_timestamps_keep_sqlite_chronological_order(storage):
    start = datetime(2026, 1, 1)
    seed(storage, [{"timestamp": value} for value in [
        None, start, None, start + timedelta(days=1),
    ]])

    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted", top_k=3)

    assert [message.id for message in messages] == ["id-2", "id-1", "id-3"]
    assert messages[0].metadata["timestamp"] is None
    assert len(loaded) == 3


@pytest.mark.parametrize("type_filter", ["input", ["input", "output"]])
def test_filters_are_applied_before_limiting_rows(storage, type_filter):
    seed(storage, [{} for _ in range(5)] + [{
        "session_id": "other", "target": "other", "trace_id": "other",
        "type": "summarize",
    } for _ in range(30)])

    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted", agent_id="assistant",
                               trace_id="trace-wanted", type=type_filter, top_k=3)

    assert [message.id for message in messages] == ["id-2", "id-3", "id-4"]
    assert len(loaded) == 3


def test_empty_matching_history_materializes_nothing(storage):
    seed(storage, [{} for _ in range(10)])
    with materialized_rows(storage) as loaded:
        assert storage.get(session_id="missing", top_k=3) == []
    assert loaded == []


def test_unfiltered_history_remains_chronological(storage):
    seed(storage, [{"session_id": f"session-{index % 2}"}
                   for index in range(10)])
    with materialized_rows(storage) as loaded:
        messages = storage.get(top_k=3)
    assert [message.id for message in messages] == ["id-7", "id-8", "id-9"]
    assert len(loaded) == 3


def test_public_add_get_round_trip_keeps_message_payloads(storage):
    start = datetime(2026, 1, 1)
    original = [ConversationMessage(
        id=f"public-{index}", conversation_id="round-trip",
        content=f"content-{index}", type="input", source="user", source_type="user",
        target="assistant", target_type="agent", trace_id="round-trip-trace",
        metadata={"timestamp": start + timedelta(seconds=index), "params": "{}",
                  "prefix": "history", "pair_id": "pair"},
        additional_args={"tool_calls": [], "index": index},
    ) for index in range(5)]
    storage.add(original, session_id="round-trip")

    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="round-trip", top_k=2)

    assert [message.id for message in messages] == ["public-3", "public-4"]
    assert len(loaded) == 2
    for actual, expected in zip(messages, original[-2:]):
        assert actual.content == expected.content
        assert actual.conversation_id == expected.conversation_id
        assert actual.trace_id == expected.trace_id
        assert actual.source == expected.source
        assert actual.target == expected.target
        assert actual.additional_args == expected.additional_args
        assert actual.metadata["timestamp"] == expected.metadata["timestamp"]
        assert actual.metadata["prefix"] == "history"
        assert actual.metadata["params"] == "{}"
        assert actual.metadata["pair_id"] == "pair"


CustomBase = declarative_base()


class CustomHistoryRow(CustomBase):
    """A valid custom SQLite table with a composite key and no id/rowid."""
    __tablename__ = "custom_history"
    __table_args__ = {"sqlite_with_rowid": False}
    partition = Column(String, primary_key=True)
    message_id = Column(String, primary_key=True)
    session_id = Column(String)
    content = Column(String)
    timestamp = Column(DateTime)
    source = Column(String)
    source_type = Column(String)
    target = Column(String)
    target_type = Column(String)
    type = Column(String)
    trace_id = Column(String)


class CustomHistoryConverter(BaseMemoryConverter):
    """Use actual ORM rows and framework messages through the converter API."""
    model_class: Any = CustomHistoryRow

    def from_sql_model(self, sql_message):
        return ConversationMessage(id=sql_message.message_id,
                                   content=sql_message.content,
                                   conversation_id=sql_message.session_id)

    def to_sql_model(self, message, **kwargs):
        return CustomHistoryRow(partition="custom", message_id=str(message.id),
                                content=message.content,
                                session_id=message.conversation_id)

    def get_sql_model_class(self):
        return self.model_class


def test_custom_converter_needs_no_conventional_id_column():
    storage = SqliteMemoryStorage(sqldb_path="sqlite://",
                                  memory_converter=CustomHistoryConverter())
    storage._new_client()
    try:
        start = datetime(2026, 1, 1)
        with storage.engine.begin() as connection:
            connection.execute(insert(CustomHistoryRow), [{
                "partition": "custom", "message_id": str(index),
                "session_id": "custom", "content": f"custom-{index}",
                "timestamp": start + timedelta(seconds=index),
            } for index in range(5)])
        with materialized_rows(storage) as loaded:
            messages = storage.get(session_id="custom", top_k=3)
        assert [message.content for message in messages] == [
            "custom-2", "custom-3", "custom-4"]
        assert len(loaded) == 3
    finally:
        storage.engine.dispose()
