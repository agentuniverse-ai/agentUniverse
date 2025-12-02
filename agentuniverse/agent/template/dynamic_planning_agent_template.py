# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/18 12:58
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: dynamic_planning_agent_template.py
from queue import Queue

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class DynamicPlanningAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['input', 'executors', 'perp_round_results']

    def output_keys(self) -> list[str]:
        return ['final_answer', 'thought', 'plan']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['executors'] = input_object.get_data('executors')
        perp_round_results = input_object.get_data('perp_round_results', [])
        formated_round_results = []
        for i, single_turn_res in enumerate(perp_round_results):
            planning_result = single_turn_res.get('planning_result', {})
            if planning_result:
                task_info = f"Round {i + 1}: The planning result is: {planning_result}"
                formated_round_results.append(task_info)
            executing_result = single_turn_res.get('executing_result', {})
            if executing_result:
                task_info = f"Round {i + 1}: The executing result is: {executing_result}"
                formated_round_results.append(task_info)
            information_result = single_turn_res.get('information', {})
            if information_result:
                task_info = f"Round {i + 1}: The information result is: {information_result}"
                formated_round_results.append(task_info)
        agent_input['perp_round_results'] = '\n'.join(formated_round_results)
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()

        output = agent_result.get('output')
        output = parse_json_markdown(output)
        final_result['thought'] = output.get('thought', '')
        final_result['type'] = output.get('type', '')
        final_result['final_answer'] = output.get('final_answer', '')
        final_result['plan'] = output.get('plan', [])

        # add planning agent log info.
        LOGGER.info(f"\nDynamic planning agent execution result is :\n" + str(output))
        return final_result

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'DynamicPlanningAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_dynamic_planning_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        try:
            thought = parse_json_markdown(agent_output).get('thought', '')
            plan = parse_json_markdown(agent_output).get('plan', [])
            final_answer = parse_json_markdown(agent_output).get('final_answer', '')
            output = thought + '\n' + str(plan) + '\n' + final_answer
        except Exception as e:
            LOGGER.info(f"\nDynamic planning agent output parse error with :\n" + str(e))
            output = agent_output
        # add planning agent final result into the stream output.
        stream_output(output_stream,
                      {"data": {
                          'output': output,
                          "agent_info": self.agent_model.info
                      }, "type": "planning_and_execute"})