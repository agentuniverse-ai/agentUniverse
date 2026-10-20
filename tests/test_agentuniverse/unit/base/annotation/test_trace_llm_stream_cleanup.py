"""Default async LLM tracing must forward streaming cleanup."""

import asyncio
import importlib
from unittest.mock import AsyncMock, Mock

import pytest

from agentuniverse.llm.llm_output import LLMOutput


@pytest.fixture
def trace(monkeypatch):
    module = importlib.import_module("agentuniverse.base.annotation.trace")
    monkeypatch.setattr(module, "_get_llm_info", Mock(return_value=(None, "test", None, None, None, None)))
    monkeypatch.setattr(module, "_llm_plugins", lambda function: function)
    monkeypatch.setattr(module, "Monitor", Mock())
    return module


class PlainAsyncIterator:
    def __init__(self):
        self.remaining = 1

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.remaining:
            raise StopAsyncIteration
        self.remaining -= 1
        return LLMOutput(text="chunk")


@pytest.mark.parametrize("early_close", [False, True])
@pytest.mark.parametrize("closeable", [False, True])
def test_trace_supports_iterators_with_or_without_aclose(trace, early_close, closeable):
    source = PlainAsyncIterator()
    if closeable:
        source.aclose = AsyncMock()

    async def run():
        result = await trace._default_llm_wrapper_async(AsyncMock(return_value=source))
        assert (await anext(result)).text == "chunk"
        if early_close:
            await result.aclose()
        else:
            assert [chunk async for chunk in result] == []

    asyncio.run(run())
    trace.Monitor.pop_invocation_chain.assert_called_once()
    if closeable:
        source.aclose.assert_awaited_once()


@pytest.mark.parametrize("cancel", [False, True])
def test_trace_cleans_up_on_iteration_error_or_cancellation(trace, cancel):
    class FailingIterator(PlainAsyncIterator):
        async def __anext__(self):
            raise asyncio.CancelledError if cancel else RuntimeError("stream failed")

    source = FailingIterator()
    source.aclose = AsyncMock()

    async def run():
        result = await trace._default_llm_wrapper_async(AsyncMock(return_value=source))
        with pytest.raises(asyncio.CancelledError if cancel else RuntimeError):
            await anext(result)

    asyncio.run(run())
    source.aclose.assert_awaited_once()
    trace.Monitor.pop_invocation_chain.assert_called_once()


def test_trace_pops_monitor_even_when_close_fails(trace):
    source = PlainAsyncIterator()
    source.aclose = AsyncMock(side_effect=RuntimeError("close failed"))

    async def run():
        result = await trace._default_llm_wrapper_async(AsyncMock(return_value=source))
        await anext(result)
        with pytest.raises(RuntimeError, match="close failed"):
            await result.aclose()

    asyncio.run(run())
    trace.Monitor.pop_invocation_chain.assert_called_once()


def test_trace_nonstream_result_unchanged(trace):
    output = LLMOutput(text="answer")
    assert asyncio.run(trace._default_llm_wrapper_async(AsyncMock(return_value=output))) is output
    trace.Monitor.pop_invocation_chain.assert_called_once()
