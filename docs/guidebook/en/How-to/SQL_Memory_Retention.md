# SQL memory retention / SQL会话记忆保留策略

`SQLMemoryRetention(storage)` supports the existing `SqlAlchemyMemoryStorage`
and **default converter** without changing ordinary `add/get/delete` behavior.
Initialize the storage normally, then explicitly preview one session AND agent:

```python
from datetime import datetime, timezone
from agentuniverse.agent.memory.memory_storage.sql_memory_retention import SQLMemoryRetention

retention = SQLMemoryRetention(storage)
plan = retention.preview(session_id="session-42", agent_id="assistant",
    before=datetime(2026, 1, 1, tzinfo=timezone.utc), keep_last=100)
print(plan.candidate_ids)  # dry run; no deletion
# After reviewing the scope and IDs, explicitly execute:
receipt = retention.execute(plan)
print(receipt.deleted_ids)
```

Rows qualify only if older than the exclusive UTC cutoff AND outside the newest
`keep_last` rows. Either condition may be used alone; no policy is rejected.
Ordering is by timestamp then integer primary key. Empty/missing scopes,
negative limits, booleans-as-counts and naive cutoffs are rejected. The default
schema has naive timestamps: this API interprets them as UTC. Configure database
session time zones to UTC; it cannot infer the time zone of historical rows.
Unknown stored timestamps reject the preview. Custom converters are unsupported.

The preview loads at most `max_rows + 1` rows (default budget 10000), rejects an
oversized scope, and rejects more than `max_candidates` deletions (default 1000).
It is intentionally for bounded session maintenance, not an unbounded table
sweeper. The plan contains IDs and hashes, not message bodies. Keep it in memory
on the same service instance; `discard(plan)` releases an unused plan.

Execution only touches unchanged previewed IDs in the exact session/agent.
New/backdated inserts are not added to the candidate set. A changed, moved or
missing candidate aborts the whole transaction, including earlier deletes.
Row locks on PostgreSQL and atomic compare-and-delete predicates protect the
write; database/locking failures roll back without automatic retry. A plan is
consumed on every execution attempt; preview again after failure. This does not
prevent another actor deleting protected rows or deliberately recreating an
identical row with the same primary key. Retention is row-based: choose a
conversation boundary yourself if tool-call groups must remain intact.

Only the returned receipt confirms commit. There is no background scheduler,
global prune or deletion during preview. The caller remains responsible for
access authorization. This operates independently of archives and ContextStore
TTL. SQLite and PostgreSQL are tested; no other dialect compatibility is claimed.

## 中文

此接口直接作用于默认 SQL 会话消息表，不改变已有 add/get/delete，也不依赖归档。
必须同时提供非空 session_id 与 agent_id。先预览固定候选 ID，再显式 execute；
时间阈值为开区间，并与保留最新条数同时生效，同时间用主键排序。数据库中的
无时区时间按 UTC 解释，应用必须保证数据库会话与历史数据采用该约定。

预览有扫描和候选数预算，超出直接报错，不给出不完整候选。执行只删除预览的
未变化行，不纳入之后新增的消息；内容变化、迁移、缺失或 SQL 错误使整个事务
回滚。每次执行均消耗计划，失败后重新预览。不支持自定义 converter；没有自动
调度或默认删除。按行保留不会自动识别工具调用组，调用方需选合适会话边界。
计划仅供当前服务实例使用，不应序列化持久化；不用时调用 discard。

## Reproduction

Run `python -m pytest tests/test_agentuniverse/integration/test_sql_memory_retention.py -q`.
By default only temporary SQLite is used. To also run PostgreSQL, set
`AU_RETENTION_TEST_POSTGRES` to a **dedicated disposable database** URL using
psycopg2. Each PostgreSQL case creates and drops its own UUID schema; it never
uses an existing application table. The failure test injects a transport error
on the second DELETE while exercising the real database transaction.
