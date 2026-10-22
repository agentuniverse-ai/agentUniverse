import asyncio
from typing import ClassVar

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import (
    ExecutingAgentTemplate,
)
from agentuniverse.agent.template.expressing_agent_template import (
    ExpressingAgentTemplate,
)
from agentuniverse.agent.template.planning_agent_template import (
    PlanningAgentTemplate,
)
from agentuniverse.agent.template.reviewing_agent_template import (
    ReviewingAgentTemplate,
)
from agentuniverse.agent.work_pattern.peer_work_pattern import PeerWorkPattern


class _PlanningStub(PlanningAgentTemplate):
    calls: ClassVar[int] = 0

    def run(self, **kwargs) -> OutputObject:
        type(self).calls += 1
        return OutputObject({"framework": ["subtask A", "subtask B"], "thought": ""})

    async def async_run(self, **kwargs) -> OutputObject:
        return self.run(**kwargs)


class _ExecutingStub(ExecutingAgentTemplate):
    calls: ClassVar[int] = 0

    def run(self, **kwargs) -> OutputObject:
        type(self).calls += 1
        return OutputObject({"executing_result": [
            {"index": 0, "input": "Question 1: subtask A", "output": "Answer 1"},
        ]})

    async def async_run(self, **kwargs) -> OutputObject:
        return self.run(**kwargs)


class _ExpressingStub(ExpressingAgentTemplate):
    calls: ClassVar[int] = 0

    def run(self, **kwargs) -> OutputObject:
        type(self).calls += 1
        return OutputObject({"output": "final expressed answer"})

    async def async_run(self, **kwargs) -> OutputObject:
        return self.run(**kwargs)


class _ReviewingStub(ReviewingAgentTemplate):
    """Always returns a failing score so the retry loop never exits early."""
    calls: ClassVar[int] = 0

    def run(self, **kwargs) -> OutputObject:
        type(self).calls += 1
        return OutputObject({"output": {"is_useful": False}, "score": 0,
                             "suggestion": "please improve"})

    async def async_run(self, **kwargs) -> OutputObject:
        return self.run(**kwargs)


def _build_pattern() -> PeerWorkPattern:
    pattern = PeerWorkPattern()
    pattern.planning = _PlanningStub()
    pattern.executing = _ExecutingStub()
    pattern.expressing = _ExpressingStub()
    pattern.reviewing = _ReviewingStub()
    return pattern


def _reset_stub_counters() -> None:
    _PlanningStub.calls = 0
    _ExecutingStub.calls = 0
    _ExpressingStub.calls = 0
    _ReviewingStub.calls = 0


def _base_input() -> dict:
    # retry_count / eval_threshold defaults are outside the scope of this fix;
    # pass them explicitly like PeerAgentTemplate.parse_input does.
    return {"input": "demo question", "retry_count": 2, "eval_threshold": 60}


def _run_pattern(pattern: PeerWorkPattern, work_pattern_input: dict,
                 asynchronous: bool = False) -> dict:
    input_object = InputObject({"input": "demo question"})
    if asynchronous:
        return asyncio.run(pattern.async_invoke(input_object, work_pattern_input))
    return pattern.invoke(input_object, work_pattern_input)


def test_invoke_invalid_jump_step_raises_value_error():
    for bad_step in ("express", "Planning", "planning ", "all"):
        pattern = _build_pattern()
        work_pattern_input = {**_base_input(), "jump_step": bad_step}
        try:
            _run_pattern(pattern, work_pattern_input)
        except ValueError as e:
            assert "jump_step" in str(e)
        else:
            raise AssertionError(f"jump_step={bad_step!r} should raise ValueError")


def test_invoke_empty_jump_step_falls_back_to_expressing():
    _reset_stub_counters()
    pattern = _build_pattern()
    result = _run_pattern(pattern, {**_base_input(), "jump_step": ""})

    assert len(result["result"]) == 2
    assert _ExpressingStub.calls == 2
    assert all("expressing_result" in rnd for rnd in result["result"])


def test_async_invoke_invalid_jump_step_raises_value_error():
    pattern = _build_pattern()
    work_pattern_input = {**_base_input(), "jump_step": "express"}
    try:
        _run_pattern(pattern, work_pattern_input, asynchronous=True)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid jump_step should raise ValueError")


def test_invoke_jump_step_none_falls_back_to_expressing():
    _reset_stub_counters()
    pattern = _build_pattern()
    result = _run_pattern(pattern, {**_base_input(), "jump_step": None})

    # two full rounds, none of them an empty no-op round
    assert len(result["result"]) == 2
    for rnd in result["result"]:
        assert "expressing_result" in rnd
        assert "reviewing_result" in rnd
    # planning/executing are reused from round one, expressing/reviewing rerun
    assert _PlanningStub.calls == 1
    assert _ExecutingStub.calls == 1
    assert _ExpressingStub.calls == 2
    assert _ReviewingStub.calls == 2


def test_invoke_missing_jump_step_falls_back_to_expressing():
    _reset_stub_counters()
    pattern = _build_pattern()
    result = _run_pattern(pattern, _base_input())

    assert len(result["result"]) == 2
    assert _ExpressingStub.calls == 2
    assert all("expressing_result" in rnd for rnd in result["result"])


def test_invoke_valid_jump_step_planning_reruns_every_step():
    _reset_stub_counters()
    pattern = _build_pattern()
    result = _run_pattern(pattern, {**_base_input(), "jump_step": "planning"})

    assert len(result["result"]) == 2
    assert _PlanningStub.calls == 2
    assert _ExecutingStub.calls == 2
    assert _ExpressingStub.calls == 2
    assert _ReviewingStub.calls == 2


def test_async_invoke_jump_step_none_falls_back_to_expressing():
    _reset_stub_counters()
    pattern = _build_pattern()
    result = _run_pattern(pattern, {**_base_input(), "jump_step": None},
                          asynchronous=True)

    assert len(result["result"]) == 2
    assert _ExpressingStub.calls == 2
    assert all("expressing_result" in rnd for rnd in result["result"])
