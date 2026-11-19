from __future__ import annotations

import asyncio
import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.action.toolkit.mcp_toolkit import MCPToolkit
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager


EXAMPLE_YAML = Path(__file__).with_name("agent_guild_observation.yaml")
APP_NAME = "agent_guild_observation_example_test"
TOOLKIT_NAME = "agent_guild_observation"


def _unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class LocalMCPFixture:
    """Serve a small Streamable HTTP MCP endpoint without external calls."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.port = _unused_port()
        self.url = f"http://127.0.0.1:{self.port}/mcp"
        self._thread: threading.Thread | None = None
        self._thread_error: BaseException | None = None
        self.mcp = FastMCP("agent-guild-observation-test", stateless_http=True)

        def guild_preflight(url: str) -> dict[str, str]:
            """Record an explicitly supplied URL for test verification."""
            self.calls.append(url)
            return {"observed_url": url, "status": "captured"}

        def should_not_register() -> str:
            """A second tool that must be filtered out by the YAML include list."""
            return "this tool is intentionally excluded"

        self.mcp.add_tool(guild_preflight, name="guild_preflight")
        self.mcp.add_tool(should_not_register, name="should_not_register")

    def __enter__(self) -> "LocalMCPFixture":
        app = self.mcp.streamable_http_app()
        config = uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="error")
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

        deadline = time.monotonic() + 10
        while not self._server.started and self._thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.05)

        if not self._server.started:
            self._stop_server()
            if self._thread_error:
                raise RuntimeError("local MCP fixture failed to start") from self._thread_error
            raise RuntimeError("local MCP fixture did not start within 10 seconds")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        MCPSessionManager().safe_close_stack()
        self._stop_server()

    def _serve(self) -> None:
        try:
            asyncio.run(self._server.serve())
        except BaseException as error:  # pragma: no cover - defensive fixture cleanup
            self._thread_error = error

    def _stop_server(self) -> None:
        if hasattr(self, "_server"):
            self._server.should_exit = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)


def _set_test_application() -> None:
    configer = Configer()
    configer.value = {"BASE_INFO": {"appname": APP_NAME}}
    ApplicationConfigManager().app_configer = AppConfiger().load_by_configer(configer)


def _load_toolkit(local_url: str) -> MCPToolkit:
    configer = Configer(str(EXAMPLE_YAML)).load()
    configer.value["url"] = local_url
    component_configer = ComponentConfiger().load_by_configer(configer)
    return MCPToolkit().initialize_by_component_configer(component_configer)


def _call_result_text(result) -> str:
    return "\n".join(item.text for item in result.content if isinstance(item, TextContent))


def test_toolkit_registers_only_included_tool_and_dispatches_exact_url():
    _set_test_application()
    tool_manager = ToolManager()

    with LocalMCPFixture() as fixture:
        _load_toolkit(fixture.url)

        included_tool = tool_manager.get_instance_obj(
            f"{TOOLKIT_NAME}@guild_preflight", new_instance=False
        )
        excluded_tool = tool_manager.get_instance_obj(
            f"{TOOLKIT_NAME}@should_not_register", new_instance=False
        )

        assert included_tool is not None
        assert excluded_tool is None
        assert fixture.calls == [], "initialization must list tools without invoking the observed target"

        observed_url = "https://public.example.test/mcp"
        result = included_tool.execute(url=observed_url)

        assert result.isError is False
        assert fixture.calls == [observed_url]
        assert observed_url in _call_result_text(result)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
