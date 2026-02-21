# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/12 10:36
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: choose_product_info_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.util.common_util import parse_json_markdown


class ChooseProductInfoAgent(AgentTemplate):

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['item_list']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        i_object = input_object.to_dict()
        for key, value in i_object.items():
            agent_input[key] = value
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Agent result parser.

        Args:
            agent_result(dict): Agent result
        Returns:
            dict: Agent result object.
        """
        final_result = dict()

        output = agent_result.get('output')
        output = parse_json_markdown(output)
        final_result['item_list'] = output.get('item_list')
        return final_result
