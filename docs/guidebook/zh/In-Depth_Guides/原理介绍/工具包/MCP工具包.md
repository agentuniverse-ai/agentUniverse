# 如何定义一个MCP工具包

MCPToolkit是工具包中的一个特殊分类，它能够通过配置链接MCPServer，获取工具信息，并通过这些信息自动创建对应的MCPTool。

MCPServer当前版本可分为三类通信模式,1)通过标准输入输出流(stdio)连接，2)通过SSE方式连接，3）通过Streamable HTTP连接，下列是各类不同MCP模式的配置yaml样例。

通过标准输入输出流连接的MCPToolkit定义示例如下：
```yaml
name: 'weather_toolkit'
description: |
  这是一个天气相关的工具包
transport: 'stdio'
command: 'python'
args:
  - 'stdio_server.py'
env:
  TIMEOUT: 100

metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

通过SSE连接的MCPToolkit定义示例如下：
```yaml
name: 'search_toolkit'
description: |
  这是一个搜索相关的工具包
transport: 'sse'
url: 'http://localhost:8000/sse'

metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

通过Streamable HTTP连接的MCPToolkit定义示例如下：
```yaml
name: 'weather'
transport: 'streamable_http'
url: 'http://localhost:8000/mcp'
metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

- 关于`transport`、`url`、`command`、`args`、`env`参数的填写方式请参考[MCP工具](../工具/MCP工具.md)

完整工具包定义示例可参考：[docx_toolkit](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/toolkit/docx_toolkit.yaml)

工具包调用可参考示例：[demo_agent_with_mcp_toolkit](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/agent/agent_instance/demo_agent_with_mcp_toolkit.yaml)

### 分页发现工具

MCP 服务可以通过多次 `tools/list` 分页返回工具。MCPToolkit 会在同一个临时会话中
继续读取 `nextCursor`，包括带有后续游标的空中间页，读取完成后再注册工具。
`include` 留空时按服务端顺序选取全部工具；显式填写时也可以选取后续页面中的工具。
MCPTool 按远端工具名逐页查找，找到后立即停止读取后续页面。

分页游标是不透明字符串，会原样传回服务端。游标重复或分页请求失败时会终止发现，
不会把不完整列表中的工具注册到工具包。无需添加配置。协议说明见
[MCP 分页规范](https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/pagination)。
