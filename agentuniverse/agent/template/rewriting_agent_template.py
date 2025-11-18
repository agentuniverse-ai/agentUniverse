# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/02 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: rewriting_agent_template.py
from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class RewritingAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input', 'generated_content', 'review_feedback']

    def output_keys(self) -> list[str]:
        return ['output', 'rewritten_content']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        generating_result = input_object.get_data('generating_result')
        if generating_result:
            agent_input['generated_content'] = generating_result.get_data('generated_content')
        reviewing_result = input_object.get_data('reviewing_result')
        if reviewing_result:
            agent_input['review_feedback'] = reviewing_result.get_data('suggestion')
            agent_input['review_score'] = reviewing_result.get_data('score')
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('rewriting')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()
        output = agent_result.get('output')
        
        final_result['output'] = output
        final_result['rewritten_content'] = output
        
        logger_info = f"\nRewriting agent execution result is :\n"
        logger_info += f"{output}\n"
        LOGGER.info(logger_info)
        
        return final_result

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        stream_output(output_stream,
                      {"data": {
                          'output': agent_output,
                          "agent_info": self.agent_model.info
                      }, "type": "rewriting"})

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RewritingAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rewriting_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
