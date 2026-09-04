# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/12 20:58
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: insurance_planning_agent.py
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class InsurancePlanningAgent(Agent):

    """Insurance planning agent that drafts a planning proposal from the user input and the product description using an LLM chain.
    """
    def input_keys(self) -> list[str]:
        """Return the input keys required by this agent.

        Returns:
            list[str]: The list of required input keys.
        """
        return ['input', 'prod_description']

    def output_keys(self) -> list[str]:
        """Return the output keys produced by this agent.

        Returns:
            list[str]: The list of output keys.
        """
        return ['planning_output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Copy the user input and product description from the input object into the agent input.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary to be filled.

        Returns:
            dict: The updated agent input.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['prod_description'] = input_object.get_data('prod_description')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Extract the generated output from the agent result, log it and expose it under the planning_output key.

        Args:
            agent_result(dict): The raw agent result.

        Returns:
            dict: The agent result enriched with the planning_output key.
        """
        planning_output = agent_result['output']
        LOGGER.info(f'智能体 insurance_planning_agent 执行结果为： {planning_output}')
        return {**agent_result, 'planning_output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        # 1. get the llm instance.
        """Run the planning chain: process the prompt and LLM, invoke the chain and return the agent input together with the generated output.

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
