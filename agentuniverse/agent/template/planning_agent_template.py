# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/17 20:36
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: planning_agent_template.py
from queue import Queue

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class PlanningAgentTemplate(AgentTemplate):

    """Planning agent template.

    Splits a task into a structured framework plus a thought, and can
    stream the planning result to an output queue.
    """
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        """Output keys of the planning agent, ['framework', 'thought']."""
        return ['framework', 'thought']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse the raw input object into the agent input dict.

        Args:
            input_object (InputObject): raw input from the caller.
            agent_input (dict): agent input dict to fill.

        Returns:
            dict: agent input with the 'input' and 'expert_framework' keys set.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('planning')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the agent result and extract framework and thought.

        Args:
            agent_result (dict): raw result of the agent execution.

        Returns:
            dict: result with the 'framework' and 'thought' keys.
        """
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
        """Initialize the planning agent from a component configer.

        Args:
            component_configer (AgentConfiger): the agent component configer.

        Returns:
            PlanningAgentTemplate: the initialized agent template.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_planning_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        """Validate that the agent has the required parameters set.

        Raises:
            ValueError: if the agent's llm_name is not configured.
        """
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        """Parse the agent output and push the framework into the output queue.

        Args:
            output_stream (Queue): queue that receives the stream output.
            agent_output (str): raw agent output to parse.
        """
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
