# 如何在agentUniverse中发布MCP服务
在agentUniverse中，您只需通过以下2个步骤，即可将您开发的工具(Tool)或者工具包(ToolKit)发布为MCP服务。

## step1. 在要发布的Tool或ToolKit配置中添加MCP服务发布参数
您可以在您想要发布的Tool或ToolKit配置中添加`as_mcp_tool: true`标记，示例如下:
```yaml
name: 'tool_name'
description: 'tool description'
as_mcp_tool: true
```
该工具会被添加到agentUniverse中的默认MCP Server当中， 默认server名字为`default_mcp_server`。

## step2. 启动MCP Server
通过MCPServerManager启动MCP服务，将步骤一中标记的工具、工具集合一键发布为MCP服务。
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
启动后您可以通过下列地址访问：
- `http://0.0.0.0:8890/default_mcp_server/sse`

完整的MCP服务发布用例您可以在[标准样例工程](../../../../../examples/sample_standard_app)中查看, 您可以使用[mcp_application.py](../../../../../examples/sample_standard_app/bootstrap/intelligence/mcp_application.py)进行MCP服务启动, 在该样例中我们将[mock_search_tool工具](../../../../../examples/sample_standard_app/intelligence/agentic/tool/custom/mock_search_tool.yaml)发布为了default_mcp_server。

您可以进一步指定所发布的MCP服务端口、host地址、通信类型等，更详细的内容请参考文档[MCP_Server](../../In-Depth_Guides/技术组件/服务化/MCP_Server.md)。