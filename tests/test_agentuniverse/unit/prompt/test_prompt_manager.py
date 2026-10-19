# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:40
# @Author  : yuewang
# @FileName: test_prompt_manager.py
"""Unit tests for PromptManager."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.prompt.prompt_manager import PromptManager


@pytest.fixture
def manager():
    """Return the PromptManager singleton."""
    return PromptManager()


class TestPromptManager:
    """Test PromptManager lookup behavior."""

    def test_singleton(self, manager):
        assert manager is PromptManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.PROMPT

    def test_register_and_get_by_raw_name(self, manager):
        prompt = object()
        manager._instance_obj_map['my.prompt.v1'] = prompt
        assert manager.get_instance_obj('my.prompt.v1') is prompt
        # lookup ignores appname entirely
        assert manager.get_instance_obj('my.prompt.v1', appname='anything') is prompt

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent.prompt.xyz') is None

    def test_unregister(self, manager):
        manager._instance_obj_map['p2'] = object()
        manager.unregister('p2')
        assert manager.get_instance_obj('p2') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
