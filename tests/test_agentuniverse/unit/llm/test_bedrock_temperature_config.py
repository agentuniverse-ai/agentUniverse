"""Check Bedrock request parameters with the optional native SDK and Stubber."""

import asyncio

import pytest

boto3 = pytest.importorskip("boto3", minversion="1.34.131")
from botocore.stub import Stubber

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.default.aws_bedrock_llm import AWSBedrockLLM


@pytest.fixture
def bedrock_client():
    """Use explicit inert credentials; Stubber handles every SDK operation."""
    manager = ApplicationConfigManager()
    try:
        original_config = manager.app_configer
    except ValueError:
        original_config = None
    manager.app_configer = AppConfiger()
    client = boto3.client(
        "bedrock-runtime", region_name="us-east-1",
        aws_access_key_id="test-only-access-key",
        aws_secret_access_key="test-only-secret-key",
        aws_session_token="test-only-session-token",
    )
    try:
        yield client
    finally:
        client.close()
        manager.app_configer = original_config


@pytest.mark.parametrize("async_call,streaming", [
    (False, False), (False, True), (True, False), (True, True),
])
@pytest.mark.parametrize("configured,override,expected", [
    (0.0, {}, 0.0),
    (0.25, {}, 0.25),
    (None, {}, 0.7),
    (0.25, {"temperature": 0.0}, 0.0),
    (0.0, {"temperature": 0.9}, 0.9),
])
def test_public_calls_preserve_temperature(
        bedrock_client, async_call, streaming, configured, override, expected):
    """The native SDK must receive the configured value, including zero."""
    llm = AWSBedrockLLM(
        model_name="amazon.nova-lite-v1:0", temperature=configured,
        max_tokens=32, aws_access_key_id=None, aws_secret_access_key=None,
        aws_session_token=None, aws_region="us-east-1",
    )
    llm._client = bedrock_client
    expected_params = {
        "modelId": "amazon.nova-lite-v1:0",
        "messages": [{"role": "user", "content": [{"text": "Hello"}]}],
        "inferenceConfig": {"maxTokens": 32, "temperature": expected},
    }
    # A Stubber-validated empty stream mapping suffices: this tests request
    # configuration, not event decoding or provider-generated content.
    response = {"stream": {}} if streaming else {
        "output": {"message": {"role": "assistant", "content": [{"text": "ok"}]}},
        "stopReason": "end_turn",
        "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
        "metrics": {"latencyMs": 1},
    }
    messages = [{"role": "user", "content": "Hello"}]
    with Stubber(bedrock_client) as stub:
        stub.add_response("converse_stream" if streaming else "converse",
                          response, expected_params)
        if async_call:
            async def invoke():
                output = await llm.acall(messages=messages, streaming=streaming, **override)
                if streaming:
                    assert [chunk async for chunk in output] == []
                else:
                    assert output.text == "ok"
            asyncio.run(invoke())
        else:
            output = llm.call(messages=messages, streaming=streaming, **override)
            if streaming:
                assert list(output) == []
            else:
                assert output.text == "ok"
        stub.assert_no_pending_responses()
    assert llm.temperature == configured
    assert messages == [{"role": "user", "content": "Hello"}]
