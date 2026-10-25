# Per-call streaming overrides

The legacy `OpenAILLM`, `OllamaLLM` and `OllamaLLMChannel` accept both `stream`
(the SDK spelling) and `streaming` (the framework spelling) in synchronous and
asynchronous calls. For boolean values, precedence is:

1. Explicit `stream`
2. Explicit `streaming`
3. The instance's configured `streaming`

Thus `stream=False, streaming=True` requests and parses a complete response;
`stream=True, streaming=False` requests and parses a stream. Explicit `False`
is an override, not a missing value. The same resolved value drives the SDK
request and response parser. Per-call choices do not modify instance defaults.

`stream` retains its previous priority at the SDK boundary. The fix makes the
legacy OpenAI parser follow that same choice and teaches the two Ollama adapters
the framework alias. The alias is consumed locally, not forwarded to SDKs.
It does not change other providers, channel capability policies, or LangChain
wrapper APIs. Supply booleans; this change does not introduce new coercion or
validation for other values.

The offline tests exercise real OpenAI 1.55.3 and Ollama 0.2.1 clients with
`httpx.MockTransport`, including real SSE/NDJSON decoding and both sync/async
response types. Ollama 0.2.1 is within the project's declared `^0.2.1` range;
there is no dependency lockfile. No running server or API credentials are needed.

```shell
python -m pytest -q tests/test_agentuniverse/unit/llm/test_stream_option_consistency.py
```
