# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 17:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt


class InsuranceAgent(Agent):

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute pet insurance agent instance.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input parsed from `input_object` by the user.

        Returns:
            dict: agent result.
        """
        # 1. get the llm instance.
        llm: LLM = self.process_llm(**kwargs)
        # 2. assemble the background by executing tools.
        tool_res: str = self.invoke_tools(input_object)
        agent_input['background'] = tool_res
        LOGGER.info(f"agent tool res: {tool_res}")
        # 3. get the agent prompt.
        prompt: ChatPrompt = self.process_prompt(agent_input, **kwargs)
        memory = self.process_memory(agent_input, **kwargs)
        agent_context = self._create_agent_context(input_object, agent_input, memory)
        # 4. invoke agent.
        messages = prompt.render(**agent_input)
        llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)
        res = llm_output.text
        # 5. return result.
        return {**agent_input, 'output': res}
