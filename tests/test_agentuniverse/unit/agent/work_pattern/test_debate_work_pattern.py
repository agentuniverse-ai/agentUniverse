# !/usr/bin/env python3

# @Time    : 2026/10/18
# @Author  : lljjcc426
# @FileName: test_debate_work_pattern.py

import asyncio

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.critic_agent_template import CriticAgentTemplate
from agentuniverse.agent.template.judge_agent_template import JudgeAgentTemplate
from agentuniverse.agent.template.proposer_agent_template import ProposerAgentTemplate
from agentuniverse.agent.work_pattern.debate_work_pattern import DebateWorkPattern

_CALLS = []
_JUDGE_SCORES = []


def _reset(*scores):
    _CALLS.clear()
    _JUDGE_SCORES.clear()
    _JUDGE_SCORES.extend(scores)


def _calls(role, method=None):
    return [call for call in _CALLS if call[0] == role and (method is None or call[1] == method)]


class _FakeProposerAgent(ProposerAgentTemplate):
    def run(self, **kwargs):
        _CALLS.append(("proposer", "run", kwargs))
        return OutputObject({"output": f'proposal-round-{kwargs.get("round_index")}'})

    async def async_run(self, **kwargs):
        _CALLS.append(("proposer", "async_run", kwargs))
        return OutputObject({"output": f'proposal-round-{kwargs.get("round_index")}'})


class _FakeCriticAgent(CriticAgentTemplate):
    def run(self, **kwargs):
        _CALLS.append(("critic", "run", kwargs))
        return OutputObject({"output": f'critique-round-{kwargs.get("round_index")}'})

    async def async_run(self, **kwargs):
        _CALLS.append(("critic", "async_run", kwargs))
        return OutputObject({"output": f'critique-round-{kwargs.get("round_index")}'})


class _FakeJudgeAgent(JudgeAgentTemplate):
    def _next_score(self):
        return _JUDGE_SCORES.pop(0) if _JUDGE_SCORES else 0

    def run(self, **kwargs):
        _CALLS.append(("judge", "run", kwargs))
        score = self._next_score()
        return OutputObject(
            {
                "output": {"suggestion": "looks good", "score": score, "final_answer": "the answer"},
                "score": score,
                "suggestion": "looks good",
            }
        )

    async def async_run(self, **kwargs):
        _CALLS.append(("judge", "async_run", kwargs))
        score = self._next_score()
        return OutputObject(
            {
                "output": {"suggestion": "looks good", "score": score, "final_answer": "the answer"},
                "score": score,
                "suggestion": "looks good",
            }
        )


def _build_pattern(proposer=None, critic=None, judge=None, **overrides):
    pattern = DebateWorkPattern()
    pattern.proposer = proposer
    pattern.critic = critic
    pattern.judge = judge
    for key, value in overrides.items():
        setattr(pattern, key, value)
    return pattern


def _full_pattern():
    return _build_pattern(_FakeProposerAgent(), _FakeCriticAgent(), _FakeJudgeAgent())


def test_invoke_reaches_consensus_in_first_round():
    _reset(80)
    pattern = _full_pattern()
    input_object = InputObject({"input": "the goal"})

    result = pattern.invoke(input_object, {"input": "the goal"})

    execution_context = result["execution_context"]
    assert execution_context["user_goal"] == "the goal"
    assert execution_context["rounds_completed"] == 1
    assert execution_context["consensus_reached"] is True
    assert execution_context["final_score"] == 80
    assert len(result["result"]) == 1
    assert sorted(result["result"][0].keys()) == ["critic_result", "judge_result", "proposal_result"]
    assert result["result"][0]["proposal_result"] == {"output": "proposal-round-1"}
    assert result["result"][0]["critic_result"] == {"output": "critique-round-1"}
    assert result["result"][0]["judge_result"]["score"] == 80
    assert len(_calls("proposer")) == 1
    assert len(_calls("critic")) == 1
    assert len(_calls("judge")) == 1


def test_invoke_exhausts_rounds_without_consensus():
    _reset(40, 40)
    pattern = _full_pattern()

    result = pattern.invoke(InputObject({"input": "the goal"}), {"input": "the goal"})

    execution_context = result["execution_context"]
    assert execution_context["rounds_completed"] == 2
    assert execution_context["consensus_reached"] is False
    assert execution_context["final_score"] == 40
    assert len(result["result"]) == 2
    assert len(_calls("proposer")) == 2
    assert len(_calls("critic")) == 2
    assert len(_calls("judge")) == 2
    assert [call[2]["round_index"] for call in _calls("judge")] == [1, 2]


