# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/02 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: supervision_agent_template.py
from queue import Queue

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class SupervisionAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input', 'implementation_result']

    def output_keys(self) -> list[str]:
        return ['output', 'feedback', 'aligned', 'score']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        implementation_result = input_object.get_data('implementation_result')
        if implementation_result:
            agent_input['implementation_result'] = implementation_result.get_data('implementation_result')
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('supervision')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()
        output = agent_result.get('output')

        try:
            parsed_output = parse_json_markdown(output)
            is_aligned = parsed_output.get('is_aligned')
            if is_aligned is None:
                is_aligned = True
            is_aligned = bool(is_aligned)
            feedback = parsed_output.get('feedback', output)
        except:
            is_aligned = True
            feedback = output

        score = 80 if is_aligned else 0

        final_result['output'] = output
        final_result['feedback'] = feedback
        final_result['aligned'] = is_aligned
        final_result['score'] = score

        logger_info = f"\nSupervision agent execution result is :\n"
        logger_info += f"aligned: {is_aligned}, score: {score}\n"
        logger_info += f"feedback: {feedback}\n"
        LOGGER.info(logger_info)

        return final_result

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        stream_output(output_stream,
                      {"data": {
                          'output': agent_output,
                          "agent_info": self.agent_model.info
                      }, "type": "supervision"})

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'SupervisionAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_supervision_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
