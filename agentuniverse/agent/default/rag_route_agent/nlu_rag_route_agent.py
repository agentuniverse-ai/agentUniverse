# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/13 11:20
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: nlu_rag_route_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


class NluRagRouteAgent(RagAgentTemplate):
    """Nlu Rag Route Agent class."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['query', 'store_info', 'store_amount']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        agent_input['query'] = input_object.get_data('query')
        agent_input['store_info'] = input_object.get_data('store_info')
        agent_input['store_amount'] = input_object.get_data('store_amount')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Agent result parser.

        Args:
            agent_result(dict): The raw result of the agent.
        Returns:
            dict: The parsed result of the agent
        """
        return agent_result

    def process_llm(self, **kwargs) -> LLM:
        llm_name = self.agent_model.profile.get('llm_model', {}).get('name') or self.llm_name
        return LLMManager().get_instance_obj(llm_name)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'NluRagRouteAgent':
        super().initialize_by_component_configer(component_configer)
        return self

    @RagAgentTemplate.prompt_version.getter
    def prompt_version(self):
        return self.agent_model.profile.get('prompt_version', 'nlu_rag_route_prompt.cn')
