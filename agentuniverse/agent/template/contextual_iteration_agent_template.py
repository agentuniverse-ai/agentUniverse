# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
# @Time    : 2025/2/1 09:50
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: contextual_iteration_agent_template.py
from typing import Optional

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.base.util.logging.logging_util import LOGGER


class ContextualIterationAgentTemplate(AgentTemplate):
    iteration: int = 0
    continue_prompt_version: Optional[str] = None
    if_loop_prompt_version: Optional[str] = None

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def customized_execute(self, input_object: InputObject, agent_input: dict,
                           memory: Memory, llm: LLM,
                           agent_context: AgentContext = None,
                           **kwargs) -> dict:
        # Build LLM from agent_context
        llm = agent_context.build_llm()

        # First LLM call
        messages = agent_context.build_messages()
        llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)
        res = llm_output.text

        if self.iteration < 1:
            self._save_memory(agent_context, llm_output, agent_input)
            self._emit_final_output(agent_context, res)
            return {**agent_input, 'output': res}

        conversation_history = [{'user': agent_input.get('input', ''), 'assistant': res}]
        agent_input['chat_history'] = json.dumps(conversation_history, ensure_ascii=False)

        # Iteration rounds with continue_prompt
        for i in range(self.iteration):
            # Build continue context
            agent_input_copy = dict(agent_input)
            agent_input_copy['chat_history'] = json.dumps(conversation_history, ensure_ascii=False)

            continue_context = AgentContext.create(
                agent_model=self._build_prompt_override_model(self.continue_prompt_version),
                session_id=agent_input.get('session_id', ''),
                input_dict=agent_input_copy,
                memory=None,
                output_stream=input_object.get_data('output_stream'),
            )
            continue_llm = continue_context.build_llm()
            continue_messages = continue_context.build_messages()
            continue_output = self.invoke_llm(continue_llm, continue_messages, input_object,
                                              agent_context=continue_context)
            continue_res = continue_output.text
            res = res + '\n' + continue_res

            if i == self.iteration - 1:
                break

            # Judge whether to continue looping
            if not self.if_loop_prompt_version:
                conversation_history.append({'user': '', 'assistant': continue_res})
                continue

            loop_context = AgentContext.create(
                agent_model=self._build_prompt_override_model(self.if_loop_prompt_version),
                session_id=agent_input.get('session_id', ''),
                input_dict=agent_input_copy,
                memory=None,
                output_stream=None,
            )
            loop_llm = loop_context.build_llm()
            loop_messages = loop_context.build_messages()
            loop_output = self.invoke_llm(loop_llm, loop_messages, input_object, agent_context=loop_context)
            if not self.if_loop(loop_output.text):
                break

            conversation_history.append({'user': '', 'assistant': continue_res})

        self._save_memory(agent_context, llm_output, agent_input)
        self._emit_final_output(agent_context, res)
        return {**agent_input, 'output': res}

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict,
                                       memory: Memory, llm: LLM,
                                       agent_context: AgentContext = None,
                                       **kwargs) -> dict:
        # Build LLM from agent_context
        llm = agent_context.build_llm()

        # First LLM call
        messages = agent_context.build_messages()
        llm_output = await self.async_invoke_llm(llm, messages, input_object, agent_context=agent_context)
        res = llm_output.text

        if self.iteration < 1:
            self._save_memory(agent_context, llm_output, agent_input)
            self._emit_final_output(agent_context, res)
            return {**agent_input, 'output': res}

        conversation_history = [{'user': agent_input.get('input', ''), 'assistant': res}]
        agent_input['chat_history'] = json.dumps(conversation_history, ensure_ascii=False)

        for i in range(self.iteration):
            agent_input_copy = dict(agent_input)
            agent_input_copy['chat_history'] = json.dumps(conversation_history, ensure_ascii=False)

            continue_context = AgentContext.create(
                agent_model=self._build_prompt_override_model(self.continue_prompt_version),
                session_id=agent_input.get('session_id', ''),
                input_dict=agent_input_copy,
                memory=None,
                output_stream=input_object.get_data('output_stream'),
            )
            continue_llm = continue_context.build_llm()
            continue_messages = continue_context.build_messages()
            continue_output = await self.async_invoke_llm(continue_llm, continue_messages, input_object,
                                                          agent_context=continue_context)
            continue_res = continue_output.text
            res = res + '\n' + continue_res

            if i == self.iteration - 1:
                break

            if not self.if_loop_prompt_version:
                conversation_history.append({'user': '', 'assistant': continue_res})
                continue

            loop_context = AgentContext.create(
                agent_model=self._build_prompt_override_model(self.if_loop_prompt_version),
                session_id=agent_input.get('session_id', ''),
                input_dict=agent_input_copy,
                memory=None,
                output_stream=None,
            )
            loop_llm = loop_context.build_llm()
            loop_messages = loop_context.build_messages()
            loop_output = await self.async_invoke_llm(loop_llm, loop_messages, input_object,
                                                      agent_context=loop_context)
            if not self.if_loop(loop_output.text):
                break

            conversation_history.append({'user': '', 'assistant': continue_res})

        self._save_memory(agent_context, llm_output, agent_input)
        self._emit_final_output(agent_context, res)
        return {**agent_input, 'output': res}

    def _build_prompt_override_model(self, prompt_version: str):
        """Build a copy of agent_model with a different prompt_version for iteration prompts."""
        from agentuniverse.agent.agent_model import AgentModel
        profile = dict(self.agent_model.profile)
        profile['prompt_version'] = prompt_version
        return AgentModel(
            info=self.agent_model.info,
            profile=profile,
            memory=self.agent_model.memory,
            action=self.agent_model.action,
            work_pattern=self.agent_model.work_pattern,
        )

    def if_loop(self, loop_res: str):
        return 'yes' in loop_res

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ContextualIterationAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        if hasattr(component_configer, "iteration"):
            self.iteration = component_configer.iteration
        if self.iteration > 0:
            try:
                self.continue_prompt_version = component_configer.continue_prompt_version
            except AttributeError as e:
                LOGGER.error("Contextual iteration agent need continue_prompt_version while iteration > 0")
        if hasattr(component_configer, "if_loop_prompt_version"):
            self.if_loop_prompt_version = component_configer.if_loop_prompt_version
        return self
