"""Offline request-contract tests using the declared Qianfan SDK."""

import asyncio
import copy

import pytest
import requests
import aiohttp

qianfan = pytest.importorskip("qianfan")

from agentuniverse.base.annotation import trace  # noqa: E402
from agentuniverse.llm.default.wenxin_llm import WenXinLLM  # noqa: E402
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger  # noqa: E402
from agentuniverse.base.config.configer import Configer  # noqa: E402


@pytest.fixture
def sdk(monkeypatch):
    # Isolate application tracing, not provider request construction.
    monkeypatch.setattr(trace, "_llm_wrapper_sync", lambda func, *a, **kw: func(*a, **kw))

    async def untraced(func, *args, **kwargs):
        return await func(*args, **kwargs)

    monkeypatch.setattr(trace, "_llm_wrapper_async", untraced)
    client = qianfan.ChatCompletion(ak="offline-key", sk="offline-secret")
    captured = []

    def response(**kwargs):
        captured.append(kwargs)
        result = qianfan.QfResponse(code=200, headers={}, body={
            "result": "answer", "id": "offline", "is_end": True,
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        })
        return iter([result]) if kwargs["stream"] else result

    async def async_response(**kwargs):
        result = response(**kwargs)
        if not kwargs["stream"]:
            return result

        async def chunks():
            for chunk in result:
                yield chunk
        return chunks()

    monkeypatch.setattr(client._client, "llm", response)
    monkeypatch.setattr(client._client, "async_llm", async_response)
    return client, captured


def model(client, stream=False, **kwargs):
    return WenXinLLM(client=client, api_key="offline-key", secret_key="offline-secret",
                     model_name="ERNIE-3.5-8K", streaming=stream, **kwargs)


def invoke(llm, asynchronous, streaming, kwargs):
    messages = [{"role": "user", "content": "question"}]
    if not asynchronous:
        result = llm._call(messages, **kwargs)
        return "".join(chunk.text for chunk in result) if streaming else result.text

    async def run():
        result = await llm._acall(messages, **kwargs)
        if streaming:
            return "".join([chunk.text async for chunk in result])
        return result.text
    return asyncio.run(run())


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("settings,overrides,expected", [
    ({"request_timeout": 7, "max_retries": 0, "max_tokens": 3000}, {}, (7, 1, 3000)),
    ({}, {}, (300, 3, 1024)),
    ({"request_timeout": None, "max_retries": None, "max_tokens": None}, {}, (300, 3, None)),
    ({"request_timeout": 7, "max_retries": 4, "max_tokens": 3000},
     {"request_timeout": 9, "max_retries": 0, "max_tokens": 128}, (9, 1, 128)),
    ({"request_timeout": 7, "max_retries": 4, "max_tokens": 3000},
     {"retry_count": 2, "max_output_tokens": 64}, (7, 2, 64)),
    ({}, {"retry_count": 1, "max_retries": 8, "max_output_tokens": 64, "max_tokens": 128}, (300, 1, 64)),
    ({}, {"request_timeout": None, "max_retries": None, "max_tokens": None}, (300, 3, None)),
])
def test_request_controls_reach_sdk_boundary(sdk, asynchronous, streaming, settings, overrides, expected):
    client, captured = sdk
    llm = model(client, streaming, **settings)
    before = copy.deepcopy(overrides)
    assert invoke(llm, asynchronous, streaming, overrides) == "answer"
    assert overrides == before
    assert len(captured) == 1
    request = captured[0]
    timeout, attempts, output_tokens = expected
    assert request["retry_config"].timeout == timeout
    assert request["retry_config"].retry_count == attempts
    assert request["body"].get("max_output_tokens") == output_tokens
    assert "max_tokens" not in request["body"]
    assert "max_retries" not in request["body"]
    assert "request_timeout" not in request["body"]
    assert request["stream"] is streaming


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("streaming", [False, True])
def test_langchain_requests_preserve_configured_controls(sdk, asynchronous, streaming):
    client, captured = sdk
    adapter = model(client, streaming, request_timeout=7, max_retries=0, max_tokens=3000).as_langchain()
    result = asyncio.run(adapter.ainvoke("question")) if asynchronous else adapter.invoke("question")
    assert result.content == "answer"
    request = captured[0]
    assert request["retry_config"].timeout == 7
    assert request["retry_config"].retry_count == 1
    assert request["body"]["max_output_tokens"] == 3000
    assert "max_tokens" not in request["body"]
    assert "max_retries" not in request["body"]


@pytest.mark.parametrize("max_retries", [0, 2])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_retry_setting_matches_actual_sdk_attempts(sdk, max_retries, asynchronous):
    client, captured = sdk
    invoke(model(client, max_retries=max_retries), False, False, {})
    retry_config = captured[0]["retry_config"]
    retry_config.backoff_factor = 0
    retry_config.jitter = 0
    attempts = []

    def failing_request():
        attempts.append(1)
        raise requests.ConnectionError("offline transport failure")

    if asynchronous:
        async def failing_async_request():
            attempts.append(1)
            raise aiohttp.ClientConnectionError("offline transport failure")

        with pytest.raises(aiohttp.ClientConnectionError, match="offline transport failure"):
            asyncio.run(client._client._async_with_retry(retry_config, failing_async_request))
    else:
        with pytest.raises(requests.ConnectionError, match="offline transport failure"):
            client._client._with_retry(retry_config, failing_request)
    assert len(attempts) == max_retries + 1


def test_component_configuration_preserves_zero_retries(sdk):
    client, captured = sdk
    config = Configer()
    config.value = {"name": "offline", "model_name": "ERNIE-3.5-8K",
                    "request_timeout": 7, "max_retries": 0, "max_tokens": 128}
    llm = model(client).initialize_by_component_configer(LLMConfiger().load_by_configer(config))
    assert invoke(llm, False, False, {}) == "answer"
    request = captured[0]
    assert request["retry_config"].timeout == 7
    assert request["retry_config"].retry_count == 1
    assert request["body"]["max_output_tokens"] == 128


def test_native_extra_parameters_and_caller_dictionary_are_preserved(sdk):
    client, captured = sdk
    overrides = {"max_output_tokens": 64, "retry_count": 1, "top_p": 0.5,
                 "system": "Be concise."}
    original = copy.deepcopy(overrides)
    assert invoke(model(client), False, False, overrides) == "answer"
    assert overrides == original
    request = captured[0]
    assert request["body"]["top_p"] == 0.5
    assert request["body"]["system"] == "Be concise."
    assert request["body"]["max_output_tokens"] == 64
