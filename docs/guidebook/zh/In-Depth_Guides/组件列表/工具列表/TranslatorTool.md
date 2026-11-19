# TranslatorTool

`TranslatorTool` 使用 Google 翻译的免费公开端点（`translate.googleapis.com/translate_a/single`）在 100+ 种语言之间翻译文本，无需申请 API Key。适合智能体在不携带任何凭证的情况下完成跨语言文本转换。

## 功能特性

- 支持 100+ 种语言（英语 `en`、中文 `zh`、日语 `ja`、韩语 `ko` 等）
- 支持自动检测源语言（`source='auto'`），并返回检测到的源语言
- 无需 API Key，零配置即可使用
- 基于 `httpx`，支持请求超时控制
- 单次翻译默认上限 50,000 字符
- 校验失败和网络异常均以结构化 `error` 返回，不会抛出未捕获异常

## 使用方式

```python
from agentuniverse.agent.action.tool.common_tool.translator_tool import TranslatorTool

tool = TranslatorTool()

# 自动检测源语言并翻译成英语
result = tool.execute(text="你好，世界", source="auto", target="en")
print(result["translated_text"])   # "Hello, world"
print(result["source_language"])   # "zh"
print(result["target_language"])   # "en"

# 使用默认源/目标语言
tool = TranslatorTool(default_source="zh", default_target="en")
print(tool.execute(text="你好")["translated_text"])
```

## YAML 配置

```yaml
name: translator_tool
description: Translate text between 100+ languages using the free Google Translate endpoint (no API key required).
tool_type: api
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.common_tool.translator_tool
  class: TranslatorTool
input_keys:
  - text
default_source: auto
default_target: en
request_timeout: 15.0
```

## 参数说明

`execute()` 方法接受以下参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `text` | `str` | 是 | 待翻译文本，自动去除首尾空白，最长 50,000 字符 |
| `source` | `str` | 否 | 源语言代码，缺省取 `default_source`；`auto` 表示自动检测 |
| `target` | `str` | 否 | 目标语言代码，缺省取 `default_target` |

工具字段：

| 字段 | 默认值 | 说明 |
| --- | --- | --- |
| `default_source` | `auto` | 默认源语言，支持自动检测 |
| `default_target` | `en` | 默认目标语言 |
| `request_timeout` | `15.0` | HTTP 请求超时时间（秒） |

返回值为字典，成功时包含 `status='success'`、`translated_text`、`source_language`、`target_language`、`original_text`、`engine`；失败时包含 `status='error'`、`error_type`（`validation_error` / `network_error` / `operation_error`）以及 `error` 详情。

## 网络依赖

该工具依赖公网访问 `https://translate.googleapis.com/translate_a/single`，无需任何环境变量或密钥配置。如运行环境无法访问 Google 服务，会返回 `network_error`。
