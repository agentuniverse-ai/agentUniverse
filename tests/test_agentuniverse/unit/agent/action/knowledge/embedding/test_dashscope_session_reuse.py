"""A multi-batch embedding operation should share one scoped HTTP session."""
import asyncio
import json
from unittest.mock import patch
import pytest
from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding import DashscopeEmbedding


class Session:
    def __init__(self, fail_batch=None):
        self.requests = []
        self.closed = False
        self.fail_batch = fail_batch

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.closed = True

    async def post(self, **kwargs):
        payload = json.loads(kwargs['data'])
        self.requests.append(payload)
        if len(self.requests) == self.fail_batch:
            raise RuntimeError('network failure')
        return Response(payload)


class Response:
    def __init__(self, payload):
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def json(self):
        return {'output': {'embeddings': [{'embedding': [float(text)]} for text in self.payload['input']['texts']]}}


@pytest.mark.parametrize('size', [1, 25, 26, 51])
def test_one_session_per_operation_and_unchanged_requests(size):
    sessions = []
    def factory():
        session = Session()
        sessions.append(session)
        return session
    embedding = DashscopeEmbedding(dashscope_api_key='test', embedding_model_name='text-embedding-v3', embedding_dims=512)
    with patch('agentuniverse.agent.action.knowledge.embedding.dashscope_embedding.aiohttp.ClientSession', side_effect=factory):
        result = asyncio.run(embedding.async_get_embeddings([str(i) for i in range(size)], text_type='query'))
    assert result == [[float(i)] for i in range(size)]
    assert len(sessions) == 1
    assert sessions[0].closed
    assert [len(p['input']['texts']) for p in sessions[0].requests] == [min(25, size - i) for i in range(0, size, 25)]
    assert all(p['parameters'] == {'text_type': 'query', 'dimension': 512, 'output_type': 'dense'} for p in sessions[0].requests)


def test_session_closes_on_failure_and_does_not_leak_to_next_call():
    first, second = Session(fail_batch=2), Session()
    embedding = DashscopeEmbedding(dashscope_api_key='test', embedding_model_name='model')
    with patch('agentuniverse.agent.action.knowledge.embedding.dashscope_embedding.aiohttp.ClientSession', side_effect=[first, second]):
        with pytest.raises(RuntimeError, match='network failure'):
            asyncio.run(embedding.async_get_embeddings([str(i) for i in range(26)]))
        assert first.closed
        assert asyncio.run(embedding.async_get_embeddings(['1'])) == [[1.]]
        assert second.closed


def test_empty_input_does_not_create_session():
    embedding = DashscopeEmbedding(dashscope_api_key='test', embedding_model_name='model')
    with patch('agentuniverse.agent.action.knowledge.embedding.dashscope_embedding.aiohttp.ClientSession') as factory:
        assert asyncio.run(embedding.async_get_embeddings([])) == []
    factory.assert_not_called()


def test_cancellation_closes_operation_session():
    entered = None
    class WaitingSession(Session):
        async def post(self, **kwargs):
            entered.set()
            await asyncio.Future()
    session = WaitingSession()
    embedding = DashscopeEmbedding(dashscope_api_key='test', embedding_model_name='model')
    async def run():
        nonlocal entered
        entered = asyncio.Event()
        with patch('agentuniverse.agent.action.knowledge.embedding.dashscope_embedding.aiohttp.ClientSession', return_value=session):
            task = asyncio.create_task(embedding.async_get_embeddings(['1']))
            await entered.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert session.closed
    asyncio.run(run())


def test_native_http_batches_reuse_connection():
    from aiohttp import web
    import agentuniverse.agent.action.knowledge.embedding.dashscope_embedding as module
    transports = set()
    batches = []
    async def handler(request):
        transports.add(request.transport)
        payload = await request.json()
        batches.append(payload['input']['texts'])
        return web.json_response({'output': {'embeddings': [
            {'embedding': [float(text)]} for text in payload['input']['texts']]}})
    async def run():
        app = web.Application()
        app.router.add_post('/embeddings', handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', 0)
        try:
            await site.start()
            port = site._server.sockets[0].getsockname()[1]
            embedding = DashscopeEmbedding(dashscope_api_key='test', embedding_model_name='model')
            with patch.object(module, 'DASHSCOPE_EMBEDDING_URL', f'http://127.0.0.1:{port}/embeddings'):
                result = await embedding.async_get_embeddings([str(i) for i in range(51)])
            assert result == [[float(i)] for i in range(51)]
        finally:
            await runner.cleanup()
    asyncio.run(run())
    assert [len(batch) for batch in batches] == [25, 25, 1]
    assert len(transports) == 1
