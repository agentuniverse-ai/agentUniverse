# Session processor flush contract

`SessionSpanProcessor` only annotates spans synchronously. It does not buffer or
export spans, so `force_flush(timeout_millis=...)` returns `True` immediately.
This follows the [OpenTelemetry SpanProcessor contract](https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.html#opentelemetry.sdk.trace.SpanProcessor.force_flush).
`on_end` and `shutdown` remain no-ops returning `None`.

Why this matters: with SDK 1.25.0, the previous implicit `None` return makes
`TracerProvider.force_flush()` report failure. If another processor is registered
after the session processor, the SDK skips that processor's flush. A real batch
processor therefore still has its ended span queued after the flush call.

Scope and limitations:

- The repository permits SDK 1.25.0. SDK 1.45.1 tolerates the previous `None`
  return at provider level; the integration failure is not universal.
- TelemetryManager appends the session processor after configured processors.
  Skipping a later processor requires a later registration or another ordering;
  the default configuration on SDK 1.25.0 still reports a false flush failure.
- The background worker or shutdown may subsequently export queued spans.
  This is not a claim of permanent data loss.
- Other processors' real failures and timeouts are not masked by this change.

Tests: `tests/test_agentuniverse/unit/base/tracing/test_session_flush_contract.py`
checks the direct contract, default provider, real batch export in both orders,
repeated flush, a following processor failure, and unchanged span attributes.

## 中文说明

SessionSpanProcessor 没有待导出的缓冲数据，刷新应立即返回 True。旧版 SDK
会把原来的 None 当作失败并可能跳过后续处理器；新版 SDK 已容忍此返回值。
修复不改变其他处理器的失败结果，也不声称已证明永久数据丢失。
