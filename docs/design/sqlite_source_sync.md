# Atomic source snapshots for SQLiteStore

`SQLiteSourceSynchronizer` is an optional programmatic ingestion helper, not a new
Store or an automatic Knowledge.insert_knowledge behavior. It replaces the complete
desired set of chunks for one explicit source. Unlike ordinary upsert, it removes
the source's obsolete chunks and keyword terms and persists a durable manifest.
Unlike ContextManager knowledge-to-session synchronization, it operates on the
file-backed retrieval index, not RAM context segments. Other backends are unsupported:
there is no generic transaction/deletion contract on Store.

```python
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.store.sqlite_source_sync import SQLiteSourceSynchronizer
from agentuniverse.agent.action.knowledge.store.document import Document

# Application/configuration and the SQLiteStore must already be initialized.
store = StoreManager().get_instance_obj("sqlite_store", strict=True)
synchronizer = SQLiteSourceSynchronizer(store)
state = synchronizer.inspect_source("manual:AX-12")
result = synchronizer.sync(
    "manual:AX-12",
    [Document(id="installation", text="Install upright.", metadata={"edition": 2})],
    expected_revision=state["revision"], pipeline_revision="reader+splitter+keywords-v1",
)
print(result["revision"], result["document_ids"])
```

Read/parse/split the complete source before calling sync. If those steps fail, do
not call sync with a partial list: a list is a complete desired snapshot, not a
batch append. Empty lists are rejected unless `allow_empty=True`, explicitly
meaning remove all managed chunks for that source. No files are deleted.
All database work is confined to the existing SQLiteStore database. In-memory
databases and SQLite URI paths are rejected. No new database is created.

## Ownership and version checks

Caller-provided document IDs identify chunks within the source. Physical IDs are
`au-sync-` plus SHA-256 of the source/logical-ID pair; the returned mapping is the
authoritative stored ID mapping. Stable chunk IDs avoid needless remove/add work.
The same logical ID in two sources does not share rows. Unmanaged legacy rows are
not adopted; even a colliding physical ID raises without overwriting it. Migrating
legacy data is an explicit separate operation, not an implicit side effect.

`expected_revision` is mandatory. Zero means no prior committed snapshot. Read the
revision before preparing a new snapshot and retain it through the operation; do
not blindly re-read/retry an old snapshot after a conflict. The second of two writers
with the same expected revision fails with SourceRevisionConflict. To retry, inspect
current state and recompute which snapshot is actually current in the source system.
This check orders sync commits, not the external source's own version semantics.

Unchanged text, metadata, extracted terms and pipeline revision cause no document
or manifest writes. Pipeline revision changes increment the source revision even
when row content is identical. Keywords are still computed on each sync; this is
incremental storage, not a cache that skips parsing/embedding/provider calls.
Metadata is canonical JSON (non-finite floats rejected). Embeddings are not stored
because SQLiteStore is a keyword backend. Returned counters distinguish inserts,
updates, deletions and unchanged desired chunks.

## Transaction, consistency and failure behavior

Keyword extraction runs first on deep copies; returned terms are used even if the
processor returns new documents. A dedicated short-lived SQLite connection then
runs BEGIN IMMEDIATE. Document rows, all keyword terms, membership digests and
source revision are committed together. Python exceptions (including interrupts)
roll back; each connection is closed. SQLite's configured journaling/durability
semantics apply. Provider side effects during preprocessing are not rolled back.

The two versioned manifest tables are `au_source_state_v1` and
`au_source_members_v1`. `inspect_source` opens a read transaction and compares managed
row/index digests; it never creates these tables. Missing/changed rows, missing
keywords and extra/duplicate keyword entries are reported as drift. Sync refuses
to overwrite or delete a source with drift. Inspect and explicitly resolve the
out-of-band write before retrying; there is no automatic destructive repair.
This is a source-local consistency check, not a whole-database integrity audit.

Competing synchronizer writers use independent connections and SQLite locking.
The caller's Store connection is never committed/rolled back by this helper. Busy
databases raise after the configured 0–60-second timeout (default 5); no hidden retry
or background task continues. If a return is lost after commit, inspect current
revision/content before retrying. SQLiteStore's existing query implementation uses
multiple separate SELECTs: this helper does **not** make concurrent public queries
snapshot-consistent. Serialize ordinary Store queries/writes with synchronization
when that consistency is required. Do not modify managed rows through legacy APIs.

No async API or distributed multi-store atomicity is claimed. The caller owns Store
connection/executor lifecycle and provider timeouts. Default limits bound desired
documents to 10,000 and combined text/serialized metadata/keyword characters to
10,000,000; provider allocations and previously managed database size are not bounded
by these input limits. Ordinary SQLiteStore behavior/configuration is unchanged.

## 中文

本工具以完整来源快照为单位，将新增、更新、过期片段删除、关键词索引与版本清单
放在同一 SQLite 事务内。必须明确来源、预期版本与处理管线版本；空快照需显式允许。
重复调用不会重复写入，同一预期版本的并发写入只允许一个成功。它不接管旧数据，
不清理其他来源；发现托管记录或索引被外部修改时先报告并拒绝覆盖。

这是 SQLite 关键词存储的增量同步，不是跨数据库分布式事务，不会节省读取和分词
本身的调用。调用者需确保提交的是完整、最新的来源快照。普通 Store 查询不是多语句
快照读，需要一致性时应由应用协调同步与查询。测试使用真实临时数据库、失败触发器、
并发写入、重开数据库及实际组件管理器/Knowledge 查询，不代表托管 CI 或线上吞吐表现。
