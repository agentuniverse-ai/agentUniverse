# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/02 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: grr_agent_template.py
from typing import Optional, Union

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.generating_agent_template import GeneratingAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.template.rewriting_agent_template import RewritingAgentTemplate
from agentuniverse.agent.work_pattern.grr_work_pattern import GRRWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class GRRAgentTemplate(AgentTemplate):
    generating_agent_name: str = "GeneratingAgent"
    reviewing_agent_name: str = "ReviewingAgent"
    rewriting_agent_name: str = "RewritingAgent"
    eval_threshold: int = 60
    retry_count: int = 2
    expert_framework: Optional[dict[str, Union[str, dict]]] = None

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input.update({
            'eval_threshold': self.eval_threshold,
            'retry_count': self.retry_count
        })
        return agent_input

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        grr_work_pattern: GRRWorkPattern = WorkPatternManager().get_instance_obj('grr_work_pattern')
        grr_work_pattern = grr_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = self.customized_execute(input_object=input_object, agent_input=agent_input, memory=memory,
                                                      grr_work_pattern=grr_work_pattern)
        self.add_grr_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        grr_work_pattern: GRRWorkPattern = WorkPatternManager().get_instance_obj('grr_work_pattern')
        grr_work_pattern = grr_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = await self.customized_async_execute(input_object=input_object, agent_input=agent_input,
                                                                  memory=memory,
                                                                  grr_work_pattern=grr_work_pattern)
        self.add_grr_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                           grr_work_pattern: GRRWorkPattern, **kwargs) -> dict:
        self.build_expert_framework(input_object)
        work_pattern_result = grr_work_pattern.invoke(input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       grr_work_pattern: GRRWorkPattern, **kwargs) -> dict:
        self.build_expert_framework(input_object)
        work_pattern_result = await grr_work_pattern.async_invoke(input_object, agent_input)
        return work_pattern_result

    def parse_result(self, agent_result: dict) -> dict:
        return {'output': agent_result.get('final_output', '')}

    def _generate_agents(self) -> dict:
        generating_agent = self._get_and_validate_agent(self.generating_agent_name, GeneratingAgentTemplate)
        reviewing_agent = self._get_and_validate_agent(self.reviewing_agent_name, ReviewingAgentTemplate)
        rewriting_agent = self._get_and_validate_agent(self.rewriting_agent_name, RewritingAgentTemplate)
        return {'generating': generating_agent,
                'reviewing': reviewing_agent,
                'rewriting': rewriting_agent}

    @staticmethod
    def _get_and_validate_agent(agent_name: str, expected_type: type):
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            return None
        if not isinstance(agent, expected_type):
            raise ValueError(f"{agent_name} is not of the expected type {expected_type.__name__}")
        return agent

    def add_grr_memory(self, grr_memory: Memory, agent_input: dict, work_pattern_result: dict):
        if not grr_memory:
            return
        query = agent_input.get('input')
        message_list = []

        def _create_message_content(turn, role, agent_name, result):
            content = (f"GRR work pattern turn {turn + 1}: The agent responsible for {role} is: {agent_name}, "
                       f"Human: {query}, AI: {result}")
            return Message(source=agent_name, content=content)

        for i, single_turn_res in enumerate(work_pattern_result.get('result', [])):
            generating_result = single_turn_res.get('generating_result', {})
            if generating_result:
                message_list.append(_create_message_content(
                    i, "generating content", self.generating_agent_name,
                    generating_result.get('generated_content')
                ))

            reviewing_result = single_turn_res.get('reviewing_result', {})
            if reviewing_result:
                message_list.append(_create_message_content(
                    i, "reviewing content", self.reviewing_agent_name,
                    reviewing_result.get('suggestion')
                ))

            rewriting_result = single_turn_res.get('rewriting_result', {})
            if rewriting_result:
                message_list.append(_create_message_content(
                    i, "rewriting content", self.rewriting_agent_name,
                    rewriting_result.get('rewritten_content')
                ))

        grr_memory.add(message_list, **agent_input)

    def build_expert_framework(self, input_object: InputObject):
        if self.expert_framework:
            context = self.expert_framework.get('context')
            selector = self.expert_framework.get('selector')
            if selector:
                selector_result = ToolManager().get_instance_obj(selector).run(**input_object.to_dict())
                if not isinstance(selector_result, dict):
                    raise ValueError("The expert framework tool selector must return a dictionary with keys "
                                     "for the specific content of generating, reviewing, and rewriting.")
                input_object.add_data('expert_framework', selector_result)
            elif context:
                if not isinstance(context, dict):
                    raise ValueError("The expert framework raw context must be a dictionary with keys "
                                     "for the specific content of generating, reviewing, and rewriting.")
                input_object.add_data('expert_framework', context)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'GRRAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        planner_config = self.agent_model.plan.get('planner', {})
        if self.agent_model.profile.get('generating') is not None or planner_config.get('generating') is not None:
            self.generating_agent_name = self.agent_model.profile.get('generating') \
                if self.agent_model.profile.get('generating') is not None else planner_config.get('generating')
        if self.agent_model.profile.get('reviewing') is not None or planner_config.get('reviewing') is not None:
            self.reviewing_agent_name = self.agent_model.profile.get('reviewing') \
                if self.agent_model.profile.get('reviewing') is not None else planner_config.get('reviewing')
        if self.agent_model.profile.get('rewriting') is not None or planner_config.get('rewriting') is not None:
            self.rewriting_agent_name = self.agent_model.profile.get('rewriting') \
                if self.agent_model.profile.get('rewriting') is not None else planner_config.get('rewriting')
        if self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold'):
            self.eval_threshold = self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold')
        if self.agent_model.profile.get('retry_count') or planner_config.get('retry_count'):
            self.retry_count = self.agent_model.profile.get('retry_count') or planner_config.get('retry_count')
        if self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework'):
            self.expert_framework = \
                self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework')
        self.memory_name = self.agent_model.memory.get('name')
        return self

