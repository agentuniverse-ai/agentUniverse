"""Discover every tools/list page within the caller's MCP session."""
from typing import AsyncIterator

from mcp import ClientSession
from mcp.types import Tool


async def iter_mcp_tools(session: ClientSession) -> AsyncIterator[Tool]:
    """Yield tools in server order without interpreting opaque cursor values."""
    cursor = None
    seen_cursors = set()
    while True:
        page = (await session.list_tools() if cursor is None
                else await session.list_tools(cursor=cursor))
        for tool in page.tools:
            yield tool
        cursor = page.nextCursor
        if cursor is None:
            return
        if cursor in seen_cursors:
            raise ValueError('MCP tools/list returned a repeated pagination cursor')
        seen_cursors.add(cursor)
