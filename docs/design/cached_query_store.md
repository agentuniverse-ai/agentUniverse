# Exact-query result cache

Repeated identical RAG lookups need not repeat an unchanged store query. This
optional Store wrapper caches successful result lists in one process. It differs
from embedding caches, schema-initialization caches and local reranking: it avoids
the actual retrieval call, not just a preparatory embedding/model/setup operation.

## Configure explicitly

Copy `agentuniverse/agent/action/knowledge/store/cached_query_store.yaml.example`
to your application's registered store-config directory as a `.yaml` file. The
`.example` suffix prevents automatic registration; Configer itself only loads the
copied `.yaml`, not `.example` files. Set `backend_store` to an existing registered
non-cache Store and `cache_revision` to an explicit corpus/retrieval configuration
version. Enable caching with `enabled: true` (the template defaults to false).

Use `stores: [cached_query_store]` in Knowledge. All normal router, reader and
post-processor configuration remains applicable. The public Knowledge query path
then passes through this wrapper; writes through the same component invalidate it.
The backend remains responsible for client setup, timeouts and thread safety.
No runtime dependencies are added. Wrapper chains, including self references,
are rejected, rather than allowed to recurse indefinitely.

## Key and ownership contract

An exact key includes sync/async mode, every Query instance field and keyword
argument. Values are type-tagged: bool, int, float, list, tuple, set and frozenset
do not collide. Set order is canonical; mapping insertion order is deliberately
preserved for providers whose filter order may matter. String comparisons and
query text are exact, with no case/Unicode normalization or semantic matching.

Non-finite numbers, unsupported objects (including image inputs), cycles, Query
subclasses, oversized keys or disabled caching delegate without caching. Such
delegation still deep-copies query/kwargs; providers requiring object identity or
uncopyable request objects should not use this wrapper. Backend results must be
lists of Documents. Documents are deep-copied on every return, including misses,
and an independently owned snapshot is cached. Unserializable result metadata or
oversized result sets bypass retention without truncating the returned list.

The standard Store `create_copy` returns the same instance, so manager calls share
one cache and invalidation state. Registration replacement with a different backend
object clears it. The normal post-fork `_new_client` hook replaces the lock and
clears inherited cache state before serving requests; this is not a live-reset API.
`clear_cache()` is the thread-safe invalidation API during service.

## Freshness and trust boundaries

- TTL is monotonic and absolute from result retention; hits do not extend it.
- All four sync and async insert/upsert/update/delete methods invalidate before
  delegation and in `finally`, including provider exceptions and cancellation.
- Reads while writes are active bypass cache. Generation checks prevent older
  in-flight reads from repopulating entries after clear/write/config changes.
- No lock spans provider IO or an await. Concurrent identical cold queries may
  both call the provider; there is **no single-flight, retry or background refresh**.
- Queries overlapping writes can still return whichever snapshot the backend
  supplies. This is not transaction isolation or linearizable read-after-write.
- Writes made directly to the underlying store, another wrapper/process, external
  database tools, in-place model/client/filter configuration changes or index rebuilds
  are not observed. Coordinate `clear_cache()` or change `cache_revision`; ordinary
  TTL alone permits stale results until expiry. Each process has its own cache.

Do not use this wrapper when results depend on hidden request/auth/session context
unless that entire scope is represented explicitly in Query/kwargs or by separate
wrapper/backend instances. A `tenant` field is a cache partition only, **not an
authorization check**: the underlying provider must enforce access. In-memory keys
and documents retain sensitive content until removal; clearing is not secure wiping.
No query/content is exposed by `cache_info()`, but existing framework tracing rules
still apply. There is no disk cache or external cache service.

## Capacity and inspection

Defaults: 128 entries, 16 MiB combined encoded key/result budget, 256 KiB per entry,
64 KiB per key, 100 documents per entry and 30-second TTL (maximum one hour).
Least-recently used entries are evicted. Expired entries are pruned on cacheable
lookup; there is no timer thread. `cache_info()` returns entries, encoded_bytes,
hits, misses, bypasses and active_writes; counters describe lookups, not provider
success or wall-clock savings. TTL-expired entries may remain counted until lookup.

The byte accounting is deterministic encoded payload size, not Python heap usage.
Keys/results must be encoded and results copied before some checks, so budgets
bound retained payload, not peak provider response/parser memory. Bound backend
output and apply process-level resource limits separately where needed.

## Verified workflow and limits of evidence

The real integration copies the supplied configuration template to YAML, registers
actual managers, loads a text file through Knowledge.insert_knowledge, reopens a
file-backed SQLite store and performs three identical public queries. Its SQLite
query method runs once, and results match. Upsert removes the old keyword result;
delete removes the updated result. Only tracing side effects are patched; SQLite,
Jieba, routing, component lookup and querying run normally.

Additional deterministic tests cover typed keys, every query field, absolute TTL,
LRU/encoded budgets, empty results, provider failures, backend/config changes,
read/write races, input/output ownership and async cancellation. Async delegates
are tested with a controlled async provider; SQLite is synchronous and these tests
do not claim real asynchronous database integration or a live-server latency gain.
Existing SQLite index and Knowledge/RRF regressions are run alongside them.
