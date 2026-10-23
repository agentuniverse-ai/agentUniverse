# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/29 16:58
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: peer_work_pattern.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import ExecutingAgentTemplate
from agentuniverse.agent.template.expressing_agent_template import ExpressingAgentTemplate
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class PeerWorkPattern(WorkPattern):
    planning: PlanningAgentTemplate = None
    executing: ExecutingAgentTemplate = None
    expressing: ExpressingAgentTemplate = None
    reviewing: ReviewingAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        peer_results = list()
        planning_result = dict()
        executing_result = dict()
        expressing_result = dict()
        reviewing_result = dict()

        retry_count = work_pattern_input.get('retry_count')
        jump_step = work_pattern_input.get('jump_step')
        eval_threshold = work_pattern_input.get('eval_threshold')

        for _ in range(retry_count):
            peer_round_results = {}

            if not planning_result or jump_step == "planning":
                planning_result = self._invoke_planning(input_object, work_pattern_input, peer_round_results)

            if not executing_result or jump_step in ["planning", "executing"]:
                executing_result = self._invoke_executing(input_object, peer_round_results)

            if not expressing_result or jump_step in ["planning", "executing", "expressing"]:
                expressing_result = self._invoke_expressing(input_object, peer_round_results)

            if not reviewing_result or jump_step in ["planning", "executing", "expressing", "reviewing"]:
                reviewing_result = self._invoke_reviewing(input_object, peer_round_results)

            peer_results.append(peer_round_results)

            if not reviewing_result or (
                    reviewing_result.get('score') and reviewing_result.get('score') >= eval_threshold):
                break

        return {'result': peer_results}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        peer_results = list()
        planning_result = dict()
        executing_result = dict()
        expressing_result = dict()
        reviewing_result = dict()

        retry_count = work_pattern_input.get('retry_count')
        jump_step = work_pattern_input.get('jump_step')
        eval_threshold = work_pattern_input.get('eval_threshold')

        for _ in range(retry_count):
            peer_round_results = {}
            if not planning_result or jump_step == "planning":
                planning_result = await self._async_invoke_planning(input_object, work_pattern_input,
                                                                    peer_round_results)

            if not executing_result or jump_step in ["planning", "executing"]:
                executing_result = await self._async_invoke_executing(input_object, peer_round_results)

            if not expressing_result or jump_step in ["planning", "executing", "expressing"]:
                expressing_result = await self._async_invoke_expressing(input_object, peer_round_results)

            if not reviewing_result or jump_step in ["planning", "executing", "expressing", "reviewing"]:
                reviewing_result = await self._async_invoke_reviewing(input_object, peer_round_results)

            peer_results.append(peer_round_results)

            if not reviewing_result or (
                    reviewing_result.get('score') and reviewing_result.get('score') >= eval_threshold):
                break
        return {'result': peer_results}

    def _invoke_planning(self, input_object: InputObject, agent_input: dict, peer_round_results: dict) -> dict:
        if not self.planning:
            planning_result = OutputObject({"framework": [agent_input.get('input')]})
        else:
            planning_result = self.planning.run(**input_object.to_dict())
            peer_round_results['planning_result'] = planning_result.to_dict()
        input_object.add_data('planning_result', planning_result)
        return planning_result.to_dict()

    async def _async_invoke_planning(self, input_object: InputObject, agent_input: dict,
                                     peer_round_results: dict) -> dict:
        if not self.planning:
            planning_result = OutputObject({"framework": [agent_input.get('input')]})
        else:
            planning_result = await self.planning.async_run(**input_object.to_dict())
            peer_round_results['planning_result'] = planning_result.to_dict()
        input_object.add_data('planning_result', planning_result)
        return planning_result.to_dict()

    def _invoke_executing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.executing:
            executing_result = OutputObject({})
        else:
            executing_result = self.executing.run(**input_object.to_dict())
            peer_round_results['executing_result'] = executing_result.to_dict()
        input_object.add_data('executing_result', executing_result)
        return executing_result.to_dict()

    async def _async_invoke_executing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.executing:
            executing_result = OutputObject({})
        else:
            executing_result = await self.executing.async_run(**input_object.to_dict())
            peer_round_results['executing_result'] = executing_result.to_dict()
        input_object.add_data('executing_result', executing_result)
        return executing_result.to_dict()

    def _invoke_expressing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.expressing:
            expressing_result = OutputObject({})
        else:
            expressing_result = self.expressing.run(**input_object.to_dict())
            peer_round_results['expressing_result'] = expressing_result.to_dict()
        input_object.add_data('expressing_result', expressing_result)
        return expressing_result.to_dict()

    async def _async_invoke_expressing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.expressing:
            expressing_result = OutputObject({})
        else:
            expressing_result = await self.expressing.async_run(**input_object.to_dict())
            peer_round_results['expressing_result'] = expressing_result.to_dict()
        input_object.add_data('expressing_result', expressing_result)
        return expressing_result.to_dict()

    def _invoke_reviewing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.reviewing:
            reviewing_result = OutputObject({})
        else:
            reviewing_result = self.reviewing.run(**input_object.to_dict())
            peer_round_results['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    async def _async_invoke_reviewing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.reviewing:
            reviewing_result = OutputObject({})
        else:
            reviewing_result = await self.reviewing.async_run(**input_object.to_dict())
            peer_round_results['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    def _validate_work_pattern_members(self):
        if self.planning and not isinstance(self.planning, PlanningAgentTemplate):
            raise ValueError(f"{self.planning} is not of the expected type AgentTemplate.")
        if self.executing and not isinstance(self.executing, ExecutingAgentTemplate):
            raise ValueError(f"{self.executing} is not of the expected type AgentTemplate.")
        if self.expressing and not isinstance(self.expressing, ExpressingAgentTemplate):
            raise ValueError(f"{self.expressing} is not of the expected type AgentTemplate.")
        if self.reviewing and not isinstance(self.reviewing, ReviewingAgentTemplate):
            raise ValueError(f"{self.reviewing} is not not of the expected type ReviewingAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        peer_work_pattern_instance = self.__class__()
        peer_work_pattern_instance.name = self.name
        peer_work_pattern_instance.description = self.description
        for key in ['planning', 'executing', 'expressing', 'reviewing']:
            if key in kwargs:
                setattr(peer_work_pattern_instance, key, kwargs[key])
        return peer_work_pattern_instance
