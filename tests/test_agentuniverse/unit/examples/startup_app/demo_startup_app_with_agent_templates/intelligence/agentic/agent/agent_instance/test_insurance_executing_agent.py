# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the InsuranceExecutingAgent example agent (pure parts)."""

from agentuniverse.agent.input_object import InputObject
from examples.startup_app.demo_startup_app_with_agent_templates.intelligence.agentic.agent.agent_instance.insurance_executing_agent import InsuranceExecutingAgent


class TestInsuranceExecutingAgent:
    """Test agent input/output keys and pure parse methods."""

    def test_input_keys(self):
        assert InsuranceExecutingAgent().input_keys() == ["sub_query_list"]

    def test_output_keys(self):
        assert InsuranceExecutingAgent().output_keys() == ["search_context"]

    def test_parse_input_copies_sub_query_list(self):
        agent = InsuranceExecutingAgent()
        input_object = InputObject({"sub_query_list": ["q1"]})
        agent_input = agent.parse_input(input_object, {})
        assert agent_input["sub_query_list"] == ["q1"]

    def test_parse_result_preserves_search_context(self):
        agent = InsuranceExecutingAgent()
        result = agent.parse_result({"search_context": "ctx", "other": 1})
        assert result["search_context"] == "ctx"
        assert result["other"] == 1
