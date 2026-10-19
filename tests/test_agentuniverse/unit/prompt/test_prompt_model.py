# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:00
# @Author  : yuewang
# @FileName: test_prompt_model.py
"""Unit tests for AgentPromptModel."""

import pytest

from agentuniverse.prompt.prompt_model import AgentPromptModel


@pytest.fixture
def model():
    """Create an empty AgentPromptModel."""
    return AgentPromptModel()


class TestAgentPromptModel:
    """Test AgentPromptModel behavior."""

    def test_defaults(self, model):
        assert model.introduction is None
        assert model.target is None
        assert model.instruction is None

    def test_bool_empty(self, model):
        assert not model

    def test_bool_nonempty(self):
        assert AgentPromptModel(introduction='i')
        assert AgentPromptModel(target='t')
        assert AgentPromptModel(instruction='ins')

    def test_get_message_type(self, model):
        assert model.get_message_type('introduction') == 'system'
        assert model.get_message_type('target') == 'system'
        assert model.get_message_type('instruction') == 'human'
        assert model.get_message_type('unknown_attr') == 'human'

    def test_add_merges_with_left_priority(self):
        left = AgentPromptModel(introduction='keep-left', target=None)
        right = AgentPromptModel(introduction='right', target='right-target')
        merged = left + right
        assert merged.introduction == 'keep-left'
        assert merged.target == 'right-target'

    def test_add_empty_left_takes_right(self):
        right = AgentPromptModel(instruction='only-right')
        merged = AgentPromptModel() + right
        assert merged.instruction == 'only-right'
        assert merged.introduction is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
