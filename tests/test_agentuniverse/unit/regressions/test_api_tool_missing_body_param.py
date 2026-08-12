"""Regression tests for APITool missing body parameter errors."""

import pytest

from agentuniverse.agent.action.tool.api_tool import APITool


def _make_api_tool(operation_id="op1"):
    tool = APITool(name="api_tool")
    tool.openapi_spec = {
        "operation": {
            "operationId": operation_id,
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "required": ["name"],
                            "properties": {"name": {"type": "string"}},
                        }
                    }
                }
            },
            "parameters": [],
        }
    }
    return tool


def test_missing_required_body_parameter_raises_validation_error():
    tool = _make_api_tool(operation_id="createUser")
    with pytest.raises(Exception, match="Missing required parameter name in operation createUser"):
        tool.do_http_request("https://api.example.com/users", "post", {}, {})


def test_missing_required_body_parameter_falls_back_to_tool_name():
    tool = _make_api_tool(operation_id="")
    with pytest.raises(Exception, match="Missing required parameter name in operation api_tool"):
        tool.do_http_request("https://api.example.com/users", "post", {}, {})
