"""Configured Ollama timeouts must reach HTTPX, not generation options."""
import asyncio
import json

import httpx
import pytest

ollama = pytest.importorskip("ollama")
from agentuniverse.llm.default.default_ollama_llm import OllamaLLM  # noqa: E402
from agentuniverse.llm.llm_channel.ollama_llm_channel import OllamaLLMChannel  # noqa: E402


def make_model(provider, timeout):
    if provider == "direct":
        return OllamaLLM(model_name="offline", request_timeout=timeout)
    model = OllamaLLMChannel(channel_model_name="offline")
    model.channel_model_config = {
        "request_timeout": timeout, "streaming": True, "temperature": 0.5,
        "max_tokens": 16, "ext_info": None,
    }
    return model


@pytest.mark.parametrize("provider", ["direct", "channel"])
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("timeout", [None, 7])
def test_timeout_reaches_real_sdk_http_request(monkeypatch, provider, asynchronous, stream, timeout):
    seen = []
    clients = []

    def respond(request):
        seen.append(request)
        result = {"message": {"role": "assistant", "content": "ok"}, "done": True}
        if stream:
            return httpx.Response(200, content=json.dumps(result) + "\n")
        return httpx.Response(200, json=result)

    transport = httpx.MockTransport(respond)
    real_sync, real_async = ollama.Client, ollama.AsyncClient

    def sync_factory(**kwargs):
        client = real_sync(**kwargs, transport=transport, trust_env=False)
        clients.append(client)
        return client

    def async_factory(**kwargs):
        client = real_async(**kwargs, transport=transport, trust_env=False)
        clients.append(client)
        return client

    monkeypatch.setattr(ollama, "Client", sync_factory)
    monkeypatch.setattr(ollama, "AsyncClient", async_factory)
    model = make_model(provider, timeout)
    messages = [{"role": "user", "content": "hello"}]

    async def run():
        try:
            result = await model._acall(messages, stream=stream)
            return [item async for item in result] if stream else [result]
        finally:
            for client in clients:
                await client._client.aclose()

    if asynchronous:
        result = asyncio.run(run())
    else:
        try:
            output = model._call(messages, stream=stream)
            result = list(output) if stream else [output]
        finally:
            for client in clients:
                client._client.close()
    assert [item.text for item in result] == ["ok"]
    assert len(seen) == 1
    assert seen[0].extensions["timeout"] == dict.fromkeys(["connect", "read", "write", "pool"], timeout)
    assert "timeout" not in json.loads(seen[0].content)["options"]


@pytest.mark.parametrize("provider", ["direct", "channel"])
def test_injected_clients_keep_their_own_timeouts(provider):
    model = make_model(provider, 7)
    sync_client = ollama.Client(timeout=3, trust_env=False)
    async_client = ollama.AsyncClient(timeout=4, trust_env=False)
    try:
        model.client, model.async_client = sync_client, async_client
        assert model._new_client() is sync_client
        assert model._new_async_client() is async_client
        assert sync_client._client.timeout.read == 3
        assert async_client._client.timeout.read == 4
    finally:
        sync_client._client.close()
        asyncio.run(async_client._client.aclose())
