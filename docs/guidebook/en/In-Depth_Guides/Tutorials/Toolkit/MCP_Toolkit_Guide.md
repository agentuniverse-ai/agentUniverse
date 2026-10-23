# Defining an MCP Toolkit

MCPToolkit is a specialized category within toolkit frameworks that establishes connectivity to MCPServer via configuration, retrieves tool information, and automatically generates corresponding MCPTool instances based on that information.

The current MCPServer version supports three communication modes:
* Standard input/output streams (stdio)
* Server-Sent Events(SSE)
* Streamable HTTP

Below are YAML configuration examples for each MCP communication mode:

1) Standard Input/Output Streams
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

2) SSE
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

3) Streamable HTTP
```yaml
name: 'weather'
transport: 'streamable_http'
url: 'http://localhost:8000/mcp'
metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

- Guidelines for filling transport, url, command, args, and env parameters can be found in [MCP Tool Guide](../Tool/MCP_Tool_Guide.md).

Complete toolkit definition examples can be referenced here: [docx_toolkit](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/toolkit/docx_toolkit.yaml).

For usage examples of toolkit invocation, see: [demo_agent_with_mcp_toolkit](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/agent/agent_instance/demo_agent_with_mcp_toolkit.yaml).

### Paginated tool discovery

MCP services may return tools across multiple `tools/list` pages. MCPToolkit
follows `nextCursor` in the same temporary session before registering tools,
including when an intermediate page is empty. Leaving `include` empty selects
all discovered tools in server order; an explicit `include` also selects tools
from later pages. MCPTool searches subsequent pages for its remote tool name
and stops as soon as it finds a match.

Cursors are opaque strings and are forwarded unchanged. A repeated cursor or
server pagination error aborts discovery; no tools from an incomplete toolkit
listing are registered. No additional configuration is required. See the
[MCP pagination specification](https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/pagination).
