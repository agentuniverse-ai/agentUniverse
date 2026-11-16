"""Check serialized embedding requests through real SDK and LangChain clients."""
import asyncio
import json

import httpx
from openai import AsyncOpenAI, OpenAI
import pytest

from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding

CASES = [
    (None, None),
    ('text-embedding-ada-002', None),
    ('text-embedding-ada-002', 0),
    ('text-embedding-3-small', None),
    ('text-embedding-3-large', None),
    ('text-embedding-3-small', 2),
    ('text-embedding-3-large', 8),
]


@pytest.mark.parametrize('model,dimensions', CASES)
@pytest.mark.parametrize('method', ['embed_query', 'embed_documents',
                                  'aembed_query', 'aembed_documents'])
def test_conversion_preserves_embedding_request(model, dimensions, method):
    async def check():
        requests = []

        def respond(request):
            body = json.loads(request.content)
            requests.append(body)
            size = body.get('dimensions', 3)
            vector = [1.0] + [0.0] * (size - 1)
            return httpx.Response(200, json={
                'object': 'list', 'model': body['model'],
                'data': [{'object': 'embedding', 'index': index, 'embedding': vector}
                         for index in range(len(body['input']))],
                'usage': {'prompt_tokens': 2, 'total_tokens': 2},
            })

        sync_http = httpx.Client(transport=httpx.MockTransport(respond))
        async_http = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        with OpenAI(api_key='offline-test', http_client=sync_http) as sync_sdk:
            async with AsyncOpenAI(api_key='offline-test', http_client=async_http) as async_sdk:
                embedding = OpenAIEmbedding(
                    embedding_model_name=model, dimensions=dimensions,
                    openai_api_key='offline-test', client=sync_sdk, async_client=async_sdk,
                )
                converted = embedding.as_langchain()
                argument = ['first', 'second'] if method.endswith('documents') else 'first'
                operation = getattr(converted, method)
                result = await operation(argument) if method.startswith('a') else operation(argument)

                assert len(requests) == 1
                assert requests[0]['model'] == (model or 'text-embedding-ada-002')
                if not dimensions:
                    assert 'dimensions' not in requests[0]
                else:
                    assert requests[0]['dimensions'] == dimensions
                size = dimensions or 3
                vector = [1.0] + [0.0] * (size - 1)
                assert result == ([vector, vector] if method.endswith('documents') else vector)
                assert converted.client is sync_sdk.embeddings
                assert converted.async_client is async_sdk.embeddings
                assert embedding.client is sync_sdk and embedding.async_client is async_sdk
                assert embedding.embedding_model_name == model
                assert embedding.dimensions == dimensions
                assert not sync_http.is_closed and not async_http.is_closed

    asyncio.run(check())
