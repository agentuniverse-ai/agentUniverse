# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for agentuniverse.base.util.agent_util."""

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.agent_util import (
    assemble_memory_input,
    assemble_memory_output,
    process_agent_llm_config,
)


class _StubMemory:
    """Duck-typed memory stand-in recording get/add interactions."""
    def __init__(self, messages=None, memory_key="chat_history"):
        self.memory_key = memory_key
        self._messages = list(messages) if messages else []
        self.added = []
    def get(self, **kwargs):
        return list(self._messages)
    def add(self, message_list, **kwargs):
        self.added.extend(message_list)


class _StubDefaultLLMConfiger:
    """Minimal stand-in exposing only the default_llm attribute."""
    def __init__(self, default_llm=None):
        self.default_llm = default_llm


def _human_message(content):
    return Message(type="human", content=content, metadata={})


class TestProcessAgentLlmConfig:
    """Tests for process_agent_llm_config."""
    def test_missing_agent_id_returns_profile_unchanged(self):
        profile = {"llm_model": {"name": "gpt"}}
        configer = _StubDefaultLLMConfiger(default_llm="default")
        assert process_agent_llm_config(None, profile, configer) == profile
    def test_none_configer_returns_profile_unchanged(self):
        profile = {"llm_model": {"name": "gpt"}}
        assert process_agent_llm_config("agent_a", profile, None) == profile
    def test_existing_llm_name_is_preserved(self):
        profile = {"llm_model": {"name": "gpt"}}
        configer = _StubDefaultLLMConfiger(default_llm="default")
        assert process_agent_llm_config("agent_a", profile, configer) == profile
    def test_default_llm_is_applied_when_name_missing(self):
        configer = _StubDefaultLLMConfiger(default_llm="default-llm")
        result = process_agent_llm_config("agent_a", {"llm_model": {}}, configer)
        assert result == {"llm_model": {"name": "default-llm"}}
    def test_no_default_llm_leaves_empty_model_config(self):
        configer = _StubDefaultLLMConfiger(default_llm=None)
        assert process_agent_llm_config("agent_a", {}, configer) == {"llm_model": {}}


class TestAssembleMemory:
    """Tests for assemble_memory_input and assemble_memory_output."""
    def test_assemble_memory_input_adds_history_to_agent_input(self):
        memory = _StubMemory(messages=[_human_message("hi")])
        agent_input = {"agent_id": "test-agent"}
        result = assemble_memory_input(memory, agent_input, None)
        assert len(result) == 1
        assert result[0].content == "hi"
        assert "hi" in agent_input[memory.memory_key]
    def test_assemble_memory_input_uses_query_params_when_given(self):
        memory = _StubMemory(messages=[_human_message("from-query")])
        agent_input = {"agent_id": "test-agent"}
        result = assemble_memory_input(memory, agent_input, {"session_id": "s1"})
        assert result[0].content == "from-query"
        assert memory.memory_key in agent_input
    def test_assemble_memory_input_none_memory_is_noop(self):
        agent_input = {"agent_id": "test-agent"}
        assert assemble_memory_input(None, agent_input, None) == []
        assert agent_input == {"agent_id": "test-agent"}
    def test_assemble_memory_output_appends_current_message(self):
        memory = _StubMemory(messages=[_human_message("history")])
        history = [_human_message("earlier")]
        result = assemble_memory_output(
            memory, {"agent_id": "test-agent"}, "current answer", "source-1", history
        )
        assert len(result) == 2
        assert result[-1].content == "current answer"
        assert result[-1].source == "source-1"
        assert memory.added[0].content == "current answer"
    def test_assemble_memory_output_creates_list_when_none(self):
        memory = _StubMemory()
        result = assemble_memory_output(memory, {"agent_id": "x"}, "answer")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].content == "answer"
