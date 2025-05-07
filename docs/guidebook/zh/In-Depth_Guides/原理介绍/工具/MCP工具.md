# MCP工具

MCP工具是一类特殊的工具Tool，它通过调用MCPServer的Tool完成相应的任务。
根据MCPServer的种类可分为两类，一是通过标准输入输出流连接的MCPServer，另一种是通过SSE连接的MCPServer。

通过标准输入输出流连接的MCPTool定义示例如下：
```yaml
name: 'calculator'
description: |
  使用该工具可以执行搜索操作。工具的输入是你想搜索的内容。
server_name: 'demo_stdio_mcp_tool'
transport: 'stdio'
command: 'python'
args:
  - 'stdio_server.py'
env:
  TIMEOUT: 100

metadata:
  type: 'TOOL'
  module: 'agentuniverse.agent.action.tool.mcp_tool'
  class: 'MCPTool'
```

通过SSE连接的MCPTool定义示例如下：
```yaml
name: 'weather'
origin_tool_name: 'get_weather'
server_name: 'demo_http_mcp_tool'
transport: 'sse'
url: 'http://localhost:8000/sse'
metadata:
  type: 'TOOL'
  module: 'agentuniverse.agent.action.tool.mcp_tool'
  class: 'MCPTool'
```

- 在MCPTool中，name除了表示agentUniverse中工具的名称，也表示MCPServer中工具的名称。如果您希望使用一个不一样的名字，您可以使用`origin_tool_name`参数指定MCPServer中的真实工具名称
- description和普通Tool不同,允许为空。如果不主动填写，会使用MCPServer中对于该工具的描述作为默认description
- server_name用于标识一个唯一的MCPServer，统一server_name的MCPServer在请求过程中共享session
- transport取值分为`stdio`和`sse`，分别表示通过标准输入输出流和SSE连接MCPServer。当transport取值为`stdio`时，需要配置`command`和`args`参数用于通过命令启动一个本地的MCPServer。`env`为可选参数，类型是dict，表示运行时的环境变量。当transport取值为`sse`时，您需要配置`url`参数用于连接一个远程的MCPServer

工具定义示例可参考：[duckduckgo_search_mcp_tool](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/tool/duckduckgo_search_mcp_tool.yaml)

工具调用可参考示例：[demo_react_agent_with_single_mcp_tool](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/agent/agent_instance/demo_react_agent_with_single_mcp_tool.yaml)