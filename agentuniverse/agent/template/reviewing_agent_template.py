# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/29 14:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: reviewing_agent_template.py
from queue import Queue

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class ReviewingAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input', 'expressing_result']

    def output_keys(self) -> list[str]:
        return ['output', 'score', 'suggestion']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['expressing_result'] = input_object.get_data('expressing_result').get_data('output')
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('reviewing')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()

        output = agent_result.get('output')
        output = parse_json_markdown(output)

        is_useful = output.get('is_useful')
        if is_useful is None:
            is_useful = False
        is_useful = bool(is_useful)
        if is_useful:
            score = 80
        else:
            score = 0

        final_result['output'] = output
        final_result['score'] = score
        final_result['suggestion'] = output.get('suggestion')
        # add reviewing agent log info.
        logger_info = f"\nReviewing agent execution result is :\n"
        reviewing_info_str = f"review suggestion: {final_result.get('suggestion')} \n"
        reviewing_info_str += f"review score: {final_result.get('score')} \n"
        LOGGER.info(logger_info + reviewing_info_str)

        return final_result

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        # add reviewing agent final result into the stream output.
        stream_output(output_stream,
                      {"data": {
                          'output': agent_output,
                          "agent_info": self.agent_model.info
                      }, "type": "reviewing"})

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ReviewingAgentTemplate':
        """Initialize the Agent by the AgentConfiger object.

        Args:
            component_configer(AgentConfiger): the ComponentConfiger object
        Returns:
            ReviewingAgentTemplate: the ReviewingAgentTemplate object
        """
        super().initialize_by_component_configer(component_configer)
        self.validate_required_params()
        return self

    @AgentTemplate.prompt_version.getter
    def prompt_version(self) -> str:
        return self.agent_model.profile.get('prompt_version', 'default_reviewing_agent.cn')

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
