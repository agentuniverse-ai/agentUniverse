# Recommended Configurations

To facilitate user adoption, we provide several basic OpenTelemetry (OTel) configurations for reference. Users can modify these based on their specific needs.

## Console Output Configuration (Local)

### Configuration File
```toml
[OTEL]
service_name = "agentuniverse-demo"
provider_class = "opentelemetry.sdk.trace.TracerProvider"
id_generator_class = "opentelemetry.sdk.trace.RandomIdGenerator"

# Instrumentation configuration list
instrumentations = [
  "agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor.LLMInstrumentor",
  "agentuniverse.base.tracing.otel.instrumentation.agent.agent_instrumentor.AgentInstrumentor",
  "agentuniverse.base.tracing.otel.instrumentation.tool.tool_instrumentor.ToolInstrumentor",
]

[OTEL.resource]
deployment = "development"
team = "llm"
version = "1.0.0"
environment = "dev"

[[OTEL.processors]]
class = "opentelemetry.sdk.trace.export.BatchSpanProcessor"

  [OTEL.processors.exporter]
  class = "opentelemetry.sdk.trace.export.ConsoleSpanExporter"

[[OTEL.metric_readers]]
class = "opentelemetry.sdk.metrics.export.PeriodicExportingMetricReader"

  [OTEL.metric_readers.args]
  export_interval_millis = 1000

  [OTEL.metric_readers.exporter]
  class = "opentelemetry.sdk.metrics.export.ConsoleMetricExporter"
```
### Features
- Outputs tracing and metric data to the console; no additional dependencies required; simple setup ideal for quick debugging.
- However, the output volume is large and not recommended for production use.

## JSON Output to Local Files

### Configuration File
```toml
[OTEL]
service_name = "agentuniverse-demo"
provider_class = "opentelemetry.sdk.trace.TracerProvider"
id_generator_class = "opentelemetry.sdk.trace.RandomIdGenerator"

instrumentations = [
  "agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor.LLMInstrumentor",
  "agentuniverse.base.tracing.otel.instrumentation.agent.agent_instrumentor.AgentInstrumentor",
  "agentuniverse.base.tracing.otel.instrumentation.tool.tool_instrumentor.ToolInstrumentor",
]

[OTEL.resource]
deployment = "development"
team = "llm"
version = "1.0.0"
environment = "dev"

[[OTEL.processors]]
class = "opentelemetry.sdk.trace.export.BatchSpanProcessor"

  [OTEL.processors.exporter]
  class = "agentuniverse.base.tracing.otel.span_processor.span_json_exporter.SpanJsonExporter"
    [OTEL.processors.exporter.args]
    base_dir = "./monitors"
```

### Features
- Trace data is saved as JSON files locally, categorized by modules such as LLM, Agent, and Tool.Each span is stored in a separate file, making it convenient for downstream processing (e.g., model fine-tuning).
- he output directory can be customized via the `base_dir` parameter.


## Exporting Data by OTLP Exporter

### Prerequisites
Set the following environment variable:
```shell
OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE = 'DELTA'
```

### Configuration File
```toml
[OTEL]
service_name = "agentuniverse-demo"
provider_class = "opentelemetry.sdk.trace.TracerProvider"
id_generator_class = "opentelemetry.sdk.trace.RandomIdGenerator"

instrumentations = [
  "agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor.LLMInstrumentor",
  "agentuniverse.base.tracing.otel.instrumentation.agent.agent_instrumentor.AgentInstrumentor",
  "agentuniverse.base.tracing.otel.instrumentation.tool.tool_instrumentor.ToolInstrumentor",
]

[OTEL.resource]
deployment = "development"
team = "llm"
version = "1.0.0"
environment = "dev"

[[OTEL.processors]]
class = "opentelemetry.sdk.trace.export.BatchSpanProcessor"

  [OTEL.processors.exporter]
  class = "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter"

    [OTEL.processors.exporter.args]
    endpoint = "http://localhost:4318/v1/traces"

[[OTEL.metric_readers]]
class = "opentelemetry.sdk.metrics.export.PeriodicExportingMetricReader"

  [OTEL.metric_readers.args]
  export_interval_millis = 1000

  [OTEL.metric_readers.exporter]
  class = "opentelemetry.exporter.otlp.proto.http.metric_exporter.OTLPMetricExporter"

    [OTEL.metric_readers.exporter.args]
    endpoint = "http://localhost:4318/v1/metrics"
```

### Features
- Sends trace and metric data to observability platforms like SigNoz or Jaeger using OTLPSpanExporter and OTLPMetricExporter.Enables visualization and monitoring of various metrics and traces through integrated platform capabilities.