# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 18:26
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_consult_agent.py
import json

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class InsuranceConsultAgent(Agent):

    """Orchestrating insurance agent that chains the planning, executing and expressing agents and returns the final answer.
    """
    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Copy the user input from the input object into the agent input.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary to be filled.

        Returns:
            dict: The updated agent input.
        """
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Return the agent result unchanged.

        Args:
            agent_result(dict): The raw agent result.

        Returns:
            dict: The agent result.
        """
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Run the insurance consultation flow: fetch the product detail, let the planning agent split the question, the executing agent search the context, and the expressing agent generate the final answer.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary.
            **kwargs: Extra keyword arguments accepted for interface compatibility.

        Returns:
            dict: The agent input enriched with the generated output.
        """
        detail_tool = ToolManager().get_instance_obj('insurance_info_tool')
        tool_res = detail_tool.run(ins_name='保险产品A')
        agent_input['prod_description'] = tool_res

        # 1. planning agent.
        planning_agent_res = AgentManager().get_instance_obj('insurance_planning_agent').run(**agent_input)
        split_questions = planning_agent_res.get_data('planning_output')
        sub_query_list = json.loads(split_questions).get('sub_query_list')

        # 2. executing agent.
        agent_input['sub_query_list'] = sub_query_list
        executing_agent_res = AgentManager().get_instance_obj('insurance_executing_agent').run(**agent_input)
        agent_input['search_context'] = executing_agent_res.get_data('search_context')

        # 3. expressing agent.
        expressing_agent_res = AgentManager().get_instance_obj('insurance_expressing_agent').run(**agent_input)
        output = expressing_agent_res.get_data('output')
        return {**agent_input, 'output': output}
