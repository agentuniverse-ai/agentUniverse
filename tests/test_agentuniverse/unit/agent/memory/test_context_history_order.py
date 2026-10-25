"""Conversation chronology must not depend on the store's LRU access times."""

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

import agentuniverse.agent.context.context_manager_manager as managers
import agentuniverse.base.util.memory_util as memory_util
from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.memory.memory import Memory


@pytest.fixture
def history(monkeypatch):
    store = RamContextStore(max_segments=2000, enable_metrics=False)
    manager = ContextManager()
    manager._hot_store = store
    monkeypatch.setattr(managers, "ContextManagerManager", lambda: SimpleNamespace(get_instance_obj=lambda _: manager))
    monkeypatch.setattr(memory_util, "LLMManager", lambda: SimpleNamespace(get_instance_obj=lambda _: None))
    return store, Memory(context_manager_name="history")


def add_turns(store, count, *, same_creation_time=False):
    start = datetime.now() - timedelta(hours=1)
    segments = []
    for index in range(count):
        segment = ContextSegment(
            id=f"turn{index:04d}",
            content=f"turn{index:04d}",
            type=ContextType.CONVERSATION,
            tokens=1,
            session_id="session",
        )
        segment.metadata.created_at = start if same_creation_time else start + timedelta(seconds=index)
        segment.metadata.last_accessed = start - timedelta(seconds=index)
        segments.append(segment)
    store.add(segments, session_id="session")


def test_repeated_reads_keep_newest_first(history):
    store, memory = history
    add_turns(store, 3)
    for _ in range(3):
        result = memory.get_with_context_budget("session", "agent", 1000)
        assert [message.content for message in result] == ["turn0002", "turn0001", "turn0000"]


def test_small_budget_keeps_latest_turn_after_a_full_read(history):
    store, memory = history
    add_turns(store, 3)
    memory.get_with_context_budget("session", "agent", 1000)
    result = memory.get_with_context_budget("session", "agent", 12)
    assert [message.content for message in result] == ["turn0002"]


def test_access_based_retrieval_cap_does_not_hide_latest_turn(history):
    store, memory = history
    add_turns(store, 1001)
    result = memory.get_with_context_budget("session", "agent", 12)
    assert [message.content for message in result] == ["turn1000"]


def test_creation_time_ties_have_stable_order(history):
    store, memory = history
    add_turns(store, 3, same_creation_time=True)
    for _ in range(3):
        result = memory.get_with_context_budget("session", "agent", 1000)
        assert [message.content for message in result] == ["turn0002", "turn0001", "turn0000"]
