import asyncio
from contextlib import AsyncExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentuniverse.base.context.mcp_session_manager import (
    MCPSessionManager,
    MCPTempClient,
)


@pytest.mark.asyncio
async def test_mcp_temp_client_websocket_exit_stack_forwarded():
    """Verify that MCPTempClient with websocket transport forwards caller exit_stack and cleans up resources."""
    manager = MCPSessionManager()
    manager.init_session()

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()

    class FakeAsyncContext:
        def __init__(self, obj):
            self.obj = obj
            self.entered = False
            self.exited = False

        async def __aenter__(self):
            self.entered = True
            return self.obj

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.exited = True

    fake_transport = (MagicMock(), MagicMock())
    fake_transport_ctx = FakeAsyncContext(fake_transport)
    fake_session_ctx = FakeAsyncContext(mock_session)

    mock_websocket_client = MagicMock(return_value=fake_transport_ctx)
    mock_client_session_cls = MagicMock(return_value=fake_session_ctx)

    with patch.dict(
        "sys.modules",
        {
            "mcp.client.websocket": MagicMock(websocket_client=mock_websocket_client),
            "mcp": MagicMock(ClientSession=mock_client_session_cls),
        },
    ), patch(
        "agentuniverse.base.context.mcp_session_manager.ClientSession",
        mock_client_session_cls,
    ):
        async with MCPTempClient(
            {"transport": "websocket", "url": "ws://localhost:8000/ws"}
        ) as temp_client:
            assert temp_client.session == mock_session
            assert fake_transport_ctx.entered is True
            assert fake_session_ctx.entered is True
            # The temporary session should not be cached in global manager dict
            assert "tmp_client" not in manager.mcp_session_dict

        # After exiting the MCPTempClient context, resources must be closed
        assert fake_transport_ctx.exited is True
        assert fake_session_ctx.exited is True


@pytest.mark.asyncio
async def test_connect_to_server_websocket_forwards_exit_stack():
    """Verify MCPSessionManager.connect_to_server forwards exit_stack for websocket transport."""
    manager = MCPSessionManager()
    manager.init_session()

    caller_stack = AsyncExitStack()

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()

    with patch.object(
        manager, "connect_to_server_via_websocket", new_callable=AsyncMock
    ) as mock_ws_connect:
        mock_ws_connect.return_value = mock_session

        session = await manager.connect_to_server(
            server_name="test_ws",
            transport="websocket",
            url="ws://127.0.0.1:9000",
            exit_stack=caller_stack,
        )

        assert session == mock_session
        mock_ws_connect.assert_awaited_once_with(
            "test_ws",
            url="ws://127.0.0.1:9000",
            session_kwargs=None,
            exit_stack=caller_stack,
        )
