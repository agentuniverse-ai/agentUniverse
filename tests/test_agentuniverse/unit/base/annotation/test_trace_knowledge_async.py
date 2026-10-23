from contextlib import nullcontext
import asyncio

from agentuniverse.base.annotation import trace


def test_trace_knowledge_awaits_default_async_wrapper(monkeypatch):
    events = []

    monkeypatch.setattr(trace, "InvocationChainContext", lambda **_: nullcontext())
    monkeypatch.setattr(
        trace,
        "_process_knowledge",
        lambda source, knowledge_input, start_info, pair_id: events.append(("input", source)),
    )
    monkeypatch.setattr(
        trace,
        "_handle_knowledge_result",
        lambda start_info, source, result, pair_id: events.append(("output", result)) or result,
    )

    @trace.trace_knowledge
    async def retrieve(query):
        return [query]

    result = asyncio.run(retrieve("question"))

    assert result == ["question"]
    assert events[0][0] == "input"
    assert events[0][1].endswith(".retrieve")
    assert events[1] == ("output", ["question"])


def test_trace_knowledge_async_extension_point_is_awaited(monkeypatch):
    calls = []

    async def custom_wrapper(func, *args, **kwargs):
        calls.append(func.__name__)
        return await func(*args, **kwargs)

    monkeypatch.setattr(trace, "_knowledge_wrapper_async", custom_wrapper)

    @trace.trace_knowledge
    async def retrieve():
        return "document"

    assert asyncio.run(retrieve()) == "document"
    assert calls == ["retrieve"]
