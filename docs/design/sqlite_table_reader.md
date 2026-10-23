# Read-only SQLite table ingestion

SQLiteTableReader maps rows of an existing local ordinary table to Documents.
It is a Reader for business records, not a schema-inspection Tool, SQL agent or
SQLiteStore writer. No extra Python dependency is required. SQLite **3.37+** is
required for authoritative ordinary/virtual/shadow table classification; older
runtime libraries fail explicitly. Existing readers and SQLiteStore are unchanged.

```python
from agentuniverse.agent.action.knowledge.reader.file.sqlite_reader import SQLiteTableReader

reader = SQLiteTableReader(table_name="products", text_columns=["description"],
                           metadata_columns=["category"], batch_size=256)
documents = reader.load_data("catalog.db")
```

For public Knowledge insertion, register the supplied `sqlite_reader.yaml`, set
`table_name` and desired columns, then configure `readers: {db: sqlite_table_reader}`
(or your actual filename extension). Use a **different target index/database** and
normal `insert_knowledge(source_path=...)`. Table name is explicit; there is no
automatic catalog-wide ingestion. The shipped table name is an example to replace.

## Snapshot and read-only boundary

The existing file is opened with a URI `mode=ro`, then `PRAGMA query_only=ON`.
A read transaction covers table classification, stored-column schema and all row
batches, including when another WAL connection commits changes during iteration.
The transaction is rolled back and the owned connection closed on every exit.
No source tables, indexes or rows are written, and a missing path is not created.
SQLite itself can use WAL/SHM sidecar files according to its normal read-only WAL
rules; this is not a promise that no filesystem metadata/sidecars are ever touched.

Only ordinary main-schema user tables are supported. Views, virtual/shadow tables,
internal sqlite_* tables, generated/hidden columns and arbitrary SQL are excluded.
Table/column names are exact schema identifiers quoted as identifiers, never caller
SQL expressions. There are no joins, predicates, extensions or attached databases.
Use a trusted export table when you need complex selection or derived data.

## Rows, IDs and provenance

Empty `text_columns` selects all stored fields; nonempty selections project exact
field names into JSON text. `metadata_columns` selects fields under sqlite_values.
Null, integer, finite real and text values retain their SQLite storage values;
BLOBs use a base64-tagged object. Declared SQLite types are recorded separately,
not treated as reliable runtime type conversion instructions. No inferred date,
decimal or boolean conversion is performed. Non-finite reals fail explicitly.

Default identity uses the declared primary-key columns in key order, including
composite WITHOUT ROWID keys. Otherwise supply `id_columns`. Null keys and duplicate
encoded key tuples reject the whole call. Rows are ordered by identity columns,
using explicit BINARY text collation and storage-type tie breakers rather than
unspecified scan order when case-insensitive keys or equal integer/real values
would otherwise tie. This may require a sort even when a differently collated
index exists; VM/time budgets still apply. IDs hash the source URI, table and ordered key
mapping, remaining stable across non-key updates at the same path. Moving a file,
renaming a table or changing key configuration changes identity. Key values may be
sensitive and are deliberately exposed in provenance; choose columns accordingly.

Metadata contains source URI, basename, table, key, zero-based sorted row position,
selected declared types and selected metadata values. `sqlite_projection_sha256`
hashes the selected schema/key configuration and ordered projected rows. It is
**not a file/database hash**: changes to unselected fields do not affect it. All
documents from one accepted snapshot share it. `ext_info` is deep-copied and cannot
replace these fields. Public Knowledge currently does not forward call-time ext_info
to readers. Source content and reader configuration are not mutated.

## Resource/error semantics

The main file size is checked against max_file_bytes (128 MiB); this is not a bound
on WAL size or engine allocation. LIMIT max_rows+1 (default max_rows 10,000) detects
overflow rather than silently truncating. Fetch batches default to 256 rows, but
the Reader API returns a complete list; this is not unlimited streaming ingestion.
Text plus metadata must fit max_row_chars (100,000) and max_output_chars (10,000,000).

A progress handler checks every 1,000 SQLite VM instructions against max_vm_steps
(5,000,000) and max_seconds (5). Time is also checked during row conversion; lock
waiting uses at most min(5,max_seconds). The 0–300-second positive time setting is
not a hard real-time guarantee: a single allocation, OS/SQLite operation or Python
serialization can exceed it before the next check. These limits are not a parser
sandbox. Use trusted databases and application-level resource controls. Exhaustion,
schema/key errors and corrupt/locked databases raise; no partial list is returned.

Stable IDs do not remove old target rows. This Reader intentionally does not combine
ingestion with destructive synchronization. Applications explicitly choose their
target-store update/prune policy and preserve the source/target separation.

## Verification / 中文

Tests use real SQLite files: projection, composite keys, literal quoted names,
read-only source preservation, concurrent WAL updates, VM/time/row/output limits,
corruption, key errors and runtime compatibility. A real registered YAML/Reader,
Store, processor and router pass public Knowledge insertion into a separate SQLite
index, close/reopen it, then retrieve a row with intact key/provenance. Only tracing
is mocked in that integration test.

本功能是业务表行数据接入，不是数据库结构审计，也不是写入端增量同步。普通主表在
同一只读事务中完成读取，避免并发更新混成多个版本。要求显式表名和唯一非空身份键，
投影列保留字段名与实际 SQLite 值；稳定 ID 不代表自动删除目标旧行。超限或异常不
返回貌似完整的部分结果。源库与目标索引应分开，格式支持与资源边界如上，不宣称
任意 SQL、安全沙箱、托管 CI 或线上效果提升。
