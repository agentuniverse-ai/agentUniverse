import asyncio
from typing import ClassVar

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.implementation_agent_template import (
    ImplementationAgentTemplate,
)
from agentuniverse.agent.template.is_agent_template import ISAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import (
    SupervisionAgentTemplate,
)
from agentuniverse.agent.work_pattern.is_work_pattern import ISWorkPattern


class _ImplementationStub(ImplementationAgentTemplate):
    responses: ClassVar[list[dict]] = []

    def run(self, **kwargs) -> OutputObject:
        return OutputObject(self.responses.pop(0))

    async def async_run(self, **kwargs) -> OutputObject:
        return self.run(**kwargs)


class _SupervisionStub(SupervisionAgentTemplate):
    responses: ClassVar[list[dict]] = []

    def run(self, **kwargs) -> OutputObject:
        return OutputObject(self.responses.pop(0))

    async def async_run(self, **kwargs) -> OutputObject:
        return self.run(**kwargs)


def _run_pattern(*, asynchronous: bool) -> dict:
    implementation = _ImplementationStub()
    _ImplementationStub.responses = [
        {"checkpoint_output": "original result"},
        {"checkpoint_output": "corrected result"},
    ]
    supervision = _SupervisionStub()
    _SupervisionStub.responses = [
        {
            "needs_correction": True,
            "feedback": "apply the requested correction",
            "score": 40,
        }
    ]
    pattern = ISWorkPattern()
    pattern.implementation = implementation
    pattern.supervision = supervision
    input_object = InputObject({"input": "complete the task"})
    work_pattern_input = {
        "input": "complete the task",
        "checkpoint_count": 1,
        "max_corrections": 1,
    }

    if asynchronous:
        return asyncio.run(pattern.async_invoke(input_object, work_pattern_input))
    return pattern.invoke(input_object, work_pattern_input)


def test_sync_and_async_results_preserve_applied_correction():
    template = ISAgentTemplate()

    sync_result = template.parse_result(_run_pattern(asynchronous=False))
    async_result = template.parse_result(_run_pattern(asynchronous=True))

    assert sync_result == async_result
    assert sync_result["output"] == "corrected result"
    assert sync_result["checkpoint_results"][-1]["effective_result"] == {"checkpoint_output": "corrected result"}
    assert sync_result["full_output"].endswith("=== Final Output ===\ncorrected result")


def test_latest_uncorrected_checkpoint_remains_the_final_output():
    planner_result = {
        "result": [
            {
                "implementation_result": {"checkpoint_output": "first implementation"},
                "correction_result": {"checkpoint_output": "first correction"},
            },
            {"implementation_result": {"checkpoint_output": "latest implementation"}},
        ],
        "execution_context": {"corrections_made": 1},
    }

    result = ISAgentTemplate().parse_result(planner_result)

    assert result["output"] == "latest implementation"
    assert result["checkpoint_results"][-1]["effective_result"] == {"checkpoint_output": "latest implementation"}
    assert "effective_result" not in planner_result["result"][-1]


def test_explicit_effective_result_takes_precedence():
    planner_result = {
        "result": [
            {
                "implementation_result": {"checkpoint_output": "original"},
                "correction_result": {"checkpoint_output": "corrected"},
                "effective_result": {"checkpoint_output": "accepted result"},
            }
        ],
        "execution_context": {},
    }

    result = ISAgentTemplate().parse_result(planner_result)

    assert result["output"] == "accepted result"
