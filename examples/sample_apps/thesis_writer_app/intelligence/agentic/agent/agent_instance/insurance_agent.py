# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 17:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_agent.py
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt
from demo_startup_app_with_single_agent.intelligence.utils.constant.prod_description import \
    PROD_DESCRIPTION_A


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
        # 2. assemble the background.
        agent_input['background'] = PROD_DESCRIPTION_A
        # 3. get the agent prompt.
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        # 4. invoke agent.
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        # 5. return result.
        return {**agent_input, 'output': res}
