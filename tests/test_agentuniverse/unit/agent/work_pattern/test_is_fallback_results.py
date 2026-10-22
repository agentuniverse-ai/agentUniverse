#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.work_pattern.is_work_pattern import ISWorkPattern


def _assert_fallback_results(result):
    checkpoint = result["result"][0]
    assert checkpoint["implementation_result"] == {"output": "task"}
    assert checkpoint["supervision_result"] == {
        "needs_correction": False,
        "feedback": "",
    }


def test_invoke_retains_fallback_results():
    pattern = ISWorkPattern()
    result = pattern.invoke(
        InputObject({"input": "task"}),
        {"input": "task", "checkpoint_count": 1},
    )

    _assert_fallback_results(result)


def test_async_invoke_retains_fallback_results():
    pattern = ISWorkPattern()
    result = asyncio.run(pattern.async_invoke(
        InputObject({"input": "task"}),
        {"input": "task", "checkpoint_count": 1},
    ))

    _assert_fallback_results(result)
