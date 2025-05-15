# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: rag_template.py

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser

from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt

from langchain_core.output_parsers import StrOutputParser


class DemoAgent(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        memory: Memory = self.process_memory(agent_input)
        llm: LLM = self.process_llm()
        prompt: Prompt = self.process_prompt(agent_input)
        tool_res: str = self.invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}")
        return self.customized_execute(input_object, agent_input, memory, llm, prompt)

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        assemble_memory_input(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | ReasoningOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        return {**agent_input, 'output': res}
