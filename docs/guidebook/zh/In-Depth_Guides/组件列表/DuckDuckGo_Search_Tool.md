# DuckDuckGo 搜索工具

`DuckDuckGoSearchTool` 是 agentUniverse 原生的网页与新闻搜索组件，无需
API Key，并将不同搜索模式的结果统一为稳定的结构化响应。

仓库中已经存在通过通用 LangChain 适配器调用 DuckDuckGo 的示例。本原生组件
适用于需要运行时参数校验、统一结果字段、明确错误信息、代理与超时配置，以及
同步/异步一致调用契约的场景。

## 功能

- 支持网页（`text`）和新闻（`news`）搜索；
- 每次返回 1-20 条结果；
- 支持区域、安全搜索、时间范围和文本搜索后端参数；
- 可通过 `DUCKDUCKGO_PROXY` 配置代理；
- `async_execute`/`async_run` 在线程中执行阻塞客户端，不阻塞事件循环；
- 网页结果统一为标题、URL、摘要，新闻结果额外包含日期、来源和图片；
- 参数、依赖和网络错误均返回确定的错误结构，不伪造降级搜索结果。

## 安装

agentUniverse 已经声明 `duckduckgo-search` 依赖。单独安装时可执行：

```bash
pip install duckduckgo-search
```

使用 DuckDuckGo 不需要申请 API Key。

## 组件配置

```yaml
name: duckduckgo_search_tool
description: 无需 API Key 的 DuckDuckGo 网页与新闻搜索工具
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

随组件提供的 YAML 还包含供工具 Schema 消费方使用的 `args_model_schema`。

## 输入参数

| 参数 | 必填 | 默认值 | 说明 |
|---|---:|---|---|
| `input` | 是 | - | 非空搜索查询。 |
| `search_type` | 否 | `text` | `text` 或 `news`。 |
| `max_results` | 否 | `5` | 1-20 的整数。 |
| `region` | 否 | 搜索库默认值 | 例如 `us-en` 或 `cn-zh`。 |
| `safesearch` | 否 | `moderate` | `on`、`moderate` 或 `off`。 |
| `timelimit` | 否 | 无 | `d`、`w`、`m` 或 `y`。 |
| `backend` | 否 | `auto` | 文本搜索后端；新闻模式忽略。 |

组件级参数还包括 `proxy` 和 1-120 秒的 `timeout`。未显式设置 `proxy`
时，会读取 `DUCKDUCKGO_PROXY` 环境变量。

## 使用方法

### 网页搜索

```python
from agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool import (
    DuckDuckGoSearchTool,
)

search = DuckDuckGoSearchTool(name="duckduckgo_search_tool")
result = search.execute(
    input="智能体框架可观测性",
    max_results=8,
    region="cn-zh",
    safesearch="moderate",
    timelimit="m",
)
```

### 新闻搜索

```python
result = search.execute(
    input="大语言模型发布",
    search_type="news",
    max_results=5,
    timelimit="w",
)
```

### 框架调用与异步调用

```python
import asyncio

search.input_keys = ["input"]
sync_result = search.run(input="agentUniverse")
async_result = asyncio.run(
    search.async_run(input="agentUniverse", search_type="news")
)
```

`run`、`async_run`、`execute` 和 `async_execute` 均遵循框架当前的关键字参数
工具调用契约。

## 返回结构

成功响应示例：

```json
{
  "status": "success",
  "query": "智能体框架可观测性",
  "search_type": "text",
  "region": "cn-zh",
  "safesearch": "moderate",
  "timelimit": "m",
  "count": 1,
  "results": [
    {
      "title": "示例结果",
      "url": "https://example.com/result",
      "snippet": "结果摘要"
    }
  ]
}
```

新闻结果额外包含 `date`、`source` 和 `image`。

参数错误、依赖缺失和网络/服务错误会返回 `status: error`、`count: 0`、空的
`results`，以及包含 `type` 和 `message` 的 `error` 对象。工具不会在实时搜索
失败时替换成 Mock 内容，因为智能体可能把工具结果当成事实依据，伪造搜索结果会
带来错误推理风险。
