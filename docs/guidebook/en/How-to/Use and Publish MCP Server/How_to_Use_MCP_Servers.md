# How to Use MCP Server in agentUniverse
In agentUniverse, you can integrate any MCP Server and make it available as a tool/toolkit for agents by following two steps.

## step1. Use MCPToolkit to Integrate MCP Server as Toolkits
The current version of MCPServer supports three communication modes: Standard Input/Output Stream (stdio), Server-Sent Events (SSE), Streamable HTTP.

Below are YAML configuration examples for each mode:

1) Standard Input/Output Stream (stdio) Mode Example
```yaml
name: 'docx_toolkit'
description: |
  这是一个docx相关的工具集
transport: 'stdio'
command: 'uvx'
args:
  - 'mcp-server-office'

metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

2) SSE Mode Example
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

3) Streamable HTTP Mode Example
```yaml
name: 'weather'
transport: 'streamable_http'
url: 'http://localhost:8000/mcp'
metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

- `Parameters: transport, url, command, args, env, and other parameters follow the official MCP specification definitions.

## step2. Configure MCPToolkit for the Agent to Use MCP Server
After integrating the MCP service in Step 1, you can configure the agent to use the MCPToolkit by adding it to the agent's configuration file under the [`action` → `toolkit`] property.

Here’s a agent configuration that uses the docx MCP Server from Step 1:
```yaml
info:
  name: 'demo_agent_with_mcp_toolkit'
  description: 'A simple demonstration react agent designed to showcase 
  the integration and usage of mcp toolkits.'
profile:
  prompt_version: qwen_react_agent.cn
  llm_model:
    name: 'qwen3-32b'
    stop: 'Observation'
    temperature: 0.1
action:
  toolkit:
    - 'docx_toolkit'
memory:
  name: 'demo_memory'
metadata:
  type: 'AGENT'
  module: 'agentuniverse.agent.template.react_agent_template'
  class: 'ReActAgentTemplate'
```

Additional Resources:  
* Sample Application Code: Refer to the [MCP Sample App](../../../../../examples/sample_apps/toolkit_demo_app).
* MCPToolkit Configuration: See the [configuration file](../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/toolkit/docx_toolkit.yaml).
* Agent Configuration: See the [agent configuration file](../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/agent/agent_instance/demo_agent_with_mcp_toolkit.yaml).  
* Test File: Check the [run script](../../../../../examples/sample_apps/toolkit_demo_app/intelligence/test/run_demo_agent_with_mcp_toolkit.py).

For more details, consult the following documentation: [MCP Toolkit Guide](../../In-Depth_Guides/Tutorials/Toolkit/MCP_Toolkit_Guide.md), [MCP Tool Guide](../../In-Depth_Guides/Tutorials/Tool/MCP_Tool_Guide.md).
