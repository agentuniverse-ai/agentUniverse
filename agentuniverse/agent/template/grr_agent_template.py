# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.template.rewriting_agent_template import RewritingAgentTemplate
from agentuniverse.agent.work_pattern.grr_work_pattern import GrrWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class GrrAgentTemplate(AgentTemplate):
    rag_agent_name: str = "RagAgent"
    reviewing_agent_name: str = "ReviewingAgent"
    rewriting_agent_name: str = "RewritingAgent"

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        grr_work_pattern: GrrWorkPattern = WorkPatternManager().get_instance_obj('grr_work_pattern')
        grr_work_pattern = grr_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = self.customized_execute(input_object=input_object, agent_input=agent_input, memory=memory,
                                                      grr_work_pattern=grr_work_pattern)
        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        grr_work_pattern: GrrWorkPattern = WorkPatternManager().get_instance_obj('grr_work_pattern')
        grr_work_pattern = grr_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = await self.customized_async_execute(input_object=input_object, agent_input=agent_input,
                                                                  memory=memory,
                                                                  grr_work_pattern=grr_work_pattern)
        return work_pattern_result

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                           grr_work_pattern: GrrWorkPattern, **kwargs) -> dict:
        work_pattern_result = grr_work_pattern.invoke(input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       grr_work_pattern: GrrWorkPattern, **kwargs) -> dict:
        work_pattern_result = await grr_work_pattern.async_invoke(input_object, agent_input)
        return work_pattern_result

    def parse_result(self, agent_result: dict) -> dict:
        final_result = agent_result.get('result').get('rewriting_result')
        return {**agent_result, 'output': final_result}

    def _generate_agents(self) -> dict:
        rag_agent = self._get_and_validate_agent(self.rag_agent_name, RagAgentTemplate)
        reviewing_agent = self._get_and_validate_agent(self.reviewing_agent_name, ReviewingAgentTemplate)
        rewriting_agent = self._get_and_validate_agent(self.rewriting_agent_name, RewritingAgentTemplate)
        return {'rag': rag_agent,
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

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'GrrAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        planner_config = self.agent_model.plan.get('planner', {})
        if self.agent_model.profile.get('rag') is not None or planner_config.get('rag') is not None:
            self.rag_agent_name = self.agent_model.profile.get('rag') \
                if self.agent_model.profile.get('rag') is not None else planner_config.get('rag')
        if self.agent_model.profile.get('reviewing') is not None or planner_config.get('reviewing') is not None:
            self.reviewing_agent_name = self.agent_model.profile.get('reviewing') \
                if self.agent_model.profile.get('reviewing') is not None else planner_config.get('reviewing')
        if self.agent_model.profile.get('rewriting') is not None or planner_config.get('rewriting') is not None:
            self.rewriting_agent_name = self.agent_model.profile.get('rewriting') \
                if self.agent_model.profile.get('rewriting') is not None else planner_config.get('rewriting')
        self.memory_name = self.agent_model.memory.get('name')
        return self
