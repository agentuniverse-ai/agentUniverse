"""Persistence is optional; stream failure state is not."""
import asyncio
import json
from concurrent.futures import Future
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from agentuniverse.agent_serve.web.request_task import EOF_SIGNAL, RequestTask


@pytest.fixture
def persistence(monkeypatch):
    library = Mock(update_interval=0)
    factory = Mock(return_value=library)
    prefix = "agentuniverse.agent_serve.web.request_task."
    monkeypatch.setattr(prefix + "RequestLibrary", factory)
    monkeypatch.setattr(prefix + "AuTraceManager", lambda: SimpleNamespace(
        get_trace_id=lambda: "failure-test"))
    return factory, library


def assert_failure(task, event, saved, persistence):
    assert json.loads(event.removeprefix("data:").strip()) == {
        "error": {"error_msg": "provider failed"}}
    assert task.request_state() == "fail"
    assert task.__request_do__.result == {"result": {"error_msg": "provider failed"}}
    factory, library = persistence
    if saved:
        library.add_request.assert_called_once_with(task.__request_do__)
        library.update_request.assert_called_once_with(task.__request_do__)
    else:
        factory.assert_not_called()


@pytest.mark.parametrize("method", ["receive_steps", "user_receive_steps"])
@pytest.mark.parametrize("saved", [False, True])
@pytest.mark.parametrize("stop_early", [False, True])
def test_threaded_stream_failure(method, saved, stop_early, persistence):
    task = RequestTask(lambda: None, saved=saved)
    task.thread = Future()
    task.thread.set_exception(ValueError("provider failed"))
    task.queue.put_nowait(EOF_SIGNAL)
    stream = getattr(task, method)()
    try:
        event = next(stream)
        # Check while suspended at the error event, not only after exhausting it.
        assert_failure(task, event, saved, persistence)
        if not stop_early:
            assert list(stream) == []
    finally:
        stream.close()


@pytest.mark.parametrize("saved", [False, True])
@pytest.mark.parametrize("stop_early", [False, True])
def test_async_stream_failure(saved, stop_early, persistence):
    async def exercise():
        task = RequestTask(lambda: None, saved=saved)
        task.async_task = asyncio.get_running_loop().create_future()
        task.async_task.set_exception(RuntimeError("provider failed"))
        task.async_queue.put_nowait(EOF_SIGNAL)
        stream = task.async_receive_steps()
        try:
            event = await stream.__anext__()
            assert_failure(task, event, saved, persistence)
            if not stop_early:
                assert [item async for item in stream] == []
        finally:
            await stream.aclose()
    asyncio.run(exercise())


@pytest.mark.parametrize("method", ["receive_steps", "user_receive_steps"])
@pytest.mark.parametrize("saved", [False, True])
def test_successful_threaded_stream_unchanged(method, saved, persistence):
    task = RequestTask(lambda: None, saved=saved)
    task.thread = Future()
    task.thread.set_result({"answer": "ok"})
    task.queue.put_nowait(EOF_SIGNAL)
    events = list(getattr(task, method)())
    assert task.request_state() == "finished"
    assert task.__request_do__.result == {"result": {"answer": "ok"}}
    if method == "receive_steps":
        assert json.loads(events[0].removeprefix("data:").strip()) == {
            "result": {"answer": "ok"}}
    else:
        assert events == []
    if not saved:
        persistence[0].assert_not_called()
