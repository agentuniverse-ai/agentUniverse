# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_prompt_manager.py
"""Unit tests for PromptManager."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


class TestPromptManager:
    def test_singleton(self):
        assert PromptManager() is PromptManager()

    def test_get_missing_instance_returns_none(self):
        assert PromptManager().get_instance_obj('no_such_prompt') is None

    def test_register_and_get(self):
        manager = PromptManager()
        prompt = Prompt(prompt_version='v1', prompt_template='tpl {x}')
        manager.register('test_prompt_185', prompt)
        try:
            retrieved = manager.get_instance_obj('test_prompt_185')
            assert retrieved is prompt
            assert retrieved.prompt_version == 'v1'
        finally:
            manager.unregister('test_prompt_185')

    def test_unregister_removes_instance(self):
        manager = PromptManager()
        manager.register('test_prompt_185_b', Prompt(prompt_version='v2'))
        manager.unregister('test_prompt_185_b')
        assert manager.get_instance_obj('test_prompt_185_b') is None

    def test_component_type_is_prompt(self):
        assert PromptManager()._component_type == ComponentEnum.PROMPT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
