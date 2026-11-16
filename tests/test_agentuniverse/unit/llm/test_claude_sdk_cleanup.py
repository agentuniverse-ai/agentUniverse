"""Exercise async cleanup with the real supported Anthropic SDK and offline HTTP."""
import asyncio
from unittest.mock import patch

import anthropic
import httpx
import pytest

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.default.claude_llm import ClaudeLLM


@pytest.mark.parametrize("streaming", [False, True])
def test_successful_async_call_closes_real_sdk_transport(monkeypatch, streaming):
    monkeypatch.setattr(ApplicationConfigManager(), "_ApplicationConfigManager__app_configer", AppConfiger())

    async def run():
        requests = []

        def handler(request):
            requests.append(request)
            if streaming:
                return httpx.Response(200, headers={"content-type": "text/event-stream"}, text=(
                    'event: content_block_delta\ndata: {"type":"content_block_delta","index":0,'
                    '"delta":{"type":"text_delta","text":"hello"}}\n\n'
                    'event: message_stop\ndata: {"type":"message_stop"}\n\n'))
            return httpx.Response(200, json={
                "id": "msg_test", "type": "message", "role": "assistant",
                "model": "claude-3-haiku-20240307", "content": [{"type": "text", "text": "hello"}],
                "stop_reason": "end_turn", "stop_sequence": None,
                "usage": {"input_tokens": 1, "output_tokens": 1},
            })

        transport = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        sdk = anthropic.AsyncAnthropic(api_key="offline-placeholder", http_client=transport, max_retries=0)
        llm = ClaudeLLM(model_name="claude-3-haiku-20240307", api_key="offline-placeholder")
        try:
            with patch.object(ClaudeLLM, "_new_async_client", return_value=sdk):
                output = await llm.acall(messages=[{"role": "user", "content": "hello"}], streaming=streaming)
                if streaming:
                    assert [chunk.text async for chunk in output] == ["hello"]
                else:
                    assert output.text == "hello"
            assert len(requests) == 1
            assert transport.is_closed
            assert llm.async_client is sdk
        finally:
            await sdk.close()

    asyncio.run(run())


def test_close_without_initialized_async_client_is_noop():
    asyncio.run(ClaudeLLM(api_key="offline-placeholder").aclose())
