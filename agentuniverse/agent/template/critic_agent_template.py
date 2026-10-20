# !/usr/bin/env python3

# @Time    : 2026/10/18
# @Author  : lljjcc426
# @FileName: critic_agent_template.py

# Configuration validation raises descriptive ValueError messages.
# ruff: noqa: TRY003

from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class CriticAgentTemplate(AgentTemplate):
    """Agent template for the critic role in the debate pattern.

    The critic agent reviews the proposer's proposal in each debate round
    and provides structured feedback for the next revision.
    """

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys
        """
        return ["input", "proposal_result", "round_index", "execution_context"]

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys ['output']
        """
        return ["output"]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the critic agent.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary.
        """
        agent_input["input"] = input_object.get_data("input")
        agent_input["round_index"] = input_object.get_data("round_index", 1)

        # Execution context
        execution_context = input_object.get_data("execution_context", {})
        agent_input["user_goal"] = execution_context.get("user_goal", "")

        # Proposal from the current round if available
        proposal_result = input_object.get_data("proposal_result", None)
        agent_input["proposal_result"] = proposal_result.get_data("output") if proposal_result else ""

        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the agent execution result.

        Args:
            agent_result (dict): Raw result from agent execution.

        Returns:
            dict: Parsed result with output key.
        """
        final_result = {}
        output = agent_result.get("output", "")
        final_result["output"] = output

        # Add critic agent log info
        round_index = agent_result.get("round_index", 1)
        logger_info = f"\nCritic agent round {round_index} result:\n{output}\n"
        LOGGER.info(logger_info)

        return final_result

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> "CriticAgentTemplate":
        """Initialize the critic agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            CriticAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get("prompt_version", "default_critic_agent.cn")
        self.validate_required_params()
        return self

    def validate_required_params(self):
        """Validate that required parameters are set.

        Raises:
            ValueError: If llm_name is not set.
        """
        if not self.llm_name:
            raise ValueError(
                f'llm_name of the agent {self.agent_model.info.get("name")}'
                f' is not set, please go to the agent profile configuration'
                ' and set the `name` attribute in the `llm_model`.'
            )

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        """Add output to the stream for real-time feedback.

        Args:
            output_stream (Queue): The output stream queue.
            agent_output (str): The agent output to stream.
        """
        if not output_stream:
            return
        # Add critic agent final result into the stream output
        stream_output(
            output_stream, {"data": {"output": agent_output, "agent_info": self.agent_model.info}, "type": "critic"}
        )
