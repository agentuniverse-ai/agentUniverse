"""Offline concurrency and resource-lifetime contracts for Bedrock."""

import asyncio
import json
import socket
import sys
import threading
from contextvars import ContextVar
from io import BytesIO
from types import ModuleType
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.default.aws_bedrock_llm import AWSBedrockLLM

REQUEST_CONTEXT = ContextVar("bedrock_test_request", default=None)
RESPONSE = {"output": {"message": {"content": [{"text": "answer"}]}}}


class Gate:
    """Keep worker I/O pending until the event-loop-side assertion releases it."""

    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.finished = threading.Event()
        self.thread = None
        self.context = None

    def block(self):
        self.thread = threading.get_ident()
        self.context = REQUEST_CONTEXT.get()
        self.started.set()
        try:
            assert self.release.wait(5), "event loop did not release the blocking SDK operation"
        finally:
            self.finished.set()


async def wait_for_event(event):
    async def poll():
        while not event.is_set():
            await asyncio.sleep(0.001)

    await asyncio.wait_for(poll(), timeout=2)


class EventStream:
    def __init__(self, events=(), gate=None, error=None, close_gate=None):
        self.events = events
        self.gate = gate
        self.error = error
        self.close_gate = close_gate
        self.closed = threading.Event()
        self.close_count = 0
        self.threads = []
        self.contexts = []
        self.read_count = 0

    def __iter__(self):
        for event in self.events:
            self.threads.append(threading.get_ident())
            self.contexts.append(REQUEST_CONTEXT.get())
            self.read_count += 1
            if self.gate:
                self.gate.block()
            yield event
        if self.error:
            raise self.error

    def close(self):
        self.threads.append(threading.get_ident())
        if self.close_gate:
            self.close_gate.block()
        self.close_count += 1
        self.closed.set()


def delta(text):
    return {"contentBlockDelta": {"delta": {"text": text}}}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setitem(sys.modules, "boto3", None)
    blocked = Mock(side_effect=AssertionError("Bedrock async unit tests must not use the network"))
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(ApplicationConfigManager(), "_ApplicationConfigManager__app_configer", AppConfiger())
    yield
    for worker in threading.enumerate():
        if worker.name.startswith("bedrock-stream"):
            worker.join(timeout=2)
            assert not worker.is_alive(), "stream worker did not shut down"


@pytest.fixture
def llm():
    model = AWSBedrockLLM(model_name="amazon.nova-lite-v1:0")
    model._client = Mock()
    model._client.converse.return_value = RESPONSE
    return model


@pytest.fixture
def embedding():
    return AWSBedrockEmbedding(embedding_model_name="amazon.titan-embed-text-v2:0", client=Mock())


@pytest.mark.parametrize("kind", ["llm", "embedding", "embedding_body"])
@pytest.mark.parametrize("cancel", [False, True])
def test_nonstream_io_does_not_block_loop(llm, embedding, kind, cancel):
    gate = Gate()
    body = BytesIO(b'{"embedding": [0.1, 0.2]}')

    def invoke(**kwargs):
        gate.block()
        return RESPONSE if kind == "llm" else {"body": body}

    if kind == "embedding_body":
        body = Mock()

        def read():
            gate.block()
            return b'{"embedding": [0.1, 0.2]}'

        body.read.side_effect = read
        embedding.client.invoke_model.return_value = {"body": body}
    else:
        (llm._client.converse if kind == "llm" else embedding.client.invoke_model).side_effect = invoke

    async def run():
        token = REQUEST_CONTEXT.set("request-123")
        try:
            operation = llm.acall([]) if kind == "llm" else embedding.async_get_embeddings(["text"])
            task = asyncio.create_task(operation)
            try:
                await wait_for_event(gate.started)
                assert gate.thread != threading.get_ident()
                assert gate.context == "request-123"
                assert not task.done()
                if cancel:
                    task.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await asyncio.wait_for(task, 1)
                    assert not gate.release.is_set()
                else:
                    gate.release.set()
                    result = await asyncio.wait_for(task, 2)
                    assert (result.text if kind == "llm" else result) == ("answer" if kind == "llm" else [[0.1, 0.2]])
            finally:
                gate.release.set()
                await wait_for_event(gate.finished)
                await asyncio.gather(task, return_exceptions=True)
        finally:
            REQUEST_CONTEXT.reset(token)

    asyncio.run(run())
    if kind == "embedding":
        assert body.closed
    elif kind == "embedding_body":
        body.close.assert_called_once()


