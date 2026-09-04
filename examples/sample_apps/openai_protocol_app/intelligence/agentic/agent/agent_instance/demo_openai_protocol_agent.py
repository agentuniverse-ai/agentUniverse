# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/24 21:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_openai_protocol_agent.py


from agentuniverse.agent.input_object import InputObject

from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate


class DemoOpenAIProtocolAgent(RagAgentTemplate,OpenAIProtocolTemplate):
    """Demo agent combining the RAG template with the OpenAI-compatible protocol.

    Exposes a plain-text ``input`` key and echoes it back through the RAG
    pipeline, formatting the result for the OpenAI-protocol streaming channel.
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
            dict: agent input dict enriched with the ``input`` data.
        """
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the raw agent result into the final result dict.

        Args:
            agent_result(dict): raw result produced by the agent execution.
        Returns:
            dict: agent result exposing the ``output`` field.
        """
        return {**agent_result, 'output': agent_result['output']}
