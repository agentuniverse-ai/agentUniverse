# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
# @Time    : 2025/2/1 09:50
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: contextual_iteration_agent_template.py
from typing import Optional
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt
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

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        assemble_memory_input(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile,
                          agent_input)
        conversation_history = []
        combined_res = ''

        # first llm call step
        lc_prompt_template = prompt.as_langchain()
        prompt_input_dict = {key: agent_input[key] for key in lc_prompt_template.input_variables
                             if key in agent_input}

        chain = lc_prompt_template | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)

        if self.iteration < 1:
            return {**agent_input, 'output': res}

        # process first result
        combined_res = res
        conversation_history.append({
            'user': lc_prompt_template.format(**prompt_input_dict),
            'assistant': res
        })
        agent_input['chat_history'] = json.dumps(conversation_history, ensure_ascii=False)

        # build iteration chain
        continue_prompt: Prompt = super(AgentTemplate, self).process_prompt(
            agent_input, prompt_version=self.continue_prompt_version)
        continue_chain = continue_prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        if self.iteration > 1:
            if_loop_prompt: Prompt = super(AgentTemplate,
                                            self).process_prompt(
                agent_input, prompt_version=self.if_loop_prompt_version)
            if_loop_prompt_chain = if_loop_prompt.as_langchain() | llm.as_langchain_runnable(
                self.agent_model.llm_params()) | StrOutputParser()

        for i in range(self.iteration):
            continue_res = self.invoke_chain(continue_chain, agent_input, input_object, **kwargs)
            res = res + '\n' + continue_res

            if i==self.iteration-1:
                break
            # judge whether loop
            if not self.if_loop_prompt_version:
                continue
            loop_res = self.invoke_chain(if_loop_prompt_chain, agent_input, input_object, **kwargs)
            if not self.if_loop(loop_res):
                break

            lc_prompt_template = continue_prompt.as_langchain()
            prompt_input_dict = {key: agent_input[key] for key in
                                 lc_prompt_template.input_variables
                                 if key in agent_input}
            conversation_history.append({
                'user': lc_prompt_template.format(**prompt_input_dict),
                'assistant': continue_res
            })
            agent_input['chat_history'] = json.dumps(conversation_history,
                                                     ensure_ascii=False)

        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        return {**agent_input, 'output': res}

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM,
                                       prompt: Prompt, **kwargs) -> dict:

        assemble_memory_input(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile,
                          agent_input)
        conversation_history = []
        combined_res = ''

        # first llm call step
        lc_prompt_template = prompt.as_langchain()
        prompt_input_dict = {key: agent_input[key] for key in
                             lc_prompt_template.input_variables
                             if key in agent_input}

        chain = lc_prompt_template | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = await self.async_invoke_chain(chain, agent_input, input_object, **kwargs)

        if self.iteration < 1:
            return {**agent_input, 'output': res}

        # process first result
        combined_res = res
        conversation_history.append({
            'user': lc_prompt_template.format(**prompt_input_dict),
            'assistant': res
        })
        agent_input['chat_history'] = json.dumps(conversation_history,
                                                 ensure_ascii=False)

        # build iteration chain
        continue_prompt: Prompt = super(AgentTemplate, self).process_prompt(
            agent_input, prompt_version=self.continue_prompt_version)
        continue_chain = continue_prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        if self.iteration > 1:
            if_loop_prompt: Prompt = super(AgentTemplate,
                                           self).process_prompt(
                agent_input, prompt_version=self.if_loop_prompt_version)
            if_loop_prompt_chain = if_loop_prompt.as_langchain() | llm.as_langchain_runnable(
                self.agent_model.llm_params()) | StrOutputParser()

        for i in range(self.iteration):
            continue_res = await self.async_invoke_chain(continue_chain, agent_input,
                                             input_object, **kwargs)
            res = res + '\n' + continue_res

            if i == self.iteration - 1:
                break
            # judge whether loop
            if not self.if_loop_prompt_version:
                continue
            loop_res = await self.async_invoke_chain(if_loop_prompt_chain, agent_input,
                                         input_object, **kwargs)
            if not self.if_loop(loop_res):
                break

            lc_prompt_template = continue_prompt.as_langchain()
            prompt_input_dict = {key: agent_input[key] for key in
                                 lc_prompt_template.input_variables
                                 if key in agent_input}
            conversation_history.append({
                'user': lc_prompt_template.format(**prompt_input_dict),
                'assistant': continue_res
            })
            agent_input['chat_history'] = json.dumps(conversation_history,
                                                     ensure_ascii=False)

        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        return {**agent_input, 'output': res}

    def if_loop(self, loop_res: str):
        return 'yes' in loop_res

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RagAgentTemplate':
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