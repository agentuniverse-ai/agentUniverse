# Gemini embedding dimensions

`GeminiEmbedding.embedding_dims` is forwarded as the Google Gen AI SDK's
`config.output_dimensionality`. For a compatible configured model such as
`gemini-embedding-001`, configuring 256 requests a 256-dimensional vector instead
of silently using the model default. Unset dimensions remain unset on the wire.
The adapter does not assume every model has 768 dimensions or supports reduction.
The provider validates requested dimensions and reports unsupported values.
There is no local truncation, padding, normalization, or fallback retry.

Native sync/async calls and the LangChain embedding adapter use the same dimension
setting. Model selection, batch ordering, task-role behavior and unconfigured
requests are unchanged. Other keyword arguments do not become SDK configuration.
No new dependency is imported when a custom client is supplied.

When changing dimensions, rebuild existing vector indexes with matching document
embeddings and collection dimensions. Model-specific dimension ranges and any
normalization requirements remain the caller's responsibility. See the
[Gemini embedding API](https://ai.google.dev/api/embeddings) and
[embedding size guide](https://ai.google.dev/gemini-api/docs/embeddings#controlling-embedding-size).
In particular, legacy `embedding-001` does not support output dimensionality;
explicitly requesting it now surfaces the provider error instead of ignoring it.

Offline regressions use real `google-genai` request conversion and response parsing,
replacing only the SDK HTTP request boundary. They cover component configuration,
batch order, sync/async calls, LangChain, unchanged defaults and provider errors.
They require the optional SDK (validated with `google-genai==1.0.0`) and skip SDK
cases when it is absent. Mocked responses verify adapter wiring, not live model
availability or server acceptance of every model/dimension combination.

```shell
python -m pytest -q tests/test_agentuniverse/unit/agent/action/knowledge/embedding/test_gemini_request_config.py
```
