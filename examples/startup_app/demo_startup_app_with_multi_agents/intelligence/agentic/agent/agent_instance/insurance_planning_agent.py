# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/12 20:58
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: insurance_planning_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt


class InsurancePlanningAgent(Agent):

    def input_keys(self) -> list[str]:
        return ['input', 'prod_description']

    def output_keys(self) -> list[str]:
        return ['planning_output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['prod_description'] = input_object.get_data('prod_description')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        planning_output = agent_result['output']
        LOGGER.info(f'智能体 insurance_planning_agent 执行结果为： {planning_output}')
        return {**agent_result, 'planning_output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        # 1. get the llm instance.
        llm: LLM = self.process_llm(**kwargs)
        # 2. get the agent prompt.
        prompt: ChatPrompt = self.process_prompt(agent_input, **kwargs)
        memory = self.process_memory(agent_input, **kwargs)
        agent_context = self._create_agent_context(input_object, agent_input, memory)
        # 3. invoke agent.
        messages = prompt.render(**agent_input)
        llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)
        res = llm_output.text
        # 4. return result.
        return {**agent_input, 'output': res}
