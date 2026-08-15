# DuckDuckGo Search Tool

`DuckDuckGoSearchTool` is a native agentUniverse search component for web and
news discovery. It requires no API key and returns a stable structured response
instead of provider-specific fields.

The repository also includes a DuckDuckGo example through the generic LangChain
adapter. Use this native component when you need runtime parameter validation,
normalized metadata, explicit error responses, proxy/timeout configuration, or
the same contract for synchronous and asynchronous execution.

## Capabilities

- web (`text`) and recent-news (`news`) search;
- 1-20 results per request;
- region, safe-search, recency, and text-backend controls;
- proxy configuration through `DUCKDUCKGO_PROXY`;
- non-blocking `async_execute`/`async_run` support;
- normalized title, URL, and snippet fields, plus news source/date/image fields;
- deterministic validation and dependency/network errors with no fabricated
  fallback results.

## Installation

`duckduckgo-search` is already declared by agentUniverse. If installing the
component independently, run:

```bash
pip install duckduckgo-search
```

No DuckDuckGo API key is required.

## Component configuration

```yaml
name: duckduckgo_search_tool
description: Search DuckDuckGo without an API key
tool_type: api
input_keys: [input]
max_results: 5
safesearch: moderate
search_type: text
backend: auto
timeout: 10
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool
  class: DuckDuckGoSearchTool
```

The packaged component file also exposes an `args_model_schema` for tool-schema
consumers.

## Input parameters

| Parameter | Required | Default | Description |
|---|---:|---|---|
| `input` | yes | - | Non-empty search query. |
| `search_type` | no | `text` | `text` or `news`. |
| `max_results` | no | `5` | Integer from 1 through 20. |
| `region` | no | provider default | Region such as `us-en` or `cn-zh`. |
| `safesearch` | no | `moderate` | `on`, `moderate`, or `off`. |
| `timelimit` | no | none | `d`, `w`, `m`, or `y`. |
| `backend` | no | `auto` | Text-search backend; ignored for news. |

Component-level options also include `proxy` and a 1-120 second `timeout`.
`proxy` defaults to the `DUCKDUCKGO_PROXY` environment variable.

## Usage

### Web search

```python
from agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool import (
    DuckDuckGoSearchTool,
)

search = DuckDuckGoSearchTool(name="duckduckgo_search_tool")
result = search.execute(
    input="agent framework observability",
    max_results=8,
    region="us-en",
    safesearch="moderate",
    timelimit="m",
)
```

### News search

```python
result = search.execute(
    input="large language model releases",
    search_type="news",
    max_results=5,
    timelimit="w",
)
```

### Framework and asynchronous calls

```python
import asyncio

search.input_keys = ["input"]
sync_result = search.run(input="agentUniverse")
async_result = asyncio.run(
    search.async_run(input="agentUniverse", search_type="news")
)
```

`run`, `async_run`, `execute`, and `async_execute` all use the framework's
modern keyword-argument tool contract.

## Response contract

Successful calls return:

```json
{
  "status": "success",
  "query": "agent framework observability",
  "search_type": "text",
  "region": "us-en",
  "safesearch": "moderate",
  "timelimit": "m",
  "count": 1,
  "results": [
    {
      "title": "Example result",
      "url": "https://example.com/result",
      "snippet": "Result summary"
    }
  ]
}
```

News results additionally contain `date`, `source`, and `image`.

Validation, missing-dependency, and network/provider failures return
`status: error`, `count: 0`, an empty `results` list, and an `error` object with
`type` and `message`. The tool deliberately does not replace failed live
searches with mock content, because fabricated search results are unsafe for
agents that treat tool output as evidence.
