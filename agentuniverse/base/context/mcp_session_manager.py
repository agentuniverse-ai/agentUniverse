# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
import os
import threading
from concurrent.futures import Future
from contextlib import AsyncExitStack, asynccontextmanager, contextmanager
# @Time    : 2024/3/11 16:02
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mcp_session_manager.py
from contextvars import ContextVar
from typing import Any
from typing import Literal
from datetime import timedelta

from anyio.from_thread import start_blocking_portal
from mcp import StdioServerParameters, stdio_client, ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

from agentuniverse.base.annotation.singleton import singleton

EncodingErrorHandler = Literal["strict", "ignore", "replace"]

DEFAULT_ENCODING = "utf-8"
DEFAULT_ENCODING_ERROR_HANDLER: EncodingErrorHandler = "strict"

DEFAULT_HTTP_TIMEOUT = 5
DEFAULT_SSE_READ_TIMEOUT = 60 * 5

DEFAULT_STREAMABLE_HTTP_TIMEOUT = timedelta(seconds=30)
DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT = timedelta(seconds=60 * 5)


class ManagedExitStack:
    """An exit stack where all async CM enter/exit operations happen in a
    single long-lived owner task, avoiding anyio's 'async exit in different
    scope' error.

    Internally spins up an AnyIO blocking portal (a background thread with
    its own event loop) and starts an owner task that holds an AsyncExitStack.
    All context manager operations are dispatched to the owner task via a
    command queue, ensuring __aenter__ and __aexit__ always run in the same
    anyio task scope.

    Safe to call from any thread or asyncio task.
    """

    def __init__(self) -> None:
        self._portal_cm = start_blocking_portal()
        self._portal = self._portal_cm.__enter__()
        self._queue: asyncio.Queue | None = None
        self._ready = threading.Event()
        self._portal.start_task_soon(self._owner_loop)
        self._ready.wait()

    async def _owner_loop(self) -> None:
        """Single long-lived task that owns the AsyncExitStack.

        All enter_async_context and aclose operations happen here, so
        __aenter__ and __aexit__ of each CM always run in the same task.
        """
        async with AsyncExitStack() as stack:
            self._queue = asyncio.Queue()
            self._ready.set()

            while True:
                cmd, args, future = await self._queue.get()
                try:
                    if cmd == 'enter':
                        result = await stack.enter_async_context(args[0])
                        future.set_result(result)
                    elif cmd == 'run':
                        func, func_args = args
                        result = await func(*func_args)
                        future.set_result(result)
                    elif cmd == 'close':
                        future.set_result(None)
                        break
                except Exception as e:
                    future.set_exception(e)
        # After break, the `async with` block exits naturally,
        # calling stack.aclose() which runs all __aexit__ in THIS task.

    def _send_cmd(self, cmd: str, args: tuple = (), timeout: float = 60) -> Any:
        """Send a command to the owner task and block until it completes."""
        future: Future = Future()
        self._portal.call(self._queue.put, (cmd, args, future))
        return future.result(timeout=timeout)

    def enter_async_context(self, cm) -> Any:
        """Enter an async context manager in the owner task.

        Safe to call from any thread or asyncio task.
        """
        return self._send_cmd('enter', (cm,))

    def run_async(self, func, *args) -> Any:
        """Run an async callable in the owner task.

        Safe to call from any thread or asyncio task.
        """
        return self._send_cmd('run', (func, args))

    def close(self) -> None:
        """Signal the owner task to close all CMs and shut down the portal."""
        try:
            self._send_cmd('close')
        except RuntimeError:
            # Portal may already be stopped (e.g. background thread exited);
            # proceed to shut down the portal context manager anyway.
            pass
        finally:
            try:
                self._portal_cm.__exit__(None, None, None)
            except RuntimeError:
                pass


