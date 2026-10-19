# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 17:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_agent.py
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class InsuranceAgent(Agent):
    """Agent instance that answers insurance questions using tool results."""

    def input_keys(self) -> list[str]:
        """Return the input keys accepted by this agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys produced by this agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Copy the user input into the agent input dict.

        Args:
            input_object (InputObject): the user-supplied input object.
            agent_input (dict): the agent input dict being populated.

        Returns:
            dict: the populated agent input dict.
        """
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Expose the output key on the final agent result.

        Args:
            agent_result (dict): the raw result produced by execution.

        Returns:
            dict: the result dict including an 'output' key.
        """
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
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        # 4. invoke agent.
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        # 5. return result.
        return {**agent_input, 'output': res}
