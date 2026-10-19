# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_memory_util.py
"""Unit tests for the memory_util helpers."""

from types import SimpleNamespace
from unittest.mock import patch

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.memory_util import (generate_messages, generate_memories,
                                                  get_memory_string, get_memory_tokens)


class TestGenerateMessages:
    """Test generate_messages coercion of memory inputs."""

    def test_message_passthrough(self):
        """An existing Message instance is returned unchanged."""
        m = Message(content="hi", type="human", metadata={})
        assert generate_messages([m]) == [m]

    def test_str_and_dict_coercion(self):
        """Strings and dicts become Messages; role maps to type."""
        [s] = generate_messages(["hello"])
        assert isinstance(s, Message) and s.content == "hello" and s.metadata == {}
        [d] = generate_messages([{"role": "human", "content": "hi"}])
        assert isinstance(d, Message) and d.type == "human" and d.content == "hi"

    def test_unknown_type_skipped(self):
        """Inputs that are not Message/dict/str are skipped."""
        assert generate_messages([1, 2.0, None]) == []


class TestGenerateMemories:
    """Test generate_memories conversion of chat history."""

    def test_converts_messages_to_dicts(self):
        """Each chat message becomes a {content, type} dict."""
        hist = SimpleNamespace(messages=[
            SimpleNamespace(content="a", type="human"),
            SimpleNamespace(content="b", type="AIMessageChunk"),
        ])
        assert generate_memories(hist) == [
            {"content": "a", "type": "human"},
            {"content": "b", "type": "ai"},
        ]
        assert generate_memories(SimpleNamespace(messages=[])) == []


class TestGetMemoryString:
    """Test get_memory_string formatting."""

    def test_human_message_formatting(self):
        """A human message is rendered with its gmt_created and source."""
        msg = Message(content="hello", type="human",
                      metadata={"gmt_created": "2024-01-01 00:00:00"}, source="web")
        s = get_memory_string([msg])
        assert all(p in s for p in ("2024-01-01 00:00:00", "Message source: web",
                                    "Message role: Human", "hello"))

    def test_system_role_and_joining(self):
        """System messages are labeled System; messages join with blank lines."""
        a = Message(content="a", type="human", metadata={})
        b = Message(content="sys", type="system", metadata={})
        s = get_memory_string([a, b])
        assert "Message role: System" in s
        assert s.count("\n\n") == 1


class TestGetMemoryTokens:
    """Test get_memory_tokens with a mocked LLM manager."""

    def test_falls_back_to_string_length(self):
        """When no LLM resolves, the count is the rendered string length."""
        msg = Message(content="hello world", type="human", metadata={})
        with patch("agentuniverse.base.util.memory_util.LLMManager") as m:
            m.return_value.get_instance_obj.return_value = None
            assert get_memory_tokens([msg]) == len(get_memory_string([msg]))

    def test_uses_llm_token_counter(self):
        """When an LLM resolves, its token counter is used."""
        msg = Message(content="hello", type="human", metadata={})
        with patch("agentuniverse.base.util.memory_util.LLMManager") as m:
            m.return_value.get_instance_obj.return_value.get_num_tokens.return_value = 7
            assert get_memory_tokens([msg], llm_name="gpt") == 7