def test_invoke_respects_custom_rounds_and_threshold():
    _reset(80, 80, 80)
    pattern = _full_pattern()

    result = pattern.invoke(
        InputObject({"input": "the goal"}),
        {"input": "the goal", "debate_rounds": 3, "consensus_threshold": 90},
    )

    execution_context = result["execution_context"]
    assert execution_context["debate_rounds"] == 3
    assert execution_context["rounds_completed"] == 3
    assert execution_context["consensus_reached"] is False
    assert execution_context["final_score"] == 80
    assert len(result["result"]) == 3
    assert len(_calls("judge")) == 3


def test_round_chaining_passes_results_between_agents():
    _reset(40, 40)
    pattern = _full_pattern()

    pattern.invoke(InputObject({"input": "the goal"}), {"input": "the goal"})

    proposer_calls = _calls("proposer")
    critic_calls = _calls("critic")
    judge_calls = _calls("judge")

    assert "proposal_result" not in proposer_calls[0][2]
    assert proposer_calls[0][2]["round_index"] == 1

    assert critic_calls[0][2]["round_index"] == 1
    assert isinstance(critic_calls[0][2]["proposal_result"], OutputObject)
    assert critic_calls[0][2]["proposal_result"].get_data("output") == "proposal-round-1"

    assert proposer_calls[1][2]["round_index"] == 2
    assert isinstance(proposer_calls[1][2]["critic_result"], OutputObject)
    assert proposer_calls[1][2]["critic_result"].get_data("output") == "critique-round-1"

    assert judge_calls[0][2]["proposal_result"] is critic_calls[0][2]["proposal_result"]
    assert proposer_calls[1][2]["critic_result"] is judge_calls[0][2]["critic_result"]


def test_invoke_validates_agent_types():
    _reset(80)
    pattern = DebateWorkPattern()
    pattern.proposer = object()

    with pytest.raises(ValueError, match="not of expected type"):
        pattern.invoke(InputObject({"input": "the goal"}), {"input": "the goal"})


def test_set_by_agent_model_creates_new_instance_and_copies_metadata():
    pattern = DebateWorkPattern()
    pattern.name = "debate_work_pattern"
    pattern.description = "A debate work pattern."

    proposer = _FakeProposerAgent()
    critic = _FakeCriticAgent()

    new_pattern = pattern.set_by_agent_model(proposer=proposer, critic=critic)

    assert new_pattern is not pattern
    assert new_pattern.name == "debate_work_pattern"
    assert new_pattern.description == "A debate work pattern."
    assert new_pattern.proposer is proposer
    assert new_pattern.critic is critic
    assert new_pattern.judge is None
    assert pattern.proposer is None
    assert pattern.critic is None
    assert pattern.judge is None


def test_async_invoke_reaches_consensus():
    _reset(40, 70)
    pattern = _full_pattern()
    input_object = InputObject({"input": "the goal"})

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(pattern.async_invoke(input_object, {"input": "the goal"}))
    finally:
        loop.close()

    execution_context = result["execution_context"]
    assert execution_context["rounds_completed"] == 2
    assert execution_context["consensus_reached"] is True
    assert execution_context["final_score"] == 70
    assert len(result["result"]) == 2
    for role in ("proposer", "critic", "judge"):
        assert len(_calls(role, "async_run")) == 2
        assert len(_calls(role, "run")) == 0


def test_invoke_without_agents_uses_fallbacks():
    _reset()
    pattern = DebateWorkPattern()
    input_object = InputObject({"input": "the goal"})

    result = pattern.invoke(input_object, {"input": "the goal"})

    execution_context = result["execution_context"]
    assert result["result"] == [{}, {}]
    assert execution_context["rounds_completed"] == 2
    assert execution_context["consensus_reached"] is False
    assert execution_context["final_score"] == 0
    assert input_object.get_data("proposal_result").get_data("output") == "the goal"
    assert input_object.get_data("critic_result").get_data("output") == ""
    assert input_object.get_data("judge_result").get_data("score") == 0


def test_invoke_with_zero_rounds_returns_initial_state():
    _reset(80)
    pattern = _full_pattern()

    result = pattern.invoke(
        InputObject({"input": "the goal"}),
        {"input": "the goal", "debate_rounds": 0},
    )

    execution_context = result["execution_context"]
    assert result["result"] == []
    assert execution_context["debate_rounds"] == 0
    assert execution_context["rounds_completed"] == 0
    assert execution_context["consensus_reached"] is False
    assert execution_context["final_score"] is None
    assert _CALLS == []
