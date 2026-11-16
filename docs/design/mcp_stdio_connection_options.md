# MCP stdio connection options / MCP 本地进程连接选项

`MCPTool` and `MCPToolkit` merge `connection_kwargs` into their transport
arguments for stdio as well as the existing remote transports. Previously,
the stdio branch returned early, so configured session options were silently
ignored both during tool discovery and during execution of a registered tool.

For example, Python callers can set the MCP SDK's session read timeout:

```python
from datetime import timedelta
from agentuniverse.agent.action.tool.mcp_tool import MCPTool

tool = MCPTool(
    name="echo",
    server_name="local_server",
    transport="stdio",
    command="python",
    args=["my_mcp_server.py"],
    connection_kwargs={
        "session_kwargs": {"read_timeout_seconds": timedelta(seconds=30)},
    },
)
```

The same option works on `MCPToolkit` and the tools it registers. Values are
passed to the existing session manager and native MCP SDK; use their expected
types (the session timeout shown here is a `timedelta`, not a numeric YAML
value). With no additional options, stdio uses the existing defaults. Normal
`command`, `args`, and `env` fields still configure the subprocess. As with
remote transports, explicitly supplied connection options override matching
transport arguments.

`MCPTool` 和 `MCPToolkit` 的 stdio 连接现在也会合并 `connection_kwargs`。
原先 stdio 分支提前返回，导致工具发现阶段和已注册工具执行阶段的会话选项被
静默忽略，例如上面的会话读取超时配置无法生效。

工具包及其注册的工具同样支持该配置。参数继续交给现有会话管理器与原生 MCP
SDK 处理，必须使用它们要求的类型；示例中的超时使用 Python `timedelta`，
不是一个可直接替代它的 YAML 数值。不传额外选项时维持原有默认行为。
`command`、`args`、`env` 仍用于配置本地服务进程；与远程传输一致，额外连接
选项中显式提供的同名参数覆盖原参数。
