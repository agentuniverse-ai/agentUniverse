"""Owned Claude transports must finish with their request, not another call."""
import asyncio

import anthropic
import httpx
import pytest

from agentuniverse.llm.default.claude_llm import ClaudeLLM

STREAM_ERROR = "interrupted stream"
MODEL = "claude-3-haiku-20240307"
MESSAGES = [{"role": "user", "content": "hello"}]
SSE = (b'event: content_block_delta\ndata: {"type":"content_block_delta","index":0,'
       b'"delta":{"type":"text_delta","text":"hello"}}\n\n')


class SyncBody(httpx.SyncByteStream):
    def __init__(self, fail=False):
        self.closed = False
        self.fail = fail

    def __iter__(self):
        yield SSE
        if self.fail:
            raise httpx.ReadError(STREAM_ERROR)
        yield b'event: message_stop\ndata: {"type":"message_stop"}\n\n'

    def close(self):
        self.closed = True


class AsyncBody(httpx.AsyncByteStream):
    def __init__(self, fail=False, block=False):
        self.closed = False
        self.fail = fail
        self.block = block
        self.waiting = asyncio.Event()

    async def __aiter__(self):
        yield SSE
        if self.fail:
            raise httpx.ReadError(STREAM_ERROR)
        if self.block:
            self.waiting.set()
            await asyncio.Event().wait()
        yield b'event: message_stop\ndata: {"type":"message_stop"}\n\n'

    async def aclose(self):
        self.closed = True


def response(request, body=None):
    if body is not None:
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body)
    return httpx.Response(400, json={"type": "error", "error": {
        "type": "invalid_request_error", "message": "invalid request"}})


def sync_sdk(body=None):
    transport = httpx.Client(transport=httpx.MockTransport(lambda req: response(req, body)))
    return anthropic.Anthropic(api_key="offline", http_client=transport, max_retries=0), transport


def async_sdk(body=None):
    transport = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: response(req, body)))
    return anthropic.AsyncAnthropic(api_key="offline", http_client=transport, max_retries=0), transport


@pytest.mark.parametrize("streaming", [False, True])
def test_sync_request_failure_closes_client(monkeypatch, streaming):
    sdk, transport = sync_sdk()
    monkeypatch.setattr(ClaudeLLM, "_new_client", lambda self: sdk)
    llm = ClaudeLLM(model_name=MODEL)
    try:
        with pytest.raises(anthropic.BadRequestError):
            result = llm._call(MESSAGES, streaming=streaming)
            if streaming:
                next(result)
        assert transport.is_closed
    finally:
        sdk.close()


@pytest.mark.parametrize("streaming", [False, True])
def test_async_request_failure_closes_client(monkeypatch, streaming):
    async def run():
        sdk, transport = async_sdk()
        monkeypatch.setattr(ClaudeLLM, "_new_async_client", lambda self: sdk)
        llm = ClaudeLLM(model_name=MODEL)
        try:
            with pytest.raises(anthropic.BadRequestError):
                result = await llm._acall(MESSAGES, streaming=streaming)
                if streaming:
                    await anext(result)
            assert transport.is_closed
        finally:
            await sdk.close()
    asyncio.run(run())


@pytest.mark.parametrize("finish", ["close", "error", "exhaust"])
def test_sync_stream_closes_response_and_client(monkeypatch, finish):
    body = SyncBody(fail=finish == "error")
    sdk, transport = sync_sdk(body)
    monkeypatch.setattr(ClaudeLLM, "_new_client", lambda self: sdk)
    result = ClaudeLLM(model_name=MODEL)._call(MESSAGES, streaming=True)
    try:
        assert next(result).text == "hello"
        if finish == "close":
            result.close()
        elif finish == "error":
            with pytest.raises(httpx.ReadError, match="interrupted stream"):
                next(result)
        else:
            assert list(result) == []
        assert body.closed
        assert transport.is_closed
    finally:
        result.close()
        sdk.close()


