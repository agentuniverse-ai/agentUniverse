"""Initial framework system instructions must use Anthropic's system field."""
import asyncio
from copy import deepcopy
import json

import anthropic
import httpx
import pytest

from agentuniverse.llm.default.claude_llm import ClaudeLLM


CASES = [
    ([{'role': 'system', 'content': 'Be concise.'}, {'role': 'user', 'content': 'Hello'}],
     {}, [{'type': 'text', 'text': 'Be concise.'}]),
    ([{'role': 'system', 'content': 'First instruction'},
      {'role': 'system', 'content': [{'type': 'text', 'text': 'Second instruction'}]},
      {'role': 'user', 'content': 'Hello'}], {},
     [{'type': 'text', 'text': 'First instruction'}, {'type': 'text', 'text': 'Second instruction'}]),
    ([{'role': 'system', 'content': 'Framework instruction'}, {'role': 'user', 'content': 'Hello'}],
     {'system': 'Caller instruction'},
     [{'type': 'text', 'text': 'Caller instruction'}, {'type': 'text', 'text': 'Framework instruction'}]),
    ([{'role': 'user', 'content': 'Hello'}], {'system': 'Native system'}, 'Native system'),
    ([{'role': 'user', 'content': 'Hello'}], {}, None),
]


@pytest.mark.parametrize('messages, options, expected_system', CASES)
@pytest.mark.parametrize('is_async', [False, True])
@pytest.mark.parametrize('streaming', [False, True])
def test_native_sdk_request_has_top_level_system(monkeypatch, messages, options, expected_system, is_async, streaming):
    original_messages, original_options = deepcopy(messages), deepcopy(options)
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        if streaming:
            return httpx.Response(200, headers={'content-type': 'text/event-stream'}, text=(
                'event: content_block_delta\ndata: {"type":"content_block_delta","index":0,'
                '"delta":{"type":"text_delta","text":"hello"}}\n\n'
                'event: message_stop\ndata: {"type":"message_stop"}\n\n'))
        return httpx.Response(200, json={
            'id': 'msg_test', 'type': 'message', 'role': 'assistant',
            'model': 'claude-3-haiku-20240307', 'content': [{'type': 'text', 'text': 'hello'}],
            'stop_reason': 'end_turn', 'stop_sequence': None,
            'usage': {'input_tokens': 1, 'output_tokens': 1},
        })

    llm = ClaudeLLM(api_key='offline', model_name='claude-3-haiku-20240307')
    if is_async:
        async def run():
            transport = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            sdk = anthropic.AsyncAnthropic(api_key='offline', http_client=transport, max_retries=0)
            monkeypatch.setattr(ClaudeLLM, '_new_async_client', lambda self: sdk)
            try:
                output = await llm._acall(messages=messages, streaming=streaming, **options)
                text = ''.join([part.text async for part in output]) if streaming else output.text
                assert text == 'hello'
            finally:
                await sdk.close()
        asyncio.run(run())
    else:
        transport = httpx.Client(transport=httpx.MockTransport(handler))
        sdk = anthropic.Anthropic(api_key='offline', http_client=transport, max_retries=0)
        monkeypatch.setattr(ClaudeLLM, '_new_client', lambda self: sdk)
        try:
            output = llm._call(messages=messages, streaming=streaming, **options)
            text = ''.join(part.text for part in output) if streaming else output.text
            assert text == 'hello'
        finally:
            sdk.close()

    assert len(requests) == 1
    assert requests[0]['messages'] == [m for m in messages if m['role'] != 'system']
    assert requests[0].get('system') == expected_system
    assert messages == original_messages
    assert options == original_options


def test_summarization_processor_with_native_claude(monkeypatch):
    from agentuniverse.agent.action.knowledge.doc_processor.summarization_processor import SummarizationProcessor
    from agentuniverse.agent.action.knowledge.store.document import Document
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager

    monkeypatch.setattr(ApplicationConfigManager(), '_ApplicationConfigManager__app_configer', AppConfiger())
    captured = []

    def handler(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json={
            'id': 'msg_summary', 'type': 'message', 'role': 'assistant',
            'model': 'claude-3-haiku-20240307', 'content': [{'type': 'text', 'text': 'A short summary.'}],
            'stop_reason': 'end_turn', 'stop_sequence': None,
            'usage': {'input_tokens': 1, 'output_tokens': 1},
        })

    transport = httpx.Client(transport=httpx.MockTransport(handler))
    sdk = anthropic.Anthropic(api_key='offline', http_client=transport, max_retries=0)
    monkeypatch.setattr(ClaudeLLM, '_new_client', lambda self: sdk)
    llm = ClaudeLLM(api_key='offline', model_name='claude-3-haiku-20240307')
    monkeypatch.setattr(SummarizationProcessor, '_get_llm', lambda self: llm)
    try:
        docs = SummarizationProcessor(llm_name='offline_claude').process_docs([Document(text='Source facts.')])
        assert docs[0].text == 'A short summary.'
        assert captured[0]['system'] == [{'type': 'text', 'text':
            'You are a helpful assistant that summarizes retrieved documents.'}]
        assert [m['role'] for m in captured[0]['messages']] == ['user']
        assert 'Source facts.' in captured[0]['messages'][0]['content']
    finally:
        sdk.close()


def test_system_blocks_are_independent_and_keep_metadata():
    block = {'type': 'text', 'text': 'Cached instructions', 'cache_control': {'type': 'ephemeral'}}
    messages = [{'role': 'system', 'content': [block]}, {'role': 'user', 'content': 'Hello'}]
    explicit = {'system': [{'type': 'text', 'text': 'Native instructions'}]}
    normalized, options = ClaudeLLM._prepare_system_messages(messages, explicit)
    assert options['system'] == [explicit['system'][0], block]
    options['system'][1]['cache_control']['type'] = 'changed'
    assert block['cache_control']['type'] == 'ephemeral'
    assert normalized == messages[1:]
