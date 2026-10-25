"""Exercise bounded legacy memory reads through a real SQLDBWrapper."""

import json
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import Column, DateTime, String, create_engine, event, insert, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    BaseMemoryConverter,
    DefaultMemoryConverter,
    SqlAlchemyMemoryStorage,
)
from agentuniverse.agent.memory.message import Message
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper


@contextmanager
def configured_storage(converter):
    """Use a real session factory, wrapper, converter and in-memory database."""
    engine = create_engine("sqlite://")
    converter.get_sql_model_class().__table__.create(engine)
    wrapper = SQLDBWrapper(db_session=sessionmaker(bind=engine))
    storage = SqlAlchemyMemoryStorage(memory_converter=converter)
    storage._sqldb_wrapper = wrapper
    try:
        yield storage, engine
    finally:
        engine.dispose()


@pytest.fixture
def legacy_storage():
    with configured_storage(DefaultMemoryConverter("legacy_history")) as pair:
        yield pair


def seed(pair, overrides):
    storage, engine = pair
    start = datetime(2026, 1, 1)
    rows = []
    for index, override in enumerate(overrides):
        row = {
            "session_id": "wanted", "agent_id": "assistant", "source": "source",
            "gmt_created": start + timedelta(seconds=index),
            "message": json.dumps({"type": "human", "content": f"message-{index}",
                                   "source": "source", "metadata": {"position": index}}),
        }
        row.update(override)
        rows.append(row)
    with engine.begin() as connection:
        connection.execute(insert(storage.memory_converter.model_class), rows)


@contextmanager
def materialized_rows(storage):
    loaded = []
    model = storage.memory_converter.get_sql_model_class()

    def on_load(instance, context):
        loaded.append(inspect(instance).identity)

    event.listen(model, "load", on_load)
    try:
        yield loaded
    finally:
        event.remove(model, "load", on_load)


@pytest.mark.parametrize("top_k", [1, 3, 10, 20, 1500, 10**30])
def test_legacy_limits_rows_before_materialization(legacy_storage, top_k):
    storage, _ = legacy_storage
    seed(legacy_storage, [{} for _ in range(1000)])
    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted", top_k=top_k)
    count = min(top_k, 1000)
    assert [message.content for message in messages] == [
        f"message-{index}" for index in range(1000 - count, 1000)]
    assert len(loaded) == count


def test_legacy_default_limit_is_ten_rows(legacy_storage):
    storage, _ = legacy_storage
    seed(legacy_storage, [{} for _ in range(75)])
    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted")
    assert [message.content for message in messages] == [
        f"message-{index}" for index in range(65, 75)]
    assert len(loaded) == 10


def test_legacy_timestamp_ties_keep_default_row_id_order(legacy_storage):
    storage, _ = legacy_storage
    start = datetime(2026, 1, 1)
    seed(legacy_storage, [{"gmt_created": start + timedelta(days=day)}
                          for day in [3, 1, 2, 2, 1]])
    with materialized_rows(storage) as loaded:
        messages = storage.get(top_k=3)
    assert [message.content for message in messages] == [
        "message-2", "message-3", "message-0"]
    assert len(loaded) == 3


def test_legacy_scopes_apply_before_limit(legacy_storage):
    storage, _ = legacy_storage
    seed(legacy_storage, [{} for _ in range(5)] + [{
        "session_id": "other", "agent_id": "other", "source": "other",
    } for _ in range(30)])
    with materialized_rows(storage) as loaded:
        messages = storage.get(session_id="wanted", agent_id="assistant",
                               source="source", top_k=3)
    assert [message.content for message in messages] == [
        "message-2", "message-3", "message-4"]
    assert len(loaded) == 3


def test_legacy_missing_scope_returns_no_rows(legacy_storage):
    storage, _ = legacy_storage
    seed(legacy_storage, [{} for _ in range(5)])
    with materialized_rows(storage) as loaded:
        assert storage.get(session_id="missing", top_k=3) == []
    assert loaded == []


def test_legacy_unfiltered_reads_keep_chronology(legacy_storage):
    storage, _ = legacy_storage
    seed(legacy_storage, [{"session_id": f"session-{index % 2}"}
                          for index in range(10)])
    with materialized_rows(storage) as loaded:
        messages = storage.get(top_k=3)
    assert [message.content for message in messages] == [
        "message-7", "message-8", "message-9"]
    assert len(loaded) == 3


def test_legacy_public_add_get_preserves_json_payloads(legacy_storage):
    storage, _ = legacy_storage
    original = [Message(type="human", content=f"public-{index}", source="source",
                        metadata={"nested": [index, {"enabled": False}]})
                for index in range(5)]
    storage.add(original, session_id="round-trip", agent_id="assistant")
    with materialized_rows(storage) as loaded:
        result = storage.get(session_id="round-trip", top_k=2)
    assert [message.to_dict() for message in result] == [
        message.to_dict() for message in original[-2:]]
    assert len(loaded) == 2


CustomBase = declarative_base()


class CustomLegacyRow(CustomBase):
    __tablename__ = "custom_legacy_history"
    __table_args__ = {"sqlite_with_rowid": False}
    partition = Column(String, primary_key=True)
    message_key = Column(String, primary_key=True)
    session_id = Column(String)
    agent_id = Column(String)
    source = Column(String)
    gmt_created = Column(DateTime)
    message = Column(String)


class CustomLegacyConverter(BaseMemoryConverter):
    model_class: Any = CustomLegacyRow

    def from_sql_model(self, sql_message):
        return Message(content=sql_message.message)

    def to_sql_model(self, message):
        return CustomLegacyRow(partition="custom", message_key=str(message.id),
                               message=message.content)

    def get_sql_model_class(self):
        return self.model_class


def test_legacy_custom_composite_keys_and_null_timestamps():
    with configured_storage(CustomLegacyConverter()) as (storage, engine):
        start = datetime(2026, 1, 1)
        stamps = [None, start + timedelta(days=1), start, start, None]
        with engine.begin() as connection:
            connection.execute(insert(CustomLegacyRow), [{
                "partition": "custom", "message_key": str(index),
                "session_id": "custom", "gmt_created": stamp,
                "message": f"custom-{index}",
            } for index, stamp in enumerate(stamps)])
        with materialized_rows(storage) as loaded:
            messages = storage.get(session_id="custom", top_k=3)
        assert [message.content for message in messages] == [
            "custom-2", "custom-3", "custom-1"]
        assert len(loaded) == 3
