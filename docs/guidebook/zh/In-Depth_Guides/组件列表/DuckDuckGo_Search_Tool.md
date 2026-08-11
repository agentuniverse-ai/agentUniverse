# DuckDuckGo 搜索工具

一个免费的网页搜索工具，通过 `duckduckgo_search` Python 包使用 [DuckDuckGo](https://duckduckgo.com) 搜索引擎。与现有的 Google、Bing 和 Tavily 搜索工具不同，此工具**无需 API 密钥**，开箱即用 —— 非常适合快速原型开发。

## 安装

安装可选依赖：

```bash
pip install duckduckgo_search
```

## 配置

### YAML 配置

```yaml
name: 'duckduckgo_search_tool'
description: '免费的 DuckDuckGo 网页搜索工具，无需 API 密钥'
class_path: 'agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool.DuckDuckGoSearchTool'
tool_type: 'api'
input_keys: ['input']
args_model:
  input:
    type: string
    description: 搜索查询字符串
    required: true
  max_results:
    type: integer
    description: 返回的最大结果数（1-20），默认 5
    required: false
  region:
    type: string
    description: 搜索结果区域代码，例如 'us', 'cn', 'uk', 'jp'
    required: false
  safesearch:
    type: string
    description: 安全搜索级别 - 'on', 'moderate', 或 'off'，默认 'moderate'
    required: false
```

### 环境变量（可选）

| 变量 | 说明 |
|------|------|
| `DUCKDUCKGO_PROXY` | DuckDuckGo 请求的代理地址（例如 `http://127.0.0.1:7890`） |

## 使用示例

### 基本用法

```python
from agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool import DuckDuckGoSearchTool

tool = DuckDuckGoSearchTool(name="duckduckgo_search_tool")
result = tool.execute("Python 编程语言")
print(result)
```

### 自定义参数

```python
tool = DuckDuckGoSearchTool(
    name="duckduckgo_search_tool",
    max_results=10,
    region="cn",
    safesearch="moderate",
)
result = tool.execute("机器学习教程")
```

### 异步用法

```python
import asyncio
from agentuniverse.agent.action.tool.tool import ToolInput

tool = DuckDuckGoSearchTool(name="duckduckgo_search_tool")
tool_input = ToolInput({"input": "Python 异步编程"})
result = asyncio.run(tool.async_execute(tool_input))
```

## 功能特性

- **无需 API 密钥** —— 零配置即可使用
- **文本搜索** —— 返回包含标题、URL 和摘要的网页结果
- **区域支持** —— 按区域代码过滤结果
- **安全搜索** —— 控制安全搜索级别
- **代理支持** —— 通过环境变量或直接参数配置
- **优雅降级** —— 当可选依赖未安装或网络错误时，自动回退到 `MockSearchTool`
- **异步支持** —— 通过 `async_execute` 实现非阻塞搜索

## 降级行为

当 `duckduckgo_search` 包未安装时，工具会自动回退到 `MockSearchTool`（与 `BingSearchTool` 使用相同的模式）。这确保了即使没有可选依赖，框架也能继续运行。