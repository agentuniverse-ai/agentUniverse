"""Knowledge decorators must finish the trace with a single await."""

import asyncio
import importlib
import inspect
from unittest.mock import Mock

import pytest

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager

trace = importlib.import_module("agentuniverse.base.annotation.trace")


@pytest.fixture
def tracing_context(monkeypatch):
    memory = Mock()
    monkeypatch.setattr(trace, "ConversationMemoryModule", lambda: memory)
    parent = {"source": "caller", "type": "agent"}
    manager = FrameworkContextManager()
    key = trace.Monitor.get_trace_id() + "_invocation_chain"
    token = manager.set_context(key, [parent])
    yield memory, parent
    manager.reset_context(key, token)


async def await_once(awaitable):
    result = await awaitable
    # Close the leaked coroutine on the unfixed implementation to keep the
    # failing regression independent of garbage-collection warning timing.
    if inspect.iscoroutine(result):
        result.close()
    return result


def test_single_await_runs_target_and_records_trace(tracing_context):
    memory, parent = tracing_context
    observed = []
    expected = ["document"]

    @trace.trace_knowledge
    async def retrieve(query, *, limit=1):
        """Retrieve matching documents."""
        await asyncio.sleep(0)
        observed.append((query, limit, trace.Monitor.get_invocation_chain().copy()))
        return expected

    async def run():
        result = await await_once(retrieve("question", limit=2))
        assert result is expected
        assert trace.Monitor.get_invocation_chain() == [parent]

    asyncio.run(run())
    assert len(observed) == 1
    assert observed[0][:2] == ("question", 2)
    assert observed[0][2][0] == parent
    assert observed[0][2][1]["type"] == "knowledge"
    memory.add_knowledge_input_info.assert_called_once()
    memory.add_knowledge_output_info.assert_called_once()
    incoming = memory.add_knowledge_input_info.call_args
    outgoing = memory.add_knowledge_output_info.call_args
    assert incoming.args[0] == parent
    assert incoming.args[2] == {"query": "question", "limit": 2}
    assert outgoing.kwargs["params"] is expected
    assert incoming.args[3] == outgoing.kwargs["pair_id"]
    assert retrieve.__name__ == "retrieve"
    assert retrieve.__doc__ == "Retrieve matching documents."


def test_target_error_propagates_and_restores_parent(tracing_context):
    memory, parent = tracing_context
    error = ValueError("lookup failed")

    @trace.trace_knowledge
    async def retrieve():
        await asyncio.sleep(0)
        raise error

    async def run():
        with pytest.raises(ValueError) as raised:
            await await_once(retrieve())
        assert raised.value is error
        assert trace.Monitor.get_invocation_chain() == [parent]

    asyncio.run(run())
    memory.add_knowledge_input_info.assert_called_once()
    memory.add_knowledge_output_info.assert_not_called()


def test_custom_async_wrapper_is_awaited_at_call_time(monkeypatch):
    calls = []

    @trace.trace_knowledge
    async def retrieve(query):
        return query.upper()

    async def custom_wrapper(func, *args, **kwargs):
        calls.append(args)
        return {"wrapped": await func(*args, **kwargs)}

    # Preserve the runtime extension point, including replacements installed
    # after the target was decorated.
    monkeypatch.setattr(trace, "_knowledge_wrapper_async", custom_wrapper)
    assert asyncio.run(await_once(retrieve("question"))) == {"wrapped": "QUESTION"}
    assert calls == [("question",)]


def test_sync_knowledge_still_returns_result_directly(tracing_context):
    memory, parent = tracing_context

    @trace.trace_knowledge
    def retrieve(query):
        return [query]

    assert retrieve("question") == ["question"]
    assert trace.Monitor.get_invocation_chain() == [parent]
    memory.add_knowledge_input_info.assert_called_once()
    memory.add_knowledge_output_info.assert_called_once()
