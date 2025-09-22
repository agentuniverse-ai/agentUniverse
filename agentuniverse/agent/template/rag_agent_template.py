# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/24 21:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: rag_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class RagAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        tool_res: str = self.invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}")
        return super().customized_execute(input_object, agent_input, memory, llm, prompt, **kwargs)

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM,
                                       prompt: Prompt, **kwargs) -> dict:
        tool_res: str = await self.async_invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}")
        return await super().customized_async_execute(input_object, agent_input, memory, llm, prompt, **kwargs)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RagAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rag_agent.cn')
        return self
