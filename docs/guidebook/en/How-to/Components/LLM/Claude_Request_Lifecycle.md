# Claude request resource ownership

Each native Claude request owns its SDK client. Non-streaming requests close that
client after success, SDK failure, response parsing failure, or cancellation.
A started streaming request closes both its SDK response and its own client on
exhaustion, iteration failure, cancellation, or explicit close of the native
provider iterator. Finishing one request never closes another request's client,
even when both use the same ClaudeLLM instance.

Streaming client construction and HTTP acquisition are lazy: they occur when the
returned native iterator is first advanced. An unstarted iterator owns no client
or HTTP response. Consequently streaming connection, configuration and HTTP errors
surface on first iteration rather than on `_call` / `_acall` return. Callers should
handle failures around iteration as well as request creation.

The `client` / `async_client` fields remain the last created client for compatibility;
they are not the ownership handle used to close an individual request. Existing
explicit `close()` / `aclose()` methods still address those fields.

This change does not implement close forwarding in generic tracing/plugin wrappers.
Use `close()` / `aclose()` on the native provider iterator when ending consumption
explicitly; cancellation while an async iteration is awaiting the SDK propagates
through it. Merely breaking a loop without closing the iterator is not a guaranteed
cleanup signal. It also does not change the existing `stream` / `streaming` alias
policy or add support for new Claude content-block types.

Offline regressions use Anthropic 0.26.1 (within the declared dependency range),
HTTPX 0.28.1 MockTransport and real response/SSE parsing. They exercise HTTP400,
read errors, early close, cancellation before headers and midstream, overlapping
requests, unstarted iterators and preserved successful cleanup. No live API calls
or full-project test result is implied.
