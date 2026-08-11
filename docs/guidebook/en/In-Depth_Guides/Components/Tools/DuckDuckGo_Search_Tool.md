# DuckDuckGo Search Tool

A free web search tool that uses the [DuckDuckGo](https://duckduckgo.com) search engine via the `duckduckgo_search` Python package. Unlike the existing Google, Bing, and Tavily search tools, this tool requires **no API key** and works out of the box — ideal for quick prototyping and developers who do not yet have accounts with paid search providers.

## Installation

Install the optional dependency:

```bash
pip install duckduckgo_search
```

## Configuration

### YAML Configuration

```yaml
name: 'duckduckgo_search_tool'
description: 'Free DuckDuckGo web search tool requiring no API key'
class_path: 'agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool.DuckDuckGoSearchTool'
tool_type: 'api'
input_keys: ['input']
args_model:
  input:
    type: string
    description: The search query string
    required: true
  max_results:
    type: integer
    description: Maximum number of results to return (1-20), default 5
    required: false
  region:
    type: string
    description: Region code for search results, e.g. 'us', 'cn', 'uk', 'jp'
    required: false
  safesearch:
    type: string
    description: Safe-search level - 'on', 'moderate', or 'off', default 'moderate'
    required: false
```

### Environment Variables (Optional)

| Variable | Description |
|----------|-------------|
| `DUCKDUCKGO_PROXY` | Proxy URL for DuckDuckGo requests (e.g. `http://127.0.0.1:7890`) |

## Usage

### Basic Usage

```python
from agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool import DuckDuckGoSearchTool

tool = DuckDuckGoSearchTool(name="duckduckgo_search_tool")
result = tool.execute("Python programming language")
print(result)
```

### With Custom Parameters

```python
tool = DuckDuckGoSearchTool(
    name="duckduckgo_search_tool",
    max_results=10,
    region="us",
    safesearch="moderate",
)
result = tool.execute("machine learning tutorials")
```

### Async Usage

```python
import asyncio
from agentuniverse.agent.action.tool.tool import ToolInput

tool = DuckDuckGoSearchTool(name="duckduckgo_search_tool")
tool_input = ToolInput({"input": "async programming in Python"})
result = asyncio.run(tool.async_execute(tool_input))
```

## Features

- **No API key required** — works with zero configuration
- **Text search** — returns web results with title, URL, and snippet
- **Region support** — filter results by region code
- **Safe search** — control the safe-search level
- **Proxy support** — configurable via environment variable or direct parameter
- **Graceful fallback** — falls back to `MockSearchTool` when the optional dependency is not installed or when network errors occur
- **Async support** — non-blocking search via `async_execute`

## Fallback Behavior

When the `duckduckgo_search` package is not installed, the tool automatically falls back to `MockSearchTool` (the same pattern used by `BingSearchTool`). This ensures the framework continues to function even without the optional dependency.