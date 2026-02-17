# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/24 21:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: rag_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class RagAgentTemplate(AgentTemplate):
    """RAG agent template.

    Kept for backward compatibility. The base AgentTemplate now handles
    tool calling and knowledge invocation via AgentContext, so this class
    only provides default input/output keys and a default prompt_version.
    """

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RagAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rag_agent.cn')
        return self
