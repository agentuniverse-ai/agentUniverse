import pytest

from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.memory.transcript import (
    messages_from_jsonl,
    messages_to_jsonl,
)


def test_jsonl_round_trip_preserves_all_message_fields():
    messages = [
        Message(
            id="message-1",
            type="human",
            content="hello",
            source="user",
            metadata={"locale": "zh-CN"},
        ),
        Message(
            id="message-2",
            type="ai",
            content=["caption", {"type": "image_url", "url": "image.png"}],
            source="assistant",
            metadata={"model": "example"},
        ),
    ]

    transcript = messages_to_jsonl(messages)

    assert transcript.endswith("\n")
    assert messages_from_jsonl(transcript) == messages
    assert messages_from_jsonl(transcript.encode()) == messages


def test_blank_lines_are_ignored():
    transcript = '\n{"id":"1","type":"human","content":"hello"}\n\n'

    messages = messages_from_jsonl(transcript)

    assert messages == [Message(id="1", type="human", content="hello")]


def test_invalid_json_reports_the_source_line():
    with pytest.raises(ValueError, match="Invalid JSON.*line 3"):
        messages_from_jsonl('\n{"content":"ok"}\nnot-json')


def test_invalid_message_reports_the_source_line():
    with pytest.raises(ValueError, match="Invalid message.*line 2"):
        messages_from_jsonl("\n[]")


def test_invalid_utf8_and_input_type_are_rejected():
    with pytest.raises(ValueError, match="valid UTF-8"):
        messages_from_jsonl(b"\xff")
    with pytest.raises(TypeError, match="str or bytes"):
        messages_from_jsonl(None)


def test_serializer_requires_message_objects():
    with pytest.raises(TypeError, match="item 2"):
        messages_to_jsonl([Message(content="ok"), {"content": "invalid"}])


def test_empty_transcript_round_trip():
    assert messages_to_jsonl([]) == ""
    assert messages_from_jsonl("") == []
