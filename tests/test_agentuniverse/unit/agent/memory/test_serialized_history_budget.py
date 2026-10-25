"""Budget checks must measure complete histories, including their separators."""

from types import SimpleNamespace

import pytest

import agentuniverse.agent.context.context_manager_manager as context_managers
import agentuniverse.agent.memory.memory as memory_module
import agentuniverse.base.util.memory_util as memory_util
from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.memory_storage.ram_memory_storage import RamMemoryStorage
from agentuniverse.agent.memory.message import Message


class BoundaryCounter:
    def get_num_tokens(self, text):
        return len(text) + 11 * text.count("\n\n")


@pytest.fixture(params=[False, True], ids=["traditional", "context"])
def history(request, monkeypatch):
    messages = [Message(content="a", type="human"), Message(content="b", type="ai")]
    storage = RamMemoryStorage()
    storage.add(messages, session_id="session", agent_id="agent")
    monkeypatch.setattr(
        memory_module, "MemoryStorageManager", lambda: SimpleNamespace(get_instance_obj=lambda _: storage)
    )
    if request.param:
        store = RamContextStore(enable_metrics=False)
        store.add(
            [ContextSegment(content=message.content, type=ContextType.CONVERSATION, tokens=1) for message in messages],
            session_id="session",
        )
        manager = ContextManager()
        manager._hot_store = store
        monkeypatch.setattr(
            context_managers, "ContextManagerManager", lambda: SimpleNamespace(get_instance_obj=lambda _: manager)
        )
    memory = Memory(context_manager_name="history" if request.param else None, memory_retrieval_storage="history")
    return memory, request.param


@pytest.mark.parametrize("counter", [None, BoundaryCounter()], ids=["characters", "nonadditive-tokenizer"])
def test_combined_history_respects_budget_and_keeps_latest(history, monkeypatch, counter):
    memory, context = history
    monkeypatch.setattr(memory_util, "LLMManager", lambda: SimpleNamespace(get_instance_obj=lambda _: counter))
    budget = 8 if context else 45
    result = memory.get_with_context_budget("session", "agent", budget)
    assert memory_util.get_memory_tokens(result) <= budget
    assert [message.content for message in result] == ["b"]


@pytest.mark.parametrize("budget", [0, 1])
def test_no_message_fits_returns_empty(history, monkeypatch, budget):
    memory, _ = history
    monkeypatch.setattr(memory_util, "LLMManager", lambda: SimpleNamespace(get_instance_obj=lambda _: None))
    assert memory.get_with_context_budget("session", "agent", budget) == []


def test_exact_complete_history_budget_keeps_both_messages(history, monkeypatch):
    memory, context = history
    monkeypatch.setattr(memory_util, "LLMManager", lambda: SimpleNamespace(get_instance_obj=lambda _: None))
    result = memory.get_with_context_budget("session", "agent", 10 if context else 47)
    assert len(result) == 2
    assert memory_util.get_memory_tokens(result) == (10 if context else 47)
