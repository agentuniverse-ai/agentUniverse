# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/9 15:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: peer_agent_template.py
from typing import Optional, Union

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.executing_agent_template import ExecutingAgentTemplate
from agentuniverse.agent.template.expressing_agent_template import ExpressingAgentTemplate
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.work_pattern.peer_work_pattern import PeerWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class PeerAgentTemplate(AgentTemplate):
    planning_agent_name: str = "PlanningAgent"
    executing_agent_name: str = "ExecutingAgent"
    expressing_agent_name: str = "ExpressingAgent"
    reviewing_agent_name: str = "ReviewingAgent"
    eval_threshold: int = 60
    retry_count: int = 2
    jump_step: str = 'expressing'
    expert_framework: Optional[dict[str, Union[str, dict]]] = None

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input.update({'eval_threshold': self.eval_threshold,
                            'retry_count': self.retry_count,
                            'jump_step': self.jump_step})
        return agent_input

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        peer_work_pattern: PeerWorkPattern = WorkPatternManager().get_instance_obj('peer_work_pattern')
        peer_work_pattern = peer_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = self.customized_execute(input_object=input_object, agent_input=agent_input, memory=memory,
                                                      peer_work_pattern=peer_work_pattern)
        self.add_peer_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        peer_work_pattern: PeerWorkPattern = WorkPatternManager().get_instance_obj('peer_work_pattern')
        peer_work_pattern = peer_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = await self.customized_async_execute(input_object=input_object, agent_input=agent_input,
                                                                  memory=memory,
                                                                  peer_work_pattern=peer_work_pattern)
        self.add_peer_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                           peer_work_pattern: PeerWorkPattern, **kwargs) -> dict:
        self.build_expert_framework(input_object)
        work_pattern_result = peer_work_pattern.invoke(input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       peer_work_pattern: PeerWorkPattern, **kwargs) -> dict:
        self.build_expert_framework(input_object)
        work_pattern_result = await peer_work_pattern.async_invoke(input_object, agent_input)
        return work_pattern_result

    def parse_result(self, agent_result: dict) -> dict:
        peer_results: list[dict] = agent_result.get('result', [])
        for item in reversed(peer_results):
            expressing_result = item.get('expressing_result')
            if expressing_result:
                return {'output': expressing_result.get('output')}

    def _generate_agents(self) -> dict:
        planning_agent = self._get_and_validate_agent(self.planning_agent_name, PlanningAgentTemplate)
        executing_agent = self._get_and_validate_agent(self.executing_agent_name, ExecutingAgentTemplate)
        expressing_agent = self._get_and_validate_agent(self.expressing_agent_name, ExpressingAgentTemplate)
        reviewing_agent = self._get_and_validate_agent(self.reviewing_agent_name, ReviewingAgentTemplate)
        return {'planning': planning_agent,
                'executing': executing_agent,
                'expressing': expressing_agent,
                'reviewing': reviewing_agent}

    @staticmethod
    def _get_and_validate_agent(agent_name: str, expected_type: type):
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            return None
        if not isinstance(agent, expected_type):
            raise ValueError(f"{agent_name} is not of the expected type {expected_type.__name__}")
        return agent

    def add_peer_memory(self, peer_memory: Memory, agent_input: dict, work_pattern_result: dict):
        if not peer_memory:
            return
        query = agent_input.get('input')
        message_list = []

        def _create_message_content(turn, role, agent_name, result):
            content = (f"Peer work pattern turn {turn + 1}: The agent responsible for {role} is: {agent_name}, "
                       f"Human: {query}, AI: {result}")
            return Message(source=agent_name, content=content)

        for i, single_turn_res in enumerate(work_pattern_result.get('result', [])):
            planning_result = single_turn_res.get('planning_result', {})
            if planning_result:
                message_list.append(_create_message_content(i, "planning and breaking down the task",
                                                            self.planning_agent_name, planning_result.get('framework')))

            executing_result = single_turn_res.get('executing_result', {})
            if executing_result:
                message_list.append(
                    _create_message_content(i, "executing the specific subtask", self.executing_agent_name,
                                            executing_result.get('executing_result')))

            expressing_result = single_turn_res.get('expressing_result', {})
            if expressing_result:
                message_list.append(
                    _create_message_content(i, "expressing and integrating the task into a final result",
                                            self.expressing_agent_name,
                                            expressing_result.get('output')))

            reviewing_result = single_turn_res.get('reviewing_result', {})
            if reviewing_result:
                message_list.append(_create_message_content(i, "reviewing and evaluating the result",
                                                            self.reviewing_agent_name,
                                                            reviewing_result.get('suggestion')))

        peer_memory.add(message_list, **agent_input)

    def build_expert_framework(self, input_object: InputObject):
        """Build expert framework from the expert framework tool selector or raw dictionary context.

        Args:
            input_object (InputObject): The input parameters passed by the user.

        Notes:
            The expert framework, whether using context or tool selector, must return a dictionary
             with keys for the specific content of planning, executing, expressing, and reviewing.
        """
        if self.expert_framework:
            context = self.expert_framework.get('context')
            selector = self.expert_framework.get('selector')
            # tool selector must return a dictionary
            # with keys for the specific content of planning, executing, expressing, and reviewing.
            if selector:
                selector_result = ToolManager().get_instance_obj(selector).run(**input_object.to_dict())
                if not isinstance(selector_result, dict):
                    raise ValueError("The expert framework tool selector must return a dictionary with keys"
                                     " for the specific content of planning, executing, expressing, and reviewing.")
                input_object.add_data('expert_framework', selector_result)
            elif context:  # raw dictionary context
                if not isinstance(context, dict):
                    raise ValueError("The expert framework raw context must be a dictionary with keys"
                                     " for the specific content of planning, executing, expressing, and reviewing.")
                input_object.add_data('expert_framework', context)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'PeerAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        planner_config = self.agent_model.plan.get('planner', {})
        if self.agent_model.profile.get('planning') is not None or planner_config.get('planning') is not None:
            self.planning_agent_name = self.agent_model.profile.get('planning') \
                if self.agent_model.profile.get('planning') is not None else planner_config.get('planning')
        if self.agent_model.profile.get('executing') is not None or planner_config.get('executing') is not None:
            self.executing_agent_name = self.agent_model.profile.get('executing') \
                if self.agent_model.profile.get('executing') is not None else planner_config.get('executing')
        if self.agent_model.profile.get('expressing') is not None or planner_config.get('expressing') is not None:
            self.expressing_agent_name = self.agent_model.profile.get('expressing') \
                if self.agent_model.profile.get('expressing') is not None else planner_config.get('expressing')
        if self.agent_model.profile.get('reviewing') is not None or planner_config.get('reviewing') is not None:
            self.reviewing_agent_name = self.agent_model.profile.get('reviewing') \
                if self.agent_model.profile.get('reviewing') is not None else planner_config.get('reviewing')
        if self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold'):
            self.eval_threshold = self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold')
        if self.agent_model.profile.get('retry_count') or planner_config.get('retry_count'):
            self.retry_count = self.agent_model.profile.get('retry_count') or planner_config.get('retry_count')
        if self.agent_model.profile.get('jump_step') or planner_config.get('jump_step'):
            self.jump_step = self.agent_model.profile.get('jump_step') or planner_config.get('jump_step')
        if self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework'):
            self.expert_framework = \
                self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework')
        return self