def test_two_llm_requests_can_progress_concurrently(llm):
    gates = [Gate(), Gate()]
    lock = threading.Lock()
    index = 0

    def converse(**kwargs):
        nonlocal index
        with lock:
            gate = gates[index]
            index += 1
        gate.block()
        return RESPONSE

    llm._client.converse.side_effect = converse

    async def run():
        tasks = [asyncio.create_task(llm._acall([])) for _ in gates]
        try:
            for gate in gates:
                await wait_for_event(gate.started)
            assert all(not task.done() for task in tasks)
        finally:
            for gate in gates:
                gate.release.set()
            await asyncio.gather(*tasks)

    asyncio.run(run())


@pytest.mark.parametrize("events", [[], [delta("a"), delta("b")], [delta("a"), {"messageStop": {}}, delta("ignored")]])
def test_stream_order_empty_stop_and_cleanup(llm, events):
    stream = EventStream(events)
    llm._client.converse_stream.return_value = {"stream": stream}

    async def run():
        token = REQUEST_CONTEXT.set("stream-context")
        try:
            chunks = [chunk async for chunk in await llm.acall([], streaming=True)]
            expected = [] if not events else (["a"] if "messageStop" in events[1] else ["a", "b"])
            assert [chunk.text for chunk in chunks] == expected
            assert [chunk.raw for chunk in chunks] == [delta(text) for text in expected]
            assert all(thread != threading.get_ident() for thread in stream.threads)
            assert len(set(stream.threads)) == 1
            assert all(context == "stream-context" for context in stream.contexts)
        finally:
            REQUEST_CONTEXT.reset(token)

    asyncio.run(run())
    assert stream.close_count == 1


@pytest.mark.parametrize("phase", ["open", "read"])
@pytest.mark.parametrize("cancel", [False, True])
def test_stream_pending_io_and_cancellation(llm, phase, cancel):
    gate = Gate()
    stream = EventStream([delta("a")], gate=gate if phase == "read" else None)

    def open_stream(**kwargs):
        if phase == "open":
            gate.block()
        return {"stream": stream}

    llm._client.converse_stream.side_effect = open_stream

    async def run():
        iterator = await llm.acall([], streaming=True)
        llm._client.converse_stream.assert_not_called()
        task = asyncio.create_task(anext(iterator))
        try:
            await wait_for_event(gate.started)
            assert gate.thread != threading.get_ident()
            assert not task.done()
            if cancel:
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 1)
                assert stream.close_count == 0
                assert not gate.release.is_set()
            else:
                gate.release.set()
                assert (await asyncio.wait_for(task, 2)).text == "a"
        finally:
            gate.release.set()
            await asyncio.gather(task, return_exceptions=True)
            await iterator.aclose()
            await wait_for_event(stream.closed)
        assert stream.close_count == 1

    asyncio.run(run())


@pytest.mark.parametrize("started", [False, True])
def test_public_stream_early_close_without_prefetch(llm, started):
    stream = EventStream([delta("a"), delta("b")])
    llm._client.converse_stream.return_value = {"stream": stream}

    async def run():
        iterator = await llm.acall([], streaming=True)
        if started:
            assert (await anext(iterator)).text == "a"
            await asyncio.sleep(0.01)
            assert stream.read_count == 1
        await iterator.aclose()
        if started:
            assert stream.close_count == 1
        else:
            llm._client.converse_stream.assert_not_called()

    asyncio.run(run())


def test_stream_close_does_not_block_event_loop(llm):
    gate = Gate()
    stream = EventStream([delta("a")], close_gate=gate)
    llm._client.converse_stream.return_value = {"stream": stream}

    async def run():
        iterator = await llm.acall([], streaming=True)
        await anext(iterator)
        close_task = asyncio.create_task(iterator.aclose())
        try:
            await wait_for_event(gate.started)
            assert not close_task.done()
            assert gate.thread != threading.get_ident()
        finally:
            gate.release.set()
            await close_task

    asyncio.run(run())
    assert stream.close_count == 1


@pytest.mark.parametrize("phase", ["open", "read", "malformed"])
def test_stream_errors_are_propagated_and_closed(llm, phase):
    stream = EventStream(error=RuntimeError("read failed"))
    if phase == "open":
        llm._client.converse_stream.side_effect = RuntimeError("open failed")
    elif phase == "malformed":
        stream = EventStream([{"contentBlockDelta": {}}])
    llm._client.converse_stream.return_value = {"stream": stream}

    async def run():
        iterator = await llm.acall([], streaming=True)
        with pytest.raises(RuntimeError, match="Error calling AWS Bedrock|Error in streaming response"):
            await anext(iterator)

    asyncio.run(run())
    assert stream.close_count == (0 if phase == "open" else 1)


