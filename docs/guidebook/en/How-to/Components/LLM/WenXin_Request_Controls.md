# WenXin native request controls

`WenXinLLM` uses Qianfan's native ChatCompletion API, not the OpenAI-compatible
Qianfan channel. Framework controls are translated before calling `do` or `ado`:

- `max_tokens` becomes `max_output_tokens`. The selected native model still decides
  whether it supports this field and what range it accepts. This does not add token
  limit support to models lacking it or clamp model-specific values locally.
- `request_timeout` is passed to the SDK as a timeout in seconds. An unset/None
  timeout is omitted, preserving the SDK's own default and environment behavior.
- `max_retries=N` becomes `retry_count=N+1`: Qianfan counts total attempts, whereas
  the framework counts retries after the initial attempt. In particular, zero
  disables retries. None omits the override. The usual framework default of two
  retries corresponds to the SDK's three total attempts.

Per-call framework values override component values. Explicit native
`max_output_tokens` and `retry_count` take precedence over their framework aliases.
Framework-only aliases are removed from the native request body. Unset framework
output limits are omitted rather than sent as null. Other native parameters and
response parsing are unchanged. The LangChain bridge preserves an explicit zero
retry setting; it uses the same native adapter for sync/async invocation and
configured streaming. This does not change the separate Qianfan OpenAI channel.

Example component settings for a native model supporting `max_output_tokens`:

```yaml
model_name: ERNIE-3.5-8K
max_tokens: 128
request_timeout: 7
max_retries: 0
```

Offline regressions use the declared-compatible Qianfan 0.3.12 SDK's request
builder and retry implementation. Only the final SDK transport is substituted;
no provider credentials or live inference are required. Tests exercise component
configuration, LangChain, sync/async, streaming, defaults, per-call precedence,
caller argument preservation and actual retry attempt counts. Qianfan creates a
disk cache under the process home; use a writable HOME in sandboxed test setups.

```shell
python -m pytest -q tests/test_agentuniverse/unit/llm/test_wenxin_request_controls.py tests/test_agentuniverse/unit/llm/test_wenxin_llm.py
```

## 中文说明

本修复仅针对 WenXinLLM 的千帆原生 SDK 调用，不改变 OpenAI 兼容渠道。
`max_tokens` 转为原生 `max_output_tokens`，模型仍负责校验字段支持情况和取值范围。
`request_timeout` 传给 SDK；未设置时保留 SDK 默认值。
`max_retries` 表示首次调用之后的重试次数，而 SDK 的 `retry_count` 表示总尝试次数，
因此转换时加一，零次重试对应一次尝试。显式原生参数优先于框架别名。
同步、异步及 LangChain 调用采用同样的规则。离线测试验证请求构造和实际重试次数，
不代表已完成真实模型推理验证。
