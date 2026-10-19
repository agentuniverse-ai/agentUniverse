# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the InsuranceExpressingAgent example agent (pure parts)."""

from agentuniverse.agent.input_object import InputObject
from examples.startup_app.demo_startup_app_with_agent_templates.intelligence.agentic.agent.agent_instance.insurance_expressing_agent import InsuranceExpressingAgent


class TestInsuranceExpressingAgent:
    """Test agent input/output keys and pure parse methods."""

    def test_input_keys(self):
        assert InsuranceExpressingAgent().input_keys() == [
            "input", "prod_description", "search_context"]

    def test_output_keys(self):
        assert InsuranceExpressingAgent().output_keys() == ["output"]

    def test_parse_input_copies_fields(self):
        agent = InsuranceExpressingAgent()
        input_object = InputObject({"input": "i", "prod_description": "p",
                                    "search_context": "s"})
        agent_input = agent.parse_input(input_object, {})
        assert agent_input == {"input": "i", "prod_description": "p",
                              "search_context": "s"}
