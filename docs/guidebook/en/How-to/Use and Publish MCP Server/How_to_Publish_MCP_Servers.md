# How to Publish an MCP Server in agentUniverse
In agentUniverse, you can publish the tools (Tool) or toolkits (Toolkit) you have developed as MCP Server by following just these two steps.

## step1. Add MCP Server Publishing Parameters to the Configuration of Your Tool/Toolkit
You can add the `as_mcp_tool: true` flag in the configuration of the Tool or Toolkit you want to publish. An example is shown below.
```yaml
name: 'tool_name'
description: 'tool description'
as_mcp_tool: true
```
The tool will be added to the default MCP Server in agentUniverse, with the default server name set to `default_mcp_server`.

## step2. Start the MCP Server
Use the MCPServerManager to start the MCP Server and automatically publish the tools and toolkits marked in Step 1 as MCP Server.
```python
from agentuniverse.agent_serve.web.mcp.mcp_server_manager import MCPServerManager
from agentuniverse.base.agentuniverse import AgentUniverse

class ServerApplication:
    """
    Server application.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start(core_mode=True)
        MCPServerManager().start_server()
        
if __name__ == "__main__":
    ServerApplication.start()
```
After starting, you can access the MCP service using the following address:
- `http://0.0.0.0:8890/default_mcp_server/sse`

For the example of MCP server deployment, refer to the [Standard Sample Project](../../../../../examples/sample_standard_app). You can start the MCP server using [mcp_application.py](../../../../../examples/sample_standard_app/bootstrap/intelligence/mcp_application.py). In this example, the [mock_search_tool](../../../../../examples/sample_standard_app/intelligence/agentic/tool/custom/mock_search_tool.yaml) is published to the default_mcp_server.

You can further customize the MCP server's port, host address, communication type, etc. For more details, please refer to the documentation: [MCP_Server](../../In-Depth_Guides/Tech_Capabilities/Service/MCP_Server.md).