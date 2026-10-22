# Source-balanced evidence selection / 来源均衡证据选择

`SourceBalancedSelector` implements a per-source cap on an already-ranked
retrieval list. It addresses the filtering direction of #248. Unlike MMR,
it does not require embeddings or compute semantic diversity. Unlike RRF,
it does not combine retrieval-channel scores. A source is an explicitly
configured publisher/document identity, **not** automatically a store name.

## Configuration and pipeline

Load the shipped `source_balanced_selector.yaml` through the normal component
configuration mechanism. Set `source_key` to an existing **top-level** metadata
field populated by your reader/ingestion pipeline, such as `publisher_id` or
`source_document_id`. Source values must be strings or None. Prefer a canonical
source identity over a basename that can collide between directories.

```yaml
# SourceBalancedSelector component fields
source_key: publisher_id
max_per_source: 1
top_n: 5
refill: false
```

```yaml
# In an existing Knowledge configuration whose components are registered:
post_processors:
  - reciprocal_rank_fusion_processor
  - source_balanced_selector
  - context_budget_compressor
```

RRF is optional; another reranker can precede the selector. The selector declares
no `channel_key`, so selecting it alone does not activate per-store copies or
change Knowledge's normal cross-store deduplication. If the source key itself
is `recall_channel`, RRF/channel-aware recall must already provide it. A final
budget compressor can further reduce the number of represented sources; this
selector does not guarantee diversity after arbitrary downstream filtering.

## Exact selection contract

- Scan in input rank order and select up to `max_per_source` occurrences of each
  source, until `top_n` is reached. No score is recomputed or modified.
- `top_n: null` keeps all quota-eligible items; zero returns an empty list.
- `refill: false` is a strict cap and can return fewer than `top_n` results.
- With `refill: true` and finite `top_n`, fill remaining slots using the earliest
  rejected occurrences, then restore original rank order. This explicitly
  relaxes the cap. With `top_n: null`, refill has no effect.
- Source strings are exact and case-sensitive; nonblank strings are not trimmed
  or normalized. Missing, None and whitespace-only values fall back to document
  ID in a separate namespace. Repeated unknown documents with the same ID share
  a cap; unrelated unknown documents do not share a fictitious source.
- Non-string, non-None source values raise ValueError rather than silently
  changing grouping. Apart from empty input/top_n=0 no-op cases, the whole batch
  is validated even if an early prefix could fill the limit.
- This is selection, not deduplication: repeated references consume quota.
  Output is a new list containing original Document objects; the component does
  not mutate them or promise that later consumers cannot mutate them.
- Time and auxiliary memory are O(N), except refill restores selected index
  order with an O(K log K) sort. Inputs must already fit in memory.

## Reproducible example

```python
from agentuniverse.agent.action.knowledge.doc_processor.source_balanced_selector import SourceBalancedSelector
from agentuniverse.agent.action.knowledge.store.document import Document

ranked = [Document(id=str(i), text=f"Evidence {i}", metadata={"source": source})
          for i, source in enumerate(["A", "A", "A", "B", "C"])]
selected = SourceBalancedSelector(top_n=3).process_docs(ranked)
assert [doc.id for doc in selected] == ["0", "3", "4"]
# Ordinary top-3 covers one source; this selection covers three.
```

This controlled example proves source coverage, **not** better answer quality.
If the first three A documents are the only relevant evidence, selecting B/C
can reduce relevance. Source labels do not establish trustworthiness or
independence, and missing labels limit what the cap can achieve. Tune the cap
against your own labeled queries; do not automatically replace global top-k.

## Validation scope

The integration test uses two real file-backed SQLiteStore instances with
JiebaKeywordExtractor, closes/reopens the databases, then invokes public
Knowledge.query_knowledge with actual worker futures, merge/dedup, RRF or
ThresholdFilter, selector and ContextBudgetCompressor. Only manager lookups,
router selection and unrelated tracing services are patched. This is not a
full application bootstrap, live vector service, or real-world relevance study.

Tests cover disabled behavior, strict/refill selection, cross-store duplicates,
persisted source metadata, RRF composition, budget truncation, YAML module/class
resolution, rejected configuration, source identity semantics, nonmutation,
repeated calls and an exhaustive small-sequence reference check.

## 中文说明

本组件用于限制同一来源占据过多召回位置。先重排或融合，再进行来源选择，
最后应用上下文预算。默认严格限额；开启 refill 才会在结果不足时放宽限额。
来源字段需要由用户的读取/入库流程提供，不能把未知来源都当作同一个出版方。
保持输入排序、原始分数和文档字段，不改动未配置本组件的检索流程。

来源覆盖增加不代表准确率一定提高；单一来源可能包含全部相关证据。因此需要
根据实际数据选择限额，不能把演示中的三来源结果当作普遍效果或比赛得分保证。
