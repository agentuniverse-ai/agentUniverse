"""RequestTool must not copy arbitrary request input into server logs."""

import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


REQUEST_TOOL = (Path(__file__).resolve().parents[6] / "agentuniverse" / "agent"
                / "action" / "tool" / "common_tool" / "request_tool.py")


def _load_method(name, log_calls):
    """Load the production method without importing optional LangChain packages."""
    module = ast.parse(REQUEST_TOOL.read_text(encoding="utf-8"))
    tool_class = next(node for node in module.body
                      if isinstance(node, ast.ClassDef) and node.name == "RequestTool")
    method = next(node for node in tool_class.body
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and node.name == name)

    def parse_json_markdown(value):
        raise ValueError(f"invalid request: {value}")

    scope = {
        "Any": Any,
        "LOGGER": SimpleNamespace(error=lambda *args: log_calls.append(args)),
        "parse_json_markdown": parse_json_markdown,
    }
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(REQUEST_TOOL), "exec"), scope)
    return scope[name]


@pytest.mark.parametrize("method_name", ["execute", "async_execute"])
def test_parse_failure_does_not_log_request_credentials(method_name):
    log_calls = []
    method = _load_method(method_name, log_calls)
    tool = SimpleNamespace(json_parser=True, method="POST",
                           _normalized_method=lambda: "POST")
    payload = '{"api_key":"supersecret", invalid}'

    if method_name == "async_execute":
        result = asyncio.run(method(tool, payload))
    else:
        result = method(tool, payload)

    assert "invalid request" in result
    assert len(log_calls) == 1
    assert "supersecret" not in repr(log_calls)
