"""Persistence is optional; stream failure state is not."""
import asyncio
import json
from concurrent.futures import Future
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import Flask

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
@pytest.mark.parametrize("end_signal", [EOF_SIGNAL, None])
def test_threaded_stream_failure(method, saved, stop_early, end_signal, persistence):
    task = RequestTask(lambda: None, saved=saved)
    task.thread = Future()
    task.thread.set_exception(ValueError("provider failed"))
    task.queue.put_nowait(end_signal)
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
@pytest.mark.parametrize("end_signal", [EOF_SIGNAL, None])
def test_async_stream_failure(saved, stop_early, end_signal, persistence):
    async def exercise():
        task = RequestTask(lambda: None, saved=saved)
        task.async_task = asyncio.get_running_loop().create_future()
        task.async_task.set_exception(RuntimeError("provider failed"))
        task.async_queue.put_nowait(end_signal)
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


@pytest.mark.parametrize("method", ["stream_run", "user_stream_run"])
@pytest.mark.parametrize("saved", [False, True])
@pytest.mark.parametrize("stop_early", [False, True])
def test_public_thread_stream_partial_output_then_failure(
        method, saved, stop_early, persistence):
    """Exercise Flask context copying and the actual worker thread."""
    chunk = '{"text": "partial answer"}'

    def producer(output_stream):
        try:
            output_stream.put_nowait(chunk)
            raise ValueError("provider failed")
        finally:
            output_stream.put_nowait(EOF_SIGNAL)

    task = RequestTask(producer, saved=saved)
    with Flask(__name__).test_request_context("/stream"):
        stream = getattr(task, method)()
    try:
        first = next(stream)
        payload = json.loads(first.removeprefix("data:").strip())
        assert payload == ({"process": chunk} if method == "stream_run"
                           else {"text": "partial answer"})
        assert task.request_state() == "running"
        assert_failure(task, next(stream), saved, persistence)
        if not stop_early:
            assert list(stream) == []
    finally:
        stream.close()
        task.thread.join(timeout=5)
    assert not task.thread.is_alive()
    assert task.request_state() == "fail"


@pytest.mark.parametrize("saved", [False, True])
@pytest.mark.parametrize("stop_early", [False, True])
def test_public_async_stream_partial_output_then_failure(
        saved, stop_early, persistence):
    """Exercise async_stream_run with a real scheduled producer coroutine."""
    async def producer(output_stream):
        try:
            await output_stream.put("partial answer")
            raise RuntimeError("provider failed")
        finally:
            await output_stream.put(EOF_SIGNAL)

    async def exercise():
        task = RequestTask(producer, saved=saved)
        stream = task.async_stream_run()
        try:
            first = await asyncio.wait_for(stream.__anext__(), timeout=5)
            assert json.loads(first.removeprefix("data:").strip()) == {
                "process": "partial answer"}
            assert task.request_state() == "running"
            event = await asyncio.wait_for(stream.__anext__(), timeout=5)
            assert_failure(task, event, saved, persistence)
            if not stop_early:
                with pytest.raises(StopAsyncIteration):
                    await asyncio.wait_for(stream.__anext__(), timeout=5)
        finally:
            await stream.aclose()
            if task.async_task is not None:
                if not task.async_task.done():
                    task.async_task.cancel()
                await asyncio.gather(task.async_task, return_exceptions=True)
        assert task.async_task.done()
        assert task.request_state() == "fail"

    asyncio.run(exercise())
