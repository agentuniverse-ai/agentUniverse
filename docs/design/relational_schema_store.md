# Relational schema context / 关系 Schema 上下文

`RelationalSchemaStore` selects catalog context for NL2SQL without reading business
rows or executing generated SQL. It reflects an explicit allowlist of qualified
tables through SQLAlchemy, ranks exact identifier-token matches in the question,
and adds shortest foreign-key bridges between selected seed tables. A customer
and product question can therefore include orders and items even when those bridge
table names are absent from the question. This is a deterministic lexical baseline,
not a learned semantic retriever or a retrieval-quality improvement claim.

```python
from sqlalchemy import create_engine
from agentuniverse.agent.action.knowledge.store.relational_schema_store import RelationalSchemaStore
from agentuniverse.agent.action.knowledge.store.query import Query
engine = create_engine('sqlite:///catalog.db')
store = RelationalSchemaStore(
    name='schema_context', client=engine,
    tables=[('main','customers'),('main','orders'),('main','items'),('main','products')],
    seed_limit=2, max_hops=3, max_context_tables=8)
docs, report = store.query_with_report(Query(query_str='customers products'))
# Register this initialized Store with StoreManager using store.get_instance_code().
# A Knowledge(stores=['schema_context']) can then query it normally.
engine.dispose()  # caller owns the engine and its credentials/pool
```

Initialization is programmatic: supplying a caller-owned Engine avoids introducing
another credential/configuration or connection lifecycle. Do not call the generic
YAML constructor without supplying the required allowlist and client. Async query
uses a worker thread; cancelling the await does not terminate database work. Set
backend statement/connect timeouts and use a thread-safe engine pool (an ordinary
in-memory SQLite connection is not portable across worker threads).

The result is one self-contained JSON Document with columns/types/nullability,
primary/unique constraints, ordered composite FK columns, actual direction of each
FK, selection scores/matched terms and admitted paths. `similarity_top_k` may be
omitted or 1. Foreign-key traversal is undirected for join discovery; output retains
the declared source/target, and does not assert cardinality, valid row references,
causality, or correctness of a generated join. Multiple parallel FKs remain distinct.
Only one lexicographically deterministic shortest bridge per seed pair is chosen;
this does not enumerate every possible join plan. Self/cyclic FKs cannot loop BFS.

Use explicit schema names (`main` for SQLite, e.g. `public` for PostgreSQL). For
PostgreSQL, target namespaces are resolved through pg_catalog object IDs, so
search_path visibility does not merge same-named tables from different schemas.
Tables outside the allowlist are never reflected or used as bridges; declarations
pointing outside are reported. Empty/unmatched questions return no documents.
Missing tables and reflection errors propagate; no stale fallback is used.

Table/hop budgets report omitted bridges. Catalog column/FK and final JSON character
budgets fail explicitly instead of publishing truncated constraints. Reflection can
materialize a catalog response before checking its budget; these are not hard server
CPU/memory/IO limits. Concurrent DDL may cause errors or a changing view; the caller
must coordinate DDL or use appropriate transaction isolation when a stable snapshot
is required. Restrict database permissions to the metadata needed by the application.
The output exposes table/column names, not row data; manage schema disclosure too.

中文：显式表白名单内按问题标识词选表，再补齐受限最短外键路径，保留复合外键
列顺序和真实方向。不同 schema 的同名表不会合并。路径/表预算会报告遗漏，
字段/外键/文本预算超出会失败，不悄悄截断约束。只反射目录，不读业务行、不生成
或执行 SQL；不保证检索提升、连接结果正确或外键数据实际有效。当前验证后端仅
SQLite/PostgreSQL，Engine 由调用方管理，通过程序注册接入 Knowledge。

Tests: set AU_SCHEMA_POSTGRES_URL to an expendable local PostgreSQL database, then
run `python -m pytest -q --import-mode=importlib tests/test_agentuniverse/integration/test_relational_schema_live.py`.
Tests require SQLAlchemy 2.x, psycopg2-binary 2.9.10 and framework runtime dependencies;
PostgreSQL fixture schemas have unique names and are cleaned in finally blocks.
Real SQLite/PostgreSQL catalogs, composite/cyclic/external FKs, cross-schema
search_path, all budgets and Knowledge query are covered. Compare this with #4129:
that contribution audits an SQLite file; it does not select relational context for
a question or complete missing bridge tables.

Reference: [SQLAlchemy reflection](https://docs.sqlalchemy.org/en/20/core/reflection.html).

Validation record: Windows Python 3.10/3.12, PostgreSQL 17 and real SQLite, each
31 passed with no skips (19 integration cases plus 12 existing Knowledge cases).
Ruff E4/E7/E9/F/I, formatting and git diff checks pass. These are local results,
not hosted CI or a language-to-SQL accuracy benchmark.
