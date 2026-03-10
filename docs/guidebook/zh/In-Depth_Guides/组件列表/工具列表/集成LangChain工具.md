# 集成LangChain工具（已废弃）

> **注意：** 自新版本起，agentUniverse已移除对LangChain的依赖。LangChain工具集成功能已不再支持。

## 替代方案

请使用agentUniverse原生的工具定义方式来创建和使用工具。详细信息请参考：

- [工具创建与使用](../../原理介绍/工具/工具创建与使用.md)
- [集成的工具](集成的工具.md)

agentUniverse现在提供了丰富的内置工具，包括：
- Google搜索工具
- Bing搜索工具
- DuckDuckGo搜索工具
- Python代码执行工具
- HTTP请求工具
- SQL数据库工具
- Web抓取工具
- MCP工具

所有工具均继承自`agentuniverse.agent.action.tool.tool.Tool`基类，通过实现`execute`方法来定义工具逻辑。
