"""Real SDK stdio server with a deliberately slow tool, for connection options."""

import json
import sys
from pathlib import Path

import anyio
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

server = Server("connection-options-fixture")
log = Path(sys.argv[1])
delay = float(sys.argv[3])


@server.list_tools()
async def list_tools():
    if len(sys.argv) > 2 and sys.argv[2] == "slow_discovery":
        log.write_text(json.dumps({"method": "tools/list"}), encoding="utf-8")
        await anyio.sleep(delay)
    return [types.Tool(name="echo", description="Echo text after a short delay", inputSchema={
        "type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]})]


@server.call_tool()
async def call_tool(name, arguments):
    log.write_text(json.dumps({"name": name, "arguments": arguments}), encoding="utf-8")
    await anyio.sleep(delay)
    return [types.TextContent(type="text", text=arguments["value"])]


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    anyio.run(main)
