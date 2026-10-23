# Offline BM25 reranking / 离线 BM25 重排

## Purpose

`BM25Reranker` is an optional recall post-processor for candidates from any
store. It uses local lexical matching, with no API key, model download or new
runtime dependency. SQLiteStore's internal BM25 ranks that store's own matches;
this component instead ranks an already recalled list, including multi-store
or vector-store results. It cannot recover relevant documents absent from recall.

Configure the supplied `bm25_reranker.yaml` through the usual component scan and
add its name to a Knowledge configuration:

```yaml
post_processors:
  - bm25_reranker
```

The shipped component returns at most five documents. The Python default is
`top_n=None` (no truncation). No existing Knowledge or store default is changed.
Example direct use:

```python
from agentuniverse.agent.action.knowledge.doc_processor.bm25_reranker import BM25Reranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query

docs = [Document(text="AX-120 manual"), Document(text="AX-12 manual")]
result = BM25Reranker(top_n=1).process_docs(docs, Query(query_str="AX-12"))
assert result[0].text == "AX-12 manual"
```

## Runnable offline comparison

With the project's Python dependencies installed, run from the repository root:

```shell
python -m examples.bm25_reranking_demo
```

The command reads the shipped BM25 YAML and prints JSON containing candidates,
original/RRF/BM25 rankings and Recall@1 for the two explicit examples below.
It requires no API key, server or model download and creates no output files.
The identifier example improves from 0 to 1; the semantic counterexample drops
from 1 to 0. These hand-authored inputs are not independent evaluation data.
This example demonstrates post-processing of fixed recalled candidates, not a
complete retrieval application. A subprocess test runs this exact module command.

## Persisted retrieval example

```shell
python -m examples.bm25_sqlite_demo
```

Run this standalone command in a fresh process. It registers real component
instances, loads the shipped BM25 YAML, inserts three manuals into temporary
SQLite storage, closes/reopens the database, and calls the public
`Knowledge.query_knowledge` with and without BM25. The standard router, managers,
keyword extraction, trace wrapper and SQL queries are not mocked. JSON reports
the original IDs, reranked IDs/text/scores and whether stored metadata stayed
unchanged. Executors and the connection are closed before temporary data is
removed. No existing application or database should be supplied to this demo.
This is a runnable single-store retrieval workflow, not a server bootstrap,
multi-store relevance benchmark or evidence that all queries improve.

## Scoring formula

For each distinct query token `t`, sum
`log(1 + (N - df(t) + 0.5)/(df(t) + 0.5)) * tf(t,d)*(k1+1) /
(tf(t,d) + k1*(1-b+b*length(d)/average_length))`.

- `N`, document frequencies and average length come from **this candidate list**.
  Repeated occurrences are not deduplicated and affect statistics. Use RRF or
  another deliberate deduplication stage first where appropriate.
- Each query token contributes once. Document frequency counts a token once
  per candidate, regardless of repetitions inside that candidate.
- Empty/None document text contributes zero length to the average and scores
  zero. An entirely empty-text batch also scores zero without division by zero.
- `k1` is finite and positive (default 1.2); `b` is finite in [0,1] (default
  0.75); `top_n` is a nonnegative integer or null. Strings and booleans are not
  accepted as numeric configuration. Construction, YAML loading and processing
  after direct field assignment validate these settings.
- Empty input or `top_n=0` returns `[]`. Otherwise missing/blank/punctuation-only
  queries raise `ValueError`. There is no implicit fallback to a different query.
- Scores are descending; ties retain original occurrence order. All-zero
  batches retain their input order. Zero-scored documents remain unless limited
  or explicitly filtered by a following component.

Scores are not probabilities, corpus-calibrated scores or comparable across
different candidate sets. Adding candidates can change both scores and ranks.
Tokenization and ranking cost scale with input tokens plus the product of
candidate count and distinct query-token count; sorting is O(N log N).
Per-document term counters are retained in memory. `top_n` bounds output only,
not scoring work or memory: bound upstream recall for large corpora.

## Tokenization and copy semantics

Text is NFC-normalized, case-folded, and matched with `\w+(?:[-.]\w+)*`.
Internal ASCII hyphens/dots are retained, so AX-12 differs from AX-120 and v1.2
differs from v1.20. Underscores remain part of words. Other punctuation separates
tokens. There is no stemming, stop-word removal, synonym expansion, transliteration
or CJK word segmentation; a continuous Chinese phrase remains a single token.
This is **not** full Chinese retrieval or a general code/symbol tokenizer.

