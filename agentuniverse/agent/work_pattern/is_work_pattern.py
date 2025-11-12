# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/02 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: is_work_pattern.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.implementation_agent_template import ImplementationAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import SupervisionAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class ISWorkPattern(WorkPattern):
    implementation: ImplementationAgentTemplate = None
    supervision: SupervisionAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        is_results = list()
        retry_count = work_pattern_input.get('retry_count', 2)
        eval_threshold = work_pattern_input.get('eval_threshold', 60)

        is_round_results = {}
        implementation_result = self._invoke_implementation(input_object, work_pattern_input, is_round_results)
        supervision_result = self._invoke_supervision(input_object, is_round_results)
        
        is_results.append(is_round_results)

        if supervision_result.get('score', 0) >= eval_threshold:
            return {'result': is_results, 'final_output': implementation_result.get('implementation_result')}

        for _ in range(retry_count):
            is_round_results = {}
            implementation_result = self._invoke_implementation(input_object, work_pattern_input, is_round_results)
            supervision_result = self._invoke_supervision(input_object, is_round_results)
            
            is_results.append(is_round_results)

            if supervision_result.get('score', 0) >= eval_threshold:
                return {'result': is_results, 'final_output': implementation_result.get('implementation_result')}

        return {'result': is_results, 'final_output': implementation_result.get('implementation_result')}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        is_results = list()
        retry_count = work_pattern_input.get('retry_count', 2)
        eval_threshold = work_pattern_input.get('eval_threshold', 60)

        is_round_results = {}
        implementation_result = await self._async_invoke_implementation(input_object, work_pattern_input, is_round_results)
        supervision_result = await self._async_invoke_supervision(input_object, is_round_results)
        
        is_results.append(is_round_results)

        if supervision_result.get('score', 0) >= eval_threshold:
            return {'result': is_results, 'final_output': implementation_result.get('implementation_result')}

        for _ in range(retry_count):
            is_round_results = {}
            implementation_result = await self._async_invoke_implementation(input_object, work_pattern_input, is_round_results)
            supervision_result = await self._async_invoke_supervision(input_object, is_round_results)
            
            is_results.append(is_round_results)

            if supervision_result.get('score', 0) >= eval_threshold:
                return {'result': is_results, 'final_output': implementation_result.get('implementation_result')}

        return {'result': is_results, 'final_output': implementation_result.get('implementation_result')}

    def _invoke_implementation(self, input_object: InputObject, agent_input: dict, is_round_results: dict) -> dict:
        if not self.implementation:
            implementation_result = OutputObject({"implementation_result": "No implementation"})
        else:
            implementation_result = self.implementation.run(**input_object.to_dict())
            is_round_results['implementation_result'] = implementation_result.to_dict()
        input_object.add_data('implementation_result', implementation_result)
        return implementation_result.to_dict()

    async def _async_invoke_implementation(self, input_object: InputObject, agent_input: dict, 
                                          is_round_results: dict) -> dict:
        if not self.implementation:
            implementation_result = OutputObject({"implementation_result": "No implementation"})
        else:
            implementation_result = await self.implementation.async_run(**input_object.to_dict())
            is_round_results['implementation_result'] = implementation_result.to_dict()
        input_object.add_data('implementation_result', implementation_result)
        return implementation_result.to_dict()

    def _invoke_supervision(self, input_object: InputObject, is_round_results: dict) -> dict:
        if not self.supervision:
            supervision_result = OutputObject({'score': 100, 'aligned': True, 'feedback': 'No supervision'})
        else:
            supervision_result = self.supervision.run(**input_object.to_dict())
            is_round_results['supervision_result'] = supervision_result.to_dict()
        input_object.add_data('supervision_result', supervision_result)
        return supervision_result.to_dict()

    async def _async_invoke_supervision(self, input_object: InputObject, is_round_results: dict) -> dict:
        if not self.supervision:
            supervision_result = OutputObject({'score': 100, 'aligned': True, 'feedback': 'No supervision'})
        else:
            supervision_result = await self.supervision.async_run(**input_object.to_dict())
            is_round_results['supervision_result'] = supervision_result.to_dict()
        input_object.add_data('supervision_result', supervision_result)
        return supervision_result.to_dict()

    def _validate_work_pattern_members(self):
        if self.implementation and not isinstance(self.implementation, ImplementationAgentTemplate):
            raise ValueError(f"{self.implementation} is not of the expected type ImplementationAgentTemplate.")
        if self.supervision and not isinstance(self.supervision, SupervisionAgentTemplate):
            raise ValueError(f"{self.supervision} is not of the expected type SupervisionAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        is_work_pattern_instance = self.__class__()
        is_work_pattern_instance.name = self.name
        is_work_pattern_instance.description = self.description
        for key in ['implementation', 'supervision']:
            if key in kwargs:
                setattr(is_work_pattern_instance, key, kwargs[key])
        return is_work_pattern_instance

