from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.memory_util import get_memory_string


def test_context_budget_counts_combined_history_and_keeps_newest_messages(monkeypatch):
    memory = Memory()
    messages = [
        Message(content="old", type="human"),
        Message(content="new", type="ai"),
    ]

    monkeypatch.setattr(
        "agentuniverse.agent.memory.memory.get_memory_tokens",
        lambda candidate, _llm: len(get_memory_string(candidate)),
    )
    single_message_budget = len(get_memory_string([messages[0]])) + len(
        get_memory_string([messages[1]])
    )
    combined_budget = len(get_memory_string(messages))
    assert combined_budget > single_message_budget

    selected = memory._select_messages_within_budget(
        messages,
        single_message_budget,
        None,
        newest_first=False,
    )

    assert selected == [messages[1]]


def test_context_manager_order_is_preserved_when_budget_is_checked(monkeypatch):
    memory = Memory()
    messages = [
        Message(content="new", type="ai"),
        Message(content="old", type="human"),
    ]

    monkeypatch.setattr(
        "agentuniverse.agent.memory.memory.get_memory_tokens",
        lambda candidate, _llm: len(get_memory_string(candidate)),
    )
    selected = memory._select_messages_within_budget(
        messages,
        len(get_memory_string([messages[0]])),
        None,
        newest_first=True,
    )

    assert selected == [messages[0]]
