"""Native SDK SSE parsing must not turn tool argument deltas into text."""
import asyncio
import json

import anthropic
import httpx
import pytest

from agentuniverse.llm.default.claude_llm import ClaudeLLM


def sse(with_tool):
    events = [
        {'type': 'message_start', 'message': {'id': 'msg_test', 'type': 'message',
         'role': 'assistant', 'model': 'claude-3-haiku-20240307', 'content': [],
         'stop_reason': None, 'stop_sequence': None,
         'usage': {'input_tokens': 1, 'output_tokens': 0}}},
        {'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}},
        {'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': 'Hello'}},
        {'type': 'content_block_stop', 'index': 0},
    ]
    if with_tool:
        events.extend([
            {'type': 'content_block_start', 'index': 1,
             'content_block': {'type': 'tool_use', 'id': 'tool_test', 'name': 'lookup', 'input': {}}},
            {'type': 'content_block_delta', 'index': 1,
             'delta': {'type': 'input_json_delta', 'partial_json': '{"query":'}},
            {'type': 'content_block_delta', 'index': 1,
             'delta': {'type': 'input_json_delta', 'partial_json': '"weather"}'}},
            {'type': 'content_block_stop', 'index': 1},
        ])
    events.extend([
        {'type': 'content_block_start', 'index': 2, 'content_block': {'type': 'text', 'text': ''}},
        {'type': 'content_block_delta', 'index': 2, 'delta': {'type': 'text_delta', 'text': ' world'}},
        {'type': 'content_block_stop', 'index': 2},
        {'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None},
         'usage': {'output_tokens': 3}},
        {'type': 'message_stop'},
    ])
    return ''.join(f"event: {event['type']}\ndata: {json.dumps(event)}\n\n" for event in events)


def response(request, with_tool):
    assert json.loads(request.content)['stream'] is True
    return httpx.Response(200, headers={'content-type': 'text/event-stream'}, content=sse(with_tool))


def check_output(chunks):
    assert [chunk.text for chunk in chunks] == ['Hello', ' world']
    assert all(chunk.raw['delta']['type'] == 'text_delta' for chunk in chunks)
    assert chunks[0].raw['index'] == 0
    assert chunks[1].raw['index'] == 2


@pytest.mark.parametrize('with_tool', [True, False])
def test_sync_native_sdk_stream(monkeypatch, with_tool):
    client = anthropic.Anthropic(api_key='test-key', max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(lambda req: response(req, with_tool))))
    monkeypatch.setattr(ClaudeLLM, '_new_client', lambda self: client)
    try:
        chunks = list(ClaudeLLM(model_name='claude-3-haiku-20240307')._call(
            [{'role': 'user', 'content': 'hello'}], streaming=True))
        check_output(chunks)
    finally:
        client.close()


@pytest.mark.parametrize('with_tool', [True, False])
def test_async_native_sdk_stream(monkeypatch, with_tool):
    async def exercise():
        client = anthropic.AsyncAnthropic(api_key='test-key', max_retries=0,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(lambda req: response(req, with_tool))))
        monkeypatch.setattr(ClaudeLLM, '_new_async_client', lambda self: client)
        try:
            stream = await ClaudeLLM(model_name='claude-3-haiku-20240307')._acall(
                [{'role': 'user', 'content': 'hello'}], streaming=True)
            check_output([chunk async for chunk in stream])
        finally:
            await client.close()
    asyncio.run(exercise())


@pytest.mark.parametrize('async_mode', [False, True])
def test_typed_tool_delta_has_no_text_attribute(async_mode):
    from anthropic.types import ContentBlockDeltaEvent, TextDelta
    from anthropic.types.beta.tools import InputJsonDelta, ToolsBetaContentBlockDeltaEvent

    events = [ContentBlockDeltaEvent(type='content_block_delta', index=0,
                                    delta=TextDelta(type='text_delta', text='Hello')),
              ToolsBetaContentBlockDeltaEvent(type='content_block_delta', index=1,
                                             delta=InputJsonDelta(type='input_json_delta', partial_json='{}')),
              ContentBlockDeltaEvent(type='content_block_delta', index=2,
                                    delta=TextDelta(type='text_delta', text=' world'))]
    llm = ClaudeLLM()
    if not async_mode:
        check_output(list(llm.generate_stream_result(iter(events))))
    else:
        async def exercise():
            async def stream():
                for event in events:
                    yield event
            check_output([chunk async for chunk in llm.agenerate_stream_result(stream())])
        asyncio.run(exercise())
