# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.template.rewriting_agent_template import RewritingAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class GrrWorkPattern(WorkPattern):
    rag: RagAgentTemplate = None
    reviewing: ReviewingAgentTemplate = None
    rewriting: RewritingAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        grr_result = dict()
        self._invoke_rag(input_object, grr_result)
        self._invoke_reviewing(input_object, grr_result)
        self._invoke_rewriting(input_object, grr_result)
        return {'result': grr_result}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        grr_result = dict()
        await self._async_invoke_rag(input_object, grr_result)
        await self._async_invoke_reviewing(input_object, grr_result)
        await self._async_invoke_rewriting(input_object, grr_result)
        return {'result': grr_result}


    def _invoke_rag(self, input_object: InputObject, grr_result: dict) -> dict:
        if not self.rag:
            rag_result = OutputObject({})
        else:
            rag_result = self.rag.run(**input_object.to_dict())
            grr_result['rag_result'] = rag_result.to_dict()
        input_object.add_data('background', rag_result.get_data('background'))
        input_object.add_data('expressing_result', rag_result)
        return rag_result.to_dict()

    async def _async_invoke_rag(self, input_object: InputObject, grr_result: dict) -> dict:
        if not self.rag:
            rag_result = OutputObject({})
        else:
            rag_result = await self.rag.async_run(**input_object.to_dict())
            grr_result['rag_result'] = rag_result.to_dict()
        input_object.add_data('background', rag_result.get_data('background'))
        input_object.add_data('expressing_result', rag_result)
        return rag_result.to_dict()

    def _invoke_reviewing(self, input_object: InputObject, grr_result: dict) -> dict:
        if not self.reviewing:
            reviewing_result = OutputObject({})
        else:
            reviewing_result = self.reviewing.run(**input_object.to_dict())
            grr_result['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('suggestion', reviewing_result.get_data('suggestion'))
        return reviewing_result.to_dict()

    async def _async_invoke_reviewing(self, input_object: InputObject, grr_result: dict) -> dict:
        if not self.reviewing:
            reviewing_result = OutputObject({})
        else:
            reviewing_result = await self.reviewing.async_run(**input_object.to_dict())
            grr_result['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('suggestion', reviewing_result.get_data('suggestion'))
        return reviewing_result.to_dict()

    def _invoke_rewriting(self, input_object: InputObject, grr_result: dict) -> dict:
        if not self.reviewing:
            rewriting_result = OutputObject({})
        else:
            rewriting_result = self.rewriting.run(**input_object.to_dict())
            grr_result['rewriting_result'] = rewriting_result.to_dict()
        input_object.add_data('rewriting_result', rewriting_result)
        return rewriting_result.to_dict()

    async def _async_invoke_rewriting(self, input_object: InputObject, grr_result: dict) -> dict:
        if not self.reviewing:
            rewriting_result = OutputObject({})
        else:
            rewriting_result = await self.rewriting.async_run(**input_object.to_dict())
            grr_result['rewriting_result'] = rewriting_result.to_dict()
        input_object.add_data('rewriting_result', rewriting_result)
        return rewriting_result.to_dict()

    def _validate_work_pattern_members(self):
        if self.rag and not isinstance(self.rag, RagAgentTemplate):
            raise ValueError(f"{self.rag} is not of the expected type RagAgentTemplate.")
        if self.reviewing and not isinstance(self.reviewing, ReviewingAgentTemplate):
            raise ValueError(f"{self.reviewing} is not not of the expected type ReviewingAgentTemplate.")
        if self.rewriting and not isinstance(self.rewriting, RewritingAgentTemplate):
            raise ValueError(f"{self.rewriting} is not not of the expected type RewritingAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        grr_work_pattern_instance = self.__class__()
        grr_work_pattern_instance.name = self.name
        grr_work_pattern_instance.description = self.description
        for key in ['rag', 'reviewing', 'rewriting']:
            if key in kwargs:
                setattr(grr_work_pattern_instance, key, kwargs[key])
        return grr_work_pattern_instance
