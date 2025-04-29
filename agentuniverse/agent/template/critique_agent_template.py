#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/28 17:50
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: critique_agent_template.py
from typing import List
from queue import Queue

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class CritiqueAgentTemplate(AgentTemplate):

    def input_keys(self) -> List[str]:
        return ['debate_history']

    def output_keys(self) -> List[str]:
        return ['concerns', 'suggestions', 'critique_score']

    def parse_input(self, input_object: InputObject,
                    agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input', '')
        agent_input['debate_history'] = input_object.get_data(
            'debate_history', [])
        agent_input['expert_framework'] = input_object.get_data(
            'expert_framework', {}).get('critique')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        try:
            output = agent_result.get('output', '')
            parsed_output = parse_json_markdown(output)
            result = {
                'concerns': parsed_output.get('concerns', []),
                'suggestions': parsed_output.get('suggestions', []),
                'critique_score':
                float(parsed_output.get('critique_score', 0.5))
            }
            if not 0 <= result['critique_score'] <= 1:
                result['critique_score'] = 0.5
            return result

        except Exception as e:
            LOGGER.error(f"Error parsing critique result: {str(e)}")
            return {'concerns': [], 'suggestions': [], 'critique_score': 0.5}

    def add_output_stream(self, output_stream: Queue,
                          agent_output: str) -> None:
        if not output_stream:
            return
        stream_output(
            output_stream, {
                "data": {
                    'output': agent_output,
                    "agent_info": self.agent_model.info
                },
                "type": "critique"
            })

    def initialize_by_component_configer(
            self,
            component_configer: AgentConfiger) -> 'CritiqueAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get(
            'prompt_version', 'default_critique_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(
                f'llm_name of the agent {self.agent_model.info.get("name")}'
                f' is not set, please go to the agent profile configuration'
                ' and set the `name` attribute in the `llm_model`.')
