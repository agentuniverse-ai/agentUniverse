# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : Yue Wang
# @FileName: secure_rag_work_pattern.py

"""Bounded, deterministic SecureRAG work pattern: ONE shared sync/async control flow, bounded inputs (retry 1..10, thresholds 0..1, validated jump_step, duck-typed members), ValueError discipline quoting the offending value.
# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003
"""

import asyncio
from collections import namedtuple
from typing import Optional

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import ExecutingAgentTemplate
from agentuniverse.agent.template.expressing_agent_template import ExpressingAgentTemplate
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern

_STAGES = ('planning', 'executing', 'reviewing', 'expressing')
_BLOCK_ANSWER = '[内容因安全审查未通过被拦截]'

def _threshold(name: str, value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
        raise ValueError(f"'{name}' must be a number from 0.0 to 1.0 (got {value!r}).")
    return float(value)

_Limits = namedtuple('_Limits', ('retry', 'jump', 'eval_threshold', 'security_threshold'))

def _expressed(execution: dict, review: Optional[dict]) -> dict:
    review = review or {}
    return {'final_answer': _BLOCK_ANSWER if review.get('action', 'pass') == 'block' else review.get('sanitized_answer', execution.get('answer', '')), 'reasons': list(review.get('reasons', []))}

_DEFAULTS = {
    'planning': lambda execution, review: {'strategy': ['hybrid_retrieval']},
    'executing': lambda execution, review: {'answer': '', 'contexts': []},
    'reviewing': lambda execution, review: {'passed': True, 'score': 1.0, 'action': 'pass', 'sanitized_answer': execution.get('answer', ''), 'reasons': []},
    'expressing': lambda execution, review: _expressed(execution, review),
}

class SecureRagWorkPattern(WorkPattern):
    """安全闭环 RAG 工作模式（bounded 变体）：每轮全新执行直到审查通过且得分达到阈值；retry/jump/阈值有界，越界以引用原值的 ValueError 报告。"""

    planning: Optional[PlanningAgentTemplate] = None
    executing: Optional[ExecutingAgentTemplate] = None
    reviewing: Optional[ReviewingAgentTemplate] = None
    expressing: Optional[ExpressingAgentTemplate] = None

    def invoke(self, input_object: InputObject, work_pattern_input: Optional[dict], **kwargs) -> dict:
        return asyncio.run(self.async_invoke(input_object, work_pattern_input, **kwargs))

    async def async_invoke(self, input_object: InputObject, work_pattern_input: Optional[dict], **kwargs) -> dict:
        limits = self._validate_work_pattern_members(work_pattern_input)
        rounds = []
        for _ in range(limits.retry):
            peers, execution, review = {}, {}, None
            for stage in _STAGES:
                produced = await self._stage(stage, limits, input_object, peers, execution, review)
                execution = produced if stage == 'executing' else execution
                review = produced if stage == 'reviewing' else review
            rounds.append(peers)
            if review.get('passed') is True and review.get('score', 0) >= limits.eval_threshold:
                break
        return {'result': rounds}

    def _validate_work_pattern_members(self, work_pattern_input) -> _Limits:
        if work_pattern_input is not None and not isinstance(work_pattern_input, dict):
            raise ValueError(f"'work_pattern_input' must be a dict or None (got {work_pattern_input!r}).")
        spec = work_pattern_input or {}
        for stage in _STAGES:
            member = getattr(self, stage)
            if member is not None and not hasattr(member, 'run') and not hasattr(member, 'async_run'):
                raise ValueError(f"'{stage}' must provide run() or async_run() (got {member!r}).")
        retry = spec.get('retry_count', 1)
        if isinstance(retry, bool) or not isinstance(retry, int) or not 1 <= retry <= 10:
            raise ValueError(f"'retry_count' must be an integer from 1 to 10 (got {retry!r}).")
        jump = spec.get('jump_step')
        if jump is not None and jump not in _STAGES:
            raise ValueError(f"'jump_step' must be one of planning, executing, reviewing, expressing or None (got {jump!r}).")
        return _Limits(retry, jump,
                       _threshold('eval_threshold', spec.get('eval_threshold', 0.6)),
                       _threshold('security_threshold', spec.get('security_threshold', 0.8)))

    @staticmethod
    def _stage_input(stage: str, limits: _Limits, execution: dict, review: Optional[dict]) -> dict:
        if stage == 'reviewing':
            return {'candidate_answer': execution.get('answer', ''), 'contexts': list(execution.get('contexts', [])),
                    'security_threshold': limits.security_threshold}
        if stage == 'expressing':
            review = review or {}
            return {'candidate_answer': execution.get('answer', ''), 'sanitized_answer': review.get('sanitized_answer', execution.get('answer', '')),
                    'review_action': review.get('action', 'pass'), 'review_reasons': list(review.get('reasons', []))}
        return {}

    async def _stage(self, stage: str, limits: _Limits, input_object: InputObject,
                     peers: dict, execution: dict, review: Optional[dict]) -> dict:
        skipped = limits.jump is not None and _STAGES.index(stage) < _STAGES.index(limits.jump)
        member, kwargs = (None, {}) if skipped else (getattr(self, stage), self._stage_input(stage, limits, execution, review))
        produced = await self._produce(stage, member, _DEFAULTS[stage](execution, review), **kwargs)
        peers[f'{stage}_result'] = produced.to_dict()
        input_object.add_data(f'{stage}_result', produced)
        return produced.to_dict()

    @staticmethod
    async def _produce(stage: str, member, default: dict, **kwargs) -> OutputObject:
        """Await async_run when the member provides it, else call run: sync-only members work on both paths."""
        if member is None:
            return OutputObject(default)
        if hasattr(member, 'async_run'):
            value = member.async_run(**kwargs)
            if asyncio.iscoroutine(value):
                value = await value
        else:
            value = member.run(**kwargs)
        return value if isinstance(value, OutputObject) else OutputObject(dict(value))

    def set_by_agent_model(self, **kwargs) -> 'SecureRagWorkPattern':
        instance = self.__class__()
        instance.name, instance.description = self.name, self.description
        for stage in _STAGES:
            if stage in kwargs:
                setattr(instance, stage, kwargs[stage])
        return instance
