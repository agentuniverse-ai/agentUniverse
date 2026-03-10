# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/25 15:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: react_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class ReActAgentTemplate(AgentTemplate):
    """ReAct agent template.

    Kept for backward compatibility. The base AgentTemplate now provides
    built-in multi-turn tool calling via AgentContext and run_tool_calling_loop,
    which subsumes the original ReAct loop that relied on LangChain.
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

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ReActAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_react_agent.cn')
        return self
