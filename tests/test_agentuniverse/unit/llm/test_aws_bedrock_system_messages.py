"""Offline tests for preserving system instructions in Bedrock Converse."""

import asyncio
import copy
import socket

import pytest

from agentuniverse.llm.default.aws_bedrock_llm import AWSBedrockLLM


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def fail_connect(*args, **kwargs):
        pytest.fail("Bedrock system-message tests must not use the network")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    monkeypatch.setattr(socket, "create_connection", fail_connect)


class RecordingClient:
    def __init__(self):
        self.requests = []

    def converse(self, **kwargs):
        self.requests.append(kwargs)
        return {"output": {"message": {"role": "assistant", "content": [{"text": "ok"}]}}}

    def converse_stream(self, **kwargs):
        self.requests.append(kwargs)
        return {"stream": iter([{"contentBlockDelta": {"delta": {"text": "ok"}}}, {"messageStop": {}}])}


def invoke(messages, streaming=False, asynchronous=False):
    client = RecordingClient()
    llm = AWSBedrockLLM(model_name="amazon.nova-lite-v1:0")
    llm._client = client
    if asynchronous:

        async def run():
            result = await llm._acall(messages, streaming=streaming)
            return "".join([chunk.text async for chunk in result]) if streaming else result.text

        text = asyncio.run(run())
    else:
        result = llm._call(messages, streaming=streaming)
        text = "".join(chunk.text for chunk in result) if streaming else result.text
    assert text == "ok"
    return client.requests[0]


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_system_messages_use_top_level_field_without_changing_conversation(streaming, asynchronous):
    messages = [
        {"role": "system", "content": "Be concise."},
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "reply"},
        {"role": "system", "content": "Answer in English."},
        {"role": "user", "content": "second"},
    ]
    original = copy.deepcopy(messages)
    request = invoke(messages, streaming, asynchronous)
    assert request["system"] == [{"text": "Be concise."}, {"text": "Answer in English."}]
    assert request["messages"] == [
        {"role": "user", "content": [{"text": "first"}]},
        {"role": "assistant", "content": [{"text": "reply"}]},
        {"role": "user", "content": [{"text": "second"}]},
    ]
    assert messages == original


@pytest.mark.parametrize("streaming", [False, True])
def test_no_system_message_omits_system_parameter(streaming):
    messages = [{"role": "user", "content": "hello"}]
    request = invoke(messages, streaming)
    assert "system" not in request
    assert request["messages"] == [{"role": "user", "content": [{"text": "hello"}]}]


@pytest.mark.parametrize("streaming", [False, True])
def test_system_text_blocks_are_normalized_without_mutating_input(streaming):
    messages = [
        {"role": "system", "content": [{"type": "text", "text": "first"}, {"text": "second"}]},
        {"role": "user", "content": [{"text": "hello"}]},
    ]
    original = copy.deepcopy(messages)
    request = invoke(messages, streaming)
    assert request["system"] == [{"text": "first"}, {"text": "second"}]
    assert messages == original


def test_native_bedrock_system_blocks_are_preserved():
    block = {"guardContent": {"text": {"text": "guarded", "qualifiers": ["guard_content"]}}}
    request = invoke([{"role": "system", "content": [block]}, {"role": "user", "content": "hello"}])
    assert request["system"] == [block]


def test_real_sdk_validates_system_parameter_without_network():
    boto3 = pytest.importorskip("boto3")
    from botocore.stub import Stubber

    client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id="synthetic",
        aws_secret_access_key="synthetic",  # noqa: S106 - offline Stubber credentials
    )
    model = "anthropic.claude-3-haiku-20240307-v1:0"
    llm = AWSBedrockLLM(model_name=model)
    llm._client = client
    with Stubber(client) as stubber:
        stubber.add_response(
            "converse",
            {
                "output": {"message": {"role": "assistant", "content": [{"text": "ok"}]}},
                "stopReason": "end_turn",
                "usage": {"inputTokens": 3, "outputTokens": 1, "totalTokens": 4},
                "metrics": {"latencyMs": 1},
            },
            {
                "modelId": model,
                "messages": [{"role": "user", "content": [{"text": "hello"}]}],
                "system": [{"text": "Be concise."}],
                "inferenceConfig": {"maxTokens": 1024, "temperature": 0.5},
            },
        )
        result = llm._call([{"role": "system", "content": "Be concise."}, {"role": "user", "content": "hello"}])
        assert result.text == "ok"
        stubber.assert_no_pending_responses()


@pytest.mark.parametrize("content", [None, 1, {"text": "not a block list"}])
def test_invalid_system_content_fails_before_inference(content):
    client = RecordingClient()
    llm = AWSBedrockLLM(model_name="amazon.nova-lite-v1:0")
    llm._client = client
    with pytest.raises(TypeError, match="System message content"):
        llm._call([{"role": "system", "content": content}, {"role": "user", "content": "hello"}])
    assert client.requests == []


def test_service_rejection_does_not_retry_as_a_user_message(monkeypatch):
    client = RecordingClient()
    llm = AWSBedrockLLM(model_name="test-model-without-system-support")
    llm._client = client

    def reject_system(**kwargs):
        client.requests.append(kwargs)
        error = "system prompts unsupported by this model"
        raise ValueError(error)

    monkeypatch.setattr(client, "converse", reject_system)
    with pytest.raises(RuntimeError, match="system prompts unsupported"):
        llm._call([{"role": "system", "content": "instruction"}, {"role": "user", "content": "hello"}])
    assert len(client.requests) == 1
    assert client.requests[0]["system"] == [{"text": "instruction"}]
    assert client.requests[0]["messages"] == [{"role": "user", "content": [{"text": "hello"}]}]


@pytest.mark.parametrize("operation", ["Converse", "ConverseStream"])
def test_request_matches_installed_sdk_shape(operation):
    pytest.importorskip("botocore")
    from botocore.session import Session
    from botocore.validate import validate_parameters

    request = invoke(
        [{"role": "system", "content": "instruction"}, {"role": "user", "content": "hello"}],
        streaming=operation == "ConverseStream",
    )
    schema = Session().get_service_model("bedrock-runtime").operation_model(operation).input_shape
    validate_parameters(request, schema)
