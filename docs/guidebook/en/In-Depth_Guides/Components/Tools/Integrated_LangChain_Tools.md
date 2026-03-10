# Integrated LangChain Tool (Deprecated)

> **Note:** Starting from the new version, agentUniverse has removed its dependency on LangChain. The LangChain tool integration feature is no longer supported.

## Alternatives

Please use agentUniverse's native tool definition approach to create and use tools. For detailed information, refer to:

- [Tool Creation and Usage](../../Tutorials/Tool/Tool_Create_And_Use.md)
- [Integrated Tools](Integrated_Tools.md)

agentUniverse now provides a rich set of built-in tools, including:
- Google Search Tool
- Bing Search Tool
- DuckDuckGo Search Tool
- Python Code Execution Tool
- HTTP Request Tool
- SQL Database Tool
- Web Fetch Tool
- MCP Tool

All tools inherit from the `agentuniverse.agent.action.tool.tool.Tool` base class and define tool logic by implementing the `execute` method.
