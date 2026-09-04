# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the InsuranceAgentTemplate example template (pure parts)."""

from agentuniverse.agent.input_object import InputObject
from examples.startup_app.demo_startup_app_with_agent_templates.intelligence.agentic.agent.agent_template.insurance_agent_template import InsuranceAgentTemplate


class TestInsuranceAgentTemplate:
    """Test template input/output keys and pure parse methods."""

    def test_input_keys(self):
        assert InsuranceAgentTemplate().input_keys() == ["input"]

    def test_output_keys(self):
        assert InsuranceAgentTemplate().output_keys() == ["output"]

    def test_default_agent_names(self):
        template = InsuranceAgentTemplate()
        assert template.planning_agent_name is None
        assert template.executing_agent_name is None
        assert template.expressing_agent_name is None

    def test_parse_result_identity(self):
        template = InsuranceAgentTemplate()
        result = template.parse_result({"input": "hi"})
        assert result == {"input": "hi"}
