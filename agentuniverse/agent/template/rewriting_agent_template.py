# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com

from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class RewritingAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input', 'expressing_result', 'suggestion']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['expressing_result'] = input_object.get_data('expressing_result').get_data('output')
        agent_input['suggestion'] = input_object.get_data('suggestion')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        rewriting_info_str = f"\ngenerating output: {agent_result.get('expressing_result')} \n\n"
        rewriting_info_str += f"background: {agent_result.get('background')} \n\n"
        rewriting_info_str += f"suggestion: {agent_result.get('suggestion')} \n\n"
        rewriting_info_str += f"final result: {agent_result.get('output')} \n"
        LOGGER.info(rewriting_info_str)
        return {**agent_result, 'output': agent_result['output']}

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        # add reviewing agent final result into the stream output.
        stream_output(output_stream,
                      {"data": {
                          'output': agent_output,
                          "agent_info": self.agent_model.info
                      }, "type": "rewriting"})

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RewritingAgentTemplate':
        """Initialize the Agent by the AgentConfiger object.

        Args:
            component_configer(AgentConfiger): the ComponentConfiger object
        Returns:
            RewritingAgentTemplate: the RewritingAgentTemplate object
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rewriting_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
