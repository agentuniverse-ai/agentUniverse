# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/17 20:36
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: planning_agent_template.py
from queue import Queue
from typing import Any

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class PlanningAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['framework', 'thought']

    @staticmethod
    def _result_to_dict(result: Any) -> dict:
        if isinstance(result, OutputObject):
            return result.to_dict()
        if isinstance(result, dict):
            return result
        return {}

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('planning')

        planning_result = self._result_to_dict(input_object.get_data('planning_result'))
        reviewing_result = self._result_to_dict(input_object.get_data('reviewing_result'))

        previous_planning_result = planning_result.get('framework')
        review_score = reviewing_result.get('score')
        review_suggestion = reviewing_result.get('suggestion')

        agent_input['previous_planning_result'] = (
            previous_planning_result if isinstance(previous_planning_result, list) else []
        )
        agent_input['review_score'] = (
            review_score if isinstance(review_score, (int, float)) else ''
        )
        agent_input['review_suggestion'] = (
            review_suggestion if isinstance(review_suggestion, str) else ''
        )
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()

        output = agent_result.get('output')
        output = parse_json_markdown(output)
        final_result['framework'] = output.get('framework')
        final_result['thought'] = output.get('thought', '')

        # add planning agent log info.
        logger_info = f"\nPlanning agent execution result is :\n"
        for index, one_framework in enumerate(final_result.get('framework')):
            logger_info += f"[{index + 1}] {one_framework} \n"
        LOGGER.info(logger_info)
        return final_result

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'PlanningAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_planning_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        try:
            output = parse_json_markdown(agent_output).get('framework')
        except:
            output = agent_output
        # add planning agent final result into the stream output.
        stream_output(output_stream,
                      {"data": {
                          'output': output,
                          "agent_info": self.agent_model.info
                      }, "type": "planning"})
