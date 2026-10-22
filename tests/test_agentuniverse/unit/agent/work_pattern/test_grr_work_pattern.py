"""Tests for Generate-Review-Rewrite work-pattern fallbacks."""

import asyncio

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.work_pattern.grr_work_pattern import GRRWorkPattern


def _assert_fallback_round(result):
    round_result = result["result"][0]
    assert round_result["generating_result"] == {"output": "draft"}
    assert round_result["reviewing_result"] == {"score": 100}


def test_invoke_records_fallback_agent_results():
    result = GRRWorkPattern().invoke(
        InputObject({"input": "draft"}),
        {"input": "draft", "retry_count": 1},
    )

    _assert_fallback_round(result)


def test_async_invoke_records_fallback_agent_results():
    result = asyncio.run(
        GRRWorkPattern().async_invoke(
            InputObject({"input": "draft"}),
            {"input": "draft", "retry_count": 1},
        )
    )

    _assert_fallback_round(result)
