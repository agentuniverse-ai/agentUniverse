# MCP Server

AgentUniverse允许用户将自己的工具通过MCP Server的形式对外提供服务。为此，您需要完成以下几个步骤。

## 1. 标记需要发布的工具
您可以在工具(Tool)或者工具包(Toolkit)的yaml定义文件中，将工具或工具包标识为可通过MCP Server调用：

```yaml
name: 'tool_name'
description: 'tool description'
as_mcp_tool:
  server_name: mcp_search_server
```
其中as_mcp_tool表示该工具或工具包可以通过MCP Server调用，而server_name表示所属的MCP服务名称，不同的MCP服务独立运行互不冲突。

如果您不需要单独区分MCP服务，可以不使用server_name字段，如下：
```yaml
name: 'tool_name'
description: 'tool description'
as_mcp_tool:
```
该工具会被添加到agentUniverse中的默认MCP Server当中

## 2.启动MCP Server
您可以参考示例工程中MCP Server启动的写法：
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
MCPServerManager的start_server接受三个参数：
- host: 表示MCP Server的host，默认值为0.0.0.0
- port: 接受一个int，表示MCP Server的uvicorn app的启动端口。默认使用8890端口。
- transport: 表示mcp server的类型，可选值为"sse"和"streamable_http"，默认值为"sse"

调用的时候，sse模式访问路径为`http://${host}:${port}/${server_name}/sse`，而streamable_http访问路径为`http://${host}:${port}/${server_name}/mcp`
以上面默认值为例，则访问mcp_search_server的路径分别为
- `http://0.0.0.0:8890/mcp_search_server/sse`
- `http://0.0.0.0:8890/mcp_search_server/mcp`