#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.base.context.mcp_session_manager import MCPSessionManager


class FakeSyncAsyncExitStack:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class TestMCPSessionManager(unittest.IsolatedAsyncioTestCase):
    async def test_clear_session_closes_sync_stack(self):
        manager = MCPSessionManager()
        stack = FakeSyncAsyncExitStack()
        manager.recover_mcp_session({"server": object()}, stack)

        try:
            with patch(
                "agentuniverse.base.context.mcp_session_manager."
                "SyncAsyncExitStack",
                FakeSyncAsyncExitStack,
            ):
                await manager.clear_session()
        finally:
            manager.recover_mcp_session(None, None)

        self.assertTrue(stack.closed)


if __name__ == "__main__":
    unittest.main()
