"""Optional real-SDK contract tests, using dummy credentials and Stubber only."""

import socket
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding
from agentuniverse.llm.default.aws_bedrock_llm import AWSBedrockLLM

boto3 = pytest.importorskip("boto3", reason="Install aws_ext to run offline SDK contract tests")
from botocore.stub import Stubber  # noqa: E402


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    blocked = Mock(side_effect=AssertionError("SDK contract tests must not connect to AWS"))
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)


@pytest.mark.parametrize("component", [AWSBedrockLLM, AWSBedrockEmbedding])
def test_runtime_client_supports_required_operations(component):
    model = component(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",  # noqa: S106 - dummy offline credentials
        aws_region="us-east-1",
    )
    if isinstance(model, AWSBedrockLLM):
        model.aws_session_token = None
        client = model._get_client()
    else:
        model._initialize_client()
        client = model.client
    try:
        assert {"Converse", "ConverseStream", "InvokeModel"} <= set(client.meta.service_model.operation_names)
    finally:
        client.close()


def test_converse_response_with_real_sdk():
    model = AWSBedrockLLM(
        model_name="amazon.nova-lite-v1:0",
        aws_access_key_id="testing",
        aws_secret_access_key="testing",  # noqa: S106 - dummy Stubber credentials, never sent
        aws_session_token=None,
        aws_region="us-east-1",
    )
    client = model._get_client()
    try:
        with Stubber(client) as stubber:
            stubber.add_response(
                "converse",
                {
                    "output": {"message": {"role": "assistant", "content": [{"text": "hello"}]}},
                    "stopReason": "end_turn",
                    "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
                    "metrics": {"latencyMs": 1},
                },
                {
                    "modelId": model.model_name,
                    "messages": [{"role": "user", "content": [{"text": "hi"}]}],
                    "inferenceConfig": {"maxTokens": 1024, "temperature": 0.5},
                },
            )
            assert model._call([{"role": "user", "content": "hi"}]).text == "hello"
            stubber.assert_no_pending_responses()
    finally:
        client.close()
