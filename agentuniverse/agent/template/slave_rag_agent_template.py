# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 11:51
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: slave_rag_agent_template.py
import re

from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.context.context_archive_utils import get_current_context_archive


class SlaveRagAgentTemplate(AgentTemplate):

    def input_keys(self) -> list[str]:
        return ['prompt_name', 'prompt_params']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:

        agent_input['prompt_name'] = input_object.get_data('prompt_name')
        agent_input['prompt_params'] = input_object.get_data('prompt_params')
        context_archive = get_current_context_archive()

        # get archive data from context
        agent_input.update(agent_input.get('prompt_params'))
        for k, v in agent_input.items():
            result = v
            if isinstance(v, str):
                pattern = r'\$\#\{(\w+)\}'
                result = re.sub(pattern, lambda match: context_archive.get(match.group(1), {}).get('data', match.group(0)), v)
            elif isinstance(v, list):
                replaced_str = []
                for origin_str in v:
                    pattern = r'\$\#\{(\w+)\}'
                    replaced_str.append(re.sub(pattern, lambda match: context_archive.get(
                        match.group(1), {}).get('data', match.group(0)), origin_str))
                result = '\n****************************\n'.join(replaced_str)

            agent_input[k] = result
            input_object.add_data(k, result)
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}
