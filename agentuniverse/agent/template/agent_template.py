# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/29 15:51
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_template.py
from abc import ABC
from typing import Optional
from queue import Queue

from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.action.toolkit.toolkit_manager import ToolkitManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.base.util.memory_util import get_memory_string
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt


class AgentTemplate(Agent, ABC):

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        llm: LLM = self.process_llm(**kwargs)
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        return self.customized_execute(input_object, agent_input, memory, llm, prompt, **kwargs)

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        llm: LLM = self.process_llm(**kwargs)
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        return await self.customized_async_execute(input_object, agent_input, memory, llm, prompt, **kwargs)

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        self.load_memory(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        self.add_memory(memory, f"Human: {agent_input.get('input')}, AI: {res}", agent_input=agent_input)
        self.add_output_stream(input_object.get_data('output_stream'), res)
        return {**agent_input, 'output': res}

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       llm: LLM, prompt: Prompt, **kwargs) -> dict:
        assemble_memory_input(memory, agent_input, self.get_memory_params(agent_input))
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = await self.async_invoke_chain(chain, agent_input, input_object, **kwargs)
        if self.memory_name:
            assemble_memory_output(memory=memory,
                                   agent_input=agent_input,
                                   content=f"Human: {agent_input.get('input')}, AI: {res}")
        self.add_output_stream(input_object.get_data('output_stream'), res)
        return {**agent_input, 'output': res}

    def validate_required_params(self):
        pass

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        pass

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'AgentTemplate':
        super().initialize_by_component_configer(component_configer)
        return self

    @property
    def llm_name(self):
        return self.agent_model.profile.get('llm_model', {}).get('name')

    @llm_name.setter
    def llm_name(self, value):
        self.agent_model.profile.get('llm_model', {})['name'] = value

    @property
    def memory_name(self):
        return self.agent_model.memory.get('name')

    @memory_name.setter
    def memory_name(self, value):
        self.agent_model.memory['name'] = value

    @property
    def knowledge_names(self):
        return self.agent_model.action.get('knowledge', [])

    @knowledge_names.setter
    def knowledge_names(self, value):
        self.agent_model.action['knowledge'] = value

    @property
    def prompt_version(self):
        return self.agent_model.profile.get('prompt_version')

    @prompt_version.setter
    def prompt_version(self, value):
        self.agent_model.profile['prompt_version'] = value

    @property
    def conversation_memory_name(self):
        return self.agent_model.memory.get('conversation_memory', '')

    @conversation_memory_name.setter
    def conversation_memory_name(self, value):
        self.agent_model.memory['conversation_memory'] = value

    def process_llm(self, **kwargs) -> LLM:
        return super().process_llm(llm_name=self.llm_name)

    def process_memory(self, agent_input: dict, **kwargs) -> Memory | None:
        if 'chat_history' in agent_input and agent_input.get('chat_history'):
            if isinstance(agent_input.get('chat_history'), list):
                agent_input['chat_history'] = get_memory_string(agent_input.get('chat_history'),
                                                                agent_input.get('agent_id'))
                return None
            else:
                return None
        return super().process_memory(agent_input=agent_input, memory_name=self.memory_name, llm_name=self.llm_name)

    def invoke_tools(self, input_object: InputObject, **kwargs) -> str:
        return super().invoke_tools(input_object=input_object, tool_names=self.tool_names)

    async def async_invoke_tools(self, input_object: InputObject, **kwargs) -> str:
        return await super().async_invoke_tools(input_object=input_object, tool_names=self.tool_names)

    def invoke_knowledge(self, query_str: str, input_object: InputObject, **kwargs) -> str:
        return super().invoke_knowledge(query_str=query_str, input_object=input_object,
                                        knowledge_names=self.knowledge_names)

    def process_prompt(self, agent_input: dict, **kwargs) -> ChatPrompt:
        return super().process_prompt(agent_input=agent_input, prompt_version=self.prompt_version)

    def create_copy(self) -> 'AgentTemplate':
        copied = super().create_copy()
        copied.llm_name = self.llm_name
        copied.memory_name = self.memory_name
        copied.knowledge_names = self.knowledge_names.copy() if self.knowledge_names is not None else None
        copied.prompt_version = self.prompt_version
        copied.conversation_memory_name = self.conversation_memory_name
        return copied
