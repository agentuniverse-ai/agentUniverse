# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : kaichuan
# @FileName: implementation_agent_template.py
from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class ImplementationAgentTemplate(AgentTemplate):
    """Agent template for task implementation in IS pattern.

    This agent is responsible for executing the main process and tasks.
    It can operate in normal mode or correction mode based on supervision feedback.
    """

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys
        """
        return ['input', 'checkpoint_index', 'total_checkpoints', 'execution_context']

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys ['output', 'checkpoint_output']
        """
        return ['output', 'checkpoint_output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the implementation agent.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary.
        """
        agent_input['input'] = input_object.get_data('input')

        # Checkpoint information
        agent_input['checkpoint_index'] = input_object.get_data('checkpoint_index', 0)
        agent_input['total_checkpoints'] = input_object.get_data('total_checkpoints', 1)

        # Execution context
        execution_context = input_object.get_data('execution_context', {})
        agent_input['user_goal'] = execution_context.get('user_goal', '')
        agent_input['checkpoint_history'] = execution_context.get('checkpoint_history', [])

        # Correction mode
        agent_input['correction_mode'] = input_object.get_data('correction_mode', False)
        if agent_input['correction_mode']:
            agent_input['supervision_feedback'] = input_object.get_data('supervision_feedback', '')
        else:
            agent_input['supervision_feedback'] = ''  # Provide empty value for normal execution mode

        # Get expert framework guidance if available
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('implementation', '')

        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the agent execution result.

        Args:
            agent_result (dict): Raw result from agent execution.

        Returns:
            dict: Parsed result with output and checkpoint_output keys.
        """
        final_result = dict()
        output = agent_result.get('output', '')
        final_result['output'] = output
        final_result['checkpoint_output'] = output

        # Add implementation agent log info
        checkpoint_idx = agent_result.get('checkpoint_index', 0)
        correction_mode = agent_result.get('correction_mode', False)
        mode_str = "Correction" if correction_mode else "Implementation"
        logger_info = f"\n{mode_str} agent checkpoint {checkpoint_idx} result:\n{output}\n"
        LOGGER.info(logger_info)

        return final_result

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ImplementationAgentTemplate':
        """Initialize the implementation agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            ImplementationAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_implementation_agent.cn')
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
        # Add implementation agent final result into the stream output
        stream_output(output_stream,
                     {"data": {
                         'output': agent_output,
                         "agent_info": self.agent_model.info
                     }, "type": "implementation"})
