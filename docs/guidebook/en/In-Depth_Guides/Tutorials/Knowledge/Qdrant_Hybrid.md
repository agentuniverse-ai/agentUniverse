# Native Qdrant dense/sparse retrieval

`QdrantHybridStore` is an opt-in Store for a **dedicated** Qdrant collection. It writes two named vectors together and uses the server's prefetch + reciprocal-rank fusion API. The existing `QdrantStore` is unchanged. This is a retrieval backend, not a sparse encoder: choose and version your own dense model and sparse vocabulary/weighting for both documents and queries.

## Install and configure

Use Python 3.10–3.12 and `pip install 'agentuniverse[qdrant_hybrid_ext]'`. The optional dependency is qdrant-client >=1.14.3,<1.15: newer client/Python combinations conflict with this project's NumPy 1.26 constraint. Python 3.13 is not supported by this extra. Real-service tests use Qdrant 1.14.1 and client 1.14.3, not all Qdrant versions.

Copy `agentuniverse/agent/action/knowledge/store/qdrant_hybrid_store.yaml.example` into your application's Store scan path. Set an authorized service URL, collection name and exact dense dimensions. `connection_args` is passed to the official client; configure authentication/TLS there using the application's normal secret mechanism, never document metadata. For a disposable local test use `http://127.0.0.1:16333`; deployed services should use authenticated TLS.

Provision once with `create_collection: true`, then set it to false before concurrent workers start. Creation races fail explicitly. Existing collections must have exactly `au_dense` (cosine, configured dimensions, no multivectors) and `au_sparse` (no IDF modifier). No collection is dropped/rebuilt and no legacy collection is adopted or migrated. Keep this collection exclusively owned by this adapter: schema checks and payload markers are not access control.

```python
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.qdrant_hybrid_store import QdrantHybridStore

store = QdrantHybridStore(
    connection_args={"url": "http://127.0.0.1:16333", "trust_env": False},
    collection_name="manuals_demo", dimensions=2, create_collection=True,
)
try:
    # Illustrative precomputed vectors, not an embedding model/quality benchmark.
    receipt = store.upsert_document([Document(
        id="manual:ZX-42", text="ZX-42 startup guide", embedding=[0.8, 0.6],
        metadata={"product": "ZX-42", "qdrant_sparse": {"indices": [42], "values": [2.0]}},
    )])
    result = store.query(Query(
        embeddings=[[1.0, 0.0]],
        ext_info={"sparse_vector": {"indices": [42], "values": [1.0]},
                  "filters": {"product": "ZX-42"}},
    ))
finally:
    store.close()
```

## Data and query contract

- Every write supplies both vectors. Dense values must be finite with nonzero norm; the adapter normalizes cosine vectors. Sparse indices are unique uint32 integers; weights are finite nonzero float32-normal values. Indices are sorted with their corresponding weights. Zero/empty sparse vectors must be handled by your preprocessing policy, not silently routed to a different mode.
- Stable string document IDs map to UUID5 point IDs, including strings that already look like UUIDs. Original IDs remain in payloads. All insert/update/upsert methods use complete idempotent replacement semantics, not create-only/existence checks. Updating replaces **both** vectors and the whole metadata payload; omitted fields disappear. IDs must be stable across ingestion runs.
- `mode` is `dense`, `sparse` or `hybrid`. Hybrid requires exactly one `Query.embeddings` vector plus `ext_info.sparse_vector`; dense needs only the former, sparse only the latter. Text/image query bundles and unknown options are rejected. `query_str` is not automatically embedded. A Knowledge pipeline must supply both vectors via a configured processor/query caller. The integration test exercises registered YAML → TxtReader → processor → Store → public Knowledge query.
- `candidate_k` bounds each prefetch list; final `similarity_top_k` cannot exceed it. A query top-k of zero returns no results without I/O. Sparse queries return only matching sparse terms. Native RRF scores are not probabilities, do not have the same scale as cosine scores, and do not imply improved relevance. Ties retain engine ordering; membership at a tied top-k boundary is not guaranteed stable.
- `ext_info.filters` supports up to 64 exact scalar equalities on top-level metadata keys. All are ANDed in both prefetch routes and final retrieval. Types matter: `true`, `1`, `1.0`, `"1"` and null differ. Nested/range/OR filters are not supported. These application filters are not authorization isolation.
- Results carry `metadata.qdrant_retrieval` with mode, score and candidate limit. With `with_vectors: true`, they also contain normalized dense vectors and `metadata.qdrant_sparse`. Inputs are copied. Remove diagnostic `qdrant_retrieval` before intentionally writing a retrieved Document back; that key is reserved.

## Failure handling and lifecycle

Batch preflight rejects duplicate IDs, malformed vectors and configured count/text/encoded-byte limits before remote writes. Empty batches are no-ops. Reads have a total text-character limit, not a transport-memory guarantee. Query/filter and write serialization budgets are checks on serialized data, not a streaming or process-memory sandbox.

Writes use `wait=True` and only return a receipt after a COMPLETED response. An ACK-only response raises; timeout, transport failure or cancellation can leave the remote outcome unknown. Read/reconcile the affected IDs before retrying. The adapter does not implement automatic retries or multi-operation transactions and does not promise atomic batch rollback. Qdrant client-level timeouts govern writes; query/create also use their supported server timeout fields. A client timeout is not proof that the server stopped writing.

Use native `async_*` methods and `await store.aclose()` for async clients. Cancellation propagates. Do not reuse an async client across event loops or close clients while operations run. Sync and async clients have separate lifecycles. Inherited public Knowledge insertion currently logs Store errors; inspect Store receipts/errors directly when strict acknowledgement is needed, rather than treating a Knowledge completion log as a transaction receipt.

## Reproduce tests

Start a disposable Qdrant service (no production data):

```sh
docker run --name au-qdrant-test -p 127.0.0.1:16333:6333 -e QDRANT__TELEMETRY_DISABLED=true qdrant/qdrant:v1.14.1
AU_QDRANT_TEST_URL=http://127.0.0.1:16333 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --import-mode=importlib tests/test_agentuniverse/unit/agent/action/knowledge/store/test_qdrant_hybrid_store.py tests/test_agentuniverse/integration/test_qdrant_hybrid_store.py
```

Install project runtime/test dependencies plus the extra first. Each integration test uses a unique temporary collection and removes only that collection. Tests cover direct native-fusion parity, dense/sparse behavior, both-vector replacement, reopen/delete, scalar filter types, schema rejection, batch preflight, async CRUD and the public Knowledge path. Cancellation is a client mock test, not proof of server rollback. Fixtures use manually supplied vectors and do **not** measure model relevance, production recall or latency.

References: [Qdrant hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/), [vectors](https://qdrant.tech/documentation/manage-data/vectors/).
