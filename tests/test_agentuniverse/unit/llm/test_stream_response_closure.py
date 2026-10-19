"""Real OpenAI/httpx response ownership at a controlled transport boundary."""
import asyncio
import json
import time

import httpx
from openai import APIError, AsyncOpenAI, OpenAI
from opentelemetry import context
from opentelemetry.metrics import NoOpMeterProvider
from opentelemetry.sdk.trace import TracerProvider
import pytest

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.tracing.otel.instrumentation.llm.consts import MetricNames
from agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor import (
    LLMMetricsRecorder, LLMSpanManager, StreamingResultProcessor,
)
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.openai_llm import OpenAILLM
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

ADAPTERS = (LLMChannel, OpenAILLM, OpenAIStyleLLM)
CHUNK = ('data: ' + json.dumps({
    'id': 'fixture', 'object': 'chat.completion.chunk', 'created': 0,
    'model': 'fixture', 'choices': [{
        'index': 0, 'delta': {'role': 'assistant', 'content': 'hello'},
        'finish_reason': None,
    }],
}) + '\n\n').encode()
DONE = b'data: [DONE]\n\n'
ERROR = b'data: {"error":{"message":"fixture failure","type":"server_error"}}\n\n'


class Body(httpx.SyncByteStream):
    def __init__(self, mode):
        self.mode = mode
        self.closes = 0

    def __iter__(self):
        yield CHUNK
        yield ERROR if self.mode == 'provider_error' else DONE

    def close(self):
        self.closes += 1


class AsyncBody(httpx.AsyncByteStream):
    def __init__(self, mode):
        self.mode = mode
        self.closes = 0
        self.entered = asyncio.Event()
        self.release = asyncio.Event()

    async def __aiter__(self):
        yield CHUNK
        if self.mode == 'cancel':
            self.entered.set()
            await self.release.wait()
        yield ERROR if self.mode == 'provider_error' else DONE

    async def aclose(self):
        self.closes += 1


@pytest.fixture(autouse=True)
def application_config():
    manager = ApplicationConfigManager()
    try:
        previous = manager.app_configer
    except ValueError:
        previous = None
    manager.app_configer = AppConfiger()
    try:
        yield
    finally:
        manager.app_configer = previous


def processor():
    provider = TracerProvider()
    manager = LLMSpanManager(provider.get_tracer(__name__), 'stream-fixture')
    manager.start_span()
    manager.defer_cleanup()
    context.detach(manager.token)
    meter = NoOpMeterProvider().get_meter(__name__)
    recorder = LLMMetricsRecorder({
        MetricNames.LLM_FIRST_TOKEN_DURATION: meter.create_histogram('fixture.first'),
        MetricNames.LLM_CALL_DURATION: meter.create_histogram('fixture.duration'),
        MetricNames.LLM_ERRORS_TOTAL: meter.create_counter('fixture.errors'),
    })
    result = StreamingResultProcessor('fixture', {}, None, time.time(), manager, {}, recorder)

    def cleanup():
        if manager.span is not None:
            manager.cleanup()
        provider.shutdown()

    return result, cleanup


def wrap_sync(output, layer):
    if layer == 'trace':
        @trace_llm
        def completion():
            return output
        return completion(), lambda: None
    if layer == 'otel':
        instrumentation, cleanup = processor()
        return instrumentation.process_sync_stream(output), cleanup
    return output, lambda: None


async def wrap_async(output, layer):
    if layer == 'trace':
        @trace_llm
        async def completion():
            return output
        return await completion(), lambda: None
    if layer == 'otel':
        instrumentation, cleanup = processor()
        return instrumentation.process_async_stream(output), cleanup
    return output, lambda: None


CASES = [('adapter', mode) for mode in ('unstarted', 'partial', 'drained', 'provider_error')]
CASES += [(layer, mode) for layer in ('trace', 'otel') for mode in ('unstarted', 'partial')]


@pytest.mark.parametrize('adapter', ADAPTERS)
@pytest.mark.parametrize('layer,mode', CASES)
def test_sync_response_closure(adapter, layer, mode):
    body = Body(mode)
    transport = httpx.MockTransport(lambda request: httpx.Response(
        200, headers={'content-type': 'text/event-stream'}, stream=body,
    ))
    http_client = httpx.Client(transport=transport)
    with OpenAI(api_key='offline-test', http_client=http_client) as sdk:
        raw = sdk.chat.completions.create(model='fixture', messages=[], stream=True)
        output, cleanup = wrap_sync(adapter().generate_stream_result(raw), layer)
        try:
            if mode in ('partial', 'provider_error'):
                assert next(output).text == 'hello'
            if mode == 'provider_error':
                with pytest.raises(APIError, match='fixture failure'):
                    list(output)
            elif mode == 'drained':
                assert [item.text for item in output] == ['hello']
            if mode in ('provider_error', 'drained'):
                assert raw.response.is_closed
                assert body.closes == 1
            output.close()
            output.close()
            assert raw.response.is_closed
            assert body.closes == 1
            assert not http_client.is_closed
            assert list(output) == []
        finally:
            raw.close()
            cleanup()


@pytest.mark.parametrize('adapter', ADAPTERS)
@pytest.mark.parametrize('layer,mode', CASES)
def test_async_response_closure(adapter, layer, mode):
    async def check():
        body = AsyncBody(mode)

        async def respond(request):
            return httpx.Response(200, headers={'content-type': 'text/event-stream'}, stream=body)

        http_client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        async with AsyncOpenAI(api_key='offline-test', http_client=http_client) as sdk:
            raw = await sdk.chat.completions.create(model='fixture', messages=[], stream=True)
            output, cleanup = await wrap_async(adapter().agenerate_stream_result(raw), layer)
            try:
                if mode in ('partial', 'provider_error'):
                    assert (await anext(output)).text == 'hello'
                if mode == 'provider_error':
                    with pytest.raises(APIError, match='fixture failure'):
                        [item async for item in output]
                elif mode == 'drained':
                    assert [item.text async for item in output] == ['hello']
                if mode in ('provider_error', 'drained'):
                    assert raw.response.is_closed
                    assert body.closes == 1
                await output.aclose()
                await output.aclose()
                assert raw.response.is_closed
                assert body.closes == 1
                assert not http_client.is_closed
                assert [item async for item in output] == []
            finally:
                await raw.close()
                cleanup()

    asyncio.run(check())


@pytest.mark.parametrize('adapter', ADAPTERS)
def test_async_cancellation_closes_response(adapter):
    async def check():
        body = AsyncBody('cancel')

        async def respond(request):
            return httpx.Response(200, headers={'content-type': 'text/event-stream'}, stream=body)

        async with AsyncOpenAI(api_key='offline-test', http_client=httpx.AsyncClient(
                transport=httpx.MockTransport(respond))) as sdk:
            raw = await sdk.chat.completions.create(model='fixture', messages=[], stream=True)
            output = adapter().agenerate_stream_result(raw)
            pending = None
            try:
                assert (await anext(output)).text == 'hello'

                async def read_next():
                    return await anext(output)

                pending = asyncio.create_task(read_next())
                await asyncio.wait_for(body.entered.wait(), timeout=2)
                pending.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await pending
                assert raw.response.is_closed
                assert body.closes == 1
            finally:
                if pending is not None and not pending.done():
                    pending.cancel()
                    try:
                        await pending
                    except asyncio.CancelledError:
                        pass
                await output.aclose()
                await raw.close()

    asyncio.run(check())
