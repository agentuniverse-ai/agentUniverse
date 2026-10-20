"""Exercise endpoint selection with real SDK requests and offline transports."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from threading import Barrier

import httpx
from openai import OpenAI, AsyncOpenAI
from openai.resources.chat.completions import AsyncCompletions
import pytest

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel


BASE = 'https://configured.invalid/v1'
OVERRIDE = 'https://override.invalid/v1'
OMITTED = object()
OPTIONS = [OMITTED, None, '', OVERRIDE]


def transport_for(seen):
    def handle(request):
        body = json.loads(request.content)
        seen.append((request, body))
        common = {'id': 'offline', 'created': 1, 'model': 'local-model'}
        if body.get('stream'):
            chunk = dict(common, object='chat.completion.chunk', choices=[
                {'index': 0, 'delta': {'role': 'assistant', 'content': request.url.host},
                 'finish_reason': None}])
            return httpx.Response(200, headers={'content-type': 'text/event-stream'},
                content=('data: ' + json.dumps(chunk) + '\n\ndata: [DONE]\n\n').encode())
        return httpx.Response(200, json=dict(common, object='chat.completion', choices=[
            {'index': 0, 'message': {'role': 'assistant', 'content': request.url.host},
             'finish_reason': 'stop'}]))
    return httpx.MockTransport(handle)


def channel_for(client=None, async_client=None):
    channel = LLMChannel(client=client, async_client=async_client,
                         channel_api_base=BASE, channel_model_name='local-model')
    channel.channel_model_config = {'streaming': False, 'temperature': 0.7,
                                    'max_tokens': 32}
    return channel


def sync_call(channel, endpoint, streaming=False, content='hello'):
    options = {} if endpoint is OMITTED else {'api_base': endpoint}
    result = channel._call([{'role': 'user', 'content': content}],
                           streaming=streaming, **options)
    return ''.join(chunk.text for chunk in result) if streaming else result.text


async def async_call(channel, endpoint, streaming=False, content='hello'):
    options = {} if endpoint is OMITTED else {'api_base': endpoint}
    result = await channel._acall([{'role': 'user', 'content': content}],
                                  streaming=streaming, **options)
    if streaming:
        return ''.join([chunk.text async for chunk in result])
    return result.text


def check_request(seen, endpoint, streaming):
    (request, body), = seen
    expected = OVERRIDE if endpoint == OVERRIDE else BASE
    assert str(request.url).startswith(expected + '/chat/completions?')
    assert request.url.params['fixture'] == 'kept'
    assert request.headers['x-offline-fixture'] == 'kept'
    assert body['stream'] is streaming
    assert body['model'] == 'local-model'
    assert body['messages'] == [{'role': 'user', 'content': 'hello'}]
    assert 'api_base' not in body


@pytest.mark.parametrize('endpoint', OPTIONS, ids=['omitted', 'none', 'empty', 'override'])
@pytest.mark.parametrize('streaming', [False, True], ids=['completion', 'stream'])
def test_sync_endpoint_options_do_not_mutate_the_cached_client(endpoint, streaming):
    seen = []
    with httpx.Client(transport=transport_for(seen)) as http_client:
        with OpenAI(api_key='offline-test', base_url=BASE, http_client=http_client,
                    default_headers={'x-offline-fixture': 'kept'},
                    default_query={'fixture': 'kept'}, max_retries=0) as sdk:
            channel = channel_for(client=sdk)
            original = sdk.base_url
            result = sync_call(channel, endpoint, streaming)
            assert result == ('override.invalid' if endpoint == OVERRIDE else 'configured.invalid')
            assert channel.client is sdk
            assert sdk.base_url == original
            assert not http_client.is_closed
            check_request(seen, endpoint, streaming)


@pytest.mark.parametrize('endpoint', OPTIONS, ids=['omitted', 'none', 'empty', 'override'])
@pytest.mark.parametrize('streaming', [False, True], ids=['completion', 'stream'])
def test_async_endpoint_options_do_not_mutate_the_cached_client(endpoint, streaming):
    async def run():
        seen = []
        async with httpx.AsyncClient(transport=transport_for(seen)) as http_client:
            async with AsyncOpenAI(api_key='offline-test', base_url=BASE, http_client=http_client,
                    default_headers={'x-offline-fixture': 'kept'},
                    default_query={'fixture': 'kept'}, max_retries=0) as sdk:
                channel = channel_for(async_client=sdk)
                original = sdk.base_url
                result = await async_call(channel, endpoint, streaming)
                assert result == ('override.invalid' if endpoint == OVERRIDE else 'configured.invalid')
                assert channel.async_client is sdk
                assert sdk.base_url == original
                assert not http_client.is_closed
                check_request(seen, endpoint, streaming)
    asyncio.run(run())


class CoordinatedOpenAI(OpenAI):
    """Pause actual shared-client URL mutations to expose the thread race."""
    route_gate = None

    @property
    def base_url(self):
        return OpenAI.base_url.fget(self)

    @base_url.setter
    def base_url(self, value):
        OpenAI.base_url.fset(self, value)
        if self.route_gate is not None:
            self.route_gate.wait(timeout=5)


def test_concurrent_sync_calls_use_their_own_endpoints():
    seen = []
    with httpx.Client(transport=transport_for(seen)) as http_client:
        with CoordinatedOpenAI(api_key='offline-test', base_url=BASE,
                                http_client=http_client, max_retries=0) as sdk:
            sdk.route_gate = Barrier(2)
            channel = channel_for(client=sdk)
            with ThreadPoolExecutor(max_workers=2) as executor:
                first = executor.submit(sync_call, channel, 'https://alpha.invalid/v1', False, 'alpha')
                second = executor.submit(sync_call, channel, 'https://beta.invalid/v1', False, 'beta')
                assert first.result(timeout=10) == 'alpha.invalid'
                assert second.result(timeout=10) == 'beta.invalid'
            assert len(seen) == 2
            assert sdk.base_url == httpx.URL(BASE + '/')


class AsyncGate:
    def __init__(self):
        self.arrivals = 0
        self.ready = asyncio.Event()

    async def wait(self):
        self.arrivals += 1
        if self.arrivals == 2:
            self.ready.set()
        await asyncio.wait_for(self.ready.wait(), timeout=5)


class CoordinatedAsyncCompletions(AsyncCompletions):
    """Delay then delegate to the real SDK serializer, transport and parser."""
    def __init__(self, client, gate):
        super().__init__(client)
        self.gate = gate

    async def create(self, *args, **kwargs):
        await self.gate.wait()
        return await super().create(*args, **kwargs)


def test_concurrent_async_calls_use_their_own_endpoints():
    async def run():
        seen = []
        async with httpx.AsyncClient(transport=transport_for(seen)) as http_client:
            async with AsyncOpenAI(api_key='offline-test', base_url=BASE,
                                    http_client=http_client, max_retries=0) as sdk:
                sdk.chat.completions = CoordinatedAsyncCompletions(sdk, AsyncGate())
                channel = channel_for(async_client=sdk)
                results = await asyncio.gather(
                    async_call(channel, 'https://alpha.invalid/v1', content='alpha'),
                    async_call(channel, 'https://beta.invalid/v1', content='beta'))
                assert results == ['alpha.invalid', 'beta.invalid']
                assert len(seen) == 2
                assert sdk.base_url == httpx.URL(BASE + '/')
    asyncio.run(run())
