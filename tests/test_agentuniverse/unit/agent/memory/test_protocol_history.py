"""Real pinned LangChain messages, plus failure boundaries for literal history."""

from copy import deepcopy

import pytest
from langchain_community.adapters.openai import convert_message_to_dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.memory.protocol_history import ProtocolHistory


def exchange():
    return [
        {"role": "system", "content": "Literal {policy}", "name": "guide"},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "比较 {x} 和 中文"},
                {"type": "image_url", "image_url": {"url": "https://example.invalid/img.png", "detail": "low"}},
            ],
        },
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_a",
                    "type": "function",
                    "function": {"name": "lookup", "arguments": '{ "city": "新加坡" }'},
                },
                {"id": "call_b", "type": "function", "function": {"name": "lookup", "arguments": '{"city":"London"}'}},
            ],
        },
        {"role": "tool", "tool_call_id": "call_b", "content": "20 {degrees}"},
        {"role": "tool", "tool_call_id": "call_a", "content": "30°C"},
        {"role": "assistant", "content": "差值是10°C"},
        {"role": "user", "content": "Explain {difference}"},
    ]


def test_wire_memory_langchain_literal_roundtrip():
    wire = exchange()
    original = deepcopy(wire)
    messages = ProtocolHistory.from_wire(wire, message_ids=[f"event-{i}" for i in range(len(wire))])
    saved = [Message.from_dict(m.to_dict()) for m in messages]
    assert ProtocolHistory.to_wire(saved) == original
    converted = ProtocolHistory.as_langchain(saved)
    assert [m.id for m in converted] == [f"event-{i}" for i in range(len(wire))]
    assert [convert_message_to_dict(m) for m in converted] == original
    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder("history")])
    assert prompt.format_messages(history=converted) == converted
    assert wire == original
    converted[1].content[0]["text"] = "changed"
    assert ProtocolHistory.to_wire(saved) == original


def test_legacy_template_semantics_unchanged():
    message = Message(type="human", content="literal {x}")
    assert message.as_langchain().input_variables == ["x"]
    assert ProtocolHistory.as_langchain([message])[0].content == "literal {x}"


@pytest.mark.parametrize(
    "value",
    [
        {"role": "developer", "content": "x"},
        {"role": [], "content": "x"},
        {"role": "user", "content": None},
        {"role": "assistant", "content": None},
        {"role": "tool", "content": "x"},
        {"role": "user", "content": 12},
        {"role": "user", "content": "x", "unknown": True},
        {"role": "user", "content": [], "name": "n"},
        {"role": "user", "content": [{"type": "audio", "data": "x"}]},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "", "detail": "low"}}]},
        {"role": "assistant", "content": [{"type": "text", "text": "x"}]},
        {"role": "user", "content": "x", "tool_call_id": "a"},
        {"role": "assistant", "content": "", "tool_calls": []},
    ],
)
def test_unsupported_messages_fail_without_coercion(value):
    with pytest.raises(ValueError):
        ProtocolHistory.from_wire([value])


@pytest.mark.parametrize("arguments", ["{", "[]", "null", '{"x":NaN}', '{"x":Infinity}', {}, "5"])
def test_invalid_function_arguments(arguments):
    wire = exchange()[2]
    wire["tool_calls"][0]["function"]["arguments"] = arguments
    with pytest.raises(ValueError):
        ProtocolHistory.from_wire([wire])


@pytest.mark.parametrize("indexes", [[3], [2], [2, 3], [2, 3, 3, 4], [2, 3, 4, 2, 3, 4], [2, 1, 3, 4]])
def test_model_input_requires_complete_unique_tool_pairs(indexes):
    messages = ProtocolHistory.from_wire([exchange()[i] for i in indexes])
    with pytest.raises(ValueError):
        ProtocolHistory.to_wire(messages)


@pytest.mark.parametrize(
    "limits", [{"max_messages": 0}, {"max_messages": True}, {"max_bytes": -1}, {"max_bytes": 3}, {"max_messages": 1}]
)
def test_bounded_history_rejects_without_truncation(limits):
    with pytest.raises(ValueError):
        ProtocolHistory.from_wire(exchange(), **limits)
    with pytest.raises(ValueError):
        ProtocolHistory.to_wire(ProtocolHistory.from_wire(exchange()), **limits)


@pytest.mark.parametrize("envelope", [{"version": 2}, {"version": True}, {"version": 1, "extra": "x"}, "bad"])
def test_unknown_envelope_is_rejected(envelope):
    with pytest.raises(ValueError):
        ProtocolHistory.to_wire([Message(type="human", content="hi", metadata={"au_protocol_history": envelope})])


def test_empty_history_and_ordinary_aliases():
    assert ProtocolHistory.as_langchain([]) == []
    for role in ("human", "user", "assistant", "ai", "system"):
        assert ProtocolHistory.as_langchain([Message(type=role, content="")])[0].content == ""


def test_original_ids_are_separate_from_database_row_ids():
    saved = ProtocolHistory.from_wire([{"role": "user", "content": "literal"}], message_ids=["provider-message"])
    saved[0].id = "42"
    assert ProtocolHistory.as_langchain(saved)[0].id == "provider-message"


def test_duplicate_calls_in_one_assistant_message():
    wire = exchange()[2]
    wire["tool_calls"][1]["id"] = "call_a"
    with pytest.raises(ValueError, match="Duplicate"):
        ProtocolHistory.to_wire(ProtocolHistory.from_wire([wire]))
