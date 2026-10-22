# Opt-in Tool result artifacts

Large results can overwhelm a planner's immediate observation. `ArtifactResultTool` wraps a selected existing Tool and, **only when enabled**, persists a complete oversized text/JSON result and returns a small content-free reference (ID, SHA-256, byte count, media type, expiry, storage summary). Small results retain their original type/value. The reference does not pretend to be a semantic summary.

```python
from agentuniverse.agent.action.tool.result_artifacts import (
    LocalToolArtifactStore, ArtifactResultTool, ArtifactReadTool,
)

# Choose a private directory for this application's/session's artifacts.
store = LocalToolArtifactStore("./private-session-artifacts", max_bytes=16_777_216,
                               max_page_chars=4096, ttl_seconds=3600)
wrapped = ArtifactResultTool(
    name="fetch_evidence", target=my_existing_tool, artifact_store=store,
    enabled=True, threshold_bytes=65_536,
    input_keys=my_existing_tool.input_keys,
)
reader = ArtifactReadTool(artifact_store=store)
reference = wrapped.run(query="approved query")
# When reference['kind'] == 'tool_artifact':
page = reader.run(artifact_id=reference["id"], expected_sha256=reference["sha256"],
                  offset=0, limit=4096)
```

Both tools are regular agentUniverse Tools: use their public `run`/`async_run`, register the configured instances in your application's ToolManager, or pass `wrapped.as_langchain()` and `reader.as_langchain()` to a planner. The wrapper invokes the target's public run/async_run including validation and legacy ToolInput dispatch. Configure these adapters programmatically; no global default or auto-loaded YAML enables persistence. Both synchronous and asynchronous target paths are supported; local serialization/publication after target completion is synchronous and bounded, not asynchronous disk I/O.

Pages contain UTF-8 decoded text with Unicode-character offsets, next_offset (null at end), total_chars, media type and verified hash. JSON is stored as canonical complete JSON; individual pages may split JSON tokens. Concatenate all pages before parsing. A read validates the full bounded artifact's hash; this favors integrity over large-file random-read efficiency. Supplying the reference's expected_sha256 additionally checks it against the read result. IDs cannot select arbitrary paths and artifact symlinks are rejected.

Store publication uses flushed temporary files and atomic no-clobber hard links, including forced-ID collision protection. Ordinary failed publications clean temporary files; no overwrite fallback occurs on unsupported filesystems. Power-loss directory durability is not guaranteed. Missing, expired, corrupt, out-of-range and oversized operations fail explicitly. Target/store failures propagate instead of truncating evidence; the target may already have performed side effects before a store failure, so do not blindly retry.

Persistence defaults to `enabled=False`. Explicit enabling is a content-retention decision: results may contain sensitive data. Use a private directory and expose its reader only to the intended application/session. This is not encryption, tenant authorization, secret detection or a defense against an adversary who can mutate the filesystem. Existing target tracing/conversation hooks may still record the full raw result; this wrapper does not change those policies or guarantee that all context paths shrink. It only changes the selected Tool's returned observation.

Expiry denies reads but does not delete data. Call `store.remove(id)` explicitly when retention ends, or manage the dedicated directory externally. There is a per-artifact byte limit, no aggregate disk quota or background cleanup. A process crash may leave a temporary file; do not mistake TTL for secure erasure. Objects/arrays must round-trip as plain JSON without coercion; embeddings or arbitrary Python objects are not automatically serialized.

Tests cover real Tool sync/async/legacy dispatch, Unicode JSON page reconstruction, a real LangChain ReAct executor with a deterministic local FakeListLLM selecting the wrapper then reader, concurrent identical results, collision/failure cleanup, corruption/expiry/missing files, cancellation and disabled defaults. Trace sinks are isolated in tests; no paid provider is called.
