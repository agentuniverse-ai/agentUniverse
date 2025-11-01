# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/02 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: is_agent_template.py
from typing import Optional, Union

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.implementation_agent_template import ImplementationAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import SupervisionAgentTemplate
from agentuniverse.agent.work_pattern.is_work_pattern import ISWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class ISAgentTemplate(AgentTemplate):
    
    implementation_agent_name: str = "ImplementationAgent"
    supervision_agent_name: str = "SupervisionAgent"
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
        is_work_pattern: ISWorkPattern = WorkPatternManager().get_instance_obj('is_work_pattern')
        is_work_pattern = is_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = self.customized_execute(input_object=input_object, agent_input=agent_input, memory=memory,
                                                      is_work_pattern=is_work_pattern)
        self.add_is_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        is_work_pattern: ISWorkPattern = WorkPatternManager().get_instance_obj('is_work_pattern')
        is_work_pattern = is_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = await self.customized_async_execute(input_object=input_object, agent_input=agent_input,
                                                                  memory=memory,
                                                                  is_work_pattern=is_work_pattern)
        self.add_is_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                           is_work_pattern: ISWorkPattern, **kwargs) -> dict:
        self.build_expert_framework(input_object)
        work_pattern_result = is_work_pattern.invoke(input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       is_work_pattern: ISWorkPattern, **kwargs) -> dict:
        self.build_expert_framework(input_object)
        work_pattern_result = await is_work_pattern.async_invoke(input_object, agent_input)
        return work_pattern_result

    def parse_result(self, agent_result: dict) -> dict:
        return {'output': agent_result.get('final_output', '')}

    def _generate_agents(self) -> dict:
        implementation_agent = self._get_and_validate_agent(self.implementation_agent_name, ImplementationAgentTemplate)
        supervision_agent = self._get_and_validate_agent(self.supervision_agent_name, SupervisionAgentTemplate)
        return {'implementation': implementation_agent,
                'supervision': supervision_agent}

    @staticmethod
    def _get_and_validate_agent(agent_name: str, expected_type: type):
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            return None
        if not isinstance(agent, expected_type):
            raise ValueError(f"{agent_name} is not of the expected type {expected_type.__name__}")
        return agent

    def add_is_memory(self, is_memory: Memory, agent_input: dict, work_pattern_result: dict):
        if not is_memory:
            return
        query = agent_input.get('input')
        message_list = []

        def _create_message_content(turn, role, agent_name, result):
            content = (f"IS work pattern turn {turn + 1}: The agent responsible for {role} is: {agent_name}, "
                       f"Human: {query}, AI: {result}")
            return Message(source=agent_name, content=content)

        for i, single_turn_res in enumerate(work_pattern_result.get('result', [])):
            implementation_result = single_turn_res.get('implementation_result', {})
            if implementation_result:
                message_list.append(_create_message_content(
                    i, "implementation", self.implementation_agent_name,
                    implementation_result.get('implementation_result')
                ))

            supervision_result = single_turn_res.get('supervision_result', {})
            if supervision_result:
                message_list.append(_create_message_content(
                    i, "supervision", self.supervision_agent_name,
                    supervision_result.get('feedback')
                ))

        is_memory.add(message_list, **agent_input)

    def build_expert_framework(self, input_object: InputObject):
        if self.expert_framework:
            context = self.expert_framework.get('context')
            selector = self.expert_framework.get('selector')
            if selector:
                selector_result = ToolManager().get_instance_obj(selector).run(**input_object.to_dict())
                if not isinstance(selector_result, dict):
                    raise ValueError("The expert framework tool selector must return a dictionary with keys "
                                     "for the specific content of implementation and supervision.")
                input_object.add_data('expert_framework', selector_result)
            elif context:
                if not isinstance(context, dict):
                    raise ValueError("The expert framework raw context must be a dictionary with keys "
                                     "for the specific content of implementation and supervision.")
                input_object.add_data('expert_framework', context)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ISAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        planner_config = self.agent_model.plan.get('planner', {})
        if self.agent_model.profile.get('implementation') is not None or planner_config.get('implementation') is not None:
            self.implementation_agent_name = self.agent_model.profile.get('implementation') \
                if self.agent_model.profile.get('implementation') is not None else planner_config.get('implementation')
        if self.agent_model.profile.get('supervision') is not None or planner_config.get('supervision') is not None:
            self.supervision_agent_name = self.agent_model.profile.get('supervision') \
                if self.agent_model.profile.get('supervision') is not None else planner_config.get('supervision')
        if self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold'):
            self.eval_threshold = self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold')
        if self.agent_model.profile.get('retry_count') or planner_config.get('retry_count'):
            self.retry_count = self.agent_model.profile.get('retry_count') or planner_config.get('retry_count')
        if self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework'):
            self.expert_framework = \
                self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework')
        self.memory_name = self.agent_model.memory.get('name')
        return self

