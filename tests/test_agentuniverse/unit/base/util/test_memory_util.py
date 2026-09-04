# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for agentuniverse.base.util.memory_util."""

from types import SimpleNamespace

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.memory_util import (
    generate_memories,
    generate_messages,
    get_memory_string,
)


class TestGenerateMessages:
    """Tests for generate_messages."""

    def test_empty_input_returns_empty_list(self):
        assert generate_messages([]) == []

    def test_string_input_becomes_message(self):
        result = generate_messages(["plain"])
        assert len(result) == 1
        assert isinstance(result[0], Message)
        assert result[0].content == "plain"

    def test_dict_input_keeps_type_and_content(self):
        result = generate_messages([{"content": "d", "type": "ai"}])
        assert result[0].type == "ai"
        assert result[0].content == "d"

    def test_message_instance_passes_through(self):
        message = Message(content="m", type="human")
        assert generate_messages([message]) == [message]


class TestGenerateMemories:
    """Tests for generate_memories."""

    def test_empty_history_returns_empty_list(self):
        assert generate_memories(SimpleNamespace(messages=[])) == []

    def test_langchain_messages_become_dicts(self):
        history = SimpleNamespace(messages=[HumanMessage(content="h"), AIMessage(content="a")])
        assert generate_memories(history) == [
            {"content": "h", "type": "human"},
            {"content": "a", "type": "ai"},
        ]

    def test_ai_message_chunk_maps_to_ai(self):
        history = SimpleNamespace(messages=[AIMessageChunk(content="chunk")])
        assert generate_memories(history) == [{"content": "chunk", "type": "ai"}]


class TestGetMemoryString:
    """Tests for get_memory_string."""

    def test_empty_messages_returns_empty_string(self):
        assert get_memory_string([]) == ""

    def test_human_message_renders_human_role(self):
        message = Message(type="human", content="hi", metadata={})
        assert get_memory_string([message]) == "Message role: Human  :hi "

    def test_system_message_renders_metadata_and_source(self):
        message = Message(
            type="system",
            content="sys",
            metadata={"gmt_created": "2024-01-01"},
            source="src",
        )
        rendered = get_memory_string([message])
        assert "2024-01-01" in rendered
        assert "Message source: src" in rendered
        assert "Message role: System" in rendered
        assert ":sys " in rendered

    def test_ai_message_renders_ai_role(self):
        message = Message(type="ai", content="answer", metadata={})
        assert get_memory_string([message]) == "Message role: AI  :answer "
