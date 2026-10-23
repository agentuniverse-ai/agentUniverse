"""A native MCP stdio server with deterministic tools/list pages."""
import json
from pathlib import Path
import sys

import anyio
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, ListToolsRequest, ListToolsResult, Tool


def tool(name):
    return Tool(name=name, description='description ' + name, inputSchema={
        'type': 'object', 'properties': {'value': {'type': 'string'}},
        'required': ['value'],
    })


async def main():
    mode, log_name = sys.argv[1:]
    log = Path(log_name)
    server = Server('pagination-fixture')

    @server.list_tools()
    async def list_tools(request: ListToolsRequest) -> ListToolsResult:
        cursor = request.params.cursor if request.params else None
        with log.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(cursor) + '\n')
        if mode == 'single':
            return ListToolsResult(tools=[tool('first'), tool('target'), tool('last')])
        if mode == 'empty':
            return ListToolsResult(tools=[])
        if cursor is None:
            return ListToolsResult(tools=[tool('first')],
                                   nextCursor='' if mode == 'empty_cursor' else 'opaque+/=1')
        if mode == 'error':
            raise McpError(ErrorData(code=-32602, message='fixture cursor expired'))
        if mode == 'cycle':
            return ListToolsResult(tools=[tool('last')], nextCursor='opaque+/=1')
        if mode == 'empty_cursor':
            assert cursor == ''
            return ListToolsResult(tools=[tool('target'), tool('last')])
        if cursor == 'opaque+/=1':
            return ListToolsResult(tools=[] if mode == 'empty_middle' else [tool('target')],
                                   nextCursor='opaque/end2')
        assert cursor == 'opaque/end2'
        names = ('target', 'last') if mode == 'empty_middle' else ('last',)
        return ListToolsResult(tools=[tool(name) for name in names])

    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == '__main__':
    anyio.run(main)
