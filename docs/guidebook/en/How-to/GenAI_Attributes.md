# GenAI attributes v1.37.0 / 固定版本GenAI属性适配

An explicitly supplied `GenAIAttributeAdapter` supplements the existing LLM and
Tool instrumentors. It does not install another tracing system or exporter, and
is independent of export filtering. Its attribute names and interpretation are
pinned to [OpenTelemetry GenAI v1.37.0](https://github.com/open-telemetry/semantic-conventions/blob/v1.37.0/docs/gen-ai/gen-ai-spans.md),
a development-status specification. This is an **attribute subset**, not a claim
of full semantic-convention conformance: existing aU span names, kinds, metrics,
legacy attributes and exporters remain in use. No schema URL is attached to
legacy attributes, since that would incorrectly claim they use that schema.

```python
from agentuniverse.base.tracing.otel.instrumentation.gen_ai_semconv import (
    GenAIAttributeAdapter, GenAIIdentity,
)
from agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor import LLMInstrumentor
from agentuniverse.base.tracing.otel.instrumentation.tool.tool_instrumentor import ToolInstrumentor

# Resolve only configurations whose actual destination your application knows.
# Account for channels, gateways and per-call endpoint/model overrides here.
def identity(llm, kwargs):
    if llm.name == "approved_openai" and not llm.channel and "api_base" not in kwargs:
        return GenAIIdentity("openai", kwargs.get("model", llm.model_name))
    return None

adapter = GenAIAttributeAdapter(identity)
LLMInstrumentor().instrument(tracer_provider=provider, gen_ai_adapter=adapter)
ToolInstrumentor().instrument(tracer_provider=provider, gen_ai_adapter=adapter)
```

Pass these options when first instrumenting. Already-installed instrumentors
must be uninstrumented/reconfigured during application startup; do not construct
or reconfigure singleton instrumentors while requests are running. The resolver
is application code and must be read-only. It returns identity at the actual
LLM call boundary; no provider is guessed from a class/registered alias. A
missing/failed resolver marks identity unknown and omits provider/model/operation
rather than manufacturing a value. A gateway that cannot report its final vendor
must remain unknown. The adapter never inspects prompts or raw response bodies.

| Observed input | Exported attribute |
| --- | --- |
| Explicit identity operation/provider/model | gen_ai.operation.name / gen_ai.provider.name / gen_ai.request.model |
| Explicitly supplied input/output usage | gen_ai.usage.input_tokens / gen_ai.usage.output_tokens |
| LLMOutput.finish_reason | gen_ai.response.finish_reasons (one-element sequence) |
| Tool name | gen_ai.operation.name=execute_tool / gen_ai.tool.name |
| Raised exception/cancellation type | error.type |

Every adapted span includes `au.gen_ai.semconv.version=1.37.0`. The aU extensions
`au.gen_ai.identity.status` (configured/unknown) and `au.gen_ai.usage.status`
(unknown/partial/provided/invalid) are **not** standard OTel attributes.

Usage is captured before legacy Monitor may estimate and mutate an LLMOutput.
Absent usage or a default empty TokenUsage stays unknown. Each direction is
omitted unless a field in that direction was explicitly supplied; explicit zero
is preserved. Negative components or totals outside signed 64-bit range are
rejected. Streaming records the latest supplied aggregate, never the sum of
repeated cumulative values. It assumes the provider's TokenUsage uses the
project's additive component representation; this does not repair inaccurate
provider parsers or distinguish an upstream provider's own estimates. Previously
observed valid usage may remain on a span that later receives invalid usage;
check its status. A failure after some output does not claim complete usage.

Parent IDs and normal span lifetime remain with the existing instrumentors.
Their error paths now include BaseException so task cancellation closes the span
and propagates. Consumers still need close/aclose when abandoning streams. A
stream returned but never started has the pre-existing deferred lifecycle; this
adapter does not add a finalizer. Existing logs and au.llm.input/output may contain
content; the adapter is not a redactor or a logging privacy switch.

## 中文

显式传入适配器才启用，固定到v1.37.0的属性子集，保留现有span名称、kind、指标和
legacy字段，不声称完整规范符合性，也不依赖导出字段策略。供应商身份由应用在
实际调用边界解析；对网关、channel或动态endpoint无法确定时返回None，不能从
兼容OpenAI的类名猜测供应商。resolver必须只读，配置在启动阶段完成。

usage在Monitor估算之前采集；缺失或默认空TokenUsage为unknown，未提供的方向
不补零，显式零值保留。流中重复累计值只保留最新一次，不累加。不修复提供方自己
的usage解析错误或估算。自定义status/version字段明确使用au前缀，不冒充标准字段。
取消路径结束span后继续抛出；提前停止消费需要关闭迭代器，未开始消费的流仍有
原有延迟生命周期限制。此功能不脱敏，不改变现有日志和输入输出字段。

## Validation

Tests exercise real SDK in-memory spans through LLM.call/acall, sync/async
streams, nested Tool.run/async_run, task cancellation and unknown/partial/zero
usage. Optional actual-collector test uses OTLP/HTTP at 127.0.0.1:14328, then
matches the emitted span ID and mapped attributes in the dedicated container's
logs. Use the included collector config and set AU_GENAI_COLLECTOR_CONTAINER to
that container name. The test uses only synthetic data; no paid provider.

Tested collector: otel/opentelemetry-collector:0.111.0,
digest sha256:7020db3692a3d722fec002f39608ffe3a5d2fa4d09e14607cf33b9416f2c1df8.
SDK 1.25.0, instrumentation 0.46b0, HTTP exporter 1.25.0; SDK instrumentation
requires setuptools<81 for pkg_resources. Full-repository CI and all provider
implementations are outside this validation.
