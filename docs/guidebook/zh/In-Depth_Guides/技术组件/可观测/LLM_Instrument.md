# LLM Instrumentor

该 Instrumentor 为 agentUniverse 框架提供自动化的 OpenTelemetry 追踪和指标收集功能，能够自动为使用 `@trace_llm` 装饰器的 LLM 调用创建 spans 和 metrics。

## Span 属性

当 LLM 被调用时，会自动创建一个 span 并设置以下属性：

### 基础属性

| 属性名                   | 类型 | 描述 | 示例值                         |
|-----------------------|------|------|-----------------------------|
| `au.span.kind`        | string | Span 类型标识 | `"llm"`                     |
| `au.llm.name`         | string | LLM 的名称 | `"gpt-4o"`                  |
| `au.llm.channel_name` | string | LLM 通道名称 | `"openai_official_channel"` |
| `au.llm.duration`     | float | LLM 执行总时长（秒） | `1.234`                     |
| `au.llm.status`       | string | LLM 执行状态 | `"success"` 或 `"error"`     |
| `au.llm.streaming`    | bool | 是否流式 | `True` 或 `False`|
### 输入输出属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.llm.input` | string | LLM 输入参数的 JSON 序列化 |
| `au.llm.llm_params` | string | LLM 参数配置的 JSON 序列化 |
| `au.trace.caller_name`          | string | 调用者名称                |
| `au.trace.caller_type`          | string | 调用者类型                |
| `au.llm.first_token.duration` | float | 首个 token 响应时间（秒） |

### Token 使用属性

| 属性名                              | 类型     | 描述                  |
|----------------------------------|--------|---------------------|
| `au.llm.usage.detail_tokens` | string | token消耗明细的 JSON 序列化 |
| `au.llm.usage.prompt_tokens` | int    | 提示词消耗token|
| `au.llm.usage.completion_tokens`| int    | 结果生成消耗token|
| `au.llm.usage.total_tokens`| int    | 总消耗token|

### 错误属性（仅在出错时设置）

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.llm.error.type` | string | 错误类型（异常类名） |
| `au.llm.error.message` | string | 错误消息 |

## Metrics 指标

请注意 agentUniverse 中 Metric 统计方式为 `DELTA`。

### Counter 计数器

| 指标名 | 类型 | 单位 | 描述 | 标签 |
|--------|------|------|------|------|
| `llm_calls_total` | Counter | `1` | LLM 调用总次数 | `llm_name`, `channel_name`, `caller` |
| `llm_errors_total` | Counter | `1` | LLM 错误总次数 | `llm_name`, `channel_name`, `caller`, `error_type` |

### Histogram 直方图

| 指标名                        | 类型 | 单位 | 描述                     | 标签 |
|----------------------------|------|------|------------------------|------|
| `llm_call_duration`        | Histogram | `s` | LLM 调用持续时间分布           | `llm_name`, `channel_name`, `caller` |
| `llm_first_token_duration` | Histogram | `s` | 首个 token 响应时间分布        | `llm_name`, `channel_name`, `caller`, `streaming` |
| `llm_total_tokens`         | Histogram | `1` | LLM 调用总 token 数量分布     | `llm_name`, `channel_name`, `caller` |
| `llm_prompt_tokens`        | Histogram | `1` | LLM 调用提示词 token 数量分布   | `llm_name`, `channel_name`, `caller` |
| `llm_completion_tokens`    | Histogram | `1` | LLM 调用完成 token 数量分布    | `llm_name`, `channel_name`, `caller` |
| `llm_cached_tokens`        | Histogram | `1` | LLM 调用命中缓存 token 数量分布  | `agent_name`, `caller`, `streaming` |
| `llm_reasoning_tokens`     | Histogram | `1` | LLM 调用中模型思考 token 数量分布 | `agent_name`, `caller`, `streaming` |

### Metric 标签说明

| 标签名 | 描述 | 可能值 |
|--------|------|--------|
| `au_llm_name` | LLM 的名称 | 任意字符串 |
| `au_llm_channel_name` | LLM 通道名称 | 任意字符串 |
| `au_trace_caller_name` | 调用来源名称| `"xxx_tool"`, `"xxx_agent"`, 等  |
| `au_trace_caller_type` | 调用来源类型| `"llm"`, `"agent"`, 等           |
| `au_llm_streaming` | 是否为流式调用 | `true`, `false` |
| `au_llm_status` | 状态标识 | 异常类名，如 `"ValueError"` |