class AsyncManagedExitStack:
    """Async counterpart of ManagedExitStack.

    Uses a dedicated asyncio.Task (instead of a background thread + portal)
    as the owner of an AsyncExitStack.  All __aenter__/__aexit__ operations
    are dispatched to the owner task via an asyncio.Queue, satisfying
    anyio's requirement that cancel scopes are entered/exited in the
    same task.

    session.call_tool() etc. can still be called directly from any task —
    only context-manager lifecycle needs the owner.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue = asyncio.Queue()
        self._ready: asyncio.Event = asyncio.Event()
        self._owner_task: asyncio.Task | None = None
        self._start_lock: asyncio.Lock = asyncio.Lock()
        self._started: bool = False

    async def _ensure_started(self) -> None:
        if self._started:
            return
        async with self._start_lock:
            if self._started:
                return
            self._owner_task = asyncio.create_task(self._owner_loop())
            await self._ready.wait()
            self._started = True

    async def _owner_loop(self) -> None:
        """Single long-lived task that owns the AsyncExitStack."""
        async with AsyncExitStack() as stack:
            self._ready.set()
            while True:
                cmd, args, future = await self._queue.get()
                try:
                    if cmd == 'enter':
                        result = await stack.enter_async_context(args[0])
                        future.set_result(result)
                    elif cmd == 'run':
                        func, func_args = args
                        result = await func(*func_args)
                        future.set_result(result)
                    elif cmd == 'close':
                        future.set_result(None)
                        break
                except Exception as e:
                    future.set_exception(e)
        # After break, the `async with` block exits naturally,
        # calling stack.aclose() which runs all __aexit__ in THIS task.

    async def enter_async_context(self, cm) -> Any:
        """Enter an async context manager in the owner task."""
        await self._ensure_started()
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self._queue.put(('enter', (cm,), future))
        return await future

    async def run_async(self, func, *args) -> Any:
        """Run an async callable in the owner task."""
        await self._ensure_started()
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self._queue.put(('run', (func, args), future))
        return await future

    async def aclose(self) -> None:
        """Signal the owner task to close all CMs and shut down."""
        if not self._started:
            return
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self._queue.put(('close', (), future))
        await future
        if self._owner_task:
            await self._owner_task


class MCPTempClient:
    """A temporary MCP client that auto-connects and cleans up via `with`.

    Creates its own ManagedExitStack for a short-lived connection, typically
    used to fetch tool metadata during initialization.

    Example:
        >>> with MCPTempClient({"transport": "stdio", "command": "uvx", "args": ["my-server"]}) as cli:
        ...     tools = cli.list_tools()
    """

    def __init__(self, connection_args: dict):
        self.connection_args = connection_args
        self._stack: ManagedExitStack | None = None
        self._session: ClientSession | None = None

    @property
    def session(self) -> ClientSession:
        return self._session

    def list_tools(self):
        """List tools from the MCP server (sync, via owner task)."""
        return self._stack.run_async(self._session.list_tools)

    def __enter__(self) -> "MCPTempClient":
        self._stack = ManagedExitStack()
        try:
            self._session = MCPSessionManager().connect_to_server(
                server_name="__tmp_client__",
                managed_stack=self._stack,
                **self.connection_args
            )
            return self
        except Exception:
            self._stack.close()
            self._stack = None
            raise

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._stack is not None:
            self._stack.close()
            self._stack = None


@singleton
class MCPSessionManager:
    """Manages MCP server sessions with per-request isolation.

    Sessions are stored in ContextVar (isolated across requests).
    Within a request, sub-threads share sessions via save/recover.
    The ManagedExitStack ensures all async CM operations happen in
    a single owner task, avoiding scope errors.
    """

    def __init__(self):
        self.__mcp_session_dict: ContextVar[dict | None] = ContextVar("__mcp_session_dict__")
        self.__managed_stack: ContextVar[ManagedExitStack | None] = ContextVar("__mcp_managed_stack__")
        # Async-native session management (no ManagedExitStack / to_thread)
        self.__async_exit_stack: ContextVar[AsyncManagedExitStack | None] = ContextVar("__async_exit_stack__")
        self.__async_session_dict: ContextVar[dict | None] = ContextVar("__async_session_dict__")
        self.__async_connect_lock: ContextVar[asyncio.Lock | None] = ContextVar("__async_connect_lock__")

    def init_session(self) -> None:
        """Initialize a new MCP session scope for the current request."""
        self.__managed_stack.set(ManagedExitStack())
        self.__mcp_session_dict.set({})

    @property
    def mcp_session_dict(self) -> dict:
        val = self.__mcp_session_dict.get(None)
        if val is None:
            val = {}
            self.__mcp_session_dict.set(val)
        return val

    @property
    def managed_stack(self) -> ManagedExitStack:
        val = self.__managed_stack.get(None)
        if val is None:
            val = ManagedExitStack()
            self.__managed_stack.set(val)
        return val

    @property
    def async_exit_stack(self) -> AsyncManagedExitStack:
        val = self.__async_exit_stack.get(None)
        if val is None:
            val = AsyncManagedExitStack()
            self.__async_exit_stack.set(val)
        return val

    @property
    def async_session_dict(self) -> dict:
        val = self.__async_session_dict.get(None)
        if val is None:
            val = {}
            self.__async_session_dict.set(val)
        return val

    @property
    def async_connect_lock(self) -> asyncio.Lock:
        val = self.__async_connect_lock.get(None)
        if val is None:
            val = asyncio.Lock()
            self.__async_connect_lock.set(val)
        return val

    # ------------------------------------------------------------------ #
    #  Session save / recover / cleanup
    # ------------------------------------------------------------------ #

    def save_mcp_session(self) -> dict:
        """Save current session dict and managed stack references for
        cross-thread propagation.

        Both the session dict and the managed stack are shared so that
        sub-threads can use existing sessions AND route async calls
        (like session.call_tool) through the original owner task.

        Sub-threads should NOT call close_session() — only the request
        owner does that. end_context() / detach_session() are safe to
        call from sub-threads (they just clear ContextVar references).
        """
        return {
            'mcp_session_dict': self.__mcp_session_dict.get(None),
            'managed_stack': self.__managed_stack.get(None),
        }

    def recover_mcp_session(self, mcp_session_dict, managed_stack=None) -> None:
        """Recover session dict and managed stack in a sub-thread context.

        The sub-thread gets access to the same session objects and can
        route async calls through the shared managed stack, but does not
        own the lifecycle (should not call close_session).
        """
        self.__mcp_session_dict.set(mcp_session_dict)
        if managed_stack is not None:
            self.__managed_stack.set(managed_stack)

    def detach_session(self) -> None:
        """Detach session references from current context without closing.

        Used by sub-threads when they finish — just removes ContextVar
        references, does not close any connections.
        """
        self.__mcp_session_dict.set(None)
        self.__managed_stack.set(None)

    def close_session(self) -> None:
        """Close all MCP connections and clean up.

        Should only be called by the request owner (the code path that
        called init_session). Closes the ManagedExitStack which shuts
        down all connections.
        """
        stack = self.__managed_stack.get(None)
        if stack is not None:
            try:
                stack.close()
            except RuntimeError:
                # Portal may already have been shut down; ignore and
                # continue with ContextVar cleanup.
                pass
        self.__managed_stack.set(None)
        self.__mcp_session_dict.set(None)

    async def init_session_async(self) -> None:
        """Initialize a new async MCP session scope for the current request."""
        self.__async_exit_stack.set(AsyncManagedExitStack())
        self.__async_session_dict.set({})
        self.__async_connect_lock.set(asyncio.Lock())

    async def close_session_async(self) -> None:
        """Close all async MCP connections and clean up.

        Should only be called by the request owner (the code path that
        called init_session_async).
        """
        stack = self.__async_exit_stack.get(None)
        if stack is not None:
            await stack.aclose()
        self.__async_exit_stack.set(None)
        self.__async_session_dict.set(None)
        self.__async_connect_lock.set(None)

    @contextmanager
    def session_scope(self):
        """Sync context manager for request-scoped MCP sessions.

        Usage::
            with MCPSessionManager().session_scope():
                agent.run(**kwargs)
        """
        self.init_session()
        try:
            yield
        finally:
            self.close_session()

    @asynccontextmanager
    async def async_session_scope(self):
        """Async context manager for request-scoped MCP sessions.

        Usage::
            async with MCPSessionManager().async_session_scope():
                await agent.async_run(**kwargs)
        """
        await self.init_session_async()
        try:
            yield
        finally:
            await self.close_session_async()

    # ------------------------------------------------------------------ #
    #  Get or create session
    # ------------------------------------------------------------------ #

    def get_mcp_server_session(
        self,
        server_name: str,
        transport: Literal["stdio", "sse", "websocket", "streamable_http"] = "stdio",
        **kwargs,
    ) -> ClientSession:
        """Get a cached session or create a new connection (sync).

        Safe to call from any thread or asyncio task.
        """
        session = self.mcp_session_dict.get(server_name)
        if session is not None:
            return session
        return self.connect_to_server(
            server_name=server_name, transport=transport, **kwargs
        )

    async def get_mcp_server_session_async(
        self,
        server_name: str,
        transport: Literal["stdio", "sse", "websocket", "streamable_http"] = "stdio",
        **kwargs,
    ) -> ClientSession:
        """Get a cached async session or create a new connection.

        Uses double-check locking to avoid duplicate connections when
        multiple coroutines concurrently request the same server.
        """
        session = self.async_session_dict.get(server_name)
        if session is not None:
            return session
        async with self.async_connect_lock:
            # Double check after acquiring lock
            session = self.async_session_dict.get(server_name)
            if session is not None:
                return session
            return await self._async_connect_to_server(
                server_name=server_name, transport=transport, **kwargs
            )

    # ------------------------------------------------------------------ #
    #  Connect (unified — one implementation per transport)
    # ------------------------------------------------------------------ #

    def connect_to_server(
        self,
        server_name: str,
        transport: Literal["stdio", "sse", "websocket", "streamable_http"] = "stdio",
        managed_stack: ManagedExitStack | None = None,
        **kwargs,
    ) -> ClientSession:
        """Connect to an MCP server using the specified transport.

        Args:
            server_name: Unique key for caching this connection.
            transport: One of "stdio", "sse", "websocket", "streamable_http".
            managed_stack: Optional external stack (used by MCPTempClient).
                           If None, uses the request-scoped stack.
            **kwargs: Transport-specific parameters.

        Returns:
            ClientSession: The connected and initialized session.
        """
        if transport == "stdio":
            return self._connect_via_stdio(server_name, managed_stack=managed_stack, **kwargs)
        elif transport == "sse":
            return self._connect_via_sse(server_name, managed_stack=managed_stack, **kwargs)
        elif transport == "streamable_http":
            return self._connect_via_streamable_http(server_name, managed_stack=managed_stack, **kwargs)
        elif transport == "websocket":
            return self._connect_via_websocket(server_name, managed_stack=managed_stack, **kwargs)
        else:
            raise ValueError(
                f"Unsupported transport: {transport}. "
                f"Must be one of: stdio, sse, websocket, streamable_http"
            )

    def _connect_via_stdio(
        self,
        server_name: str,
        *,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
        encoding: str = DEFAULT_ENCODING,
        encoding_error_handler: EncodingErrorHandler = DEFAULT_ENCODING_ERROR_HANDLER,
        session_kwargs: dict | None = None,
        managed_stack: ManagedExitStack | None = None,
    ) -> ClientSession:
        env = env or {}
        if "PATH" not in env:
            env["PATH"] = os.environ.get("PATH", "")

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
            encoding=encoding,
            encoding_error_handler=encoding_error_handler,
        )

        stack = managed_stack if managed_stack is not None else self.managed_stack
        read, write = stack.enter_async_context(stdio_client(server_params))
        session_kwargs = session_kwargs or {}
        session = stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        stack.run_async(session.initialize)

        if managed_stack is None:
            self.mcp_session_dict[server_name] = session
        return session

    def _connect_via_sse(
        self,
        server_name: str,
        *,
        url: str,
        headers: dict | None = None,
        timeout: float = DEFAULT_HTTP_TIMEOUT,
        sse_read_timeout: float = DEFAULT_SSE_READ_TIMEOUT,
        session_kwargs: dict | None = None,
        managed_stack: ManagedExitStack | None = None,
    ) -> ClientSession:
        stack = managed_stack if managed_stack is not None else self.managed_stack
        read, write = stack.enter_async_context(
            sse_client(url, headers, timeout, sse_read_timeout)
        )
        session_kwargs = session_kwargs or {}
        session = stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        stack.run_async(session.initialize)

        if managed_stack is None:
            self.mcp_session_dict[server_name] = session
        return session

    def _connect_via_streamable_http(
        self,
        server_name: str,
        *,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: timedelta = DEFAULT_STREAMABLE_HTTP_TIMEOUT,
        sse_read_timeout: timedelta = DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT,
        session_kwargs: dict[str, Any] | None = None,
        managed_stack: ManagedExitStack | None = None,
    ) -> ClientSession:
        stack = managed_stack if managed_stack is not None else self.managed_stack
        read, write, _ = stack.enter_async_context(
            streamablehttp_client(url, headers, timeout, sse_read_timeout)
        )
        session_kwargs = session_kwargs or {}
        session = stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        stack.run_async(session.initialize)

        if managed_stack is None:
            self.mcp_session_dict[server_name] = session
        return session

    def _connect_via_websocket(
        self,
        server_name: str,
        *,
        url: str,
        session_kwargs: dict[str, Any] | None = None,
        managed_stack: ManagedExitStack | None = None,
    ) -> ClientSession:
        try:
            from mcp.client.websocket import websocket_client
        except ImportError:
            raise ImportError(
                "Could not import websocket_client. "
                "To use Websocket connections, please install the required "
                "dependency with: 'pip install mcp[ws]' or 'pip install websockets'"
            ) from None

        stack = managed_stack if managed_stack is not None else self.managed_stack
        read, write = stack.enter_async_context(websocket_client(url))
        session_kwargs = session_kwargs or {}
        session = stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        stack.run_async(session.initialize)

        if managed_stack is None:
            self.mcp_session_dict[server_name] = session
        return session

    # ------------------------------------------------------------------ #
    #  Async-native connect (no ManagedExitStack / to_thread)
    # ------------------------------------------------------------------ #

    async def _async_connect_to_server(
        self,
        server_name: str,
        transport: Literal["stdio", "sse", "websocket", "streamable_http"] = "stdio",
        **kwargs,
    ) -> ClientSession:
        if transport == "stdio":
            return await self._async_connect_via_stdio(server_name, **kwargs)
        elif transport == "sse":
            return await self._async_connect_via_sse(server_name, **kwargs)
        elif transport == "streamable_http":
            return await self._async_connect_via_streamable_http(server_name, **kwargs)
        elif transport == "websocket":
            return await self._async_connect_via_websocket(server_name, **kwargs)
        else:
            raise ValueError(
                f"Unsupported transport: {transport}. "
                f"Must be one of: stdio, sse, websocket, streamable_http"
            )

    async def _async_connect_via_stdio(
        self,
        server_name: str,
        *,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
        encoding: str = DEFAULT_ENCODING,
        encoding_error_handler: EncodingErrorHandler = DEFAULT_ENCODING_ERROR_HANDLER,
        session_kwargs: dict | None = None,
    ) -> ClientSession:
        env = env or {}
        if "PATH" not in env:
            env["PATH"] = os.environ.get("PATH", "")

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
            encoding=encoding,
            encoding_error_handler=encoding_error_handler,
        )

        stack = self.async_exit_stack
        read, write = await stack.enter_async_context(stdio_client(server_params))
        session_kwargs = session_kwargs or {}
        session = await stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        await stack.run_async(session.initialize)
        self.async_session_dict[server_name] = session
        return session

    async def _async_connect_via_sse(
        self,
        server_name: str,
        *,
        url: str,
        headers: dict | None = None,
        timeout: float = DEFAULT_HTTP_TIMEOUT,
        sse_read_timeout: float = DEFAULT_SSE_READ_TIMEOUT,
        session_kwargs: dict | None = None,
    ) -> ClientSession:
        stack = self.async_exit_stack
        read, write = await stack.enter_async_context(
            sse_client(url, headers, timeout, sse_read_timeout)
        )
        session_kwargs = session_kwargs or {}
        session = await stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        await stack.run_async(session.initialize)
        self.async_session_dict[server_name] = session
        return session

    async def _async_connect_via_streamable_http(
        self,
        server_name: str,
        *,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: timedelta = DEFAULT_STREAMABLE_HTTP_TIMEOUT,
        sse_read_timeout: timedelta = DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT,
        session_kwargs: dict[str, Any] | None = None,
    ) -> ClientSession:
        stack = self.async_exit_stack
        read, write, _ = await stack.enter_async_context(
            streamablehttp_client(url, headers, timeout, sse_read_timeout)
        )
        session_kwargs = session_kwargs or {}
        session = await stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        await stack.run_async(session.initialize)
        self.async_session_dict[server_name] = session
        return session

    async def _async_connect_via_websocket(
        self,
        server_name: str,
        *,
        url: str,
        session_kwargs: dict[str, Any] | None = None,
    ) -> ClientSession:
        try:
            from mcp.client.websocket import websocket_client
        except ImportError:
            raise ImportError(
                "Could not import websocket_client. "
                "To use Websocket connections, please install the required "
                "dependency with: 'pip install mcp[ws]' or 'pip install websockets'"
            ) from None

        stack = self.async_exit_stack
        read, write = await stack.enter_async_context(websocket_client(url))
        session_kwargs = session_kwargs or {}
        session = await stack.enter_async_context(ClientSession(read, write, **session_kwargs))
        await stack.run_async(session.initialize)
        self.async_session_dict[server_name] = session
        return session
