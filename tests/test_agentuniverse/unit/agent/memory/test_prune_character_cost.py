"""Pruning should preserve suffixes without repeatedly rendering all history."""

from types import SimpleNamespace

import pytest

import agentuniverse.agent.memory.memory as memory_module
import agentuniverse.base.util.memory_util as memory_util
from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.llm.llm_manager import LLMManager


@pytest.fixture
def counting(monkeypatch):
    monkeypatch.setattr(LLMManager(), "get_instance_obj", lambda _: None)
    monkeypatch.setattr(
        memory_module, "MemoryCompressorManager", lambda: SimpleNamespace(get_instance_obj=lambda _: None)
    )


@pytest.mark.parametrize("count", [100, 200])
def test_character_pruning_has_linear_serialization_work(counting, monkeypatch, count):
    original = memory_util.get_memory_string
    visited_messages = 0

    def measured(messages, *args, **kwargs):
        nonlocal visited_messages
        visited_messages += len(messages)
        return original(messages, *args, **kwargs)

    monkeypatch.setattr(memory_util, "get_memory_string", measured)
    monkeypatch.setattr(memory_module, "get_memory_string", measured)
    messages = [Message(content="x", type="human") for _ in range(count)]

    assert Memory(max_tokens=1).prune(messages) == []
    assert len(messages) == count
    assert visited_messages <= 3 * count


@pytest.mark.parametrize(
    "budget, expected", [(100, ["old", "middle", "new"]), (57, ["middle", "new"]), (26, ["new"]), (1, [])]
)
def test_exact_suffix_and_input_list_are_preserved(counting, budget, expected):
    messages = [Message(content=text, type="human") for text in ["old", "middle", "new"]]
    result = Memory(max_tokens=budget).prune(messages)
    assert [message.content for message in result] == expected
    assert [message.content for message in messages] == ["old", "middle", "new"]


def test_filtered_trace_messages_do_not_add_separator_cost(counting, monkeypatch):
    monkeypatch.setattr(memory_util, "FrameworkContextManager", lambda: SimpleNamespace(get_context=lambda _: "active"))
    hidden = ConversationMessage(type="output", content="hidden", trace_id="active", metadata={})
    messages = [Message(content="old", type="human"), hidden, Message(content="new", type="human")]
    result = Memory(max_tokens=26).prune(messages)
    assert result == [hidden, messages[-1]]


def test_compressor_receives_removed_prefix_and_exact_remaining_budget(counting, monkeypatch):
    calls = []

    class Compressor:
        def compress_memory(self, messages, budget):
            calls.append(([message.content for message in messages], budget))
            return "summary"

    monkeypatch.setattr(
        memory_module, "MemoryCompressorManager", lambda: SimpleNamespace(get_instance_obj=lambda _: Compressor())
    )
    messages = [Message(content="old", type="human"), Message(content="new", type="human")]
    result = Memory(max_tokens=30).prune(messages)
    assert calls == [(["old"], 4)]
    assert [message.content for message in result] == ["summary", "new"]


def test_custom_tokenizer_retains_exact_suffix_counting(counting, monkeypatch):
    class BoundaryCounter:
        def get_num_tokens(self, text):
            return len(text) + 11 * text.count("\n\n")

    monkeypatch.setattr(LLMManager(), "get_instance_obj", lambda _: BoundaryCounter())
    messages = [Message(content="old", type="human"), Message(content="new", type="human")]
    assert Memory(max_tokens=60).prune(messages) == [messages[-1]]


def test_nonmonotone_tokenizer_keeps_first_fitting_suffix(counting, monkeypatch):
    class NonmonotoneCounter:
        def get_num_tokens(self, text):
            return {3: 100, 2: 4, 1: 10, 0: 0}[text.count("Message role:")]

    monkeypatch.setattr(LLMManager(), "get_instance_obj", lambda _: NonmonotoneCounter())
    messages = [Message(content=text, type="human") for text in ["old", "middle", "new"]]
    assert Memory(max_tokens=5).prune(messages) == messages[1:]
