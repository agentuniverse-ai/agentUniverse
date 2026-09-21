# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/21
# @FileName: test_process_llm_token_missing_llm_model.py
import unittest
from unittest import mock

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.base.util.prompt_util import process_llm_token


class FakeLLM:
    def __init__(self, max_tokens_value=1024):
        self.max_tokens = max_tokens_value

    def max_context_length(self):
        return 8192

    def get_num_tokens(self, text):
        return 1


class FakePrompt:
    input_variables = ['background']

    def format(self, **kwargs):
        return 'prompt'


def _run(profile):
    planner_input = {'background': 'hello'}
    with mock.patch('agentuniverse.base.util.prompt_util.LLMManager') as llm_manager:
        llm_manager.return_value.get_instance_obj.return_value = None
        process_llm_token(FakeLLM(), FakePrompt(), profile, planner_input)
    return planner_input


class TestProcessLlmTokenMissingLlmModel(unittest.TestCase):
    """An agent profile without an llm_model section must skip the token
    processing instead of raising AttributeError on llm_model.get()."""

    def test_profile_without_llm_model_returns_prompt_untouched(self):
        profile = {'name': 'demo_agent', 'introduction': 'hi'}
        planner_input = _run(profile)
        self.assertEqual('hello', planner_input['background'])

    def test_profile_with_empty_llm_model_returns_prompt_untouched(self):
        profile = {'name': 'demo_agent', 'llm_model': None}
        planner_input = _run(profile)
        self.assertEqual('hello', planner_input['background'])


class TestAgentModelLlmParams(unittest.TestCase):
    def test_llm_params_without_llm_model_returns_empty_dict(self):
        model = AgentModel(profile={'introduction': 'hi'})
        self.assertEqual({}, model.llm_params())

    def test_planner_handle_llm_without_llm_model_returns_none(self):
        from agentuniverse.agent.plan.planner.planning_planner.planning_planner import \
            PlanningPlanner

        agent_model = AgentModel(profile={'introduction': 'hi'})
        with mock.patch('agentuniverse.agent.plan.planner.planner.LLMManager'
                        ) as llm_manager:
            llm_manager.return_value.get_instance_obj.return_value = None
            llm = PlanningPlanner().handle_llm(agent_model)
        self.assertIsNone(llm)

    def test_llm_params_with_llm_model_keeps_supported_bind_values(self):
        model = AgentModel(profile={
            'llm_model': {'name': 'default_llm', 'model_name': 'gpt-test',
                          'temperature': 0.2},
        })
        self.assertEqual({'model': 'gpt-test', 'temperature': 0.2},
                         model.llm_params())


if __name__ == '__main__':
    unittest.main()
