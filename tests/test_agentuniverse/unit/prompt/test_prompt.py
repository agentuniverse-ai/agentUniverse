# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_prompt.py
"""Unit tests for the Prompt base class."""

import pytest

from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_model import AgentPromptModel
from langchain_core.prompts import PromptTemplate


class TestPrompt:
    def test_as_langchain(self):
        prompt = Prompt(prompt_version='v1', prompt_template='Hello {name}',
                        input_variables=['name'])
        template = prompt.as_langchain()
        assert isinstance(template, PromptTemplate)
        assert template.template == 'Hello {name}'
        assert template.input_variables == ['name']

    def test_get_instance_code_returns_version(self):
        prompt = Prompt(prompt_version='v1')
        assert prompt.get_instance_code() == 'v1'

    def test_build_prompt_joins_ordered_fields(self):
        prompt = Prompt()
        model = AgentPromptModel(introduction='Intro {name}', instruction='Do {task}')
        result = prompt.build_prompt(model, ['introduction', 'target', 'instruction'])
        assert result is prompt
        assert prompt.prompt_template == 'Intro {name}\nDo {task}'

    def test_build_prompt_extracts_input_variables(self):
        prompt = Prompt()
        model = AgentPromptModel(introduction='Hi {name}')
        prompt.build_prompt(model, ['introduction'])
        assert prompt.input_variables == ['name']

    def test_build_prompt_skips_missing_fields(self):
        prompt = Prompt()
        model = AgentPromptModel(target='Goal {g}')
        prompt.build_prompt(model, ['introduction', 'target'])
        assert prompt.prompt_template == 'Goal {g}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
