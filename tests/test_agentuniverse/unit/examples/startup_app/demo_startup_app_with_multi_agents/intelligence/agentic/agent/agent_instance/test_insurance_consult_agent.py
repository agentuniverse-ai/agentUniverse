# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_consult_agent.py
import unittest

from agentuniverse.agent.input_object import InputObject

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.agentic.agent.agent_instance.insurance_consult_agent import (
    InsuranceConsultAgent,
)


class InsuranceConsultAgentTest(unittest.TestCase):
    """Unit tests for InsuranceConsultAgent pure behaviors."""

    def setUp(self):
        self.agent = InsuranceConsultAgent()

    def test_input_keys(self):
        self.assertEqual(self.agent.input_keys(), ['input'])

    def test_output_keys(self):
        self.assertEqual(self.agent.output_keys(), ['output'])

    def test_parse_input_reads_input_field(self):
        input_object = InputObject({'input': 'which insurance?'})
        agent_input = self.agent.parse_input(input_object, {})
        self.assertEqual(agent_input['input'], 'which insurance?')

    def test_parse_input_keeps_existing_agent_input(self):
        input_object = InputObject({'input': 'q'})
        agent_input = self.agent.parse_input(input_object, {'extra': 3})
        self.assertEqual(agent_input['extra'], 3)
        self.assertEqual(agent_input['input'], 'q')

    def test_parse_result_returns_result_unchanged(self):
        agent_result = {'output': 'consult answer', 'other': 'kept'}
        self.assertEqual(self.agent.parse_result(agent_result), agent_result)
