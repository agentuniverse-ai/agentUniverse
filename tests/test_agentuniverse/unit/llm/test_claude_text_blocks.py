"""Native Anthropic response objects must retain every returned text block."""
import pytest
import anthropic
import httpx
from anthropic.types import Message

from agentuniverse.llm.default.claude_llm import ClaudeLLM


def response_payload(texts):
    return {
        'id': 'msg_offline', 'type': 'message', 'role': 'assistant',
        'model': 'claude-3-haiku-20240307',
        'content': [{'type': 'text', 'text': text} for text in texts],
        'stop_reason': 'end_turn', 'stop_sequence': None,
        'usage': {'input_tokens': 2, 'output_tokens': 8},
    }


@pytest.mark.parametrize('texts', [
    ['First sentence. ', 'Second sentence.'],
    ['', 'Visible answer'],
    ['中文', '\n', '第二段'],
    ['start', '', ' middle', ' end'],
    ['One block'],
    [''],
    ['', ''],
])
def test_parse_native_message_preserves_all_text(texts):
    message = Message(**response_payload(texts))
    result = ClaudeLLM.parse_result(message)
    expected = ''.join(texts)
    if expected:
        assert result.text == expected
        assert result.raw is message
        assert result.raw.usage.output_tokens == 8
    else:
        assert result is None


def test_empty_content_still_raises():
    with pytest.raises(ValueError, match='no content blocks'):
        ClaudeLLM.parse_result(Message(**response_payload([])))


def test_nonstream_call_with_native_sdk_response(monkeypatch):
    def handler(request):
        assert request.url.path == '/v1/messages'
        return httpx.Response(200, json=response_payload(['The answer is ', 'complete.']))

    transport = httpx.Client(transport=httpx.MockTransport(handler))
    sdk = anthropic.Anthropic(api_key='offline-placeholder', http_client=transport, max_retries=0)
    monkeypatch.setattr(ClaudeLLM, '_new_client', lambda self: sdk)
    try:
        result = ClaudeLLM(api_key='offline-placeholder', model_name='claude-3-haiku-20240307')._call(
            messages=[{'role': 'user', 'content': 'Summarize'}], streaming=False)
        assert result.text == 'The answer is complete.'
        assert isinstance(result.raw, Message)
        assert len(result.raw.content) == 2
        assert transport.is_closed
    finally:
        sdk.close()
