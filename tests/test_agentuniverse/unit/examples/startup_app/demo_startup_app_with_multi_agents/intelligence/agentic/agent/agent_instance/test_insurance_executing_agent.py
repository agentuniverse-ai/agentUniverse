# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_executing_agent.py
import unittest

from agentuniverse.agent.input_object import InputObject

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.agentic.agent.agent_instance.insurance_executing_agent import (
    InsuranceExecutingAgent,
)


class InsuranceExecutingAgentTest(unittest.TestCase):
    """Unit tests for InsuranceExecutingAgent pure behaviors."""

    def setUp(self):
        self.agent = InsuranceExecutingAgent()

    def test_input_keys(self):
        self.assertEqual(self.agent.input_keys(), ['sub_query_list'])

    def test_output_keys(self):
        self.assertEqual(self.agent.output_keys(), ['search_context'])

    def test_parse_input_reads_sub_query_list(self):
        input_object = InputObject({'sub_query_list': ['q1', 'q2']})
        agent_input = self.agent.parse_input(input_object, {})
        self.assertEqual(agent_input['sub_query_list'], ['q1', 'q2'])

    def test_parse_input_keeps_existing_agent_input(self):
        input_object = InputObject({'sub_query_list': ['q1']})
        agent_input = self.agent.parse_input(input_object, {'extra': 'kept'})
        self.assertEqual(agent_input['extra'], 'kept')
        self.assertEqual(agent_input['sub_query_list'], ['q1'])

    def test_parse_result_exposes_search_context(self):
        agent_result = self.agent.parse_result(
            {'search_context': 'result context', 'flag': True})
        self.assertEqual(agent_result['search_context'], 'result context')

    def test_parse_result_keeps_original_keys(self):
        agent_result = self.agent.parse_result(
            {'search_context': 'ctx', 'extra': 42})
        self.assertEqual(agent_result['extra'], 42)
