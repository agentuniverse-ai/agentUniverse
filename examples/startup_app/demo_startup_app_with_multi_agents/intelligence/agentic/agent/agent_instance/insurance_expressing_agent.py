# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 20:56
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_expressing_agent.py
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class InsuranceExpressingAgent(Agent):

    """Insurance expressing agent that generates the final natural-language insurance response from the product description and search context.
    """
    def input_keys(self) -> list[str]:
        """Return the input keys required by this agent.

        Returns:
            list[str]: The list of required input keys.
        """
        return ['input', 'prod_description', 'search_context']

    def output_keys(self) -> list[str]:
        """Return the output keys produced by this agent.

        Returns:
            list[str]: The list of output keys.
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Copy the input, product description and search context from the input object into the agent input.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary to be filled.

        Returns:
            dict: The updated agent input.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['prod_description'] = input_object.get_data('prod_description')
        agent_input['search_context'] = input_object.get_data('search_context')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Extract the generated output from the agent result and log it.

        Args:
            agent_result(dict): The raw agent result.

        Returns:
            dict: The agent result enriched with the output key.
        """
        output = agent_result['output']
        LOGGER.info(f'智能体 insurance_expressing_agent 执行结果为： {output}')
        return {**agent_result, 'output': output}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        # 1. get the llm instance.
        """Run the expressing chain: process the prompt and LLM, invoke the chain and return the agent input together with the generated output.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary.
            **kwargs: Extra keyword arguments passed to the chain invocation.

        Returns:
            dict: The agent input enriched with the generated output.
        """
        llm: LLM = self.process_llm(**kwargs)
        # 2. get the agent prompt.
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        # 3. invoke agent.
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        # 4. return result.
        return {**agent_input, 'output': res}
