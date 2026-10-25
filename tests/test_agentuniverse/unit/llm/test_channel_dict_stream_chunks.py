"""Use real SDK models and the native channel/LangChain streaming adapters."""

import asyncio
from copy import deepcopy

from openai.types.chat import ChatCompletionChunk
import pytest

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel


def payload(delta=None, finish=None, usage=None):
    return {
        'id': 'chunk-local', 'object': 'chat.completion.chunk',
        'created': 1, 'model': 'local-model',
        'choices': [] if delta is None else [
            {'index': 0, 'delta': delta, 'finish_reason': finish}],
        'usage': usage,
        'vendor_metadata': {'request': ['local', 1]},
    }


CASES = [
    payload({'role': 'assistant'}),
    payload({'content': 'hello 世界'}),
    payload({}, finish='stop'),
    payload({'role': 'assistant', 'tool_calls': [
        {'index': 0, 'id': 'call-local', 'type': 'function',
         'function': {'name': 'lookup', 'arguments': '{"query":'}}]}),
    payload(usage={'prompt_tokens': 3, 'completion_tokens': 2, 'total_tokens': 5}),
]


@pytest.mark.parametrize('data', CASES)
@pytest.mark.parametrize('sdk_model', [False, True], ids=['dict', 'sdk'])
def test_dictionary_and_sdk_chunks_preserve_the_same_fields(data, sdk_model):
    original = deepcopy(data)
    chunk = ChatCompletionChunk.model_validate(data) if sdk_model else deepcopy(data)
    expected_raw = chunk.model_dump() if sdk_model else chunk
    result = LLMChannel.parse_result(chunk)
    assert result.raw == expected_raw
    assert data == original
    if not sdk_model:
        assert result.raw is chunk
    if data['choices']:
        delta = data['choices'][0]['delta']
        assert result.text == (delta.get('content') or '')
        assert result.message.content == result.text
        assert result.message.type == delta.get('role')
    else:
        assert result.text == ''
        assert result.usage.prompt_tokens == 3
        assert result.usage.completion_tokens == 2
        assert result.usage.total_tokens == 5


@pytest.mark.parametrize('delta', [{'content': 'minimal'}, {'role': 'assistant'}])
def test_sparse_dictionary_chunks_need_no_sdk_methods(delta):
    chunk = {'choices': [{'delta': delta}]}
    result = LLMChannel.parse_result(chunk)
    assert result.raw is chunk
    assert result.text == delta.get('content', '')


def mixed_chunks():
    return [
        ChatCompletionChunk.model_validate(payload({'role': 'assistant'})),
        payload({'content': 'hello '}),
        ChatCompletionChunk.model_validate(payload({'content': '世界'})),
        payload({}, finish='stop'),
        payload(usage={'prompt_tokens': 3, 'completion_tokens': 2, 'total_tokens': 5}),
    ]


async def async_chunks(chunks):
    for chunk in chunks:
        yield chunk


def check_outputs(outputs, inputs):
    assert len(outputs) == 5
    assert ''.join(out.text for out in outputs) == 'hello 世界'
    assert outputs[0].message.type == 'assistant'
    assert outputs[3].raw['choices'][0]['finish_reason'] == 'stop'
    assert outputs[-1].usage.total_tokens == 5
    for output, chunk in zip(outputs, inputs):
        assert output.raw == (chunk if isinstance(chunk, dict) else chunk.model_dump())


def test_sync_channel_accepts_a_mixed_stream():
    channel = LLMChannel()
    inputs = mixed_chunks()
    check_outputs(list(channel.generate_stream_result(iter(inputs))), inputs)


def test_async_channel_accepts_a_mixed_stream():
    async def run():
        channel = LLMChannel()
        inputs = mixed_chunks()
        outputs = [out async for out in channel.agenerate_stream_result(async_chunks(inputs))]
        check_outputs(outputs, inputs)
    asyncio.run(run())


@pytest.fixture
def bridge():
    channel = LLMChannel(channel_model_name='local-model',
                         channel_api_base='https://example.invalid/v1')
    channel.channel_model_config = {'temperature': 0.7, 'request_timeout': 1,
                                    'max_tokens': 32, 'max_retries': 0, 'streaming': True}
    instance = channel.as_langchain()
    try:
        yield channel, instance
    finally:
        instance.client._client.close()
        asyncio.run(instance.async_client._client.close())


def check_generations(generations):
    assert len(generations) == 4  # The usage-only chunk has no message choice.
    assert ''.join(item.text for item in generations) == 'hello 世界'
    assert generations[-1].generation_info == {'finish_reason': 'stop'}


def test_sync_langchain_adapter_receives_dictionary_raw(bridge):
    channel, instance = bridge
    outputs = channel.generate_stream_result(iter(mixed_chunks()))
    check_generations(list(instance.as_langchain_chunk(outputs)))


def test_async_langchain_adapter_receives_dictionary_raw(bridge):
    async def run():
        channel, instance = bridge
        outputs = channel.agenerate_stream_result(async_chunks(mixed_chunks()))
        generations = [item async for item in instance.as_langchain_achunk(outputs)]
        check_generations(generations)
    asyncio.run(run())


def test_parsing_does_not_modify_nested_dictionary_metadata():
    chunk = payload({'content': 'hello'})
    original = deepcopy(chunk)
    result = LLMChannel.parse_result(chunk)
    assert chunk == original
    assert result.raw['vendor_metadata'] == {'request': ['local', 1]}
