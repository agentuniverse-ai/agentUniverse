# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : Claude Code
# @FileName: generating_agent_template.py
from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class GeneratingAgentTemplate(AgentTemplate):
    """Agent template for content generation in GRR pattern.

    This agent is responsible for creating initial content based on user specifications.
    It takes user input and generates content according to requirements.
    """

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys ['input']
        """
        return ['input']

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys ['output']
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the generating agent.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary.
        """
        agent_input['input'] = input_object.get_data('input')
        # Get expert framework guidance if available
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('generating', '')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the agent execution result.

        Args:
            agent_result (dict): Raw result from agent execution.

        Returns:
            dict: Parsed result with output key.
        """
        final_result = dict()
        output = agent_result.get('output', '')
        final_result['output'] = output

        # Add generating agent log info
        logger_info = f"\nGenerating agent execution result:\n{output}\n"
        LOGGER.info(logger_info)
        return final_result

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'GeneratingAgentTemplate':
        """Initialize the generating agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            GeneratingAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_generating_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        """Validate that required parameters are set.

        Raises:
            ValueError: If llm_name is not set.
        """
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                           f' is not set, please go to the agent profile configuration'
                           ' and set the `name` attribute in the `llm_model`.')

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        """Add output to the stream for real-time feedback.

        Args:
            output_stream (Queue): The output stream queue.
            agent_output (str): The agent output to stream.
        """
        if not output_stream:
            return
        # Add generating agent final result into the stream output
        stream_output(output_stream,
                     {"data": {
                         'output': agent_output,
                         "agent_info": self.agent_model.info
                     }, "type": "generating"})
