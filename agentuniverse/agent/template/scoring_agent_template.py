# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/11 11:45
# @Author  : yiying.cy
# @Email   : yiying.cy@antgroup.com
# @FileName: prompt_scoring_agent_template.py
from queue import Queue

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class ScoringAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input', 'expressing_result']

    def output_keys(self) -> list[str]:
        return ['output', 'score', 'reason']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        # In PromptOptimizationWorkPattern, expressing_result is passed as an OutputObject with 'output' data
        expressing_result_obj = input_object.get_data('expressing_result')
        agent_input['expressing_result'] = expressing_result_obj
        agent_input['scoring_standard'] = input_object.get_data('scoring_standard')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()

        output = agent_result.get('output')
        output = parse_json_markdown(output)

        score = output.get('score')
        if score is None:
            score = 0
        
        final_result['output'] = output
        final_result['score'] = score
        final_result['reason'] = output.get('reason')
        
        # add scoring agent log info.
        logger_info = f"\nPrompt Scoring agent execution result is :\n"
        scoring_info_str = f"score: {final_result.get('score')} \n"
        scoring_info_str += f"reason: {final_result.get('reason')} \n"
        LOGGER.info(logger_info + scoring_info_str)

        return final_result

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        # add scoring agent final result into the stream output.
        stream_output(output_stream,
                      {"data": {
                          'output': agent_output,
                          "agent_info": self.agent_model.info
                      }, "type": "scoring"})

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ScoringAgentTemplate':
        """Initialize the Agent by the AgentConfiger object.

        Args:
            component_configer(AgentConfiger): the ComponentConfiger object
        Returns:
            ScoringAgentTemplate: the ScoringAgentTemplate object
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_scoring_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
