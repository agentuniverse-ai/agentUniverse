# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/17 20:36
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_protocol_planning_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate


class OpenAIProtocolPlanningAgentTemplate(OpenAIProtocolTemplate, PlanningAgentTemplate):
    def parse_openai_protocol_output(self, output_object: OutputObject) -> OutputObject:
        return output_object

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        self.add_output_stream(input_object.get_data('output_stream', None), '## Planning  \n\n')
        return super().parse_input(input_object, agent_input)
