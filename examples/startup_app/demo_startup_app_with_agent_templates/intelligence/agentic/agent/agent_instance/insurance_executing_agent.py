# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/26 20:27
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: insurance_executing_agent.py
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER


class InsuranceExecutingAgent(Agent):

    def input_keys(self) -> list[str]:
        return ['sub_query_list']

    def output_keys(self) -> list[str]:
        return ['search_context']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['sub_query_list'] = input_object.get_data('sub_query_list')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        search_context = agent_result['search_context']
        LOGGER.info(f'智能体 insurance_executing_agent 执行结果为： {search_context}')
        return {**agent_result, 'search_context': search_context}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        search_tool: Tool = ToolManager().get_instance_obj('insurance_search_context_tool')
        search_res = ''
        for sub_query in agent_input.get('sub_query_list'):
            search_res += search_tool.run(input=sub_query) + '\n'
        return {'search_context': search_res}
