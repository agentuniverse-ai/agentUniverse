# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_planning_agent.py
import unittest

from agentuniverse.agent.input_object import InputObject

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.agentic.agent.agent_instance.insurance_planning_agent import (
    InsurancePlanningAgent,
)


class InsurancePlanningAgentTest(unittest.TestCase):
    """Unit tests for InsurancePlanningAgent pure behaviors."""

    def setUp(self):
        self.agent = InsurancePlanningAgent()

    def test_input_keys(self):
        self.assertEqual(self.agent.input_keys(),
                         ['input', 'prod_description'])

    def test_output_keys(self):
        self.assertEqual(self.agent.output_keys(), ['planning_output'])

    def test_parse_input_reads_all_fields(self):
        input_object = InputObject({
            'input': 'make a plan',
            'prod_description': 'product B',
        })
        agent_input = self.agent.parse_input(input_object, {})
        self.assertEqual(agent_input['input'], 'make a plan')
        self.assertEqual(agent_input['prod_description'], 'product B')

    def test_parse_input_keeps_existing_agent_input(self):
        input_object = InputObject({
            'input': 'q',
            'prod_description': 'p',
        })
        agent_input = self.agent.parse_input(input_object, {'extra': 2})
        self.assertEqual(agent_input['extra'], 2)

    def test_parse_result_maps_output_to_planning_output(self):
        agent_result = self.agent.parse_result({'output': 'the plan'})
        self.assertEqual(agent_result['planning_output'], 'the plan')
        self.assertEqual(agent_result['output'], 'the plan')

    def test_parse_result_keeps_original_keys(self):
        agent_result = self.agent.parse_result(
            {'output': 'plan', 'other': 'kept'})
        self.assertEqual(agent_result['other'], 'kept')
