# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 12:00
# @Author  : Yue Wang
# @FileName: test_discussion_group_template.py
"""Unit tests for discussion_group_template."""

import pytest

from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.peer_agent_app.intelligence.agentic.agent.agent_template.discussion_group_template import (
    DiscussionGroupTemplate,
)


class TestDiscussionGroupTemplate:
    """Test DiscussionGroupTemplate pure behaviors."""

    @pytest.fixture
    def template(self):
        return DiscussionGroupTemplate()

    def test_defaults(self, template):
        assert template.participant_names is None
        assert template.total_round == 2
        assert template.topic is None

    def test_keys(self, template):
        assert template.input_keys() == ["input"]
        assert template.output_keys() == ["output"]

    def test_parse_result_passthrough(self, template):
        assert template.parse_result({"output": "v"}) == {"output": "v"}

    def test_parse_input(self, template):
        template.participant_names = ["alpha", "beta"]
        template.total_round = 3
        agent_input = {}
        result = template.parse_input(InputObject({"input": "topic"}), agent_input)
        assert result is agent_input
        assert agent_input["input"] == "topic"
        assert agent_input["participants"] == ["alpha", "beta"]
        assert agent_input["total_round"] == 3

    def test_parse_input_falls_back_to_topic(self, template):
        template.topic = "built-in topic"
        agent_input = {}
        template.parse_input(InputObject({"other": 1}), agent_input)
        assert agent_input["input"] == "built-in topic"

    def test_generate_participant_agents_empty_raises(self):
        template = DiscussionGroupTemplate()
        template.participant_names = []
        with pytest.raises(ValueError, match="participant agents is empty"):
            template.generate_participant_agents()

    def test_initialize_keeps_state(self, template):
        template.participant_names = ["alpha"]
        template.total_round = 4
        assert template.participant_names == ["alpha"]
        assert template.total_round == 4
