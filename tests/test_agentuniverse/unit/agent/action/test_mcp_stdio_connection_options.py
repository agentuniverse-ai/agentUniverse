"""Exercise configured session timeouts with the real MCP stdio SDK and server."""

import asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

import pytest

pytest.importorskip("mcp")
from mcp.shared.exceptions import McpError

from agentuniverse.agent.action.tool.mcp_tool import MCPTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.action.toolkit.mcp_toolkit import MCPToolkit
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager

SERVER = Path(__file__).parent / "fixtures" / "options_mcp_server.py"


@pytest.fixture(autouse=True)
def isolate_registry():
    manager = ToolManager()
    previous_tools = manager._instance_obj_map.copy()
    config = ApplicationConfigManager()
    try:
        previous_config = config.app_configer
    except ValueError:
        previous_config = None
    config.app_configer = AppConfiger()
    try:
        yield
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(previous_tools)
        config.app_configer = previous_config


@pytest.mark.parametrize("kind", ["tool", "toolkit"])
@pytest.mark.parametrize("timeout", [None, 2.0, 10.0])
def test_stdio_session_timeout_reaches_real_call(tmp_path, kind, timeout):
    log = tmp_path / "call.json"
    options = {} if timeout is None else {"session_kwargs": {"read_timeout_seconds": timedelta(seconds=timeout)}}
    # Allow native server startup, then keep a timed-out reply pending past
    # process shutdown so SDK late-response cleanup cannot mask the timeout.
    delay = "8" if timeout == 2.0 else "0.05"
    args = {"transport": "stdio", "command": sys.executable, "args": [str(SERVER), str(log), "call", delay],
            "env": {"PYTHONPATH": os.pathsep.join(sys.path)}, "connection_kwargs": options,
            "server_name": "connection-options"}

    async def operation():
        manager = MCPSessionManager()
        manager.init_session()
        try:
            if kind == "tool":
                tool = MCPTool(name="echo", **args)
                await tool.get_tool_info()
            else:
                toolkit = MCPToolkit(name="options", **args)
                await toolkit.get_all_tools()
                tool = ToolManager().get_instance_obj("options@echo", new_instance=False)
                assert tool is not None
                assert tool.connection_kwargs == options
            if timeout == 2.0:
                with pytest.raises(McpError, match="Timed out"):
                    await tool.async_execute(value="Café")
            else:
                result = await tool.async_execute(value="Café")
                assert not result.isError
                assert result.content[0].text == "Café"
        finally:
            await manager.clear_session()

    asyncio.run(asyncio.wait_for(operation(), timeout=15))
    assert json.loads(log.read_text(encoding="utf-8")) == {"name": "echo", "arguments": {"value": "Café"}}


def error_leaves(error):
    children = getattr(error, "exceptions", ())
    return [leaf for child in children for leaf in error_leaves(child)] if children else [error]


@pytest.mark.parametrize("kind", ["tool", "toolkit"])
@pytest.mark.parametrize("timeout", [2.0, 10.0])
def test_stdio_timeout_applies_to_metadata_discovery(tmp_path, kind, timeout):
    log = tmp_path / "discovery.json"
    args = {"transport": "stdio", "command": sys.executable,
            "args": [str(SERVER), str(log), "slow_discovery", "8" if timeout == 2.0 else "0.05"],
            "env": {"PYTHONPATH": os.pathsep.join(sys.path)},
            "connection_kwargs": {"session_kwargs": {"read_timeout_seconds": timedelta(seconds=timeout)}}}
    if kind == "tool":
        instance = MCPTool(name="echo", **args)
        operation = instance.get_tool_info()
    else:
        instance = MCPToolkit(name="discovery", **args)
        operation = instance.get_all_tools()
    if timeout == 2.0:
        with pytest.raises(Exception) as raised:
            asyncio.run(asyncio.wait_for(operation, timeout=15))
        assert any(isinstance(leaf, McpError) and "Timed out" in str(leaf) for leaf in error_leaves(raised.value))
    else:
        asyncio.run(asyncio.wait_for(operation, timeout=15))
        if kind == "tool":
            assert instance.input_keys == ["value"]
        else:
            assert instance.include == ["echo"]
    assert json.loads(log.read_text(encoding="utf-8")) == {"method": "tools/list"}
