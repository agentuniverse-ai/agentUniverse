#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A minimal MCP server for local testing. No project dependencies needed.

Exposes two tools via stdio transport:
  - echo(message: str)  → returns "Echo: {message}"
  - add(a: int, b: int) → returns the sum as string

Usage:
    python mock_mcp_server.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mock-test-server")


@mcp.tool()
def echo(message: str) -> str:
    """Echo back the input message."""
    return f"Echo: {message}"


@mcp.tool()
def add(a: int, b: int) -> str:
    """Add two numbers and return the result as a string."""
    return str(int(a) + int(b))


if __name__ == "__main__":
    mcp.run()
