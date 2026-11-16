import pytest
from contextlib import AsyncExitStack

from agentuniverse.base.context import mcp_session_manager


def test_sync_cleanup_does_not_create_unused_portal(monkeypatch):
    manager = mcp_session_manager.MCPSessionManager()
    manager.recover_mcp_session(None, None)
    monkeypatch.setattr(mcp_session_manager, "pick_exit_stack",
                        lambda: pytest.fail("cleanup created an unused MCP exit stack"))

    manager.safe_close_stack()

    assert manager.save_mcp_session() == {"mcp_session_dict": None, "exit_stack": None}


@pytest.mark.asyncio
async def test_async_cleanup_still_closes_existing_stack():
    manager = mcp_session_manager.MCPSessionManager()
    stack = AsyncExitStack()
    closed = []
    stack.push_async_callback(lambda: record_close(closed))
    manager.recover_mcp_session({}, stack)

    await manager.safe_close_stack_async()

    assert closed == [True]
    assert manager.save_mcp_session() == {"mcp_session_dict": None, "exit_stack": None}


async def record_close(closed):
    closed.append(True)


@pytest.mark.asyncio
async def test_async_cleanup_does_not_create_unused_portal(monkeypatch):
    manager = mcp_session_manager.MCPSessionManager()
    manager.recover_mcp_session(None, None)
    monkeypatch.setattr(mcp_session_manager, "pick_exit_stack",
                        lambda: pytest.fail("cleanup created an unused MCP exit stack"))

    await manager.safe_close_stack_async()

    assert manager.save_mcp_session() == {"mcp_session_dict": None, "exit_stack": None}