@pytest.mark.parametrize("finish", ["close", "error", "exhaust", "cancel"])
def test_async_stream_closes_response_and_client(monkeypatch, finish):
    async def run():
        body = AsyncBody(fail=finish == "error", block=finish == "cancel")
        sdk, transport = async_sdk(body)
        monkeypatch.setattr(ClaudeLLM, "_new_async_client", lambda self: sdk)
        result = await ClaudeLLM(model_name=MODEL)._acall(MESSAGES, streaming=True)
        try:
            assert (await anext(result)).text == "hello"
            if finish == "close":
                await result.aclose()
            elif finish == "error":
                with pytest.raises(httpx.ReadError, match="interrupted stream"):
                    await anext(result)
            elif finish == "cancel":
                task = asyncio.create_task(anext(result))
                await asyncio.wait_for(body.waiting.wait(), 2)
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
            else:
                assert [chunk async for chunk in result] == []
            assert body.closed
            assert transport.is_closed
        finally:
            await result.aclose()
            await sdk.close()
    asyncio.run(run())


def test_overlapping_sync_streams_close_only_their_own_client(monkeypatch):
    first, t1 = sync_sdk(SyncBody())
    second, t2 = sync_sdk(SyncBody())
    clients = iter([first, second])
    monkeypatch.setattr(ClaudeLLM, "_new_client", lambda self: next(clients))
    llm = ClaudeLLM(model_name=MODEL)
    a = llm._call(MESSAGES, streaming=True)
    b = None
    try:
        assert next(a).text == "hello"
        b = llm._call(MESSAGES, streaming=True)
        assert next(b).text == "hello"
        assert list(a) == []
        assert t1.is_closed
        assert not t2.is_closed
        assert list(b) == []
        assert t2.is_closed
    finally:
        a.close()
        if b is not None:
            b.close()
        first.close()
        second.close()


def test_overlapping_async_streams_close_only_their_own_client(monkeypatch):
    async def run():
        first, t1 = async_sdk(AsyncBody())
        second, t2 = async_sdk(AsyncBody())
        clients = iter([first, second])
        monkeypatch.setattr(ClaudeLLM, "_new_async_client", lambda self: next(clients))
        llm = ClaudeLLM(model_name=MODEL)
        a = await llm._acall(MESSAGES, streaming=True)
        b = None
        try:
            assert (await anext(a)).text == "hello"
            b = await llm._acall(MESSAGES, streaming=True)
            assert (await anext(b)).text == "hello"
            assert [chunk async for chunk in a] == []
            assert t1.is_closed
            assert not t2.is_closed
            assert [chunk async for chunk in b] == []
            assert t2.is_closed
        finally:
            await a.aclose()
            if b is not None:
                await b.aclose()
            await first.close()
            await second.close()
    asyncio.run(run())


def test_unstarted_sync_stream_acquires_no_client(monkeypatch):
    created = []
    monkeypatch.setattr(ClaudeLLM, "_new_client", lambda self: created.append(True))
    result = ClaudeLLM(model_name=MODEL)._call(MESSAGES, streaming=True)
    result.close()
    assert created == []


def test_unstarted_async_stream_acquires_no_client(monkeypatch):
    async def run():
        created = []
        monkeypatch.setattr(ClaudeLLM, "_new_async_client", lambda self: created.append(True))
        result = await ClaudeLLM(model_name=MODEL)._acall(MESSAGES, streaming=True)
        await result.aclose()
        assert created == []
    asyncio.run(run())


@pytest.mark.parametrize("streaming", [False, True])
def test_cancellation_before_response_closes_client(monkeypatch, streaming):
    async def run():
        waiting = asyncio.Event()

        async def handler(request):
            waiting.set()
            await asyncio.Event().wait()

        transport = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        sdk = anthropic.AsyncAnthropic(api_key="offline", http_client=transport, max_retries=0)
        monkeypatch.setattr(ClaudeLLM, "_new_async_client", lambda self: sdk)
        llm = ClaudeLLM(model_name=MODEL)

        async def invoke():
            result = await llm._acall(MESSAGES, streaming=streaming)
            if streaming:
                await anext(result)

        task = asyncio.create_task(invoke())
        try:
            await asyncio.wait_for(waiting.wait(), 2)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert transport.is_closed
        finally:
            task.cancel()
            await sdk.close()
    asyncio.run(run())
