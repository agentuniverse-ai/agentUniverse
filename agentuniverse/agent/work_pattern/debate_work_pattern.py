#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/28 17:50
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: debate_work_pattern.py
import asyncio
from typing import Dict, Any, List

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate
from agentuniverse.agent.template.critique_agent_template import CritiqueAgentTemplate
from agentuniverse.agent.template.enhanced_executing_agent_template import EnhancedExecutingAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.base.util.logging.logging_util import LOGGER


class DebateWorkPattern(WorkPattern):
    planning: PlanningAgentTemplate = None
    critique: CritiqueAgentTemplate = None
    executing: EnhancedExecutingAgentTemplate = None

    def invoke(self, input_object: InputObject,
               work_pattern_input: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        self._validate_work_pattern_members()
        debate_results = {
            'rounds': [],
            'final_plan': {},
            'execution_result': {}
        }
        debate_rounds = work_pattern_input.get('debate_rounds', 3)
        consensus_threshold = work_pattern_input.get('consensus_threshold',
                                                     0.8)
        execute_result = work_pattern_input.get('execute_result', True)
        debate_history = []
        consensus_reached: bool = False
        debate_round: int = 0
        for round_num in range(1, debate_rounds + 1):
            LOGGER.info(f"Starting debate round {round_num}")
            round_results = {'round': round_num}
            planning_result = self._invoke_planning(input_object,
                                                    debate_history)
            LOGGER.info(
                f"Debate round {round_num} planning result: {planning_result}")
            debate_history.append(
                f'Debate round {round_num} planning result: {planning_result.get("thought", "")}'
            )
            round_results['planning'] = planning_result

            critique_result = self._invoke_critique(input_object,
                                                    debate_history)
            LOGGER.info(
                f"Debate round {round_num} critique result: {critique_result}")
            debate_history.append(
                f'Debate round {round_num} critique result:\n'
                f'- concerns: {critique_result.get("concerns", [])}\n'
                f'- suggestions: {critique_result.get("suggestions", [])}\n'
                f'- critique score: {critique_result.get("critique_score", 0.5)}'
            )
            round_results['critique'] = critique_result
            consensus_score = self._evaluate_consensus(critique_result)
            round_results['consensus_score'] = consensus_score

            debate_history.append(round_results)
            debate_results['rounds'].append(round_results)
            debate_round = round_num
            if consensus_score >= consensus_threshold:
                consensus_reached = True
                break

        final_plan = debate_results['rounds'][-1]['planning']
        debate_results['final_plan'] = final_plan
        LOGGER.info(f'Debate Results: {debate_results}')

        execution_result: Dict[str, Any] = {}
        if execute_result and self.executing:
            execution_result = self._invoke_executing(input_object,
                                                      debate_history,
                                                      final_plan)
            debate_results['execution_result'] = execution_result
        return {
            'result': debate_results,
            'consensus_reached': consensus_reached,
            'debate_rounds': debate_round,
            'plan': final_plan,
            'execution': execution_result,
        }

    async def async_invoke(self, input_object: InputObject,
                           work_pattern_input: Dict[str,
                                                    Any], **kwargs) -> dict:
        return await asyncio.get_running_loop().run_in_executor(
            None, self.invoke, input_object, work_pattern_input, **kwargs)

    def _evaluate_consensus(self, critique_result: Dict[str, Any]) -> float:
        critique_score = critique_result.get('critique_score')
        if critique_score is not None and isinstance(critique_score,
                                                     (int, float)):
            return max(0.0, min(1.0, float(critique_score)))

        concerns = critique_result.get('concerns', [])
        if not concerns:
            return 1.0
        consensus = max(0.0, 1.0 - (len(concerns) * 0.1))
        return consensus

    def _invoke_planning(self, input_object: InputObject,
                         debate_history: List[str]) -> dict:
        if not self.planning:
            return OutputObject({
                "framework": [input_object.get_data('input')]
            }).to_dict()
        planning_input = InputObject(input_object.to_dict())
        planning_input.add_data('debate_history', debate_history)
        planning_result = self.planning.run(**planning_input.to_dict())
        return planning_result.to_dict()

    def _invoke_critique(self, input_object: InputObject,
                         debate_history: List[str]) -> dict:
        if not self.critique:
            return OutputObject({"critique": []}).to_dict()
        critique_input = InputObject(input_object.to_dict())
        critique_input.add_data('debate_history', debate_history)
        critique_result = self.critique.run(**critique_input.to_dict())
        return critique_result.to_dict()

    def _invoke_executing(
        self,
        input_object: InputObject,
        debate_history: List[str],
        final_plan: Dict[str, Any],
    ) -> dict:
        if not self.executing:
            return OutputObject({}).to_dict()

        executing_input = InputObject(input_object.to_dict())
        executing_input.add_data('debate_history', debate_history)
        executing_input.add_data('planning_result', InputObject(final_plan))
        executing_result = self.executing.run(**executing_input.to_dict())
        return executing_result.to_dict()

    def _validate_work_pattern_members(self):
        if self.planning and not isinstance(self.planning,
                                            PlanningAgentTemplate):
            raise ValueError(
                f"{self.planning} is not of the expected type PlanningAgentTemplate."
            )
        if self.critique and not isinstance(self.critique,
                                            CritiqueAgentTemplate):
            raise ValueError(
                f"{self.critique} is not of the expected type CritiqueAgentTemplate."
            )
        if self.executing and not isinstance(self.executing,
                                             EnhancedExecutingAgentTemplate):
            raise ValueError(
                f"{self.executing} is not of the expected type ExecutingAgentTemplate."
            )

    def set_by_agent_model(self, **kwargs):
        debate_work_pattern_instance = self.__class__()
        debate_work_pattern_instance.name = self.name
        debate_work_pattern_instance.description = self.description
        for key in ['planning', 'critique', 'executing']:
            if key in kwargs:
                setattr(debate_work_pattern_instance, key, kwargs[key])
        return debate_work_pattern_instance
