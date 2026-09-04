# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the InsurancePlanningAgent example agent (pure parts)."""

from agentuniverse.agent.input_object import InputObject
from examples.startup_app.demo_startup_app_with_agent_templates.intelligence.agentic.agent.agent_instance.insurance_planning_agent import InsurancePlanningAgent


class TestInsurancePlanningAgent:
    """Test agent input/output keys and pure parse methods."""

    def test_input_keys(self):
        assert InsurancePlanningAgent().input_keys() == [
            "input", "prod_description"]

    def test_output_keys(self):
        assert InsurancePlanningAgent().output_keys() == ["planning_output"]

    def test_parse_input_copies_fields(self):
        agent = InsurancePlanningAgent()
        input_object = InputObject({"input": "i", "prod_description": "p"})
        agent_input = agent.parse_input(input_object, {})
        assert agent_input == {"input": "i", "prod_description": "p"}

    def test_parse_result_exposes_planning_output(self):
        agent = InsurancePlanningAgent()
        result = agent.parse_result({"output": "plan"})
        assert result["planning_output"] == "plan"
