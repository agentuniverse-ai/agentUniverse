#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/28 17:50
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: debate_agent_template.py
from typing import Dict, List, Optional, Any, Tuple
from queue import Queue

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate
from agentuniverse.agent.template.critique_agent_template import CritiqueAgentTemplate
from agentuniverse.agent.template.enhanced_executing_agent_template import EnhancedExecutingAgentTemplate
from agentuniverse.agent.work_pattern.debate_work_pattern import DebateWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output


class DebateAgentTemplate(AgentTemplate):
    planning_agent_name: str = "planning_agent"
    critique_agent_name: str = "critique_agent"
    executing_agent_name: str = "executing_agent"
    debate_rounds: int = 3
    consensus_threshold: float = 0.8
    execute_result: bool = True
    expert_framework: Optional[Dict] = None

    def input_keys(self) -> List[str]:
        return ['input']

    def output_keys(self) -> List[str]:
        return ['plan', 'execution', 'debate_rounds', 'consensus_reached']

    def parse_input(self, input_object: InputObject,
                    agent_input: Dict[str, Any]) -> Dict[str, Any]:
        agent_input['input'] = input_object.get_data('input')
        agent_input.update({
            'debate_rounds': self.debate_rounds,
            'consensus_threshold': self.consensus_threshold,
            'execute_result': self.execute_result
        })
        return agent_input

    def _prepare_execution(self, agent_input: Dict[str, Any],
                           **kwargs) -> Tuple[Memory, DebateWorkPattern]:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        debate_work_pattern: DebateWorkPattern = WorkPatternManager(
        ).get_instance_obj('debate_work_pattern')
        debate_work_pattern = debate_work_pattern.set_by_agent_model(**agents)
        return memory, debate_work_pattern

    def execute(self, input_object: InputObject, agent_input: Dict[str, Any],
                **kwargs) -> Dict[str, Any]:
        memory, debate_work_pattern = self._prepare_execution(
            agent_input, **kwargs)
        work_pattern_result = self.customized_execute(
            input_object=input_object,
            agent_input=agent_input,
            memory=memory,
            debate_work_pattern=debate_work_pattern)
        return work_pattern_result

    async def async_execute(self, input_object: InputObject,
                            agent_input: Dict[str, Any],
                            **kwargs) -> Dict[str, Any]:
        memory, debate_work_pattern = self._prepare_execution(
            agent_input, **kwargs)
        work_pattern_result = await self.customized_async_execute(
            input_object=input_object,
            agent_input=agent_input,
            memory=memory,
            debate_work_pattern=debate_work_pattern)
        return work_pattern_result

    def customized_execute(self, input_object: InputObject,
                           agent_input: Dict[str, Any], memory: Memory,
                           debate_work_pattern: DebateWorkPattern,
                           **kwargs) -> dict:
        self.build_expert_framework(input_object)
        work_pattern_result = debate_work_pattern.invoke(
            input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject,
                                       agent_input: Dict[str,
                                                         Any], memory: Memory,
                                       debate_work_pattern: DebateWorkPattern,
                                       **kwargs) -> Dict[str, Any]:
        self.build_expert_framework(input_object)
        work_pattern_result = await debate_work_pattern.async_invoke(
            input_object, agent_input)
        return work_pattern_result

    def parse_result(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        result = agent_result.get('result', {})
        final_plan = result.get('final_plan', {})
        execution_result = result.get('execution_result', {})
        return {
            'plan':
            final_plan,
            'execution':
            execution_result,
            'debate_rounds':
            len(result.get('rounds', [])),
            'consensus_reached':
            any(
                round.get('consensus_score', 0) >= self.consensus_threshold
                for round in result.get('rounds', [])),
        }

    def _generate_agents(self) -> Dict[str, Any]:
        planning_agent = self._get_and_validate_agent(self.planning_agent_name,
                                                      PlanningAgentTemplate)
        critique_agent = self._get_and_validate_agent(self.critique_agent_name,
                                                      CritiqueAgentTemplate)
        executing_agent = self._get_and_validate_agent(
            self.executing_agent_name,
            EnhancedExecutingAgentTemplate) if self.execute_result else None

        return {
            'planning': planning_agent,
            'critique': critique_agent,
            'executing': executing_agent
        }

    @staticmethod
    def _get_and_validate_agent(agent_name: str, expected_type: type):
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            return None
        if not isinstance(agent, expected_type):
            raise ValueError(
                f"{agent_name} is not of the expected type {expected_type.__name__}"
            )
        return agent

    def build_expert_framework(self, input_object: InputObject):
        if self.expert_framework:
            input_object.add_data('expert_framework', self.expert_framework)

    def add_output_stream(self, output_stream: Queue,
                          agent_output: str) -> None:
        if not output_stream:
            return
        stream_output(
            output_stream, {
                "data": {
                    'output': agent_output,
                    "agent_info": self.agent_model.info
                },
                "type": "debate"
            })

    def initialize_by_component_configer(
            self, component_configer: AgentConfiger) -> 'DebateAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        debate_config = self.agent_model.plan.get('debate', {})
        if self.agent_model.profile.get(
                'planning') is not None or debate_config.get(
                    'planning') is not None:
            self.planning_agent_name = self.agent_model.profile.get('planning') \
                if self.agent_model.profile.get('planning') is not None else debate_config.get('planning')
        if self.agent_model.profile.get(
                'critique') is not None or debate_config.get(
                    'critique') is not None:
            self.critique_agent_name = self.agent_model.profile.get('critique') \
                if self.agent_model.profile.get('critique') is not None else debate_config.get('critique')
        if self.agent_model.profile.get(
                'executing') is not None or debate_config.get(
                    'executing') is not None:
            self.executing_agent_name = self.agent_model.profile.get('executing') \
                if self.agent_model.profile.get('executing') is not None else debate_config.get('executing')

        if self.agent_model.profile.get('debate_rounds') or debate_config.get(
                'debate_rounds'):
            self.debate_rounds = self.agent_model.profile.get(
                'debate_rounds') or debate_config.get('debate_rounds')

        if self.agent_model.profile.get(
                'consensus_threshold') or debate_config.get(
                    'consensus_threshold'):
            self.consensus_threshold = self.agent_model.profile.get(
                'consensus_threshold') or debate_config.get(
                    'consensus_threshold')

        if self.agent_model.profile.get(
                'execute_result') is not None or debate_config.get(
                    'execute_result') is not None:
            self.execute_result = self.agent_model.profile.get('execute_result') \
                if self.agent_model.profile.get('execute_result') is not None else debate_config.get('execute_result')

        if self.agent_model.profile.get(
                'expert_framework') or debate_config.get('expert_framework'):
            self.expert_framework = self.agent_model.profile.get(
                'expert_framework') or debate_config.get('expert_framework')

        self.memory_name = self.agent_model.memory.get('name')
        return self
