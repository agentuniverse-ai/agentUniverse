# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_default_memory.py
"""Unit tests for the DefaultMemory implementation."""

import pytest

from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.memory.default.default_memory import DefaultMemory
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.llm.default.default_openai_llm import DefaultOpenAILLM


class TestDefaultMemory:
    """Test the DefaultMemory class and its inherited defaults."""

    @pytest.fixture
    def memory(self):
        """Create a DefaultMemory instance for testing."""
        return DefaultMemory(name="default_memory")

    def test_initialization(self, memory):
        """Test basic initialization of a DefaultMemory instance."""
        assert memory.name == "default_memory"
        assert memory.component_type == ComponentEnum.MEMORY
        assert isinstance(memory.llm, DefaultOpenAILLM)

    def test_class_hierarchy(self, memory):
        """Test that DefaultMemory inherits from the memory base classes."""
        assert isinstance(memory, ChatMemory)
        assert isinstance(memory, Memory)

    def test_default_field_values(self, memory):
        """Test the default values of the memory data fields."""
        assert memory.type is None
        assert memory.memory_key == "chat_history"
        assert memory.max_tokens == 2000
        assert memory.input_key == "input"
        assert memory.output_key == "output"

    def test_default_llm_uses_gpt4o(self, memory):
        """Test that the default memory LLM is a gpt-4o DefaultOpenAILLM."""
        assert memory.llm.model_name == "gpt-4o"
        assert memory.llm.max_context_length() == 128000

    def test_llm_is_always_initialized_to_default(self):
        """Test that __init__ overrides any llm passed in by the caller."""
        other_llm = DefaultOpenAILLM(model_name="gpt-3.5-turbo")
        default_memory = DefaultMemory(llm=other_llm)
        assert isinstance(default_memory.llm, DefaultOpenAILLM)
        assert default_memory.llm.model_name == "gpt-4o"
        assert default_memory.llm is not other_llm

    def test_llm_api_key_read_from_env(self, monkeypatch):
        """Test that the default LLM picks up the OPENAI_API_KEY env variable."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        default_memory = DefaultMemory()
        assert default_memory.llm.api_key == "sk-test-key"

    def test_llm_api_key_is_none_without_env(self, monkeypatch):
        """Test that the default LLM has no api key when env is unset."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        default_memory = DefaultMemory()
        assert default_memory.llm.api_key is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
