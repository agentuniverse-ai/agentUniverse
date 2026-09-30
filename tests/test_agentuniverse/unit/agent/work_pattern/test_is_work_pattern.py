"""Tests for the implementation-supervision work pattern."""

import asyncio

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.work_pattern.is_work_pattern import ISWorkPattern


class _CorrectionLimitedPattern(ISWorkPattern):
    def _invoke_implementation(self, *args, **kwargs):
        return {"output": "initial"}

    def _invoke_supervision(self, *args, **kwargs):
        return {"needs_correction": True, "feedback": "revise"}

    def _invoke_correction(self, *args, **kwargs):
        raise AssertionError("correction limit should prevent this call")

    async def _async_invoke_implementation(self, *args, **kwargs):
        return {"output": "initial"}

    async def _async_invoke_supervision(self, *args, **kwargs):
        return {"needs_correction": True, "feedback": "revise"}

    async def _async_invoke_correction(self, *args, **kwargs):
        raise AssertionError("correction limit should prevent this call")


def test_invoke_does_not_report_blocked_correction_as_applied():
    result = _CorrectionLimitedPattern().invoke(
        InputObject({"input": "goal"}),
        {"input": "goal", "checkpoint_count": 1, "max_corrections": 0},
    )

    assert result["execution_context"]["checkpoint_history"][0]["corrected"] is False
    assert result["execution_context"]["corrections_made"] == 0


def test_async_invoke_does_not_report_blocked_correction_as_applied():
    result = asyncio.run(
        _CorrectionLimitedPattern().async_invoke(
            InputObject({"input": "goal"}),
            {"input": "goal", "checkpoint_count": 1, "max_corrections": 0},
        )
    )

    assert result["execution_context"]["checkpoint_history"][0]["corrected"] is False
    assert result["execution_context"]["corrections_made"] == 0
