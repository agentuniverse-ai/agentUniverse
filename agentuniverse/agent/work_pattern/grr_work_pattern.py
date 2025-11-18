# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/02 00:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: grr_work_pattern.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.generating_agent_template import GeneratingAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.template.rewriting_agent_template import RewritingAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class GRRWorkPattern(WorkPattern):
    generating: GeneratingAgentTemplate = None
    reviewing: ReviewingAgentTemplate = None
    rewriting: RewritingAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        grr_results = list()
        retry_count = work_pattern_input.get('retry_count', 2)
        eval_threshold = work_pattern_input.get('eval_threshold', 60)

        grr_round_results = {}
        generating_result = self._invoke_generating(input_object, work_pattern_input, grr_round_results)
        reviewing_result = self._invoke_reviewing(input_object, grr_round_results)
        
        grr_results.append(grr_round_results)

        if reviewing_result.get('score', 0) >= eval_threshold:
            return {'result': grr_results, 'final_output': generating_result.get('generated_content')}

        for _ in range(retry_count):
            grr_round_results = {}
            rewriting_result = self._invoke_rewriting(input_object, grr_round_results)
            input_object.add_data('generating_result', OutputObject(rewriting_result))
            reviewing_result = self._invoke_reviewing(input_object, grr_round_results)
            
            grr_results.append(grr_round_results)

            if reviewing_result.get('score', 0) >= eval_threshold:
                return {'result': grr_results, 'final_output': rewriting_result.get('rewritten_content')}

        last_result = grr_results[-1]
        final_output = (last_result.get('rewriting_result', {}).get('rewritten_content') or 
                       last_result.get('generating_result', {}).get('generated_content'))
        return {'result': grr_results, 'final_output': final_output}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        grr_results = list()
        retry_count = work_pattern_input.get('retry_count', 2)
        eval_threshold = work_pattern_input.get('eval_threshold', 60)

        grr_round_results = {}
        generating_result = await self._async_invoke_generating(input_object, work_pattern_input, grr_round_results)
        reviewing_result = await self._async_invoke_reviewing(input_object, grr_round_results)
        
        grr_results.append(grr_round_results)

        if reviewing_result.get('score', 0) >= eval_threshold:
            return {'result': grr_results, 'final_output': generating_result.get('generated_content')}

        for _ in range(retry_count):
            grr_round_results = {}
            rewriting_result = await self._async_invoke_rewriting(input_object, grr_round_results)
            input_object.add_data('generating_result', OutputObject(rewriting_result))
            reviewing_result = await self._async_invoke_reviewing(input_object, grr_round_results)
            
            grr_results.append(grr_round_results)

            if reviewing_result.get('score', 0) >= eval_threshold:
                return {'result': grr_results, 'final_output': rewriting_result.get('rewritten_content')}

        last_result = grr_results[-1]
        final_output = (last_result.get('rewriting_result', {}).get('rewritten_content') or 
                       last_result.get('generating_result', {}).get('generated_content'))
        return {'result': grr_results, 'final_output': final_output}

    def _invoke_generating(self, input_object: InputObject, agent_input: dict, grr_round_results: dict) -> dict:
        if not self.generating:
            generating_result = OutputObject({"generated_content": agent_input.get('input')})
        else:
            generating_result = self.generating.run(**input_object.to_dict())
            grr_round_results['generating_result'] = generating_result.to_dict()
        input_object.add_data('generating_result', generating_result)
        return generating_result.to_dict()

    async def _async_invoke_generating(self, input_object: InputObject, agent_input: dict, 
                                      grr_round_results: dict) -> dict:
        if not self.generating:
            generating_result = OutputObject({"generated_content": agent_input.get('input')})
        else:
            generating_result = await self.generating.async_run(**input_object.to_dict())
            grr_round_results['generating_result'] = generating_result.to_dict()
        input_object.add_data('generating_result', generating_result)
        return generating_result.to_dict()

    def _invoke_reviewing(self, input_object: InputObject, grr_round_results: dict) -> dict:
        if not self.reviewing:
            reviewing_result = OutputObject({'score': 100, 'suggestion': 'No review'})
        else:
            content_result = input_object.get_data('generating_result')
            if content_result:
                content = (content_result.get_data('rewritten_content') or 
                          content_result.get_data('generated_content') or 
                          content_result.get_data('output'))
                input_object.add_data('expressing_result', OutputObject({'output': content}))
            
            reviewing_result = self.reviewing.run(**input_object.to_dict())
            grr_round_results['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    async def _async_invoke_reviewing(self, input_object: InputObject, grr_round_results: dict) -> dict:
        if not self.reviewing:
            reviewing_result = OutputObject({'score': 100, 'suggestion': 'No review'})
        else:
            content_result = input_object.get_data('generating_result')
            if content_result:
                content = (content_result.get_data('rewritten_content') or 
                          content_result.get_data('generated_content') or 
                          content_result.get_data('output'))
                input_object.add_data('expressing_result', OutputObject({'output': content}))
            
            reviewing_result = await self.reviewing.async_run(**input_object.to_dict())
            grr_round_results['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    def _invoke_rewriting(self, input_object: InputObject, grr_round_results: dict) -> dict:
        if not self.rewriting:
            generating_result = input_object.get_data('generating_result')
            rewriting_result = OutputObject(generating_result.to_dict() if generating_result else {})
        else:
            generating_result = input_object.get_data('generating_result')
            if generating_result:
                input_object.add_data('generated_content', generating_result.get_data('generated_content'))
            reviewing_result = input_object.get_data('reviewing_result')
            if reviewing_result:
                input_object.add_data('review_feedback', reviewing_result.get_data('suggestion'))
            rewriting_result = self.rewriting.run(**input_object.to_dict())
            grr_round_results['rewriting_result'] = rewriting_result.to_dict()
        input_object.add_data('rewriting_result', rewriting_result)
        return rewriting_result.to_dict()

    async def _async_invoke_rewriting(self, input_object: InputObject, grr_round_results: dict) -> dict:
        if not self.rewriting:
            generating_result = input_object.get_data('generating_result')
            rewriting_result = OutputObject(generating_result.to_dict() if generating_result else {})
        else:
            generating_result = input_object.get_data('generating_result')
            if generating_result:
                input_object.add_data('generated_content', generating_result.get_data('generated_content'))
            reviewing_result = input_object.get_data('reviewing_result')
            if reviewing_result:
                input_object.add_data('review_feedback', reviewing_result.get_data('suggestion'))
            rewriting_result = await self.rewriting.async_run(**input_object.to_dict())
            grr_round_results['rewriting_result'] = rewriting_result.to_dict()
        input_object.add_data('rewriting_result', rewriting_result)
        return rewriting_result.to_dict()

    def _validate_work_pattern_members(self):
        if self.generating and not isinstance(self.generating, GeneratingAgentTemplate):
            raise ValueError(f"{self.generating} is not of the expected type GeneratingAgentTemplate.")
        if self.reviewing and not isinstance(self.reviewing, ReviewingAgentTemplate):
            raise ValueError(f"{self.reviewing} is not of the expected type ReviewingAgentTemplate.")
        if self.rewriting and not isinstance(self.rewriting, RewritingAgentTemplate):
            raise ValueError(f"{self.rewriting} is not of the expected type RewritingAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        grr_work_pattern_instance = self.__class__()
        grr_work_pattern_instance.name = self.name
        grr_work_pattern_instance.description = self.description
        for key in ['generating', 'reviewing', 'rewriting']:
            if key in kwargs:
                setattr(grr_work_pattern_instance, key, kwargs[key])
        return grr_work_pattern_instance

