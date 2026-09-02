# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_memory_compressor.py
"""Unit tests for the base MemoryCompressor component."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.memory.memory_compressor.memory_compressor import MemoryCompressor
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum

_COMPRESSOR_MODULE = "agentuniverse.agent.memory.memory_compressor.memory_compressor"


class TestMemoryCompressor:
    """Test the MemoryCompressor base component behavior."""

    @pytest.fixture
    def compressor(self):
        """Create a MemoryCompressor instance for testing."""
        return MemoryCompressor()

    def test_default_attribute_values(self, compressor):
        assert compressor.name is None
        assert compressor.description is None
        assert compressor.compressor_prompt_version is None
        assert compressor.compressor_llm_name is None

    def test_component_type(self, compressor):
        assert isinstance(compressor, ComponentBase)
        assert compressor.component_type == ComponentEnum.MEMORY_COMPRESSOR

    def test_initialize_by_component_configer_full(self, compressor):
        configer = SimpleNamespace(name="summary_compressor", description="Compress history.",
                                   compressor_prompt_version="memory_compress_prompt",
                                   compressor_llm_name="default_openai_llm")
        result = compressor._initialize_by_component_configer(configer)
        assert result is compressor
        assert compressor.name == "summary_compressor"
        assert compressor.description == "Compress history."
        assert compressor.compressor_prompt_version == "memory_compress_prompt"
        assert compressor.compressor_llm_name == "default_openai_llm"

    def test_initialize_by_component_configer_partial(self, compressor):
        compressor._initialize_by_component_configer(SimpleNamespace(name="named_compressor"))
        assert compressor.name == "named_compressor"
        assert compressor.description is None
        assert compressor.compressor_prompt_version is None
        assert compressor.compressor_llm_name is None

    def test_initialize_skips_falsy_values(self, compressor):
        compressor.name = "preset_name"
        compressor._initialize_by_component_configer(
            SimpleNamespace(name="", description=None, compressor_prompt_version="", compressor_llm_name="llm_a"))
        assert compressor.name == "preset_name"
        assert compressor.description is None
        assert compressor.compressor_prompt_version is None
        assert compressor.compressor_llm_name == "llm_a"

    def test_compress_memory_empty_when_instances_missing(self, monkeypatch):
        class FakePromptManager:
            def get_instance_obj(self, component_instance_name, appname=None, new_instance=False):
                return None

        class FakeLLMManager:
            def get_instance_obj(self, component_instance_name, appname=None, new_instance=True):
                return None

        monkeypatch.setattr(f"{_COMPRESSOR_MODULE}.PromptManager", FakePromptManager)
        monkeypatch.setattr(f"{_COMPRESSOR_MODULE}.LLMManager", FakeLLMManager)
        assert MemoryCompressor().compress_memory(new_memories=[], max_tokens=500,
                                                  existing_memory="old") == ""

    def test_compress_memory_empty_when_llm_missing(self, monkeypatch):
        class FakePromptManager:
            def get_instance_obj(self, component_instance_name, appname=None, new_instance=False):
                return object()

        class FakeLLMManager:
            def get_instance_obj(self, component_instance_name, appname=None, new_instance=True):
                return None

        monkeypatch.setattr(f"{_COMPRESSOR_MODULE}.PromptManager", FakePromptManager)
        monkeypatch.setattr(f"{_COMPRESSOR_MODULE}.LLMManager", FakeLLMManager)
        assert MemoryCompressor().compress_memory(new_memories=[]) == ""
