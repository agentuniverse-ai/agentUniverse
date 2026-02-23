# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: demo_agent.py

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt


class DemoAgent(AgentTemplate):
    """A demo agent template that wires memory, LLM, prompt, tools and knowledge.

       This agent reads the user input, optionally invokes tools and retrieves
       knowledge, then runs the prompt + LLM chain to produce a text answer.
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

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        memory: Memory = self.process_memory(agent_input)
        llm: LLM = self.process_llm()
        prompt: ChatPrompt = self.process_prompt(agent_input)
        agent_context = self._create_agent_context(input_object, agent_input, memory)
        tool_res: str = self.invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}")

        assemble_memory_input(memory, agent_input)

        messages = prompt.render(**agent_input)
        llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)
        res = llm_output.text

        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        return {**agent_input, 'output': res}
