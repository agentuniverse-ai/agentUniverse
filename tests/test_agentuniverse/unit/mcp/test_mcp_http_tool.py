#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for MCP session management and tool execution over HTTP transports.

Tests ManagedExitStack, MCPSessionManager, MCPTempClient, and MCPTool
via streamable-http and SSE transports against a local mock MCP server.

The tests start HTTP servers as subprocesses, run all checks, then tear down.

Run:
    pytest tests/test_agentuniverse/unit/mcp/test_mcp_http_tool.py -v

Or directly:
    python tests/test_agentuniverse/unit/mcp/test_mcp_http_tool.py
"""
import asyncio
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error

import pytest

from mcp import ClientSession

from agentuniverse.base.context.mcp_session_manager import (
    ManagedExitStack,
    MCPSessionManager,
    MCPTempClient,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PYTHON = sys.executable
HTTP_SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mock_mcp_http_server.py")

STREAMABLE_HTTP_HOST = "127.0.0.1"
STREAMABLE_HTTP_PORT = 18765
STREAMABLE_HTTP_URL = f"http://{STREAMABLE_HTTP_HOST}:{STREAMABLE_HTTP_PORT}/mcp"

SSE_HOST = "127.0.0.1"
SSE_PORT = 18766
SSE_URL = f"http://{SSE_HOST}:{SSE_PORT}/sse"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wait_for_server(proc: subprocess.Popen, host: str, port: int, timeout: float = 20):
    """Wait until the HTTP server is fully ready (not just TCP-open).

    uvicorn may bind the port before the ASGI application is initialised,
    so a plain TCP check leads to 502 errors.  This function sends a real
    HTTP GET and treats *any* HTTP response (including 4xx/5xx) as "ready".
    """
    url = f"http://{host}:{port}/"
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                f"Server process exited unexpectedly with code {proc.returncode}"
            )
        try:
            urllib.request.urlopen(url, timeout=2)
            return  # 2xx — ready
        except urllib.error.HTTPError:
            return  # 4xx/5xx — ASGI app is responding, good enough
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    raise RuntimeError(f"Server on {host}:{port} did not become ready within {timeout}s")


def _start_server(transport: str, host: str, port: int) -> subprocess.Popen:
    """Start the mock HTTP MCP server in a subprocess."""
    proc = subprocess.Popen(
        [
            PYTHON, HTTP_SERVER_SCRIPT,
            "--transport", transport,
            "--host", host,
            "--port", str(port),
        ],
        # DEVNULL avoids pipe-buffer saturation from uvicorn logs
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _wait_for_server(proc, host, port)
    return proc


def _stop_server(proc: subprocess.Popen):
    """Gracefully stop a server subprocess."""
    if proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


def _streamable_http_connect_args() -> dict:
    """Connection kwargs for the streamable-http mock server."""
    return {
        "transport": "streamable_http",
        "url": STREAMABLE_HTTP_URL,
    }


def _sse_connect_args() -> dict:
    """Connection kwargs for the SSE mock server."""
    return {
        "transport": "sse",
        "url": SSE_URL,
    }


def _assert_text_contains(result, expected: str):
    """Assert that at least one TextContent in result.content contains *expected*."""
    texts = [getattr(c, "text", "") for c in result.content]
    assert any(expected in t for t in texts), (
        f"Expected '{expected}' in result content, got: {texts}"
    )


# ---------------------------------------------------------------------------
# Fixtures — start/stop HTTP servers once per module
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def streamable_http_server():
    """Launch a streamable-http MCP server for the entire test module."""
    proc = _start_server("streamable-http", STREAMABLE_HTTP_HOST, STREAMABLE_HTTP_PORT)
    yield proc
    _stop_server(proc)


@pytest.fixture(scope="module")
def sse_server():
    """Launch an SSE MCP server for the entire test module."""
    proc = _start_server("sse", SSE_HOST, SSE_PORT)
    yield proc
    _stop_server(proc)


# =========================================================================
#  1. ManagedExitStack — streamable-http
# =========================================================================

class TestManagedExitStackHTTP:
    """Test ManagedExitStack with streamable-http transport."""

    def test_enter_run_close(self, streamable_http_server):
        """Basic lifecycle: enter CMs, run async calls, close cleanly."""
        from mcp.client.streamable_http import streamablehttp_client

        stack = ManagedExitStack()
        try:
            read, write, _ = stack.enter_async_context(
                streamablehttp_client(STREAMABLE_HTTP_URL)
            )
            session = stack.enter_async_context(ClientSession(read, write))
            stack.run_async(session.initialize)

            # echo
            result = stack.run_async(session.call_tool, "echo", {"message": "hello http"})
            _assert_text_contains(result, "Echo: hello http")

            # add
            result = stack.run_async(session.call_tool, "add", {"a": 10, "b": 32})
            _assert_text_contains(result, "42")
        finally:
            stack.close()

    def test_multiple_sessions_same_stack(self, streamable_http_server):
        """Multiple independent connections on one stack."""
        from mcp.client.streamable_http import streamablehttp_client

        stack = ManagedExitStack()
        try:
            sessions = []
            for _ in range(2):
                r, w, _ = stack.enter_async_context(
                    streamablehttp_client(STREAMABLE_HTTP_URL)
                )
                s = stack.enter_async_context(ClientSession(r, w))
                stack.run_async(s.initialize)
                sessions.append(s)

            r0 = stack.run_async(sessions[0].call_tool, "echo", {"message": "s0"})
            r1 = stack.run_async(sessions[1].call_tool, "echo", {"message": "s1"})
            _assert_text_contains(r0, "Echo: s0")
            _assert_text_contains(r1, "Echo: s1")
        finally:
            stack.close()


# =========================================================================
#  2. ManagedExitStack — SSE
# =========================================================================

class TestManagedExitStackSSE:
    """Test ManagedExitStack with SSE transport."""

    def test_enter_run_close(self, sse_server):
        """Basic lifecycle over SSE."""
        from mcp.client.sse import sse_client

        stack = ManagedExitStack()
        try:
            read, write = stack.enter_async_context(sse_client(SSE_URL))
            session = stack.enter_async_context(ClientSession(read, write))
            stack.run_async(session.initialize)

            result = stack.run_async(session.call_tool, "echo", {"message": "hello sse"})
            _assert_text_contains(result, "Echo: hello sse")

            result = stack.run_async(session.call_tool, "add", {"a": 7, "b": 8})
            _assert_text_contains(result, "15")
        finally:
            stack.close()


# =========================================================================
#  3. MCPSessionManager — streamable-http
# =========================================================================

class TestMCPSessionManagerHTTP:
    """Test connect, cache, and cleanup via MCPSessionManager (streamable-http)."""

    def setup_method(self):
        self.mgr = MCPSessionManager()
        self.mgr.init_session()

    def teardown_method(self):
        self.mgr.close_session()

    def test_connect_and_cache(self, streamable_http_server):
        """First call connects; second call returns cached session."""
        s1 = self.mgr.get_mcp_server_session(
            server_name="http_srv", **_streamable_http_connect_args()
        )
        s2 = self.mgr.get_mcp_server_session(
            server_name="http_srv", **_streamable_http_connect_args()
        )
        assert s1 is s2

    def test_call_tool_sync(self, streamable_http_server):
        """Sync tool call through the session manager."""
        session = self.mgr.get_mcp_server_session(
            server_name="http_sync_srv", **_streamable_http_connect_args()
        )
        result = self.mgr.managed_stack.run_async(
            session.call_tool, "add", {"a": 10, "b": 20}
        )
        _assert_text_contains(result, "30")

    def test_call_tool_async(self, streamable_http_server):
        """Async session acquisition + tool call."""

        async def _run():
            session = await self.mgr.get_mcp_server_session_async(
                server_name="http_async_srv", **_streamable_http_connect_args()
            )
            assert session is not None
            result = await asyncio.to_thread(
                self.mgr.managed_stack.run_async,
                session.call_tool, "echo", {"message": "async http hello"},
            )
            _assert_text_contains(result, "Echo: async http hello")

        asyncio.run(_run())

    def test_save_recover_across_threads(self, streamable_http_server):
        """Sessions shared via save/recover are usable in sub-threads."""
        session = self.mgr.get_mcp_server_session(
            server_name="http_shared_srv", **_streamable_http_connect_args()
        )

        saved = self.mgr.save_mcp_session()
        errors = []

        def worker():
            try:
                self.mgr.recover_mcp_session(**saved)
                s = self.mgr.mcp_session_dict.get("http_shared_srv")
                assert s is session, "Sub-thread should see the same session object"

                result = self.mgr.managed_stack.run_async(
                    s.call_tool, "echo", {"message": "from http worker"}
                )
                _assert_text_contains(result, "Echo: from http worker")
            except Exception as e:
                errors.append(e)

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=30)
        assert not errors, f"Worker thread error: {errors[0]}"


# =========================================================================
#  4. MCPSessionManager — SSE
# =========================================================================

class TestMCPSessionManagerSSE:
    """Test connect, cache, and cleanup via MCPSessionManager (SSE)."""

    def setup_method(self):
        self.mgr = MCPSessionManager()
        self.mgr.init_session()

    def teardown_method(self):
        self.mgr.close_session()

    def test_connect_and_cache(self, sse_server):
        s1 = self.mgr.get_mcp_server_session(
            server_name="sse_srv", **_sse_connect_args()
        )
        s2 = self.mgr.get_mcp_server_session(
            server_name="sse_srv", **_sse_connect_args()
        )
        assert s1 is s2

    def test_call_tool_sync(self, sse_server):
        session = self.mgr.get_mcp_server_session(
            server_name="sse_sync_srv", **_sse_connect_args()
        )
        result = self.mgr.managed_stack.run_async(
            session.call_tool, "echo", {"message": "sse sync"}
        )
        _assert_text_contains(result, "Echo: sse sync")

    def test_call_tool_async(self, sse_server):
        async def _run():
            session = await self.mgr.get_mcp_server_session_async(
                server_name="sse_async_srv", **_sse_connect_args()
            )
            result = await asyncio.to_thread(
                self.mgr.managed_stack.run_async,
                session.call_tool, "add", {"a": 55, "b": 45},
            )
            _assert_text_contains(result, "100")

        asyncio.run(_run())


# =========================================================================
#  5. MCPTempClient — HTTP transports
# =========================================================================

class TestMCPTempClientHTTP:
    """Test the sync context-manager based temp client over HTTP."""

    def test_list_tools_streamable_http(self, streamable_http_server):
        with MCPTempClient(_streamable_http_connect_args()) as client:
            tools_list = client.list_tools()

        names = [t.name for t in tools_list.tools]
        assert "echo" in names
        assert "add" in names

    def test_list_tools_sse(self, sse_server):
        with MCPTempClient(_sse_connect_args()) as client:
            tools_list = client.list_tools()

        names = [t.name for t in tools_list.tools]
        assert "echo" in names
        assert "add" in names

    def test_context_manager_cleanup(self, streamable_http_server):
        with MCPTempClient(_streamable_http_connect_args()) as client:
            _ = client.list_tools()
        # If we get here without error, cleanup succeeded.


# =========================================================================
#  6. MCPTool — streamable-http execute() and async_execute()
# =========================================================================

class TestMCPToolExecutionHTTP:
    """Test MCPTool.execute and MCPTool.async_execute over streamable-http."""

    def setup_method(self):
        self.mgr = MCPSessionManager()
        self.mgr.init_session()

    def teardown_method(self):
        self.mgr.close_session()

    @staticmethod
    def _make_tool(tool_name: str, input_keys: list, description: str = ""):
        from agentuniverse.agent.action.tool.mcp_tool import MCPTool

        return MCPTool(
            name=f"http_test__{tool_name}",
            server_name="http_tool_test_srv",
            transport="streamable_http",
            url=STREAMABLE_HTTP_URL,
            origin_tool_name=tool_name,
            input_keys=input_keys,
            description=description or f"Test {tool_name} (http)",
            args_model_schema={
                "type": "object",
                "properties": {
                    k: {"type": "string"} for k in input_keys
                },
                "required": input_keys,
            },
        )

    def test_sync_execute_echo(self, streamable_http_server):
        tool = self._make_tool("echo", ["message"])
        result = tool.execute(message="http sync works")
        _assert_text_contains(result, "Echo: http sync works")

    def test_sync_execute_add(self, streamable_http_server):
        tool = self._make_tool("add", ["a", "b"])
        result = tool.execute(a=100, b=200)
        _assert_text_contains(result, "300")

    def test_async_execute_echo(self, streamable_http_server):
        tool = self._make_tool("echo", ["message"])

        async def _run():
            result = await tool.async_execute(message="http async works")
            _assert_text_contains(result, "Echo: http async works")

        asyncio.run(_run())

    def test_async_execute_add(self, streamable_http_server):
        tool = self._make_tool("add", ["a", "b"])

        async def _run():
            result = await tool.async_execute(a=7, b=8)
            _assert_text_contains(result, "15")

        asyncio.run(_run())

    def test_sync_and_async_share_session(self, streamable_http_server):
        tool = self._make_tool("echo", ["message"])

        tool.execute(message="first")

        async def _run():
            result = await tool.async_execute(message="second")
            _assert_text_contains(result, "Echo: second")

        asyncio.run(_run())

        assert "http_tool_test_srv" in self.mgr.mcp_session_dict


# =========================================================================
#  7. MCPTool — SSE execute() and async_execute()
# =========================================================================

class TestMCPToolExecutionSSE:
    """Test MCPTool.execute and MCPTool.async_execute over SSE."""

    def setup_method(self):
        self.mgr = MCPSessionManager()
        self.mgr.init_session()

    def teardown_method(self):
        self.mgr.close_session()

    @staticmethod
    def _make_tool(tool_name: str, input_keys: list, description: str = ""):
        from agentuniverse.agent.action.tool.mcp_tool import MCPTool

        return MCPTool(
            name=f"sse_test__{tool_name}",
            server_name="sse_tool_test_srv",
            transport="sse",
            url=SSE_URL,
            origin_tool_name=tool_name,
            input_keys=input_keys,
            description=description or f"Test {tool_name} (sse)",
            args_model_schema={
                "type": "object",
                "properties": {
                    k: {"type": "string"} for k in input_keys
                },
                "required": input_keys,
            },
        )

    def test_sync_execute_echo(self, sse_server):
        tool = self._make_tool("echo", ["message"])
        result = tool.execute(message="sse sync works")
        _assert_text_contains(result, "Echo: sse sync works")

    def test_sync_execute_add(self, sse_server):
        tool = self._make_tool("add", ["a", "b"])
        result = tool.execute(a=33, b=67)
        _assert_text_contains(result, "100")

    def test_async_execute_echo(self, sse_server):
        tool = self._make_tool("echo", ["message"])

        async def _run():
            result = await tool.async_execute(message="sse async works")
            _assert_text_contains(result, "Echo: sse async works")

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
