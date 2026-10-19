# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/24 21:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_summarize_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate


class SummarizeRagAgentTemplate(RagAgentTemplate):
    """RAG agent template specialized for summarizing memory content.

    Extends the base RAG template to accept both the raw ``input`` and the
    prior ``summarize_content`` so agents can build on existing summaries.
    """

    def input_keys(self) -> list[str]:
        return ['input', 'summarize_content']

    def output_keys(self) -> list[str]:
        """Return the keys present in the output of this template.

        Returns:
            The output key names, always ``['output']``.
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Copy the summarization inputs into the agent input dict.

        Args:
            input_object: The agent input object holding the source data.
            agent_input: The mutable agent input dict to fill.

        Returns:
            The agent input dict enriched with ``input`` and ``summarize_content``.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['summarize_content'] = input_object.get_data('summarize_content')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Expose the final output of the raw agent result.

        Args:
            agent_result: The raw result dict produced by the agent.

        Returns:
            A new dict merging ``agent_result`` with its ``output`` value.
        """
        return {**agent_result, 'output': agent_result['output']}
