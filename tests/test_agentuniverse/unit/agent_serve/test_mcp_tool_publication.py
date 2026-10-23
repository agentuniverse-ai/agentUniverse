"""Publish annotated aU tools through the real MCP schema and call machinery."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterator
from typing import Annotated, Any

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.tools.base import Tool as PublishedTool
from pydantic import BaseModel, Field

from agentuniverse.agent.action.tool.common_tool.simple_math_tool import AddTool
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent_serve.web.mcp.mcp_server_manager import create_exposed_tool_method_wrapper
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.configer import Configer

ExposeTool = Callable[[Tool], Callable[..., Any]]


class LookupRequest(BaseModel):
    """A tool-module parameter type unavailable in the publishing module."""

    query: str


class LookupResponse(BaseModel):
    """A structured tool result resolved in the same namespace as its method."""

    text: str
    limit: int


class SyncLookupTool(Tool):
    """Exercise the synchronous execution fallback."""

    def execute(self, request: LookupRequest, *, limit: Annotated[int, Field(ge=1, le=5)] = 3) -> LookupResponse:
        """Look up a request with a bounded result limit."""
        return LookupResponse(text=request.query, limit=limit)


class AsyncLookupTool(SyncLookupTool):
    """Exercise a native async method with explicitly quoted forward references."""

    # Keep explicit quotes to cover nested string annotations under future annotations.
    async def async_execute(
        self, request: "LookupRequest", *, limit: Annotated[int, Field(ge=1, le=5)] = 3  # noqa: UP037
    ) -> "LookupResponse":  # noqa: UP037
        """Look up a request without entering the sync implementation."""
        return LookupResponse(text=request.query, limit=limit)


class UntypedTool(Tool):
    """Keep legacy unannotated methods publishable."""

    def execute(self, value="ready"):
        """Echo a value without a parameter or return annotation."""
        return value


@pytest.fixture
def expose_tool() -> Iterator[ExposeTool]:
    """Use the real registry while restoring application and registration state."""
    config_manager = ApplicationConfigManager()
    try:
        previous_config = config_manager.app_configer
    except ValueError:
        previous_config = None
    config = Configer()
    config.value = {"BASE_INFO": {"appname": "mcp_publication_test"}}
    config_manager.app_configer = AppConfiger().load_by_configer(config)
    manager = ToolManager()
    registrations: list[str] = []

    def expose(instance: Tool) -> Callable[..., Any]:
        code = instance.get_instance_code()
        manager.register(code, instance)
        registrations.append(code)
        return create_exposed_tool_method_wrapper(instance.name)

    try:
        yield expose
    finally:
        for code in registrations:
            manager.unregister(code)
        config_manager.app_configer = previous_config


@pytest.mark.parametrize("tool_class", [SyncLookupTool, AsyncLookupTool])
def test_publish_and_call_model_parameters(expose_tool: ExposeTool, tool_class: type[Tool]) -> None:
    """Custom models and defaults survive real MCP registration and invocation."""
    instance = tool_class(name="lookup")
    published = PublishedTool.from_function(expose_tool(instance), name=instance.name)
    schema = published.parameters

    assert set(schema["properties"]) == {"request", "limit"}
    assert schema["required"] == ["request"]
    assert schema["$defs"]["LookupRequest"]["properties"]["query"]["type"] == "string"
    assert schema["properties"]["limit"]["default"] == 3
    assert schema["properties"]["limit"]["minimum"] == 1
    assert schema["properties"]["limit"]["maximum"] == 5
    if hasattr(published, "output_schema"):
        assert set(published.output_schema["properties"]) == {"text", "limit"}
    assert published.is_async is (tool_class is AsyncLookupTool)
    result = asyncio.run(published.run({"request": {"query": "evidence"}}))
    assert result == LookupResponse(text="evidence", limit=3)


@pytest.mark.parametrize("tool_class", [SyncLookupTool, AsyncLookupTool])
@pytest.mark.parametrize("arguments", [{"request": {}}, {"request": {"query": "evidence"}, "limit": 0}])
def test_reject_invalid_model_and_annotated_arguments(
    expose_tool: ExposeTool, tool_class: type[Tool], arguments: dict[str, Any]
) -> None:
    """Resolving types retains nested-model and Annotated validation."""
    instance = tool_class(name="validated_lookup")
    published = PublishedTool.from_function(expose_tool(instance), name=instance.name)

    with pytest.raises(ToolError, match="validation error"):
        asyncio.run(published.run(arguments))


def test_fastmcp_discovers_and_calls_published_tool(expose_tool: ExposeTool) -> None:
    """FastMCP exposes a valid schema and executes the registered tool end to end."""
    server = FastMCP("publication_test")
    server.add_tool(expose_tool(SyncLookupTool(name="lookup")), name="lookup")

    async def exercise_server() -> None:
        tools = await server.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "lookup"
        assert set(tools[0].inputSchema["properties"]) == {"request", "limit"}
        result = await server.call_tool("lookup", {"request": {"query": "evidence"}, "limit": 2})
        content = result[0] if isinstance(result, tuple) else result
        assert '"evidence"' in content[0].text
        assert '"limit": 2' in content[0].text

    asyncio.run(exercise_server())


def test_publish_existing_builtin_annotations(expose_tool: ExposeTool) -> None:
    """An existing tool without postponed annotations remains callable."""
    published = PublishedTool.from_function(expose_tool(AddTool(name="add")), name="add")

    assert published.parameters["properties"]["input"]["type"] == "string"
    assert asyncio.run(published.run({"input": "1,2"})) == 3.0


def test_publish_unannotated_method(expose_tool: ExposeTool) -> None:
    """Publishing does not add a required return annotation to legacy tools."""
    published = PublishedTool.from_function(expose_tool(UntypedTool(name="echo")), name="echo")

    assert published.parameters.get("required", []) == []
    assert asyncio.run(published.run({})) == "ready"
