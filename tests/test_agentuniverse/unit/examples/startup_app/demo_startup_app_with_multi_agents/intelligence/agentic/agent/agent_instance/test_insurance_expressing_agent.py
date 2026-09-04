# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_expressing_agent.py
import unittest

from agentuniverse.agent.input_object import InputObject

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.agentic.agent.agent_instance.insurance_expressing_agent import (
    InsuranceExpressingAgent,
)


class InsuranceExpressingAgentTest(unittest.TestCase):
    """Unit tests for InsuranceExpressingAgent pure behaviors."""

    def setUp(self):
        self.agent = InsuranceExpressingAgent()

    def test_input_keys(self):
        self.assertEqual(self.agent.input_keys(),
                         ['input', 'prod_description', 'search_context'])

    def test_output_keys(self):
        self.assertEqual(self.agent.output_keys(), ['output'])

    def test_parse_input_reads_all_fields(self):
        input_object = InputObject({
            'input': 'user question',
            'prod_description': 'product A',
            'search_context': 'search result',
        })
        agent_input = self.agent.parse_input(input_object, {})
        self.assertEqual(agent_input['input'], 'user question')
        self.assertEqual(agent_input['prod_description'], 'product A')
        self.assertEqual(agent_input['search_context'], 'search result')

    def test_parse_input_keeps_existing_agent_input(self):
        input_object = InputObject({
            'input': 'q',
            'prod_description': 'p',
            'search_context': 's',
        })
        agent_input = self.agent.parse_input(input_object, {'extra': 1})
        self.assertEqual(agent_input['extra'], 1)

    def test_parse_result_exposes_output(self):
        agent_result = self.agent.parse_result({'output': 'final answer'})
        self.assertEqual(agent_result['output'], 'final answer')

    def test_parse_result_keeps_original_keys(self):
        agent_result = self.agent.parse_result(
            {'output': 'ans', 'other': 'kept'})
        self.assertEqual(agent_result['other'], 'kept')
