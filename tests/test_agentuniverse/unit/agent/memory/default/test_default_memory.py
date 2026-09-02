# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:15
# @Author  : yuewang
# @FileName: test_default_memory.py
"""Unit tests for DefaultMemory."""

import pytest

from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.memory.default.default_memory import DefaultMemory
from agentuniverse.llm.default.default_openai_llm import DefaultOpenAILLM


@pytest.fixture
def memory():
    """Create a DefaultMemory instance for testing."""
    return DefaultMemory(name="test_default_memory", description="d")


class TestDefaultMemory:
    """Test DefaultMemory initialization behavior."""

    def test_name_and_description(self, memory):
        """Test that name/description are set from kwargs."""
        assert memory.name == "test_default_memory"
        assert memory.description == "d"

    def test_is_chat_memory(self, memory):
        """Test that DefaultMemory is a ChatMemory subclass instance."""
        assert isinstance(memory, ChatMemory)
        assert type(memory).__name__ == "DefaultMemory"

    def test_llm_is_default_openai_llm(self, memory):
        """Test that the memory uses a DefaultOpenAILLM instance."""
        assert isinstance(memory.llm, DefaultOpenAILLM)

    def test_llm_model_name(self, memory):
        """Test that the memory LLM is configured with gpt-4o."""
        assert memory.llm.model_name == "gpt-4o"

    def test_llm_is_independent_per_instance(self):
        """Test that two memories do not share the same LLM object."""
        m1 = DefaultMemory(name="m1")
        m2 = DefaultMemory(name="m2")
        assert m1.llm is not m2.llm
        assert m1.llm.model_name == m2.llm.model_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
