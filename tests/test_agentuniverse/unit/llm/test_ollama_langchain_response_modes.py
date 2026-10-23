"""Exercise both Ollama bridges through LangChain and real offline SDK clients."""

import asyncio
import json

import httpx
import pytest

ollama = pytest.importorskip("ollama")

from agentuniverse.base.annotation import trace  # noqa: E402
from agentuniverse.llm.default.default_ollama_llm import OllamaLLM  # noqa: E402
from agentuniverse.llm.llm_channel.ollama_llm_channel import OllamaLLMChannel  # noqa: E402

MODES = [
    (False, {}),
    (True, {}),
    (True, {"stream": False}),
    (True, {"streaming": False}),
    (False, {"stream": True, "streaming": False}),
    (True, {"stream": False, "streaming": True}),
]


@pytest.mark.parametrize("provider", ["direct", "channel"])
@pytest.mark.parametrize("entrypoint", ["invoke", "ainvoke", "stream", "astream"])
@pytest.mark.parametrize("default,overrides", MODES)
def test_langchain_accepts_complete_and_streamed_responses(
    monkeypatch, provider, entrypoint, default, overrides
):
    requests = []
    # BaseChatModel consumes stream itself for invoke/ainvoke. The streaming
    # alias still reaches the provider; stream/astream forward both aliases.
    if entrypoint in {"invoke", "ainvoke"}:
        expected_stream = overrides.get("streaming", default)
    else:
        expected_stream = overrides.get("stream", overrides.get("streaming", default))

    def handle(request):
        body = json.loads(request.content)
        requests.append(body)
        complete = {
            "model": "offline-model",
            "message": {"role": "assistant", "content": "hello world"},
            "done": True,
            "eval_count": 2,
        }
        if body["stream"]:
            chunks = [
                {"message": {"role": "assistant", "content": text}, "done": False}
                for text in ["hello", " world"]
            ]
            complete["message"]["content"] = ""
            chunks.append(complete)
            return httpx.Response(
                200,
                headers={"content-type": "application/x-ndjson"},
                content="".join(json.dumps(chunk) + "\n" for chunk in chunks),
            )
        return httpx.Response(200, json=complete)

    transport = httpx.MockTransport(handle)
    client = ollama.Client(host="https://offline.invalid", transport=transport, trust_env=False)
    async_client = ollama.AsyncClient(host="https://offline.invalid", transport=transport, trust_env=False)
    if provider == "direct":
        model = OllamaLLM(model_name="offline-model", streaming=default)
    else:
        model = OllamaLLMChannel(channel_model_name="offline-model")
        model.channel_model_config = {
            "streaming": default,
            "temperature": 0.5,
            "max_tokens": 16,
            "request_timeout": None,
            "ext_info": None,
        }
    model.client = client
    model.async_client = async_client
    # Isolate application tracing, not provider calls or response parsing.
    monkeypatch.setattr(trace, "_llm_wrapper_sync", lambda func, *a, **kw: func(*a, **kw))

    async def untraced(func, *args, **kwargs):
        return await func(*args, **kwargs)

    monkeypatch.setattr(trace, "_llm_wrapper_async", untraced)
    adapter = model.as_langchain()

    async def run_async():
        if entrypoint == "ainvoke":
            return [await adapter.ainvoke("hi", stop=["STOP"], **overrides)]
        return [chunk async for chunk in adapter.astream("hi", stop=["STOP"], **overrides)]

    try:
        if entrypoint.startswith("a"):
            result = asyncio.run(run_async())
        elif entrypoint == "invoke":
            result = [adapter.invoke("hi", stop=["STOP"], **overrides)]
        else:
            result = list(adapter.stream("hi", stop=["STOP"], **overrides))
        assert "".join(chunk.content for chunk in result) == "hello world"
        assert result[-1].response_metadata["done"] is True
        assert result[-1].response_metadata["eval_count"] == 2
        assert len(requests) == 1
        assert requests[0]["stream"] is expected_stream
        assert requests[0]["model"] == "offline-model"
        assert requests[0]["options"]["stop"] == ["STOP"]
        assert requests[0]["messages"][0]["content"] == "hi"
        assert model.streaming is default
    finally:
        client._client.close()
        asyncio.run(async_client._client.aclose())
