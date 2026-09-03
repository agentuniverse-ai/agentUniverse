import sys
from contextlib import asynccontextmanager
from types import ModuleType
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from agentuniverse.base.context import mcp_session_manager
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager, MCPTempClient


class _TrackedClientSession:
    def __init__(
        self,
        events: list[str],
        initialize_error: Exception | None = None,
    ) -> None:
        self.events = events
        self.initialize_error = initialize_error

    async def __aenter__(self) -> "_TrackedClientSession":
        self.events.append("session_enter")
        return self

    async def __aexit__(self, *_args) -> None:
        self.events.append("session_exit")

    async def initialize(self) -> None:
        self.events.append("session_initialize")
        if self.initialize_error:
            raise self.initialize_error


def _fake_websocket_module(events: list[str]) -> ModuleType:
    @asynccontextmanager
    async def websocket_client(_url: str):
        events.append("websocket_enter")
        try:
            yield "reader", "writer"
        finally:
            events.append("websocket_exit")

    websocket_module = ModuleType("mcp.client.websocket")
    websocket_module.websocket_client = websocket_client
    return websocket_module


def _session_factory(
    events: list[str],
    initialize_error: Exception | None = None,
):
    def create_session(*_args, **_kwargs) -> _TrackedClientSession:
        return _TrackedClientSession(events, initialize_error)

    return create_session


class MCPTempClientWebSocketTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.manager = MCPSessionManager()
        self.manager.init_session()

    async def asyncTearDown(self) -> None:
        await self.manager.safe_close_stack_async()

    async def test_temp_client_closes_websocket_resources_without_caching(self) -> None:
        events: list[str] = []
        websocket_module = _fake_websocket_module(events)

        with (
            patch.dict(sys.modules, {"mcp.client.websocket": websocket_module}),
            patch.object(
                mcp_session_manager,
                "ClientSession",
                _session_factory(events),
            ),
        ):
            async with MCPTempClient({"transport": "websocket", "url": "ws://example.test"}) as client:
                self.assertIsInstance(client.session, _TrackedClientSession)
                self.assertEqual(
                    events,
                    ["websocket_enter", "session_enter", "session_initialize"],
                )

        self.assertEqual(
            events,
            [
                "websocket_enter",
                "session_enter",
                "session_initialize",
                "session_exit",
                "websocket_exit",
            ],
        )
        self.assertNotIn("tmp_client", self.manager.mcp_session_dict)

    async def test_manager_owned_websocket_remains_cached_until_manager_closes(
        self,
    ) -> None:
        events: list[str] = []
        websocket_module = _fake_websocket_module(events)

        with (
            patch.dict(sys.modules, {"mcp.client.websocket": websocket_module}),
            patch.object(
                mcp_session_manager,
                "ClientSession",
                _session_factory(events),
            ),
        ):
            session = await self.manager.connect_to_server(
                server_name="shared_server",
                transport="websocket",
                url="ws://example.test",
            )

            self.assertIs(session, self.manager.mcp_session_dict["shared_server"])
            self.assertEqual(
                events,
                ["websocket_enter", "session_enter", "session_initialize"],
            )

            await self.manager.safe_close_stack_async()

        self.assertEqual(
            events,
            [
                "websocket_enter",
                "session_enter",
                "session_initialize",
                "session_exit",
                "websocket_exit",
            ],
        )

    async def test_temp_client_closes_websocket_resources_when_initialize_fails(
        self,
    ) -> None:
        events: list[str] = []
        websocket_module = _fake_websocket_module(events)

        with (
            patch.dict(sys.modules, {"mcp.client.websocket": websocket_module}),
            patch.object(
                mcp_session_manager,
                "ClientSession",
                _session_factory(events, RuntimeError("initialize failed")),
            ),
            self.assertRaisesRegex(RuntimeError, "initialize failed"),
        ):
            async with MCPTempClient({"transport": "websocket", "url": "ws://example.test"}):
                self.fail("MCPTempClient should not enter after initialization fails")

        self.assertEqual(
            events,
            [
                "websocket_enter",
                "session_enter",
                "session_initialize",
                "session_exit",
                "websocket_exit",
            ],
        )
        self.assertNotIn("tmp_client", self.manager.mcp_session_dict)
