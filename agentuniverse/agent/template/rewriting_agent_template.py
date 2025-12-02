# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : Claude Code
# @FileName: rewriting_agent_template.py
from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class RewritingAgentTemplate(AgentTemplate):
    """Agent template for content rewriting in GRR pattern.

    This agent is responsible for rewriting and improving content based on
    review feedback. It takes the original generated content, review suggestions,
    and produces an improved version.
    """

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys ['input', 'generating_result', 'reviewing_result']
        """
        return ['input', 'generating_result', 'reviewing_result']

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys ['output']
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the rewriting agent.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary.
        """
        agent_input['input'] = input_object.get_data('input')

        # Get the generated content
        generating_result = input_object.get_data('generating_result')
        if generating_result:
            agent_input['generated_content'] = generating_result.get_data('output', '')

        # Get review feedback and suggestions
        reviewing_result = input_object.get_data('reviewing_result')
        if reviewing_result:
            agent_input['review_score'] = reviewing_result.get_data('score', 0)
            agent_input['review_suggestion'] = reviewing_result.get_data('suggestion', '')
            agent_input['review_output'] = reviewing_result.get_data('output', '')

        # Get expert framework guidance if available
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('rewriting', '')

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

        # Add rewriting agent log info
        logger_info = f"\nRewriting agent execution result:\n{output}\n"
        LOGGER.info(logger_info)
        return final_result

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RewritingAgentTemplate':
        """Initialize the rewriting agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            RewritingAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rewriting_agent.cn')
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
        # Add rewriting agent final result into the stream output
        stream_output(output_stream,
                     {"data": {
                         'output': agent_output,
                         "agent_info": self.agent_model.info
                     }, "type": "rewriting"})
