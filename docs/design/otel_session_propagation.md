# AU session propagation

`AUSessionPropagator.extract` takes the first value returned by the configured
getter and stores that **string**, not the getter's list, in OpenTelemetry
baggage. This preserves the session ID when another service propagates it with
`W3CBaggagePropagator`. The `AU-SessionId` header takes precedence over
`auSessionId`. Extraction still updates the AU session and the supplied span's
`au.trace.session.id` attribute; this change does not redesign their lifecycle.

Injection has two explicit modes:

- `inject(carrier)` keeps the existing behavior: use the ambient AU session.
- `inject(carrier, context=ctx)` uses session baggage from that context only.
  `AU-SessionId` takes precedence over `auSessionId`. An explicitly empty context,
  absent session, empty string, or non-string value emits no session headers;
  it never falls back to a different ambient session. If the preferred key is
  present but empty/invalid, the lower-priority key is not substituted.

A nonempty string is emitted under both header names using the supplied setter.
Injection does not change the current AU session or the supplied context.

```python
from opentelemetry.baggage import set_baggage
from opentelemetry.context import Context
from agentuniverse.base.tracing.otel.propagator.au_session_propagator import AUSessionPropagator

ctx = set_baggage("auSessionId", "example-session", Context())
headers = {}
AUSessionPropagator().inject(headers, context=ctx)
assert headers == {"AU-SessionId": "example-session", "auSessionId": "example-session"}
```

Compatibility: code that read session baggage as a one-element list should now
read it as a string. Callers that explicitly passed an empty context while
expecting the ambient session should omit `context` instead. Legacy list-valued
session baggage is not automatically coerced into a string.

Tests: `tests/test_agentuniverse/unit/base/tracing/test_session_propagation_contract.py`
uses real OpenTelemetry contexts, W3C/composite propagators and spans, plus
custom getter/setter and parallel explicit-context cases. No service is required.

## 中文说明

提取会话时仅把 getter 返回的第一个字符串写入 baggage，避免跨标准传播器时
会话 ID 变成列表的文本表示。显式传入 context 时只读取该 context，不回退到
环境会话；不传 context 时保持原有 AU 会话行为。两个键均存在时 HTTP 风格键
优先。此变更不处理上下文生命周期或清理逻辑。
