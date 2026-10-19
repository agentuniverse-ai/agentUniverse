# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:45
# @Author  : yuewang
# @FileName: test_memory_compressor.py
"""Unit tests for MemoryCompressor."""

import pytest
from unittest.mock import MagicMock

from agentuniverse.agent.memory.memory_compressor.memory_compressor import MemoryCompressor
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt_manager import PromptManager


class FakeChain:
    """Minimal chain supporting the | operator and invoke."""

    def __init__(self, name):
        self.name = name
        self.last_input = None

    def __or__(self, other):
        return self

    def invoke(self, input=None):
        self.last_input = input
        return f'compressed({input["max_tokens"]})'


@pytest.fixture
def compressor():
    """Create a MemoryCompressor with fixed config."""
    return MemoryCompressor(
        name='test_compressor',
        description='d',
        compressor_prompt_version='v1',
        compressor_llm_name='llm1',
    )


class TestMemoryCompressorConfig:
    """Test component config initialization."""

    def test_component_type(self, compressor):
        assert compressor.component_type == ComponentEnum.MEMORY_COMPRESSOR

    def test_initialize_by_component_configer(self):
        config = type('C', (), {'name': 'c2', 'description': 'dd',
                                'compressor_prompt_version': 'v2',
                                'compressor_llm_name': 'llm2'})()
        c = MemoryCompressor()
        assert c._initialize_by_component_configer(config) is c
        assert c.name == 'c2'
        assert c.compressor_prompt_version == 'v2'
        assert c.compressor_llm_name == 'llm2'

class TestMemoryCompressorCompress:
    """Test compress_memory with mocked Prompt/LLM managers."""

    def test_returns_empty_when_prompt_or_llm_missing(self, compressor, monkeypatch):
        monkeypatch.setattr(PromptManager(), 'get_instance_obj', lambda name: None)
        monkeypatch.setattr(LLMManager(), 'get_instance_obj', lambda name: None)
        result = compressor.compress_memory([Message(type='human', content='x', metadata={})])
        assert result == ''

    def test_compress_invokes_chain_with_memory_string(self, compressor, monkeypatch):
        prompt_chain = FakeChain('prompt')
        llm_mock = MagicMock()
        llm_mock.as_langchain.return_value = prompt_chain  # | keeps the first chain
        monkeypatch.setattr(PromptManager(), 'get_instance_obj', lambda name: MagicMock(
            as_langchain=MagicMock(return_value=prompt_chain)))
        monkeypatch.setattr(LLMManager(), 'get_instance_obj', lambda name: llm_mock)
        memories = [Message(type='human', content='hello world', metadata={})]
        result = compressor.compress_memory(memories, max_tokens=123, existing_memory='old')
        assert result == 'compressed(123)'
        assert 'hello world' in prompt_chain.last_input['new_lines']
        assert prompt_chain.last_input['summary'] == 'old'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
