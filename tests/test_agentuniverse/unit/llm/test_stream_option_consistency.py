"""Exercise real SDK response types with offline HTTP transports."""

import asyncio
import json

import httpx
import ollama
import openai
import pytest

from agentuniverse.llm.default.default_ollama_llm import OllamaLLM
from agentuniverse.llm.llm_channel.ollama_llm_channel import OllamaLLMChannel
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_llm import OpenAILLM

OPTIONS = [
    {},
    {"stream": True},
    {"stream": False},
    {"streaming": True},
    {"streaming": False},
    {"stream": True, "streaming": False},
    {"stream": False, "streaming": True},
]


def sdk_response(provider, body):
    """Return valid SSE, NDJSON or JSON for the SDK-requested mode."""
    if provider == "openai":
        choice = {"index": 0, "finish_reason": "stop"}
        response = {"id": "offline", "created": 0, "model": "test-model"}
        if body["stream"]:
            choice["delta"] = {"role": "assistant", "content": "hello"}
            response.update(object="chat.completion.chunk", choices=[choice])
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                content="data: " + json.dumps(response) + "\n\ndata: [DONE]\n\n",
            )
        choice["message"] = {"role": "assistant", "content": "hello"}
        response.update(object="chat.completion", choices=[choice])
    else:
        response = {"model": "test-model", "done": True, "message": {"role": "assistant", "content": "hello"}}
        if body["stream"]:
            return httpx.Response(
                200,
                headers={"content-type": "application/x-ndjson"},
                content=json.dumps(response) + "\n",
            )
    return httpx.Response(200, json=response)


@pytest.mark.parametrize("provider", ["openai", "ollama", "ollama_channel"])
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("default", [False, True])
@pytest.mark.parametrize("overrides", OPTIONS)
def test_request_and_parser_use_one_stream_choice(monkeypatch, provider, asynchronous, default, overrides):
    requests = []
    expected_stream = overrides.get("stream", overrides.get("streaming", default))

    def handle(request):
        body = json.loads(request.content)
        requests.append(body)
        return sdk_response(provider, body)

    transport = httpx.MockTransport(handle)
    if provider == "openai":
        client = openai.OpenAI(
            api_key="offline-key",
            base_url="https://offline.invalid/v1",
            http_client=httpx.Client(transport=transport, trust_env=False),
        )
        async_client = openai.AsyncOpenAI(
            api_key="offline-key",
            base_url="https://offline.invalid/v1",
            http_client=httpx.AsyncClient(transport=transport, trust_env=False),
        )
        model = OpenAILLM(model_name="test-model", streaming=default)
    else:
        client = ollama.Client(host="https://offline.invalid", transport=transport, trust_env=False)
        async_client = ollama.AsyncClient(host="https://offline.invalid", transport=transport, trust_env=False)
        if provider == "ollama":
            model = OllamaLLM(model_name="test-model", streaming=default)
        else:
            model = OllamaLLMChannel(channel_model_name="test-model")
            model.channel_model_config = {
                "streaming": default,
                "temperature": 0.5,
                "max_tokens": 16,
                "request_timeout": None,
                "ext_info": None,
            }
    monkeypatch.setattr(type(model), "_new_client", lambda self: client)
    monkeypatch.setattr(type(model), "_new_async_client", lambda self: async_client)
    messages = [{"role": "user", "content": "hello"}]

    async def run():
        result = await model._acall(messages, **overrides)
        if expected_stream:
            assert not isinstance(result, LLMOutput)
            return [item.text async for item in result]
        assert isinstance(result, LLMOutput)
        return [result.text]

    try:
        if asynchronous:
            texts = asyncio.run(run())
        else:
            result = model._call(messages, **overrides)
            if expected_stream:
                assert not isinstance(result, LLMOutput)
                texts = [item.text for item in result]
            else:
                assert isinstance(result, LLMOutput)
                texts = [result.text]
        assert texts == ["hello"]
        assert len(requests) == 1
        assert requests[0]["stream"] is expected_stream
        assert "streaming" not in requests[0]
        assert model.streaming is default
    finally:
        if provider == "openai":
            client.close()
            asyncio.run(async_client.close())
        else:
            client._client.close()
            asyncio.run(async_client._client.aclose())
