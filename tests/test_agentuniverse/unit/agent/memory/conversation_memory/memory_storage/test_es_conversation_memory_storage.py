# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08 10:00
# @Author  : test
# @FileName: test_es_conversation_memory_storage.py
"""Unit tests for es_conversation_memory_storage (offline, no ES server)."""

import datetime
import json

import pytest

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.memory_storage.es_conversation_memory_storage import (
    DefaultMemoryConverter,
    ElasticsearchMemoryStorage,
)


class TestElasticsearchMemoryStorage:
    """Tests for ElasticsearchMemoryStorage instantiation defaults."""

    def test_storage_defaults(self):
        storage = ElasticsearchMemoryStorage()
        assert storage.es_url == "http://localhost:9200"
        assert storage.index_name == "memory" and storage.memory_converter is None
        assert storage.user is None and storage.password is None and storage.timeout == 60
        assert storage.client is None


class TestDefaultMemoryConverter:
    """Tests for the pure DefaultMemoryConverter class."""

    @pytest.fixture
    def converter(self):
        return DefaultMemoryConverter("memory")

    @pytest.fixture
    def message(self):
        return ConversationMessage(
            id="es-msg-1", type="output", source="agent_a", source_type="agent",
            target="agent_b", target_type="agent", content="es hello", trace_id="tr-1",
            metadata={"prefix": "pre", "timestamp": datetime.datetime(2024, 1, 1, 12, 0, 0),
                      "params": "{}", "pair_id": "pair-1", "additional_args": {}})

    def test_to_es_action_format(self, converter, message):
        line1, line2 = converter.to_es_action(message, session_id="s1").split("\n")
        assert json.loads(line1) == {"index": {"_index": "memory", "_id": "es-msg-1"}}
        doc = json.loads(line2)
        assert doc["session_id"] == "s1" and doc["content"] == "es hello"
        assert doc["type"] == "output" and doc["trace_id"] == "tr-1"
        assert doc["source_type"] == "agent" and doc["target_type"] == "agent"
        assert doc["prefix"] == "pre" and doc["params"] == "{}" and doc["pair_id"] == "pair-1"
        assert doc["timestamp"] == "2024-01-01T12:00:00"

    def test_to_es_action_default_timestamp(self, converter):
        msg = ConversationMessage(id="es-msg-2", type="input", source_type="user",
                                  target_type="agent", content="x", metadata={})
        doc = json.loads(converter.to_es_action(msg, session_id="s2").split("\n")[1])
        assert doc["session_id"] == "s2"
        assert isinstance(datetime.datetime.fromisoformat(doc["timestamp"]), datetime.datetime)

    def test_from_es_hit(self, converter):
        hit = {"_id": "es-msg-1",
               "_source": {"session_id": "s1", "source": "agent_a", "source_type": "agent",
                           "target": "agent_b", "target_type": "agent", "content": "es hello",
                           "prefix": "pre", "timestamp": "2024-01-01T12:00:00", "params": "{}",
                           "pair_id": "pair-1", "type": "output", "trace_id": "tr-1",
                           "additional_args": {}}}
        msg = converter.from_es_hit(hit)
        assert isinstance(msg, ConversationMessage)
        assert msg.id == "es-msg-1" and msg.conversation_id == "s1"
        assert msg.type == "output" and msg.content == "es hello" and msg.trace_id == "tr-1"
        assert (msg.source, msg.source_type, msg.target, msg.target_type) == \
            ("agent_a", "agent", "agent_b", "agent")
        assert msg.metadata["timestamp"] == datetime.datetime(2024, 1, 1, 12, 0, 0)
        assert msg.metadata["prefix"] == "pre" and msg.metadata["pair_id"] == "pair-1"

    def test_to_es_action_from_es_hit_roundtrip(self, converter, message):
        action = converter.to_es_action(message, session_id="s1")
        line1, line2 = action.split("\n")
        hit = {"_id": json.loads(line1)["index"]["_id"], "_source": json.loads(line2)}
        back = converter.from_es_hit(hit)
        assert back.id == "es-msg-1" and back.content == "es hello"
        assert back.type == "output" and back.conversation_id == "s1"
        assert back.trace_id == "tr-1" and back.metadata["prefix"] == "pre"
        assert back.metadata["timestamp"] == datetime.datetime(2024, 1, 1, 12, 0, 0)
