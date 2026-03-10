#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A minimal MCP server for local HTTP testing.

Exposes two tools via HTTP transport (SSE or streamable-http):
  - echo(message: str)  → returns "Echo: {message}"
  - add(a: int, b: int) → returns the sum as string

Usage:
    # streamable-http (default, endpoint: /mcp)
    python mock_mcp_http_server.py --transport streamable-http --port 18765

    # sse (endpoint: /sse)
    python mock_mcp_http_server.py --transport sse --port 18766
"""
import argparse

from mcp.server.fastmcp import FastMCP

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock MCP HTTP server for testing")
    parser.add_argument(
        "--transport",
        default="streamable-http",
        choices=["sse", "streamable-http"],
        help="Transport type (default: streamable-http)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18765)
    args = parser.parse_args()

    # host/port are constructor params, not run() params
    mcp = FastMCP("mock-http-test-server", host=args.host, port=args.port)

    @mcp.tool()
    def echo(message: str) -> str:
        """Echo back the input message."""
        return f"Echo: {message}"

    @mcp.tool()
    def add(a: int, b: int) -> str:
        """Add two numbers and return the result as a string."""
        return str(int(a) + int(b))

    mcp.run(transport=args.transport)
