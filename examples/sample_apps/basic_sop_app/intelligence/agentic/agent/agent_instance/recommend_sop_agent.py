# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/16 14:08
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: recommend_sop_agent.py
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.base.util.prompt_util import process_llm_token

from agentuniverse.agent.action.tool.tool_manager import ToolManager

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt
from basic_sop_app.intelligence.utils.constant import product_info


class RecommendSopAgent(AgentTemplate):
    """Agent template that runs the product recommendation SOP end to end.

    It orchestrates the choose-product-info and choose-product agents plus the
    product-info tool, then asks the LLM to produce the final recommendation.
    """

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        for key, value in input_object.to_dict().items():
            agent_input[key] = value
        LOGGER.info(f"agent, agent input: {agent_input}, input_object: {input_object.to_dict()}")
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Agent result parser.

        Args:
            agent_result(dict): Agent result
        Returns:
            dict: Agent result object.
        """
        return {**agent_result}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Run the recommendation SOP by resolving memory and LLM first.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
            **kwargs: additional agent execution arguments.
        Returns:
            dict: The agent result dict.
        """
        memory: Memory = self.process_memory(agent_input, **kwargs)
        llm: LLM = self.process_llm(**kwargs)
        return self.customized_execute(input_object, agent_input, memory, llm, **kwargs)

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                           llm: LLM, **kwargs) -> dict:
        """Execute the full product recommendation workflow.

        The method gathers candidate items, enriches them with product info,
        selects the final products, and generates the recommendation output.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input dict mutated with the recommendation data.
            memory (Memory): the memory instance resolved by the agent.
            llm (LLM): the LLM instance resolved by the agent.
            **kwargs: additional agent execution arguments.
        Returns:
            dict: The agent result dict containing the output text.
        """

        # invoke choose_product_info_agent to target required items
        choose_product_info_agent: Agent = AgentManager().get_instance_obj('choose_product_info_agent')
        choose_product_info_agent_res: OutputObject = choose_product_info_agent.run(**input_object.to_dict())
        LOGGER.info(f"choose_product_info_agent_res: {choose_product_info_agent_res.to_dict()}")
        product_info_item_list = choose_product_info_agent_res.get_data('item_list')

        # invoke product_info_tool to get product info under items
        product_description_dict: dict = ToolManager().get_instance_obj('product_info_tool').run(
            input=product_info_item_list)
        input_object.add_data('product_b_description', product_description_dict['B'])
        input_object.add_data('product_c_description', product_description_dict['C'])

        # invoke choose_product_agent
        choose_product_agent: Agent = AgentManager().get_instance_obj('choose_product_agent')
        if not choose_product_agent:
            raise ValueError('No choose_product_agent found')
        choose_product_agent_res: OutputObject = choose_product_agent.run(**input_object.to_dict())
        LOGGER.info(f"choose_product_agent_res: {choose_product_agent_res.to_dict()}")
        product_list = choose_product_agent_res.get_data('product_list')
        choose_product_reason = choose_product_agent_res.get_data('reason')

        # bottom line logic for product choice
        if not product_list:
            product_list = ["B"]
            choose_product_reason += "\n根据您的要求未能找到合适的产品，建议看看下面的产品"

        # construct inputs for llm
        agent_input['reason'] = choose_product_reason
        product_names = ""
        product_description_list = ""
        product_recommendation = ""
        for product in product_list:
            product_names += product_info.PRODUCT_NAME_MAP.get(product) + "\n"
            product_description_list += product_info.PRODUCT_NAME_MAP.get(product) + "\n"
            product_description_list += product_description_dict.get(product) + "\n"
            product_recommendation += product_info.PRODUCT_RECOMMENDATION_MAP.get(product) + "\n"
        agent_input['product_description_list'] = product_description_list
        agent_input['product_names'] = product_names
        agent_input['product_recommendation'] = product_recommendation

        # process prompt and token
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)

        # invoke llm
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        LOGGER.info(f"product recommend sop agent res: {res}")
        return {'output': res}
