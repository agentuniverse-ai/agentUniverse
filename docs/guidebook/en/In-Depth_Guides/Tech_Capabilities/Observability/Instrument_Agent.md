# Agent Instrument

This Instrumentor provides automated OpenTelemetry tracing and metric collection for the agentUniverse framework. It automatically creates spans and metrics for Agent calls decorated with `@trace_agent`.


## Span Attributes

When an Agent is invoked, a span is automatically created with the following attributes:

### Base Attributes

| Attribute Name | Type | Description | Example Value            |
|--------|------|------|--------------------------|
| `au.span.kind` | string | Span kind identifier | `"agent"`                |
| `au.agent.name` | string | Name of the Agent | `"ChatAgent"`            |
| `au.agent.pair_id` | string | ID for this Agent call | `"agent-1234-5678"`      |
| `au.agent.duration` | float | Total execution duration of the Agent (in seconds) | `1.234`                  |
| `au.agent.status` | string | Execution status of the Agent | `"success"` or `"error"` |
| `au.agent.streaming` | bool | Whether the response is streaming | `True` or `False`        |

### Input/Output Attributes

| Attribute Name                             | Type | Description                   |
|---------------------------------|------|----------------------|
| `au.agent.input`                | string | JSON serialized input arguments to the Agent |
| `au.agent.output`               | string | JSON serialized output result from the Agent |
| `au.trace.caller_name`          | string | Name of the caller                |
| `au.trace.caller_type`          | string | Type of the caller                |
| `au.agent.first_token.duration` | float | Time to first token in seconds     |

### Token Usage Attributes

| Attribute Name                             | Type | Description                  |
|--------------------------------|--------|---------------------|
| `au.agent.usage.detail_tokens` | string | JSON serialized details of token usage |
| `au.agent.usage.prompt_tokens` | int    | Number of prompt tokens consumed|
| `au.agent.usage.completion_tokens`| int    | Number of completion tokens generated|
| `au.agent.usage.total_tokens`| int    | Total number of tokens used|

### Error Attributes (only set on error)

| Attribute Name                             | Type | Description |
|--------|------|------|
| `au.agent.error.type` | string | Error type (exception class name) |
| `au.agent.error.message` | string | Error message |

## Metrics

Note: The metric aggregation method in agentUniverse is `DELTA`.

### Counter Metrics

| Metric Name | Type | Unit | Description | Tags |
|--------|------|------|------|------|
| `agent_calls_total` | Counter | `1` | Total number of Agent calls | `agent_name`, `caller`, `streaming` |
| `agent_errors_total` | Counter | `1` | Total number of Agent errors | `agent_name`, `caller`, `error_type`, `streaming` |

### Histogram Metrics

| Metric Name | Type | Unit | Description | Tags |
|------------------------------|------|------|--------------------------|------|
| `agent_call_duration`        | Histogram | `s` | Distribution of Agent call durations           | `agent_name`, `caller`, `streaming` |
| `agent_first_token_duration` | Histogram | `s` | Distribution of time to first token          | `agent_name`, `caller`, `streaming` |
| `agent_total_tokens`         | Histogram | `1` | Distribution of total tokens per Agent call     | `agent_name`, `caller`, `streaming` |
| `agent_prompt_tokens`        | Histogram | `1` | Distribution of prompt tokens per Agent call   | `agent_name`, `caller`, `streaming` |
| `agent_completion_tokens`    | Histogram | `1` | Distribution of completion tokens per Agent call    | `agent_name`, `caller`, `streaming` |
| `agent_cached_tokens`        | Histogram | `1` | Distribution of cached tokens per Agent call	  | `agent_name`, `caller`, `streaming` |
| `agent_reasoning_tokens`     | Histogram | `1` | Distribution of reasoning tokens per Agent call | `agent_name`, `caller`, `streaming` |

### Metric Tag Descriptions

| Tag Name	                    | Description        | Possible Values                                  |
|------------------------|---------|--------------------------------------------------|
| `au_agent_name`        | Name of the Agent | Any string                                    |
| `au_trace_caller_name` | Name of the caller source  | `"xxx_tool"`, `"xxx_agent"`, etc                 |
| `au_trace_caller_type` | 	Type of the caller source  | `"llm"`, `"agent"`, etc                          |
| `au_agent_streaming`| Whether the call is streaming | `true`, `false`                                  |
| `au_agent_status`| Status indicator    | `"success"` or exception class name like `"ValueError"` |
