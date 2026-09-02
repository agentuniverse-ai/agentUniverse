# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 10:30
# @Author  : Yue Wang
# @FileName: test_agent_util.py
"""Unit tests for agent_util memory helpers."""

from unittest.mock import MagicMock, patch

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.agent_util import (
    assemble_memory_input,
    assemble_memory_output,
    process_agent_llm_config,
)


class TestAssembleMemoryInput:
    """Test assemble_memory_input."""

    def test_returns_empty_list_without_memory(self):
        """No memory object produces an empty message list."""
        assert assemble_memory_input(None, {"input": "hi"}) == []

    def test_retrieves_messages_and_fills_agent_input(self):
        """Retrieved messages are returned and their string is stored in agent_input."""
        memory = MagicMock()
        memory.memory_key = "memory"
        stored = [Message(content="old", source="user")]
        memory.get.return_value = stored
        with patch("agentuniverse.base.util.agent_util.get_memory_string",
                   return_value="old") as mock_str:
            agent_input = {"input": "hi"}
            result = assemble_memory_input(memory, agent_input)
        assert result is stored
        assert agent_input["memory"] == "old"
        mock_str.assert_called_once_with(stored, None)

    def test_uses_query_params_when_provided(self):
        memory = MagicMock()
        memory.memory_key = "memory"
        memory.get.return_value = []
        with patch("agentuniverse.base.util.agent_util.get_memory_string", return_value=""):
            assemble_memory_input(memory, {"input": "hi"}, {"input": "q"})
        memory.get.assert_called_once_with(input="q")


class TestAssembleMemoryOutput:
    """Test assemble_memory_output."""

    def test_appends_current_message(self):
        """The current content is wrapped into a Message and appended."""
        result = assemble_memory_output(None, {}, "answer", source="agent")
        assert result[0].content == "answer"
        assert result[0].source == "agent"

    def test_extends_existing_messages_and_adds_to_memory(self):
        """Existing history is kept and the new message is added to memory."""
        memory = MagicMock()
        history = [Message(content="old", source="user")]
        agent_input = {"input": "hi"}
        result = assemble_memory_output(memory, agent_input, "answer",
                                        source="agent", memory_messages=history)
        assert [m.content for m in result] == ["old", "answer"]
        added, kwargs = memory.add.call_args
        assert added[0][0].content == "answer"
        assert kwargs == agent_input


class TestProcessAgentLlmConfig:
    """Test process_agent_llm_config default LLM resolution."""

    def test_keeps_explicit_llm_name(self):
        configer = MagicMock()
        configer.default_llm = "default-llm"
        profile = process_agent_llm_config("agent_1", {"llm_model": {"name": "gpt-4"}}, configer)
        assert profile["llm_model"]["name"] == "gpt-4"

    def test_fills_default_llm_name(self):
        configer = MagicMock()
        configer.default_llm = "default-llm"
        result = process_agent_llm_config("agent_1", {"name": "a"}, configer)
        assert result["llm_model"]["name"] == "default-llm"

    def test_no_default_llm_available(self):
        """Without a configured default LLM the profile only gains an empty llm_model."""
        configer = MagicMock()
        configer.default_llm = None
        assert process_agent_llm_config("agent_1", None, configer) == {"llm_model": {}}
