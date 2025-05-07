# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 17:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_agent.py
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt
from demo_startup_app_with_single_agent_and_memory.intelligence.utils.constant.prod_description import \
    PROD_DESCRIPTION_A


class InsuranceAgent(Agent):

    def input_keys(self) -> list[str]:
        return ['input', 'session_id']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['session_id'] = input_object.get_data('session_id')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute insurance agent instance.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input parsed from `input_object` by the user.

        Returns:
            dict: agent result.
        """
        # 1. get the llm instance.
        llm: LLM = self.process_llm(**kwargs)
        # 2. get the memory instance.
        memory: Memory = self.process_memory(agent_input, **kwargs)
        # 3. assemble the background.
        agent_input['background'] = PROD_DESCRIPTION_A
        # 4. get the agent prompt.
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        # 5. assemble the memory input.
        assemble_memory_input(memory, agent_input)
        # 6. invoke agent.
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        # 7. assemble the memory output.
        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        # 8. return result.
        return {**agent_input, 'output': res}
