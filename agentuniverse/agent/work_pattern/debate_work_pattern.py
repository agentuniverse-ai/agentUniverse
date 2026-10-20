# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/18
# @Author  : lljjcc426
# @FileName: debate_work_pattern.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.critic_agent_template import CriticAgentTemplate
from agentuniverse.agent.template.judge_agent_template import JudgeAgentTemplate
from agentuniverse.agent.template.proposer_agent_template import ProposerAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class DebateWorkPattern(WorkPattern):
    """Debate work pattern for consensus-driven problem solving.

    This pattern uses three agents with distinct responsibilities:
    - Proposer: Drafts an initial proposal and revises it based on critique
    - Critic: Reviews the proposal and provides structured feedback
    - Judge: Scores each debate round and decides whether consensus is reached

    The pattern runs debate rounds until the judge's score reaches the consensus
    threshold or the maximum number of debate rounds is exhausted.
    """

    proposer: ProposerAgentTemplate = None
    critic: CriticAgentTemplate = None
    judge: JudgeAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute debate pattern synchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary containing:
                - debate_rounds (int): Maximum number of debate rounds (default: 2)
                - consensus_threshold (int): Score threshold for reaching consensus (default: 60)
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result containing all debate round results.
        """
        self._validate_work_pattern_members()

        debate_results = list()
        debate_rounds = work_pattern_input.get('debate_rounds', 2)
        consensus_threshold = work_pattern_input.get('consensus_threshold', 60)

        # Track overall execution state
        execution_context = {
            'user_goal': work_pattern_input.get('input'),
            'debate_rounds': debate_rounds,
            'rounds_completed': 0,
            'consensus_reached': False,
            'final_score': None
        }

        for round_index in range(debate_rounds):
            debate_round_result = {}

            # Proposer agent drafts or revises the proposal
            self._invoke_proposer(
                input_object,
                work_pattern_input,
                round_index,
                execution_context,
                debate_round_result
            )

            # Critic agent reviews the proposal and provides feedback
            self._invoke_critic(
                input_object,
                work_pattern_input,
                round_index,
                execution_context,
                debate_round_result
            )

            # Judge agent scores the round and issues a verdict
            judge_result = self._invoke_judge(
                input_object,
                work_pattern_input,
                round_index,
                execution_context,
                debate_round_result
            )

            execution_context['rounds_completed'] = round_index + 1
            score = judge_result.get('score', 0)
            execution_context['final_score'] = score

            debate_results.append(debate_round_result)

            # Stop early once the judge confirms consensus
            if score is not None and score >= consensus_threshold:
                execution_context['consensus_reached'] = True
                break

        return {'result': debate_results, 'execution_context': execution_context}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute debate pattern asynchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary containing:
                - debate_rounds (int): Maximum number of debate rounds (default: 2)
                - consensus_threshold (int): Score threshold for reaching consensus (default: 60)
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result containing all debate round results.
        """
        self._validate_work_pattern_members()

        debate_results = list()
        debate_rounds = work_pattern_input.get('debate_rounds', 2)
        consensus_threshold = work_pattern_input.get('consensus_threshold', 60)

        # Track overall execution state
        execution_context = {
            'user_goal': work_pattern_input.get('input'),
            'debate_rounds': debate_rounds,
            'rounds_completed': 0,
            'consensus_reached': False,
            'final_score': None
        }

        for round_index in range(debate_rounds):
            debate_round_result = {}

            # Proposer agent drafts or revises the proposal
            await self._async_invoke_proposer(
                input_object,
                work_pattern_input,
                round_index,
                execution_context,
                debate_round_result
            )

            # Critic agent reviews the proposal and provides feedback
            await self._async_invoke_critic(
                input_object,
                work_pattern_input,
                round_index,
                execution_context,
                debate_round_result
            )

            # Judge agent scores the round and issues a verdict
            judge_result = await self._async_invoke_judge(
                input_object,
                work_pattern_input,
                round_index,
                execution_context,
                debate_round_result
            )

            execution_context['rounds_completed'] = round_index + 1
            score = judge_result.get('score', 0)
            execution_context['final_score'] = score

            debate_results.append(debate_round_result)

            # Stop early once the judge confirms consensus
            if score is not None and score >= consensus_threshold:
                execution_context['consensus_reached'] = True
                break

        return {'result': debate_results, 'execution_context': execution_context}

    def _invoke_proposer(self, input_object: InputObject, agent_input: dict,
                         round_index: int, execution_context: dict,
                         debate_round_result: dict) -> dict:
        """Invoke proposer agent synchronously."""
        if not self.proposer:
            proposal_result = OutputObject({"output": agent_input.get('input')})
        else:
            proposer_input = {
                **input_object.to_dict(),
                'round_index': round_index + 1,
                'execution_context': execution_context
            }
            proposal_result = self.proposer.run(**proposer_input)
            debate_round_result['proposal_result'] = proposal_result.to_dict()
        input_object.add_data('proposal_result', proposal_result)
        return proposal_result.to_dict()

    async def _async_invoke_proposer(self, input_object: InputObject, agent_input: dict,
                                     round_index: int, execution_context: dict,
                                     debate_round_result: dict) -> dict:
        """Invoke proposer agent asynchronously."""
        if not self.proposer:
            proposal_result = OutputObject({"output": agent_input.get('input')})
        else:
            proposer_input = {
                **input_object.to_dict(),
                'round_index': round_index + 1,
                'execution_context': execution_context
            }
            proposal_result = await self.proposer.async_run(**proposer_input)
            debate_round_result['proposal_result'] = proposal_result.to_dict()
        input_object.add_data('proposal_result', proposal_result)
        return proposal_result.to_dict()

    def _invoke_critic(self, input_object: InputObject, agent_input: dict,
                       round_index: int, execution_context: dict,
                       debate_round_result: dict) -> dict:
        """Invoke critic agent synchronously."""
        if not self.critic:
            critic_result = OutputObject({"output": ""})
        else:
            critic_input = {
                **input_object.to_dict(),
                'round_index': round_index + 1,
                'execution_context': execution_context
            }
            critic_result = self.critic.run(**critic_input)
            debate_round_result['critic_result'] = critic_result.to_dict()
        input_object.add_data('critic_result', critic_result)
        return critic_result.to_dict()

    async def _async_invoke_critic(self, input_object: InputObject, agent_input: dict,
                                   round_index: int, execution_context: dict,
                                   debate_round_result: dict) -> dict:
        """Invoke critic agent asynchronously."""
        if not self.critic:
            critic_result = OutputObject({"output": ""})
        else:
            critic_input = {
                **input_object.to_dict(),
                'round_index': round_index + 1,
                'execution_context': execution_context
            }
            critic_result = await self.critic.async_run(**critic_input)
            debate_round_result['critic_result'] = critic_result.to_dict()
        input_object.add_data('critic_result', critic_result)
        return critic_result.to_dict()

    def _invoke_judge(self, input_object: InputObject, agent_input: dict,
                      round_index: int, execution_context: dict,
                      debate_round_result: dict) -> dict:
        """Invoke judge agent synchronously."""
        if not self.judge:
            judge_result = OutputObject({"output": {}, "score": 0, "suggestion": ""})
        else:
            judge_input = {
                **input_object.to_dict(),
                'round_index': round_index + 1,
                'execution_context': execution_context
            }
            judge_result = self.judge.run(**judge_input)
            debate_round_result['judge_result'] = judge_result.to_dict()
        input_object.add_data('judge_result', judge_result)
        return judge_result.to_dict()

    async def _async_invoke_judge(self, input_object: InputObject, agent_input: dict,
                                  round_index: int, execution_context: dict,
                                  debate_round_result: dict) -> dict:
        """Invoke judge agent asynchronously."""
        if not self.judge:
            judge_result = OutputObject({"output": {}, "score": 0, "suggestion": ""})
        else:
            judge_input = {
                **input_object.to_dict(),
                'round_index': round_index + 1,
                'execution_context': execution_context
            }
            judge_result = await self.judge.async_run(**judge_input)
            debate_round_result['judge_result'] = judge_result.to_dict()
        input_object.add_data('judge_result', judge_result)
        return judge_result.to_dict()

    def _validate_work_pattern_members(self):
        """Validate that agents are of the correct type."""
        if self.proposer and not isinstance(self.proposer, ProposerAgentTemplate):
            raise ValueError(f"{self.proposer} is not of expected type ProposerAgentTemplate.")
        if self.critic and not isinstance(self.critic, CriticAgentTemplate):
            raise ValueError(f"{self.critic} is not of expected type CriticAgentTemplate.")
        if self.judge and not isinstance(self.judge, JudgeAgentTemplate):
            raise ValueError(f"{self.judge} is not of expected type JudgeAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        """Create new instance with dynamically injected agents.

        Args:
            **kwargs: Agent instances to inject (proposer, critic, judge).

        Returns:
            DebateWorkPattern: New instance with injected agents.
        """
        debate_work_pattern_instance = self.__class__()
        debate_work_pattern_instance.name = self.name
        debate_work_pattern_instance.description = self.description
        for key in ['proposer', 'critic', 'judge']:
            if key in kwargs:
                setattr(debate_work_pattern_instance, key, kwargs[key])
        return debate_work_pattern_instance
