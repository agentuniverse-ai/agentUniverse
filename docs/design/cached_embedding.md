# Bounded embedding cache

`CachedEmbedding` wraps a named existing Embedding component. Configure it as
the embedding component of a store, or obtain its LangChain adapter. It uses
an in-process LRU cache only: no disk files, shared service or new dependencies.

```yaml
name: cached_embedding
backend_name: openai_embedding
cache_version: my-model-and-options-v1
max_entries: 1024
metadata:
  type: EMBEDDING
  module: agentuniverse.agent.action.knowledge.embedding.cached_embedding
  class: CachedEmbedding
```

Keys isolate the actual backend object, exposed model/dimensions, explicit
cache version, type-tagged keyword options and exact text. Query/document
roles remain separate when passed as `text_type`; omitted and explicitly supplied
defaults may create redundant entries but cannot conflate distinct options.
Supported options are null, strings, booleans, integers, finite floats, lists,
tuples and recursively string-keyed dictionaries. Lists and tuples remain distinct;
mapping order is retained conservatively. Non-string keys, unsupported objects and
cyclic/deeply recursive structures fail before provider IO. Options are deep-copied
once for the key and provider call so provider mutations do not alter caller data.
**Bump cache_version when changing endpoint, provider revision, normalization or
other settings not exposed as model/dimensions.** Do not mutate configuration or
backend settings during an active request. Nondeterministic providers should not
be cached. Nested cache backends are rejected to prevent recursive delegation.

Input duplicates share one backend request and are reconstructed in original
order with independent output lists. Whole responses are validated for count,
finite numeric values and consistent dimensions before storing any new entry.
Exceptions and cancellation are not cached. Partial cache hits are retained
when a new request fails. A zero capacity disables retention (batch dedup remains).
LRU capacity bounds entry count, not bytes; large texts/vectors still consume RAM.

Sync and async methods share the cache but never hold its lock across provider
IO. Simultaneous misses may issue duplicate requests: there is no single-flight
or cross-process cache. `clear_cache()` increments a generation so old requests
cannot repopulate it, without cancelling their callers. Cache backend references
are retained until replacement to prevent object-ID reuse collisions.

Only use for data allowed to remain in process memory. Keys retain raw text and
options; never log/export the cache. Clearing drops Python references, not a
cryptographic memory wipe. A cache hit still requires backend component lookup.
The wrapper does not change upstream defaults or introduce a global cache.

Tests use a deterministic provider and the actual OpenAIEmbedding implementation
with SDK IO mocked, plus LangChain adapter and existing embedding regressions.
The integration suite also registers the shipped YAML with the real embedding
manager and exercises real FAISS insertion, query and persisted index reopening.
The underlying embedding provider is deterministic; no live API or production
latency benchmark is claimed.

Manager lookups copy configuration but deliberately share the registered cache
state. `clear_cache()` on one copy clears that state for all copies. The backend
is resolved with `new_instance=False` so lookup copies do not invalidate keys.
Use a provider that supports the intended concurrent call pattern; this wrapper
does not serialize provider IO. Changing a copy's version isolates entries;
capacity changes can evict entries shared by other copies, never change vectors.

## 中文

这是可选的进程内向量缓存，默认管线不变。文本、角色、模型、维度、调用参数
及显式版本共同隔离结果；更换端点或未暴露的模型设置必须更新版本。
不会把失败、取消、数量不符或非有限向量写入缓存；并发未命中可能重复请求。
容量限制是条目数而非字节数，需结合输入长度配置。缓存保留原文，不适合
禁止在内存中保留的数据。验证采用模拟提供商边界，不宣称真实 API 加速效果。
