# !/usr/bin/env python3

# @Time    : 2026/10/18
# @Author  : lljjcc426
# @FileName: judge_agent_template.py

# Configuration validation raises descriptive ValueError messages.
# ruff: noqa: TRY003

from queue import Queue

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class JudgeAgentTemplate(AgentTemplate):
    """Agent template for the judge role in the debate pattern.

    The judge agent scores each debate round based on the proposal and the
    critic's feedback, and decides whether consensus has been reached.
    """

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys
        """
        return ["input", "proposal_result", "critic_result", "round_index", "execution_context"]

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys ['output', 'score', 'suggestion']
        """
        return ["output", "score", "suggestion"]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the judge agent.

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

        # Proposal and critique of the current round
        agent_input["proposal_result"] = input_object.get_data("proposal_result").get_data("output")
        agent_input["critic_result"] = input_object.get_data("critic_result").get_data("output")

        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the agent execution result.

        Args:
            agent_result (dict): Raw result from agent execution.

        Returns:
            dict: Parsed result with output, score and suggestion keys.
        """
        final_result = {}

        output = agent_result.get("output")
        output = parse_json_markdown(output)

        score = output.get("score")
        if score is None:
            score = 0
        try:
            score = int(score)
        except (TypeError, ValueError):
            score = 0

        final_result["output"] = output
        final_result["score"] = score
        final_result["suggestion"] = output.get("suggestion")
        # add judge agent log info.
        round_index = agent_result.get("round_index", 1)
        logger_info = f"\nJudge agent round {round_index} execution result is :\n"
        judge_info_str = f"judge suggestion: {final_result.get('suggestion')} \n"
        judge_info_str += f"judge score: {final_result.get('score')} \n"
        LOGGER.info(logger_info + judge_info_str)

        return final_result

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> "JudgeAgentTemplate":
        """Initialize the judge agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            JudgeAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get("prompt_version", "default_judge_agent.cn")
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
        # Add judge agent final result into the stream output
        stream_output(
            output_stream, {"data": {"output": agent_output, "agent_info": self.agent_model.info}, "type": "judge"}
        )
