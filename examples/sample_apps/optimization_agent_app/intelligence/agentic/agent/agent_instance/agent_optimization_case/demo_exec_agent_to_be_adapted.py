# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/11 11:15
# @Author  : yiying.cy
# @Email   : yiying.cy@antgroup.com
# @FileName: demo_exec_agent_to_be_adapted.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER as logger
from agentuniverse.agent.template.answer_agent_template import AnswerAgentTemplate


class DemoAnswerAgentToBeAdapted(AnswerAgentTemplate):
    def input_keys(self) -> list[str]:
        return ['fund_info','user_info']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['fund_info'] = input_object.get_data('fund_info')
        agent_input['user_info'] = input_object.get_data('user_info')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        logger.info(f"DemoAnswerAgentToBeAdapted parse_result: {agent_result['output']}")
        return {**agent_result, 'output': agent_result['output']}
