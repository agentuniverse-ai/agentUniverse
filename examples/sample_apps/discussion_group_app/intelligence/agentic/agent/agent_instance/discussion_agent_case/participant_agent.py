# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/6 22:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: participant_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate


class ParticipantAgent(RagAgentTemplate):
    """Agent representing a single participant in a discussion group.

    Each participant receives the topic input together with the discussion
    metadata (agent name, current round and participant list) and contributes
    its own result back to the group.
    """

    def input_keys(self) -> list[str]:
        """Get the input keys required by this agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Get the output keys produced by this agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse the user input object into the agent input dict.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input prepared by the framework.
        Returns:
            dict: agent input dict enriched with the discussion context.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['agent_name'] = input_object.get_data('agent_name')
        agent_input['total_round'] = input_object.get_data('total_round')
        agent_input['cur_round'] = input_object.get_data('cur_round')
        agent_input['participants'] = input_object.get_data('participants')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Pass the raw agent result through unchanged.

        Args:
            agent_result(dict): raw result produced by the agent execution.
        Returns:
            dict: agent result dict, unmodified.
        """
        return agent_result
