# SQLite FTS5 full-text backend

SQLiteFTS5Store is an independent file-backed Store, not an in-place modification
or migration of SQLiteStore. The older backend selects Jieba keywords, maintains
an inverted index and scores candidates in Python. This backend indexes the whole
document text with SQLite FTS5 and ranks matches in SQL. It does not need an
embedding API, keyword extractor or external database server.

## Setup and example

Use Python's sqlite3 build with FTS5 and JSON functions. The optional trigram
tokenizer requires SQLite 3.34+ with that tokenizer enabled. No extension is loaded
from disk; missing build capabilities produce explicit errors during initialization.

Copy `agentuniverse/agent/action/knowledge/store/fts5_store.yaml.example` into the
application's store configuration directory with a `.yaml` suffix. Choose a new
local database path and register normally. Set Knowledge `stores` to
`[sqlite_fts5_store]`; configure readers as usual. The template is not automatically
activated. The parent directory must exist. `:memory:` and arbitrary SQLite URI
options are intentionally unsupported because each operation owns a fresh connection.

Programmatic use:

```python
from agentuniverse.agent.action.knowledge.store.fts5_store import SQLiteFTS5Store
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query

store = SQLiteFTS5Store(db_path="./manuals-fts5.db")
store._new_client()  # normally called by framework bootstrap/post-fork hooks
store.upsert_document([Document(id="manual-1", text="battery charging procedure",
                                metadata={"edition": 2})])
result = store.query(Query(query_str="charging procedure", similarity_top_k=5,
    ext_info={"fts5": {"match_mode": "phrase", "metadata_equals": {"edition": 2}}}))
```

## Matching and language

The default tokenizer is `unicode61 remove_diacritics 2`. It is word-oriented,
case-insensitive and accent-folding; it is not a Chinese word segmenter. Choose
`tokenizer: trigram` for substring retrieval, including unsegmented Chinese text.
Trigram terms shorter than three Unicode characters are rejected rather than
silently presented as supported. It is not semantic/word-aware Chinese retrieval.
Tokenizer choice is persisted in the schema and checked on every database operation;
changing it requires a separately rebuilt database, not an implicit conversion.

`query.ext_info['fts5']` accepts `match_mode` (`any`, `all`, `phrase`) and
`metadata_equals`. All search input is quoted as FTS literal strings: raw FTS
operators, column selection and prefixes are not executed as query programs.
`any`/`all` split on whitespace, treating each resulting string as an FTS phrase;
`phrase` uses the entire query. Punctuation is still interpreted by the chosen
tokenizer. Query.keywords is not an alternate text source; query_str is authoritative.
Vector/image/text-bundle queries are explicitly unsupported. Blank text yields [].

Metadata equality supports at most 16 simple top-level keys (ASCII letters,
digits and underscores, starting with a letter/underscore) and JSON scalars. Types
are distinguished: true, integer 1, real 1.0 and text "1" differ. Null means an
existing JSON-null property, not a missing property. Integer filters are signed
64-bit SQLite values. This is not an arbitrary filter language or authorization
mechanism. Other namespaces in Query.ext_info remain available to the caller.

Results use SQLite's BM25 ordering (lower is better), with ID as deterministic tie
break. Raw score and mode are stamped under reserved `metadata['__fts5']`; ingestion
rejects that reserved key. Remove it before reinserting a retrieved result. Original
text, ID, JSON metadata, embeddings and keywords are persisted; embeddings and
keywords are payload, not indexed fields. Query metadata is always an object to
hold the score. No generalized relevance/latency improvement is claimed.

## Transactions and lifecycle

- Schema v1 uses a content table, FTS5 external-content table and insert/delete/
  update triggers. Initialization is transactional and rejects incompatible marker
  versions/tokenizers or missing triggers. Existing SQLiteStore tables are untouched.
- `insert_document` rejects existing IDs; `upsert_document` inserts or replaces
  field values; `update_document` requires every ID to exist. Duplicate IDs within
  a batch are rejected. All batch validation happens before any write; a SQL/trigger
  failure rolls back rows and index changes together. Deleting an absent ID is a no-op.
- Connections are private per operation, closed on success/error and safe to use
  from different caller threads without sharing a connection. SQLite serializes
  writers; there is no connection pool or automatic journal-mode change.
- Normal framework initialization runs schema creation/checking. Queries do not
  create missing databases; nonempty operations use `mode=rw`. An empty query can
  return without touching storage. No shared client needs explicit shutdown.
- Do not mutate component configuration while requests are running, edit these
  internal tables/triggers by hand, or reuse their reserved namespace for unrelated
  tables. There is no automatic repair/rebuild of corrupted/external modifications.

Async methods run the same real SQLite operations in worker threads. They snapshot
validated inputs before dispatch. On cancellation, a cooperative event interrupts
row loops/SQLite VM checks and the coroutine waits for its worker to close the
connection, including repeated cancellation requests. If cancellation arrives after
commit, the write may already have succeeded; cancellation is not proof of rollback.
Tests exercise cancellation *before* commit and verify actual rollback. Repeated
cancellation during deletion also verifies that searchable data survives and the
worker releases its write lock before the cancelled coroutine returns.

## Bounds

Defaults: 1,000 documents per write, 1 million serialized characters per document,
10 million per batch, 4,096 query+filter characters, 64 literal terms, at most 1,000
results and 4 million result characters. Oversized results fail rather than silently
truncate. The requested top_k is separately validated, including rejecting zero.

SQL has a 5-second busy timeout and a progress handler checking elapsed execution
and a 5-million-VM-step budget every 1,000 steps. These checks are cooperative, not
a strict total deadline: lock waits, filesystem calls, callbacks, Python validation
and allocations may occur between/outside VM callbacks. Cancellation can wait for
such work. Bounds do not cap total on-disk database size or SQLite heap usage; use
process/filesystem controls for those. JSON serialization follows JSON value rules,
not arbitrary Python-object roundtrips. Non-finite JSON values are rejected.

## Verification

Tests use actual on-disk SQLite FTS5, not a fake database client: word/phrase/trigram
search, type-sensitive filtering, ranking ties, reopening, trigger rollback,
all sync/async CRUD methods, simultaneous writers, VM-budget interruption and an
event-controlled real trigger during async cancellation. The configuration test
copies the shipped template to YAML, uses real component managers/router/readers,
inserts a file through Knowledge, registers a fresh store against the persisted
database and retrieves a late document word without a keyword extractor. Only
tracing side effects are patched in that pipeline. Existing SQLiteStore and RRF
regressions are included to guard adjacent behavior, not prove corpus-wide quality.

SQLite semantics reference: https://www.sqlite.org/fts5.html (FTS5, tokenizers,
external-content triggers and BM25). This feature has no hosted-CI/score claim.
