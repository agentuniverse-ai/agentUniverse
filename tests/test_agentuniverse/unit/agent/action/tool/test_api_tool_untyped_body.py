"""Untyped OpenAPI properties must survive the complete HTTP request path."""

import json
from copy import deepcopy
from typing import Any

import httpx
import pytest
from pydantic import BaseModel, Field

from agentuniverse.agent.action.tool import api_tool
from agentuniverse.agent.action.tool.api_tool import APITool
from agentuniverse.agent.action.tool.tool import ToolInput


class APIBody(BaseModel):
    payload: Any = Field(description="Application-defined JSON value")
    enabled: bool
    count: int


@pytest.mark.parametrize("empty_schema", [False, True], ids=["pydantic-any", "empty-schema"])
@pytest.mark.parametrize("value", [
    {"nested": [1, False, None]}, ["a", 2], "keep me", 7, 1.25, 0, False, "", None,
])
def test_untyped_body_value_reaches_native_httpx(monkeypatch, empty_schema, value):
    schema = APIBody.model_json_schema()
    assert "type" not in schema["properties"]["payload"]
    if empty_schema:
        schema["properties"]["payload"] = {}
    tool = APITool(openapi_spec={
        "url": "https://example.invalid/values",
        "method": "post",
        "operation": {"parameters": []},
        "requestBody": {"content": {"application/json": {"schema": schema}}},
    })
    params = {"payload": value, "enabled": "false", "count": "2"}
    original = deepcopy(params)
    received = []

    def handle(request):
        assert request.headers["Content-Type"] == "application/json"
        decoded = json.loads(request.content)
        received.append(decoded)
        return httpx.Response(200, json=decoded)

    # The production APITool and HTTPX serializer run unchanged; only the
    # external HTTP dispatch boundary is redirected to a native MockTransport.
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(api_tool.ssrf_proxy, "post", client.post)
        output = json.loads(tool.execute(ToolInput(params)))
    expected = {"payload": value, "enabled": False, "count": 2}
    assert received == [expected]
    assert type(received[0]["payload"]) is type(value)
    assert output == expected
    assert params == original
