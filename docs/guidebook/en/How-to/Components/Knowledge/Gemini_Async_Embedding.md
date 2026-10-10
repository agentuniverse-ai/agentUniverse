# Asynchronous Gemini embeddings

`GeminiEmbedding.async_get_embeddings()` executes the existing synchronous
`get_embeddings()` method through `asyncio.to_thread`. Lazy SDK initialization
and the blocking embedding request therefore do not run on the event-loop
thread. This also supports injected synchronous clients without requiring a
particular version of the optional `google-genai` async API.

Model selection, result ordering, forwarded keyword arguments and existing
exception behavior remain those of `get_embeddings()`. Python context variables
are propagated to the worker. The synchronous API and LangChain wrapper are
unchanged.

Cancelling the coroutine releases the awaiting task but cannot stop a synchronous
SDK request already running in the executor. Configure timeouts on your client
where needed. Calls use the event loop's default executor; this change does not
add concurrency limits or promise thread safety for arbitrary injected clients.
Callers must only share clients that support their intended concurrent usage.

Offline regressions (no Gemini SDK installation or credentials needed):

```shell
python -m pytest -q tests/test_agentuniverse/unit/agent/action/knowledge/embedding/test_gemini_async_nonblocking.py
```