@pytest.mark.parametrize("started", [False, True])
def test_synchronous_stream_can_be_closed_before_exhaustion(llm, started):
    stream = EventStream([delta("a")])
    llm._client.converse_stream.return_value = {"stream": stream}
    iterator = llm._call([], streaming=True)
    if started:
        assert next(iterator).text == "a"
    iterator.close()
    iterator.close()
    assert list(iterator) == []
    assert stream.close_count == 1


@pytest.mark.parametrize("kind", ["llm", "embedding"])
def test_nonstream_errors_remain_visible(llm, embedding, kind):
    method = llm._client.converse if kind == "llm" else embedding.client.invoke_model
    method.side_effect = RuntimeError("AWS unavailable")
    operation = llm._acall([]) if kind == "llm" else embedding.async_get_embeddings(["text"])
    with pytest.raises(Exception, match="AWS unavailable"):
        asyncio.run(operation)


def test_embedding_parse_error_still_closes_body(embedding):
    body = BytesIO(b"not json")
    embedding.client.invoke_model.return_value = {"body": body}
    with pytest.raises(Exception, match="Failed to get embedding"):
        asyncio.run(embedding.async_get_embeddings(["text"]))
    assert body.closed


@pytest.mark.parametrize("component", [AWSBedrockLLM, AWSBedrockEmbedding])
def test_concurrent_lazy_client_creation_is_serialized(component, monkeypatch):
    gate = Gate()
    sdk = ModuleType("boto3")
    session = Mock()

    def new_session(**kwargs):
        gate.block()
        return session

    sdk.Session = Mock(side_effect=new_session)
    sdk.client = Mock(side_effect=AssertionError("Do not use boto3's shared default session"))
    config = ModuleType("botocore.config")
    config.Config = Mock()
    monkeypatch.setitem(sys.modules, "boto3", sdk)
    monkeypatch.setitem(sys.modules, "botocore", ModuleType("botocore"))
    monkeypatch.setitem(sys.modules, "botocore.config", config)
    model = component(aws_access_key_id=None, aws_secret_access_key=None)
    initialize = model._get_client if component is AWSBedrockLLM else model._initialize_client

    async def run():
        tasks = [asyncio.create_task(asyncio.to_thread(initialize)) for _ in range(2)]
        try:
            await wait_for_event(gate.started)
            assert not any(task.done() for task in tasks)
        finally:
            gate.release.set()
            await asyncio.gather(*tasks)

    asyncio.run(run())
    sdk.Session.assert_called_once()
    session.client.assert_called_once()


def test_stream_mode_is_captured_before_lazy_open(llm):
    stream = EventStream([delta("a")])
    llm._client.converse_stream.return_value = {"stream": stream}

    async def run():
        llm.streaming = True
        iterator = await llm._acall([])
        llm.streaming = False
        assert [chunk.text async for chunk in iterator] == ["a"]

    asyncio.run(run())


def test_cancellation_during_close_does_not_cancel_cleanup(llm):
    gate = Gate()
    stream = EventStream([delta("a")], close_gate=gate)
    llm._client.converse_stream.return_value = {"stream": stream}

    async def run():
        iterator = await llm.acall([], streaming=True)
        await anext(iterator)
        task = asyncio.create_task(iterator.aclose())
        try:
            await wait_for_event(gate.started)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 1)
            assert not stream.closed.is_set()
        finally:
            gate.release.set()
            await wait_for_event(stream.closed)

    asyncio.run(run())
    assert stream.close_count == 1


def test_async_embedding_preserves_batch_order_and_kwargs(embedding):
    embedding.embedding_model_name = "cohere.embed-multilingual-v3"
    bodies = [BytesIO(b'{"embeddings": [[0.1]]}'), BytesIO(b'{"embeddings": [[0.2]]}')]
    embedding.client.invoke_model.side_effect = [{"body": body} for body in bodies]
    assert asyncio.run(embedding.async_get_embeddings(["first", "second"], input_type="search_query")) == [[0.1], [0.2]]
    requests = [json.loads(call.kwargs["body"]) for call in embedding.client.invoke_model.call_args_list]
    assert requests == [
        {"texts": ["first"], "input_type": "search_query"},
        {"texts": ["second"], "input_type": "search_query"},
    ]
    assert all(body.closed for body in bodies)


def test_missing_model_error_is_preserved(embedding):
    embedding.embedding_model_name = None
    with pytest.raises(ValueError, match="embedding_model_name"):
        asyncio.run(embedding.async_get_embeddings(["test"]))
    embedding.client.invoke_model.assert_not_called()
