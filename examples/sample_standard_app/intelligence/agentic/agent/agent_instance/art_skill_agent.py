# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: art_skill_agent.py

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate


class ArtSkillAgent(AgentTemplate):
    """Agent for algorithmic art creation using skill system."""

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}