Each result is a shallow Document copy with a new top-level metadata dictionary.
Text, identity, keywords and embeddings are preserved; nested metadata and other
mutable values are shared. The processor never mutates them. Default output key
`bm25_score` preserves `relevance_score`; a configured key collision intentionally
replaces that key in the result only. An existing `bm25_score` is recomputed.

## Composition and evidence

For multi-store fusion, configure RRF with `channel_key: recall_channel` and put
it before BM25. BM25 itself has no channel key and does not enable channel-aware
recall. Keep both scores by leaving distinct score fields. A following
`ThresholdFilter` must specify `score_field: bm25_score` to filter BM25 scores.
Place `ContextBudgetCompressor` after reranking; truncation means the preserved
BM25 score describes the original candidate, not the shortened text.

The integration tests insert documents into two actual SQLite databases, close
and reopen them, and invoke public `Knowledge.query_knowledge`. They exercise
worker futures, persistence, deduplication, RRF composition, score filtering,
context budgeting and the disabled path. Manager lookups, a controlled broad
recall router and tracing are mocked; database operations and processors are not.
The broad router supplies candidates using a shared keyword while the original
query is used for reranking. This is not a live vector-store or full app bootstrap
test.

A separate integration test scans the actual processor package and registers
the discovered BM25 YAML through the framework bootstrap registration method.
It checks real manager lookup, configured output limits, ranking and isolation
of fetched copies. Singleton state is isolated for the test; discovery,
registration and lookup are not mocked. It does not start application servers
or by itself prove platform compatibility. The complete suite was also run on
Linux Bookworm x86_64/Python 3.12.12 and Windows/Python 3.10 and 3.12.

Two deliberately small, explicitly labeled examples compare original ordering,
RRF and BM25 using Recall@1:

| Query / intended evidence | Original | RRF | BM25 |
| --- | ---: | ---: | ---: |
| AX-12 / exact model manual | 0 | 0 | 1 |
| car repair / automobile servicing (not invoice) | 1 | 1 | 0 |

These are controlled examples, not aggregate relevance claims. The counterexample
is intentional: lexical ranking can hurt semantic intent. Choose it for exact-term
use cases and validate on your own relevance labels, not merely passing unit tests.

A separate local evaluation used all 300 externally labeled BEIR SciFact test
queries and 5,183 documents, with fixed body/title TF-IDF top100 channel union.
BM25 default reranking gave mean nDCG@10 0.6362 versus 0.6346 for body-first
ordering, but Recall@10 fell from 0.7652 to 0.7537; 51 queries worsened on nDCG.
This is not a significant-improvement claim or a standard BEIR leaderboard run.
It supports keeping this component optional, with task-specific evaluation.
Data attribution: [SciFact](https://github.com/allenai/scifact), distributed by
[BEIR](https://github.com/beir-cellar/beir). Dataset files are not bundled here.

Reproduce using `python -m examples.bm25_scifact_evaluation /path/to/scifact.zip`.
Download the archive separately from the BEIR dataset link and review its
license; the script verifies its SHA256 and emits full per-query IDs/metrics as
JSON. It uses body/title TF-IDF cosine recall (top100 per channel), a body-first
union baseline, RRF k=60 and BM25 k1=1.2/b=.75 over the same candidate union.
All 300 test queries are used without tuning. Positive labels are binary and
unjudged results count as zero. Scores on this setup are not comparable to
published leaderboard runs with different retrieval/candidate generation.

## 中文说明

本组件对已召回的候选文档做离线词项重排，不替代召回，不调用外部 API。
默认写入 `bm25_score`，保留原有 `relevance_score`；只有显式加入
`post_processors` 才启用。YAML 默认最多返回 5 条，Python 默认不截断。

统计范围是当前候选列表，而非完整语料；增加候选可能改变分数与排序。
重复查询词只计一次，候选重复项不会自动去重。空文档得零分，同分保持原顺序。
非空处理遇到空查询或无词项的查询会报错，避免静默使用错误查询。
参数会在构造、配置加载及处理入口校验。`top_n` 仅限制输出，不限制计算输入。

英文大小写、规范等价的 Unicode 文本、带连字符的型号及带点的版本号有明确规则；
不支持中文分词、同义词推断或词干还原，因此不能声称所有检索任务都变好。
返回浅拷贝文档和独立的顶层元数据字典，不修改输入；内部嵌套对象仍共享。
可按 RRF → BM25 → 指定 `bm25_score` 的阈值过滤 → 上下文预算顺序组合。
测试含真实 SQLite 写入/关闭/重新打开及公开 Knowledge 查询链路，
也保留了词面匹配不如语义排序的反例，不把这些小样本包装为生产效果评测。
