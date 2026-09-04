"""Bedrock optional-SDK and LLM contracts, without AWS calls."""

import asyncio
import importlib.util
import runpy
import socket
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, Mock

import pytest
import tomli

from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding
from agentuniverse.llm.default.aws_bedrock_llm import AWSBedrockLLM


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    blocked = Mock(side_effect=AssertionError("Offline tests must not open network connections"))
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)


@pytest.fixture
def llm(monkeypatch):
    monkeypatch.setitem(sys.modules, "boto3", None)
    model = AWSBedrockLLM(model_name="amazon.nova-lite-v1:0", aws_access_key_id=None, aws_secret_access_key=None)
    model._client = Mock()
    return model


@pytest.mark.parametrize("use_async", [False, True])
def test_llm_call(llm, use_async):
    response = {"output": {"message": {"content": [{"text": "hello"}]}}}
    llm._client.converse.return_value = response
    messages = [{"role": "user", "content": "hi"}]
    output = asyncio.run(llm._acall(messages, top_p=0.9)) if use_async else llm._call(messages, top_p=0.9)
    assert output.text == "hello"
    assert output.raw == response
    llm._client.converse.assert_called_once_with(
        modelId=llm.model_name,
        messages=[{"role": "user", "content": [{"text": "hi"}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0.5, "topP": 0.9},
    )


@pytest.mark.parametrize("use_async", [False, True])
def test_llm_stream(llm, use_async):
    stream = MagicMock(spec=["__iter__", "close"])
    stream.__iter__.return_value = iter(
        [
            {"contentBlockDelta": {"delta": {"text": "one"}}},
            {"contentBlockDelta": {"delta": {"text": "two"}}},
            {"messageStop": {}},
        ]
    )
    llm._client.converse_stream.return_value = {"stream": stream}

    async def collect():
        return [chunk.text async for chunk in await llm._acall([], streaming=True)]

    result = asyncio.run(collect()) if use_async else [chunk.text for chunk in llm._call([], streaming=True)]
    assert result == ["one", "two"]


@pytest.mark.parametrize("use_async", [False, True])
def test_llm_api_error(llm, use_async):
    llm._client.converse.side_effect = RuntimeError("service unavailable")
    with pytest.raises(RuntimeError, match="Error calling AWS Bedrock: service unavailable"):
        if use_async:
            asyncio.run(llm._acall([]))
        else:
            llm._call([])


@pytest.mark.parametrize("component", [AWSBedrockLLM, AWSBedrockEmbedding])
def test_sdk_is_optional_until_first_use(component, monkeypatch):
    monkeypatch.setitem(sys.modules, "boto3", None)
    model = component(aws_access_key_id=None, aws_secret_access_key=None)
    with pytest.raises(ImportError, match=r"pip install 'agentUniverse\[aws_ext\]'"):
        if isinstance(model, AWSBedrockLLM):
            model._get_client()
        else:
            model._initialize_client()


def test_embedding_client_creation_and_reuse(monkeypatch):
    sdk = ModuleType("boto3")
    sdk.Session = Mock()
    config_module = ModuleType("botocore.config")
    config_module.Config = Mock()
    monkeypatch.setitem(sys.modules, "boto3", sdk)
    monkeypatch.setitem(sys.modules, "botocore", ModuleType("botocore"))
    monkeypatch.setitem(sys.modules, "botocore.config", config_module)
    model = AWSBedrockEmbedding(aws_access_key_id=None, aws_secret_access_key=None, aws_region="us-west-2")
    model._initialize_client()
    model._initialize_client()
    sdk.Session.assert_called_once_with(region_name="us-west-2")
    config_module.Config.assert_called_once_with(retries={"max_attempts": 3, "mode": "adaptive"})
    sdk.Session.return_value.client.assert_called_once_with(
        service_name="bedrock-runtime", config=config_module.Config.return_value
    )


def test_aws_extra_declares_optional_sdk():
    root = Path(__file__).resolve().parents[4]
    with (root / "pyproject.toml").open("rb") as stream:
        poetry = tomli.load(stream)["tool"]["poetry"]
    assert poetry["dependencies"]["boto3"] == {"version": ">=1.34.131,<2.0.0", "optional": True}
    assert poetry["extras"]["aws_ext"] == ["boto3"]


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("installed", [False, True])
@pytest.mark.parametrize(
    ("relative_path", "class_name"),
    [
        ("llm/test_aws_bedrock_llm.py", "TestAWSBedrockLLM"),
        ("agent/action/knowledge/embedding/test_aws_bedrock_embedding.py", "EmbeddingTest"),
    ],
)
def test_live_tests_require_explicit_opt_in(monkeypatch, enabled, installed, relative_path, class_name):
    monkeypatch.setenv("AGENTUNIVERSE_RUN_AWS_TESTS", "1" if enabled else "0")
    monkeypatch.setattr(importlib.util, "find_spec", Mock(return_value=object() if installed else None))
    namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / relative_path))
    assert getattr(namespace[class_name], "__unittest_skip__", False) == (not (enabled and installed))
