# Projected Parquet knowledge ingestion

ParquetReader converts each row of a local Parquet file to a Document, keeping field
names in JSON text and typed source metadata. It is an opt-in registered Reader,
not a pandas import, SQL engine or partitioned-dataset scanner. It uses the existing
`pyarrow` project dependency (declared ^16.1.0), without adding a runtime dependency.
The component imports it lazily and gives an actionable ImportError in minimal
environments without it. Compatibility tests target the declared 16.1.0 baseline.
Minimal Windows environments also need `tzdata` to decode timezone-aware timestamps
if no system timezone database is available; the project's pandas installation
normally supplies it there. Missing timezone data raises an actionable error,
never strips the timezone or converts the value to naive time.

```python
from agentuniverse.agent.action.knowledge.reader.file.parquet_reader import ParquetReader

reader = ParquetReader(text_columns=["description"], metadata_columns=["category"],
                       id_column="product_id", batch_size=256)
documents = reader.load_data("catalog.parquet")
```

For Knowledge, register the supplied `parquet_reader.yaml`, configure its columns,
and set `readers: {parquet: parquet_reader}`. Then normal
`insert_knowledge(source_path="catalog.parquet")` uses the reader. Existing format
defaults are unchanged. Set the registered Store and normal processors as usual;
this reader performs no embedding, keyword extraction or database operations.

## Projection and values

`text_columns: []` selects all top-level fields. Nonempty selections require exact
existing top-level names; unknown/duplicate names and duplicate schema fields fail.
Nested structs can be selected as complete top-level columns; dotted nested-field
projection is not supplied. `metadata_columns` selects extra fields under
`parquet_values`; `id_column` is also decoded when configured. Unselected data
columns are not included in output. Field types for selected columns are recorded
in `parquet_column_types`, not the whole file schema.

Null/bool/int/string and finite float values stay JSON values. Decimal becomes an
exact decimal string; date/time/timestamp becomes ISO text. Binary becomes
`{"base64": "..."}`; durations retain days/seconds/microseconds. Lists, structs and
map pair lists are recursively represented. Arrow type metadata disambiguates
these encodings. Nanosecond timestamp/time/duration values are encoded as exact
integer tags (`epoch_nanoseconds` plus timezone, `nanoseconds_since_midnight`,
or `nanoseconds`), including inside nested fields; they are never rounded to Python
microsecond precision. Map pair order and duplicate keys are preserved. Metadata distinguishes
these encodings from ordinary string/struct values. Non-finite floats and unknown
Python/Arrow-extension value types raise rather than silently losing information.
This is not a general Arrow round-trip serializer. No row is silently skipped.

## Source identity and limits

Metadata records resolved local file URI, basename, SHA-256, zero-based global row
index and zero-based row group. Reader output is ordered by physical file row order.
The default ID hashes file URI, snapshot digest and row index: rewriting or moving
the file changes IDs. With `id_column`, nonempty string/integer values (not bool or
null) must be unique in the file. IDs then hash file URI, column name and value,
remaining stable across row reordering/data updates at the same path. Output includes
the original ID and the current snapshot digest. ID stability is not automatic
deletion of old database rows; ordinary Knowledge insertion retains its semantics.

The reader takes one immutable in-memory file snapshot capped by `max_file_bytes`
(default 32 MiB), so the digest and decoded bytes agree. PyArrow then decodes only
selected columns in `batch_size` (256) batches, not a full pandas table. Declared
rows exceeding `max_rows` (10,000) fail before row decoding; actual count is checked
too. Row text plus metadata must fit `max_row_chars` (100,000); combined output must
fit `max_output_chars` (10,000,000). Limits reject the whole call, not return an
apparently complete truncated list. The Reader API still returns a list of all
accepted Documents, so output memory is not streaming/unbounded-file support.

Compressed-file and post-decoding character limits are **not** a parser sandbox
or a strict peak-memory bound: an individual encoded page/value can allocate before
its decoded size is checked. Only process trusted files within application resource
controls. Readers close owned Python and Arrow handles on success/failure. No file
is modified. `ext_info` is deep-copied and cannot replace reserved provenance keys;
normal Knowledge loading currently does not forward call-time ext_info to readers.

## Verification

Tests write/read real multi-row-group Parquet files, including typed/nested values,
projection, nulls, ID/reordering semantics, invalid IDs, size limits, corruption,
empty files and optional-dependency behavior. Full registered YAML/manager integration
passes a real file through public Knowledge insertion into SQLite, closes/reopens the
store, and retrieves one row with preserved metadata. Only tracing is mocked there.
These are functional tests, not production throughput or retrieval-quality claims.

## 中文

本 Reader 将 Parquet 行转成带列名的知识文档，支持选择正文列、元数据列及稳定主键列，
同时记录文件哈希、全局行号和行组位置。它按批解码选中的列，不依赖 pandas；但仍遵循
Reader 返回完整列表的接口，不宣称可以无限流式读取大文件。默认无主键时文件改写会
改变 ID；指定唯一主键列后，同一路径的行重排或内容更新保留 ID。

重复主键、未知列、超限、非有限数字均明确失败，不静默跳行。压缩文件限额与解码后
字符限额不能替代进程内存隔离。仅添加显式配置的 Parquet 能力，不改动其他文件类型
默认行为，也不自动删除数据库旧行。

API reference: [Apache Arrow ParquetFile](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html).
