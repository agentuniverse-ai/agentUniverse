# Span export field policies / Span 导出字段策略

`PolicySpanExporter` creates a separate, allowlisted export view of completed
OpenTelemetry spans. It works independently of GenAI instrumentation and can
wrap the existing `SpanJsonExporter`, an OTLP exporter, or an SDK exporter.

```python
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from agentuniverse.base.tracing.otel.span_processor.policy_span_exporter import (
    ExportField, PolicySpanExporter, SpanExportPolicy,
)
from agentuniverse.base.tracing.otel.span_processor.span_json_exporter import SpanJsonExporter

policy = SpanExportPolicy(attributes={
    "au.span.kind": ExportField(str, values=frozenset({"llm", "tool", "agent"})),
    "au.llm.usage.prompt_tokens": ExportField(int),
    "au.llm.usage.completion_tokens": ExportField(int),
})
provider.add_span_processor(SimpleSpanProcessor(
    PolicySpanExporter(SpanJsonExporter("./approved-monitor"), policy)
))
```

The empty policy exports IDs, parent relationships, timestamps, kind and status
code, with a constant name. It omits attributes, resources, events, links,
status descriptions, trace state, and original instrumentation scope metadata.
Literal approved span/event names can be enabled. Resources and event fields
have separate rules. Fields require exact scalar types (booleans are not
integers), finite floats, signed 64-bit integers, bounded strings, and explicitly
enabled homogeneous arrays. Oversized or nested values are omitted rather than
stringified or partly disclosed. String limits count Unicode code points.
Rules are copied and frozen; the original span and business input are unchanged.

For the JSON exporter, explicitly allow only trusted routing values as above:
`au.span.kind` controls its output directory. With the empty policy it writes no
files. This wrapper is an export boundary, not a universal secret detector:
allowing a string field permits any text satisfying that rule. Wrap **every**
exporting processor; an additional raw exporter, logs, metrics and in-memory
instrumentation remain outside its scope. No global exporter is automatically
reconfigured. This does not remove sensitive data already captured in memory.

Projection failures fail the entire batch before delegation; downstream failures
return FAILURE without retrying original data. Cancellation/BaseException is
not swallowed. Flush and shutdown delegate to the owned downstream exporter;
do not share that exporter with another owner.

## 中文

此包装器可独立使用，不依赖 GenAI 语义适配。默认仅保留追踪 ID、父子关系、
时间、kind 与状态码；名称改为固定值，其余文本和载荷入口默认关闭。字段、
资源和事件均需显式允许，类型与长度不合格直接省略，不转换嵌套数据为字符串。
字符串长度按 Unicode 码点计数，数组需单独启用。原 span 与业务输入不变。

现有 JSON 导出器按 `au.span.kind` 选择文件夹，因此示例使用固定枚举值；
空策略不会生成 JSON 文件。需包装每个导出 processor；日志、指标、其他原始
导出器和内存中已采集的内容不在此边界内。允许某字符串字段意味着接受规则内
的任意文本，不能把它当成万能脱敏器。转换失败不会发送部分批次或回退到原始
数据；flush/shutdown 委托给唯一下游。不要让多个所有者共享同一个下游。

Validation uses real SDK spans, in-memory and actual JSON-file exporters,
parent/child relationships, exception and asyncio cancellation spans, all field
boundaries, input immutability and failure/lifecycle behavior. No live remote
collector or whole-project CI result is implied.
