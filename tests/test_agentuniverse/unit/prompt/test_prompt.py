# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:35
# @Author  : yuewang
# @FileName: test_prompt.py
"""Unit tests for the base Prompt class."""

from types import SimpleNamespace

import pytest
from langchain_core.prompts import PromptTemplate

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_model import AgentPromptModel


@pytest.fixture
def prompt():
    """Create a base Prompt."""
    return Prompt()


class TestPrompt:
    """Test Prompt behavior."""

    def test_component_type(self, prompt):
        assert prompt.component_type == ComponentEnum.PROMPT

    def test_as_langchain(self, prompt):
        prompt.prompt_template = 'Say {word}'
        prompt.input_variables = ['word']
        lc = prompt.as_langchain()
        assert isinstance(lc, PromptTemplate)
        assert lc.input_variables == ['word']

    def test_build_prompt(self, prompt):
        model = AgentPromptModel(introduction='intro', instruction='do {q}')
        result = prompt.build_prompt(model, ['introduction', 'instruction'])
        assert result is prompt
        assert prompt.prompt_template == 'intro\ndo {q}'
        assert prompt.input_variables == ['q']

    def test_initialize_by_component_configer(self, prompt):
        configer = SimpleNamespace(
            configer=SimpleNamespace(value={'instruction': 'say {x}', 'metadata': {'m': 1}}),
            metadata_version='v9')
        assert prompt.initialize_by_component_configer(configer) is prompt
        assert prompt.prompt_version == 'v9'
        assert prompt.prompt_template == 'say {x}'
        assert prompt.input_variables == ['x']
        assert not hasattr(prompt, 'metadata') or 'metadata' not in prompt.prompt_template

    def test_get_instance_code_returns_prompt_version(self, prompt):
        prompt.prompt_version = 'my.prompt.v1'
        assert prompt.get_instance_code() == 'my.prompt.v1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
