"""Stdio PATH defaults belong to each connection, not caller configuration."""

import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from copy import deepcopy

import pytest

from agentuniverse.base.context import mcp_session_manager as module


class Session:
    def __init__(self, read, write, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def initialize(self):
        pass


@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("environment", [None, {}, {"APP_MODE": "test"}, {"APP_MODE": "test", "PATH": "explicit"}])
def test_stdio_environment_is_not_mutated_or_pinned(monkeypatch, sync, environment):
    environment = deepcopy(environment)
    captured = []
    original = deepcopy(environment)

    @asynccontextmanager
    async def transport(params):
        captured.append(dict(params.env))
        yield object(), object()

    monkeypatch.setattr(module, "stdio_client", transport)
    monkeypatch.setattr(module, "ClientSession", Session)
    manager = module.MCPSessionManager()
    saved = manager.save_mcp_session()

    async def connect_async():
        async with AsyncExitStack() as stack:
            return await manager.connect_to_server_via_stdio(
                "environment-test", command="unused", args=[], env=environment, exit_stack=stack)

    try:
        if sync:
            manager.init_session()
        for path in ["first-path", "second-path"]:
            monkeypatch.setenv("PATH", path)
            if sync:
                manager.connect_to_server_via_stdio_sync(
                    "environment-test", command="unused", args=[], env=environment)
            else:
                asyncio.run(connect_async())
            assert environment == original
            expected = dict(original or {})
            expected.setdefault("PATH", path)
            assert captured[-1] == expected
    finally:
        if sync:
            manager.safe_close_stack()
        manager.recover_mcp_session(**saved)
