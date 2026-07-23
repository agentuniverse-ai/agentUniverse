import asyncio

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import (
    ExecutingAgentTemplate,
)
from agentuniverse.agent.template.expressing_agent_template import (
    ExpressingAgentTemplate,
)
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.work_pattern.peer_work_pattern import PeerWorkPattern


class RecordingPlanningAgent(PlanningAgentTemplate):
    calls: list[dict] = []

    def run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        return OutputObject({"framework": [f"plan-{len(self.calls)}"]})

    async def async_run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        return OutputObject({"framework": [f"plan-{len(self.calls)}"]})


class RecordingExecutingAgent(ExecutingAgentTemplate):
    calls: list[dict] = []

    def run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        return OutputObject({"executing_result": []})

    async def async_run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        return OutputObject({"executing_result": []})


class RecordingExpressingAgent(ExpressingAgentTemplate):
    calls: list[dict] = []

    def run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        return OutputObject({"output": f"answer-{len(self.calls)}"})

    async def async_run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        return OutputObject({"output": f"answer-{len(self.calls)}"})


class RecordingReviewingAgent(ReviewingAgentTemplate):
    calls: list[dict] = []
    review_scores: list[int] = []

    def run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        call_number = len(self.calls)
        return OutputObject({
            "score": self.review_scores[call_number - 1],
            "suggestion": f"review-{call_number}",
        })

    async def async_run(self, **kwargs) -> OutputObject:
        self.calls.append(kwargs)
        call_number = len(self.calls)
        return OutputObject({
            "score": self.review_scores[call_number - 1],
            "suggestion": f"review-{call_number}",
        })


def _build_pattern(review_scores: list[int]) -> tuple[
    PeerWorkPattern,
    RecordingPlanningAgent,
]:
    planning = RecordingPlanningAgent()
    reviewing = RecordingReviewingAgent()
    reviewing.review_scores = list(review_scores)

    pattern = PeerWorkPattern()
    pattern.planning = planning
    pattern.executing = RecordingExecutingAgent()
    pattern.expressing = RecordingExpressingAgent()
    pattern.reviewing = reviewing
    return pattern, planning


def _assert_retry_feedback(
    result: dict,
    planning: RecordingPlanningAgent,
) -> None:
    assert len(result["result"]) == 2
    assert len(planning.calls) == 2
    assert [
        round_result["reviewing_result"]["score"]
        for round_result in result["result"]
    ] == [0, 80]

    second_planning_input = planning.calls[1]
    assert second_planning_input["planning_result"].framework == ["plan-1"]
    assert second_planning_input["reviewing_result"].score == 0
    assert second_planning_input["reviewing_result"].suggestion == "review-1"


def test_invoke_passes_previous_planning_and_review_feedback_on_retry():
    pattern, planning = _build_pattern([0, 80])

    result = pattern.invoke(
        InputObject({"input": "analyse the event"}),
        {
            "retry_count": 2,
            "jump_step": "planning",
            "eval_threshold": 60,
        },
    )

    _assert_retry_feedback(result, planning)


def test_async_invoke_passes_previous_planning_and_review_feedback_on_retry():
    async def exercise():
        pattern, planning = _build_pattern([0, 80])
        result = await pattern.async_invoke(
            InputObject({"input": "analyse the event"}),
            {
                "retry_count": 2,
                "jump_step": "planning",
                "eval_threshold": 60,
            },
        )
        return result, planning

    result, planning = asyncio.run(exercise())

    _assert_retry_feedback(result, planning)


def test_invoke_stops_after_first_passing_review():
    pattern, planning = _build_pattern([80])

    result = pattern.invoke(
        InputObject({"input": "analyse the event"}),
        {
            "retry_count": 3,
            "jump_step": "planning",
            "eval_threshold": 60,
        },
    )

    assert len(result["result"]) == 1
    assert len(planning.calls) == 1
