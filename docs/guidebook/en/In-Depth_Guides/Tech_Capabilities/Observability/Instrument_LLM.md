# LLM Instrumentor

This Instrumentor provides automated OpenTelemetry tracing and metrics collection for the agentUniverse framework. It automatically creates spans and metrics for LLM calls decorated with `@trace_llm`.

## Span Attributes

When an LLM is called, a span is automatically created with the following attributes:

### Base Attributes

| Attribute Name | Type | Description | Example Value               |
|-----------------------|------|------|-----------------------------|
| `au.span.kind`        | string | Span kind identifier | `"llm"`                     |
| `au.llm.name`         | string | Name of the LLM | `"gpt-4o"`                  |
| `au.llm.channel_name` | string | LLM channel name | `"openai_official_channel"` |
| `au.llm.duration`     | float | Total execution time of the LLM call (seconds) | `1.234`                     |
| `au.llm.status`       | string | Execution status of the LLM | `"success"` or `"error"`    |
| `au.llm.streaming`    | bool | 	Whether streaming is used | `True` or `False`           |

### Input/Output Attributes

| Attribute Name                             | Type | Description |
|--------|------|------|
| `au.llm.input` | string | JSON serialization of input parameters |
| `au.llm.llm_params` | string | JSON serialization of LLM parameter configurations |
| `au.trace.caller_name`          | string | Name of the caller               |
| `au.trace.caller_type`          | string | Type of the caller                |
| `au.llm.first_token.duration` | float | Time taken to receive the first token (seconds) |

### Token Usage Attributes

| Attribute Name                             | Type | Description                  |
|----------------------------------|--------|---------------------|
| `au.llm.usage.detail_tokens` | string | JSON serialization of detailed token usage |
| `au.llm.usage.prompt_tokens` | int    | Number of tokens used in the prompt|
| `au.llm.usage.completion_tokens`| int    | Number of tokens generated in the response|
| `au.llm.usage.total_tokens`| int    | 	Total number of tokens used|

### Error Attributes (only set on error)

| Attribute Name                             | Type | Description |
|--------|------|------|
| `au.llm.error.type` | string | Error type (exception class name) |
| `au.llm.error.message` | string | Error message |

## Metrics

Note: The metric aggregation method in agentUniverse is `DELTA`.

### Counter Metrics

| Metric Name | Type | Unit | Description | Tags |
|--------|------|------|------|------|
| `llm_calls_total` | Counter | `1` | Total number of LLM calls | `llm_name`, `channel_name`, `caller` |
| `llm_errors_total` | Counter | `1` | Total number of LLM errors | `llm_name`, `channel_name`, `caller`, `error_type` |

### Histogram Metrics

| Metric Name | Type | Unit | Description | Tags |
|----------------------------|------|------|------------------------|------|
| `llm_call_duration`        | Histogram | `s` | Distribution of LLM call durations           | `llm_name`, `channel_name`, `caller` |
| `llm_first_token_duration` | Histogram | `s` | Distribution of time to first token        | `llm_name`, `channel_name`, `caller`, `streaming` |
| `llm_total_tokens`         | Histogram | `1` | Distribution of total tokens used per call     | `llm_name`, `channel_name`, `caller` |
| `llm_prompt_tokens`        | Histogram | `1` | Distribution of prompt tokens used   | `llm_name`, `channel_name`, `caller` |
| `llm_completion_tokens`    | Histogram | `1` | Distribution of completion tokens generated    | `llm_name`, `channel_name`, `caller` |
| `llm_cached_tokens`        | Histogram | `1` | Distribution of cached tokens hit  | `agent_name`, `caller`, `streaming` |
| `llm_reasoning_tokens`     | Histogram | `1` | Distribution of reasoning tokens used | `agent_name`, `caller`, `streaming` |

### Metric Tag Descriptions

| Tag Name	                    | Description        | Possible Values                 |
|--------|------|---------------------------------|
| `au_llm_name` | Name of the LLM | Any string                      |
| `au_llm_channel_name` | Name of the LLM channel | Any string                      |
| `au_trace_caller_name` | Name of the calling component| `"xxx_tool"`, `"xxx_agent"`, etc |
| `au_trace_caller_type` | Type of the calling component| `"llm"`, `"agent"`, etc            |
| `au_llm_streaming` | Whether the call was streaming | `true`, `false`                 |
| `au_llm_status` | Status of the LLM call | Exception class name like `"ValueError"`           |

