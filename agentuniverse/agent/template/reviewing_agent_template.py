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

    """Template agent that reviews another agent's output and produces a score and a suggestion."""
    def input_keys(self) -> list[str]:
        return ['input', 'expressing_result']

    def output_keys(self) -> list[str]:
        """Return the output key names produced by this agent.
        
        Returns:
            list[str]: The output keys.
        """
        return ['output', 'score', 'suggestion']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Populate the agent input with the request, the expressed result and the expert framework.
        
        Args:
            input_object (InputObject): Parsed user input.
            agent_input (dict): Agent input dict.
        
        Returns:
            dict: Updated agent input dict.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['expressing_result'] = input_object.get_data('expressing_result').get_data('output')
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('reviewing')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the reviewed output into a final result with output, score and suggestion.
        
        Args:
            agent_result (dict): Raw agent result.
        
        Returns:
            dict: Result dict with 'output', 'score' and 'suggestion' keys.
        """
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
        """Push the reviewed agent output into the streaming queue.
        
        Args:
            output_stream (Queue): The streaming output queue.
            agent_output (str): The agent output text to stream.
        """
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
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_reviewing_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        """Validate that required parameters such as llm_name are configured.
        
        Raises:
            ValueError: If llm_name is not set for the agent.
        """
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
