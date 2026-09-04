# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01 10:00
# @Author  : Yue Wang
# @FileName: test_mcp_session_manager.py
"""Unit tests for MCPSessionManager."""

import asyncio

import pytest

from agentuniverse.base.context.mcp_session_manager import (
    MCPSessionManager,
    SyncAsyncExitStack,
    pick_exit_stack,
)


class TestSyncAsyncExitStack:
    """Test suite for the sync/async bridge helpers."""

    def test_pick_exit_stack_returns_sync_stack_outside_loop(self):
        stack = pick_exit_stack()
        try:
            assert isinstance(stack, SyncAsyncExitStack)
        finally:
            stack.close()

    def test_sync_stack_runs_async_function(self):
        stack = SyncAsyncExitStack()
        try:
            async def add(a, b):
                return a + b

            assert stack.run_async(add, 2, 3) == 5
        finally:
            stack.close()

    def test_sync_stack_enter_async_context(self):
        from contextlib import asynccontextmanager

        entered = []

        @asynccontextmanager
        async def resource(value):
            entered.append(value)
            yield value

        stack = SyncAsyncExitStack()
        try:
            handle = stack.enter_async_context(resource(42))
            assert handle == 42
            assert entered == [42]
        finally:
            stack.close()


class TestMCPSessionManager:
    """Test suite for MCPSessionManager."""

    @pytest.fixture
    def manager(self):
        m = MCPSessionManager()
        m.init_session()
        yield m
        m.safe_close_stack()

    def test_pick_exit_stack_returns_async_stack_inside_loop(self):
        async def probe():
            from contextlib import AsyncExitStack

            stack = pick_exit_stack()
            try:
                assert isinstance(stack, AsyncExitStack)
            finally:
                await stack.aclose()

        asyncio.run(probe())

    def test_init_session_initializes_empty_state(self, manager):
        assert manager.mcp_session_dict == {}
        saved = manager.save_mcp_session()
        assert set(saved.keys()) == {'mcp_session_dict', 'exit_stack'}

    def test_mcp_session_dict_stores_servers(self, manager):
        fake_session = object()
        manager.mcp_session_dict['server_a'] = fake_session
        assert manager.mcp_session_dict['server_a'] is fake_session

    def test_get_session_sync_returns_cached_session(self, manager):
        fake_session = object()
        manager.mcp_session_dict['cached'] = fake_session
        assert manager.get_mcp_server_session_sync('cached') is fake_session

    def test_save_and_recover_restore_state(self, manager):
        saved = manager.save_mcp_session()
        manager.mcp_session_dict['temp'] = object()
        manager.recover_mcp_session(saved['mcp_session_dict'], saved['exit_stack'])
        assert manager.mcp_session_dict == saved['mcp_session_dict']
        assert manager.exit_stack is saved['exit_stack']

    def test_connect_to_server_requires_url_for_sse(self):
        async def attempt():
            with pytest.raises(ValueError):
                await MCPSessionManager().connect_to_server(
                    server_name='x', transport='sse')

        asyncio.run(attempt())

    def test_connect_to_server_rejects_unknown_transport(self):
        async def attempt():
            with pytest.raises(ValueError):
                await MCPSessionManager().connect_to_server(
                    server_name='x', transport='carrier_pigeon')

        asyncio.run(attempt())
