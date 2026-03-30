# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/29 15:51
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_template.py
from abc import ABC
from typing import Optional, List
from queue import Queue

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.prompt.chat_prompt import ChatPrompt


class AgentTemplate(Agent, ABC):
    llm_name: Optional[str] = ''
    memory_name: Optional[str] = None
    knowledge_names: Optional[list[str]] = None
    prompt_version: Optional[str] = None
    conversation_memory_name: Optional[str] = None

    def _create_agent_context(self, input_object: InputObject,
                              agent_input: dict, memory: Memory) -> 'AgentContext':
        if self.prompt_version and not self.agent_model.profile.get('prompt_version'):
            self.agent_model.profile['prompt_version'] = self.prompt_version
        return super()._create_agent_context(input_object, agent_input, memory)

    async def _async_create_agent_context(self, input_object: InputObject,
                                          agent_input: dict, memory: Memory) -> 'AgentContext':
        if self.prompt_version and not self.agent_model.profile.get('prompt_version'):
            self.agent_model.profile['prompt_version'] = self.prompt_version
        return await super()._async_create_agent_context(input_object, agent_input, memory)

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        llm: LLM = self.process_llm(**kwargs)
        agent_context = self._create_agent_context(input_object, agent_input, memory)
        return self.customized_execute(input_object, agent_input, memory, llm,
                                       agent_context=agent_context, **kwargs)

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = await self.async_process_memory(agent_input, **kwargs)
        llm: LLM = self.process_llm(**kwargs)
        agent_context = await self._async_create_agent_context(input_object, agent_input, memory)
        return await self.customized_async_execute(input_object, agent_input, memory, llm,
                                                    agent_context=agent_context, **kwargs)

    def customized_execute(self, input_object: InputObject, agent_input: dict,
                           memory: Memory, llm: LLM,
                           agent_context: AgentContext = None,
                           **kwargs) -> dict:
        # 1. Build LLM from agent_context
        llm = agent_context.build_llm()

        # 2. Run tool-calling loop
        llm_output = self.run_tool_calling_loop(
            llm, agent_context, input_object,
            max_iterations=agent_context.max_iterations,
        )

        res = llm_output.text

        # 3. Persist memory
        self._save_memory(agent_context, llm_output, agent_input)

        # 4. Emit final output to stream
        self._emit_final_output(agent_context, res)

        return {**agent_input, 'output': res}

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict,
                                       memory: Memory, llm: LLM,
                                       agent_context: AgentContext = None,
                                       **kwargs) -> dict:
        # 1. Build LLM from agent_context
        llm = agent_context.build_llm()

        # 2. Run async tool-calling loop
        llm_output = await self.async_run_tool_calling_loop(
            llm, agent_context, input_object,
            max_iterations=agent_context.max_iterations,
        )

        res = llm_output.text

        # 3. Persist memory
        await self._async_save_memory(agent_context, llm_output, agent_input)

        # 4. Emit final output to stream
        self._emit_final_output(agent_context, res)

        return {**agent_input, 'output': res}

    def _save_memory(self, context: AgentContext, llm_output: LLMOutput,
                     agent_input: dict) -> None:
        """Collect conversation messages and persist to memory.

        Subclasses may override to customise the memory strategy.
        """
        if not context.memory:
            return
        memory_messages = self._collect_memory_messages(context, llm_output)
        self.add_memory(context.memory, memory_messages, agent_input=agent_input)

    async def _async_save_memory(self, context: AgentContext, llm_output: LLMOutput,
                                 agent_input: dict) -> None:
        """Async version of :meth:`_save_memory`."""
        if not context.memory:
            return
        memory_messages = self._collect_memory_messages(context, llm_output)
        await self.async_add_memory(context.memory, memory_messages, agent_input=agent_input)

    def _emit_final_output(self, context: AgentContext, output_text: str) -> None:
        """Push the final output to the output stream.

        Subclasses may override to customise the format (e.g. OpenAI protocol).
        """
        self.add_output_stream(context.output_stream, output_text)

    def _collect_memory_messages(self, context: AgentContext,
                                 final_output: LLMOutput) -> List[Message]:
        """Collect messages to persist to memory.

        Includes: user input, all tool call/result messages, final AI response.
        Excludes: system message, few-shot messages, prior chat history.
        """
        messages = []
        # current_messages contains: [user_msg, assistant(tool_calls), tool_results, ...]
        for msg in context.current_messages:
            messages.append(msg)
        # Append the final AI response
        if final_output.message:
            messages.append(final_output.message)
        else:
            messages.append(Message(
                type=ChatMessageEnum.ASSISTANT,
                content=final_output.text,
            ))
        return messages

    def validate_required_params(self):
        pass

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        pass

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'AgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.llm_name = self.agent_model.profile.get('llm_model', {}).get('name')
        self.memory_name = self.agent_model.memory.get('name')
        self.knowledge_names = self.agent_model.action.get('knowledge', [])
        self.conversation_memory_name = self.agent_model.memory.get('conversation_memory', '')
        return self

    def process_llm(self, **kwargs) -> LLM:
        return super().process_llm(llm_name=self.llm_name)

    def process_memory(self, agent_input: dict, **kwargs) -> Memory | None:
        return super().process_memory(agent_input=agent_input,
                                      memory_name=self.memory_name,
                                      llm_name=self.llm_name)

    async def async_process_memory(self, agent_input: dict, **kwargs) -> Memory | None:
        return await super().async_process_memory(agent_input=agent_input,
                                                  memory_name=self.memory_name,
                                                  llm_name=self.llm_name)

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
