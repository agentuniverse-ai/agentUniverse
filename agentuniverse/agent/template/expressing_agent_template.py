# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/17 20:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: expressing_agent_template.py
from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class ExpressingAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input', 'executing_result']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['background'] = self.build_execution_context(input_object)
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('expressing')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()
        final_result['output'] = agent_result['output']
        # add expressing agent log info.
        logger_info = f"\nExpressing agent execution result is :\n"
        logger_info += f"{final_result.get('output')}"
        LOGGER.info(logger_info)

        return final_result

    def build_execution_context(self, input_object: InputObject) -> str:
        executing_result = input_object.get_data('executing_result').get_data('executing_result', [])
        execution_context_list = [
            f"question:{execution.get('input')}\nanswer:{execution.get('output')}"
            for execution in executing_result
        ]
        return '\n\n'.join(execution_context_list)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ExpressingAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.validate_required_params()
        return self

    @AgentTemplate.prompt_version.getter
    def prompt_version(self) -> str:
        return self.agent_model.profile.get('prompt_version',
                                            'default_expressing_agent.cn')

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        # add expressing agent final result into the stream output.
        stream_output(output_stream,
                      {"data": {
                          'output': agent_output,
                          "agent_info": self.agent_model.info
                      }, "type": "expressing"})
