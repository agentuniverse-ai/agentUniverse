# Tool Instrumentor

The Instrumentor provides automated OpenTelemetry tracing and metric collection capabilities for the agentUniverse framework. It automatically creates spans and metrics for Tool invocations decorated with `@trace_tool`.

## Span Attributes

When a Tool is invoked, a span is automatically created with the following attributes:

### Basic Attributes

| Attribute Name | Type | Description | Example Value            |
|--------|------|------|--------------------------|
| `au.span.kind` | string | Identifier for the span kind | `"tool"`                 |
| `au.tool.name` | string | Name of the Tool | `"SearchTool"`           |
| `au.tool.pair_id` | string | ID for the Tool invocation | `"tool-1234-5678"`       |
| `au.tool.duration` | float | Total execution time of the Tool (in seconds) | `0.856`                  |
| `au.tool.status` | string | Execution status of the Tool | `"success"` or `"error"` |

### Input/Output Attributes

| Attribute Name                             | Type | Description |
|--------|------|------|
| `au.tool.input` | string | JSON serialization of input arguments |
| `au.tool.output` | string | JSON serialization of output result |
| `au.trace.caller_name`          | string | Name of the caller               |
| `au.trace.caller_type`          | string | Type of the caller                |

### Token Usage Attributes

| Attribute Name                             | Type | Description           |
|------------------------------------|------|--------------|
| `au.tool.usage.detail_tokens`      | string | JSON serialization of token usage details |
| `au.tool.usage.prompt_tokens`     | int    | Number of prompt tokens consumed|
| `au.tool.usage.completion_tokens` | int    | Number of completion tokens generated|
| `au.tool.usage.total_tokens`      | int    | Total number of tokens consumed|

### Error Attributes (only set on error)

| Attribute Name                             | Type | Description |
|--------|------|------|
| `au.tool.error.type` | string | Error type (exception class name) |
| `au.tool.error.message` | string | Error message |

## Metrics

Note: The metric aggregation method in agentUniverse is `DELTA`。

### Counter Metrics

| Metric Name | Type | Unit | Description | Tags |
|--------|------|------|------|------|
| `tool_calls_total` | Counter | `1` | Total number of Tool calls | `tool_name`, `caller` |
| `tool_errors_total` | Counter | `1` | Total number of Tool errors | `tool_name`, `caller`, `error_type` |

### Histogram Metrics

| Metric Name | Type | Unit | Description | Tags |
|--------------------------|------|------|-------------------------|------|
| `tool_call_duration`     | Histogram | `s` | Distribution of Tool call durations           | `tool_name`, `caller` |
| `tool_total_tokens`      | Histogram | `1` | Distribution of total tokens per Tool call     | `tool_name`, `caller` |
| `tool_prompt_tokens`     | Histogram | `1` | Distribution of prompt tokens per Tool call   | `tool_name`, `caller` |
| `tool_completion_tokens` | Histogram | `1` | Distribution of completion tokens per Tool call    | `tool_name`, `caller` |
| `tool_cached_tokens`     | Histogram | `1` | Distribution of cached tokens hit during Tool calls  | `agent_name`, `caller`, `streaming` |
| `tool_reasoning_tokens`  | Histogram | `1` | Distribution of model reasoning tokens per Tool call | `agent_name`, `caller`, `streaming` |

### Metric Tag Descriptions

| Tag Name	                    | Description        | Possible Values                  |
|--------|------|----------------------------------|
| `au_tool_name` | Name of the Tool	 | Any string                       |
| `au_trace_caller_name` | Name of the caller    | `"xxx_tool"`, `"xxx_agent"`, etc |
| `au_trace_caller_type` | Type of the caller    | `"llm"`, `"agent"`, etc          |
| `au_tool_status`| Status indicator      | `"success"` or exception class name like `"ValueError"`  |

