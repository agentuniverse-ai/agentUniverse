# As-of version selection for recalled documents

Add `effective_version_selector` to Knowledge.post_processors before final
budget truncation. This optional processor does not change the default pipeline.

Each chunk must have a distinct stored Document.id and carry:
```json
{"logical_document_id": "policy-A", "document_version": "v2",
 "valid_from": "2026-02-01T00:00:00Z", "valid_to": null}
```
Invoke `knowledge.query_knowledge(query_str="policy", ext_info={"as_of":
"2026-02-15T00:00:00Z"})`. Do not use today's wall clock implicitly: the caller
supplies an explicit timezone-qualified timestamp for reproducible history queries.

Intervals include the start and exclude the end. Missing/null end means open-ended.
The latest active start wins per logical document; all recalled chunks of that
version retain incoming order and object identity. Version labels are opaque strings,
not lexicographically sorted semvers. Distinct versions with equal active starts
raise rather than silently choosing. Chunks of one version must agree on intervals.
Any malformed timestamp/interval raises; missing required identity/version/start
is excluded by default, or raises with `missing: error`.

This differs from temporal-decay reranking (#3333): it enforces explicit validity,
not preference for newer documents. General metadata filtering (#3910) does not
resolve competing versions while keeping their chunk sets.

## Limits
Selection only knows **recalled candidates**, not all stored versions. Broad enough
recall and distinct chunk IDs are prerequisites. It cannot recover versions/chunks
discarded by a store or earlier processor, and cannot guarantee the authoritative
version if it was not recalled. Store-level date prefiltering may be appropriate
for large histories. Never use this as an authorization boundary.
Timestamps use ISO `YYYY-MM-DDTHH:MM:SS[.ffffff](Z|±HH:MM)`; no inferred date-only
timezone, leap seconds or natural-language dates. It preserves data, not legal truth.
Numeric offsets require hours 00–23 and minutes 00–59; malformed offsets are
rejected rather than normalized into a different effective time.

## 中文
用明确的查询时间选择同一逻辑文档当时生效的最新版本，保留该版本的全部已召回分片。
不按版本字符串大小排序，不自动使用当前时间，不改写原文。结束时间为开区间。
若底层检索未召回正确版本，本组件不能凭空补回，因此不宣称全库历史查询保证。
测试包含 SQLite 持久化后重新打开、Knowledge 查询启用/关闭对照和时区边界。
