# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_prompt_model.py
"""Unit tests for AgentPromptModel."""

import pytest

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.prompt.prompt_model import AgentPromptModel


class TestAgentPromptModel:
    def test_defaults_are_none(self):
        model = AgentPromptModel()
        assert model.introduction is None
        assert model.target is None
        assert model.instruction is None

    def test_bool_empty_is_false(self):
        assert not AgentPromptModel()

    def test_bool_with_content_is_true(self):
        assert AgentPromptModel(target='goal')

    def test_add_merges_fields(self):
        merged = AgentPromptModel(introduction='intro') + AgentPromptModel(target='goal')
        assert merged.introduction == 'intro'
        assert merged.target == 'goal'
        assert merged.instruction is None

    def test_add_left_wins_on_conflict(self):
        merged = AgentPromptModel(instruction='left') + AgentPromptModel(instruction='right')
        assert merged.instruction == 'left'

    def test_get_message_type_mapping(self):
        model = AgentPromptModel()
        assert model.get_message_type('introduction') == ChatMessageEnum.SYSTEM.value
        assert model.get_message_type('instruction') == ChatMessageEnum.HUMAN.value

    def test_get_message_type_default_human(self):
        assert AgentPromptModel().get_message_type('unknown_field') == ChatMessageEnum.HUMAN.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
