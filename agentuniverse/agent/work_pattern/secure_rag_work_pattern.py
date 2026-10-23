# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/18
# @Author  : ASUKAAAAA1204
# @FileName: secure_rag_work_pattern.py

from typing import Optional

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import ExecutingAgentTemplate
from agentuniverse.agent.template.expressing_agent_template import ExpressingAgentTemplate
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class SecureRagWorkPattern(WorkPattern):
    """安全闭环 RAG 工作模式。

    四个角色按顺序串联，每轮可重试：
      1. planning   检索规划：根据用户问题规划检索策略（关键词/向量/混合、数据源选择）。
      2. executing  检索与生成：检索相关知识片段并基于知识生成候选回答。
      3. reviewing  安全审查：对候选回答进行敏感词过滤、合规知识库校验、数据脱敏，
                     输出安全得分与处置动作（pass/mask/block）。
      4. expressing 表达输出：审查通过则输出最终答案；否则输出脱敏后答案或拦截提示。

    适用于需要内容安全管控的知识服务（如 RAG 知识问答、天理裁决式安全技能等场景）。
    """

    planning: Optional[PlanningAgentTemplate] = None
    executing: Optional[ExecutingAgentTemplate] = None
    reviewing: Optional[ReviewingAgentTemplate] = None
    expressing: Optional[ExpressingAgentTemplate] = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        peer_results = list()
        planning_result = None
        executing_result = None
        reviewing_result = None
        expressing_result = None

        retry_count = work_pattern_input.get('retry_count', 1)
        jump_step = work_pattern_input.get('jump_step')
        eval_threshold = work_pattern_input.get('eval_threshold', 0.6)
        security_threshold = work_pattern_input.get('security_threshold', 0.8)

        for _ in range(retry_count):
            peer_round_results = {}

            # 安全闭环：每一轮都从头重新规划、检索、生成、审查、表达，使 retry 真正生效
            planning_result = None
            executing_result = None
            reviewing_result = None
            expressing_result = None
            if planning_result is None or jump_step == "planning":
                planning_result = self._invoke_planning(input_object, work_pattern_input, peer_round_results)

            if executing_result is None or jump_step in ["planning", "executing"]:
                executing_result = self._invoke_executing(input_object, peer_round_results)

            if reviewing_result is None or jump_step in ["planning", "executing", "reviewing"]:
                reviewing_result = self._invoke_reviewing(
                    input_object, executing_result, peer_round_results, security_threshold
                )

            if expressing_result is None or jump_step in ["planning", "executing", "reviewing", "expressing"]:
                expressing_result = self._invoke_expressing(
                    input_object, executing_result, reviewing_result, peer_round_results, security_threshold
                )

            peer_results.append(peer_round_results)

            # 审查通过且得分达标即可结束重试
            if (
                reviewing_result.get('passed') is True
                and reviewing_result.get('score', 0) >= eval_threshold
            ):
                break

        return {'result': peer_results}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        self._validate_work_pattern_members()

        peer_results = list()
        planning_result = None
        executing_result = None
        reviewing_result = None
        expressing_result = None

        retry_count = work_pattern_input.get('retry_count', 1)
        jump_step = work_pattern_input.get('jump_step')
        eval_threshold = work_pattern_input.get('eval_threshold', 0.6)
        security_threshold = work_pattern_input.get('security_threshold', 0.8)

        for _ in range(retry_count):
            peer_round_results = {}

            # 安全闭环：每一轮都从头重新规划、检索、生成、审查、表达，使 retry 真正生效
            planning_result = None
            executing_result = None
            reviewing_result = None
            expressing_result = None

            if planning_result is None or jump_step == "planning":
                planning_result = await self._async_invoke_planning(input_object, work_pattern_input,
                                                                    peer_round_results)

            if executing_result is None or jump_step in ["planning", "executing"]:
                executing_result = await self._async_invoke_executing(input_object, peer_round_results)

            if reviewing_result is None or jump_step in ["planning", "executing", "reviewing"]:
                reviewing_result = await self._async_invoke_reviewing(
                    input_object, executing_result, peer_round_results, security_threshold
                )

            if expressing_result is None or jump_step in ["planning", "executing", "reviewing", "expressing"]:
                expressing_result = await self._async_invoke_expressing(
                    input_object, executing_result, reviewing_result, peer_round_results, security_threshold
                )

            peer_results.append(peer_round_results)

            if (
                reviewing_result.get('passed') is True
                and reviewing_result.get('score', 0) >= eval_threshold
            ):
                break
        return {'result': peer_results}

    # ---------------- planning ----------------
    def _invoke_planning(self, input_object: InputObject, agent_input: dict, peer_round_results: dict) -> dict:
        if not self.planning:
            planning_result = OutputObject({"strategy": ["hybrid_retrieval"]})
        else:
            planning_result = self.planning.run(**input_object.to_dict())
            peer_round_results['planning_result'] = planning_result.to_dict()
        input_object.add_data('planning_result', planning_result)
        return planning_result.to_dict()

    async def _async_invoke_planning(self, input_object: InputObject, agent_input: dict,
                                     peer_round_results: dict) -> dict:
        if not self.planning:
            planning_result = OutputObject({"strategy": ["hybrid_retrieval"]})
        else:
            planning_result = await self.planning.async_run(**input_object.to_dict())
            peer_round_results['planning_result'] = planning_result.to_dict()
        input_object.add_data('planning_result', planning_result)
        return planning_result.to_dict()

    # ---------------- executing ----------------
    def _invoke_executing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.executing:
            executing_result = OutputObject({"answer": "", "contexts": []})
        else:
            executing_result = self.executing.run(**input_object.to_dict())
            peer_round_results['executing_result'] = executing_result.to_dict()
        input_object.add_data('executing_result', executing_result)
        return executing_result.to_dict()

    async def _async_invoke_executing(self, input_object: InputObject, peer_round_results: dict) -> dict:
        if not self.executing:
            executing_result = OutputObject({"answer": "", "contexts": []})
        else:
            executing_result = await self.executing.async_run(**input_object.to_dict())
            peer_round_results['executing_result'] = executing_result.to_dict()
        input_object.add_data('executing_result', executing_result)
        return executing_result.to_dict()

    # ---------------- reviewing ----------------
    def _invoke_reviewing(self, input_object: InputObject, executing_result: dict,
                          peer_round_results: dict, security_threshold: float) -> dict:
        review_input = dict(input_object.to_dict())
        review_input['candidate_answer'] = executing_result.get('answer', '')
        review_input['contexts'] = executing_result.get('contexts', [])
        review_input['security_threshold'] = security_threshold

        if not self.reviewing:
            reviewing_result = OutputObject({
                'passed': True,
                'score': 1.0,
                'action': 'pass',
                'sanitized_answer': review_input['candidate_answer'],
                'reasons': [],
            })
        else:
            reviewing_result = self.reviewing.run(**review_input)
            peer_round_results['reviewing_result'] = reviewing_result.to_dict()

        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    async def _async_invoke_reviewing(self, input_object: InputObject, executing_result: dict,
                                      peer_round_results: dict, security_threshold: float) -> dict:
        review_input = dict(input_object.to_dict())
        review_input['candidate_answer'] = executing_result.get('answer', '')
        review_input['contexts'] = executing_result.get('contexts', [])
        review_input['security_threshold'] = security_threshold

        if not self.reviewing:
            reviewing_result = OutputObject({
                'passed': True,
                'score': 1.0,
                'action': 'pass',
                'sanitized_answer': review_input['candidate_answer'],
                'reasons': [],
            })
        else:
            reviewing_result = await self.reviewing.async_run(**review_input)
            peer_round_results['reviewing_result'] = reviewing_result.to_dict()

        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    # ---------------- expressing ----------------
    def _invoke_expressing(self, input_object: InputObject, executing_result: dict,
                           reviewing_result: dict, peer_round_results: dict, security_threshold: float) -> dict:
        candidate = executing_result.get('answer', '')
        action = reviewing_result.get('action', 'pass')
        sanitized = reviewing_result.get('sanitized_answer', candidate)
        reasons = reviewing_result.get('reasons', [])

        express_input = dict(input_object.to_dict())
        express_input['candidate_answer'] = candidate
        express_input['sanitized_answer'] = sanitized
        express_input['review_action'] = action
        express_input['review_reasons'] = reasons

        if not self.expressing:
            if action == 'block':
                final = OutputObject({"final_answer": "[内容因安全审查未通过被拦截]", "reasons": reasons})
            elif action == 'mask':
                final = OutputObject({"final_answer": sanitized, "reasons": reasons})
            else:
                final = OutputObject({"final_answer": candidate, "reasons": reasons})
        else:
            final = self.expressing.run(**express_input)
            peer_round_results['expressing_result'] = final.to_dict()

        input_object.add_data('expressing_result', final)
        return final.to_dict()

    async def _async_invoke_expressing(self, input_object: InputObject, executing_result: dict,
                                       reviewing_result: dict, peer_round_results: dict,
                                       security_threshold: float) -> dict:
        candidate = executing_result.get('answer', '')
        action = reviewing_result.get('action', 'pass')
        sanitized = reviewing_result.get('sanitized_answer', candidate)
        reasons = reviewing_result.get('reasons', [])

        express_input = dict(input_object.to_dict())
        express_input['candidate_answer'] = candidate
        express_input['sanitized_answer'] = sanitized
        express_input['review_action'] = action
        express_input['review_reasons'] = reasons

        if not self.expressing:
            if action == 'block':
                final = OutputObject({"final_answer": "[内容因安全审查未通过被拦截]", "reasons": reasons})
            elif action == 'mask':
                final = OutputObject({"final_answer": sanitized, "reasons": reasons})
            else:
                final = OutputObject({"final_answer": candidate, "reasons": reasons})
        else:
            final = await self.expressing.async_run(**express_input)
            peer_round_results['expressing_result'] = final.to_dict()

        input_object.add_data('expressing_result', final)
        return final.to_dict()

    def _validate_work_pattern_members(self):
        if self.planning is not None and not isinstance(self.planning, PlanningAgentTemplate):
            raise ValueError(f"{self.planning} is not of the expected type PlanningAgentTemplate.")
        if self.executing is not None and not isinstance(self.executing, ExecutingAgentTemplate):
            raise ValueError(f"{self.executing} is not of the expected type ExecutingAgentTemplate.")
        if self.reviewing is not None and not isinstance(self.reviewing, ReviewingAgentTemplate):
            raise ValueError(f"{self.reviewing} is not of the expected type ReviewingAgentTemplate.")
        if self.expressing is not None and not isinstance(self.expressing, ExpressingAgentTemplate):
            raise ValueError(f"{self.expressing} is not of the expected type ExpressingAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        secure_rag_instance = self.__class__()
        secure_rag_instance.name = self.name
        secure_rag_instance.description = self.description
        for key in ['planning', 'executing', 'reviewing', 'expressing']:
            if key in kwargs:
                setattr(secure_rag_instance, key, kwargs[key])
        return secure_rag_instance
