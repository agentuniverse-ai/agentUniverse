# Sentence-window retrieval / 句子检索与原文上下文扩展

This is one paired feature, not two independent contributions:
`SentenceWindowSplitter` runs before storage; `SentenceWindowExpander` runs
after retrieval and sentence-level ranking. Search the focused sentence, then
return its exact original neighborhood to recover conditions and pronoun context.
It does not infer missing facts, summarize, or fetch an external source at query time.

## Configuration

Register the two supplied YAML components through the usual component scan.
For whole-file text input, an example Knowledge configuration fragment is:

```yaml
readers:
  txt: default_txt_reader
insert_processors:
  - sentence_window_splitter
post_processors:
  - sentence_window_expander
```

Here `default_txt_reader` resolves to the existing **whole-file** `TxtReader`, not
`LineTxtReader`. Other Knowledge/store settings are application-specific.
The splitter defaults to `window_radius: 1` and `max_window_chars: 2000`;
the expander defaults to the same character budget, with score fields
`[relevance_score, bm25_score, rrf_score]`.

The insertion order is reader → sentence splitter → any required keyword/vector
extraction → store. Newly generated sentence chunks clear prior embeddings and
keywords; the configured store must compute whatever its retrieval method needs.
At recall, use RRF/reranking/MMR/score thresholds **before** expansion: their scores
and vectors describe the sentence. Expansion removes vectors/keywords and moves
configured score fields into each original sentence's match record. Run a final
context-budget processor after expansion if needed. If it truncates text, window
offsets continue to describe the pre-truncation expansion, not the shortened text.
Configure any additional custom distance/score keys explicitly in `score_fields`.

Do not apply the splitter to already-split output or the expander twice. Reserved
`sentence_window` metadata collisions and wrong processing stages raise an error.
Documents without window metadata pass through the expander unchanged, so mixed
ordinary/sentence results remain usable. Present but malformed metadata raises;
it is never silently replaced with invented context.

## Exact offsets, segmentation and limits

The splitter preserves zero-based, half-open Python string offsets of each
trimmed sentence and window. Context is an exact source substring, including
inter-sentence whitespace. Leading/trailing whitespace outside the first/last
sentence is not part of a window. Empty/whitespace-only documents pass through.
Reader newline normalization may happen before processing; file-byte offsets
are not promised.

The intentionally conservative segmentation heuristic recognizes `. ! ?` before
whitespace/end (with common closing quotes/brackets), `。！？` without requiring
whitespace, and blank lines. Decimal/internal dots are not boundaries. A small
explicit list (Dr/Mr/Mrs/Ms/Prof/Sr/Jr/e.g/i.e) and initial/acronym forms avoid
several common false boundaries. It is not a multilingual NLP segmenter: ambiguous
abbreviations, poetry, bullet lists, code, unusual quotation marks and domain
notation need application validation. There is no semantic sentence-boundary model.

`window_radius` counts neighboring sentences; context is added nearest-first,
left before right at equal distance, only when the expanded range fits
`max_window_chars`. An individual sentence exceeding the budget is kept alone
and marked `over_budget`. Thus budgets are **soft character limits**, not hard
token caps. The expander's limit controls merging; it never silently truncates a
larger already-stored window. Bound upstream candidate counts and use a final
model-token budget separately.

## Identity, serialization and overlap

Sentence IDs include parent document ID, source identity, source-text SHA-256,
and sentence offsets. `metadata.source` identifies the origin; if absent,
`file_name` is used. Supply unique source IDs or unique parent IDs where filenames
can collide. Identical sentences—even identical full documents—from different
declared sources stay distinct. A source revision produces new IDs; removing old
revisions is the application's ingestion lifecycle responsibility, not performed
by this feature.

The JSON-compatible `metadata.sentence_window` record stores version, stage,
source identity/digest/length, sentence index/offsets, window offsets/text and
overflow status. It survives the actual SQLite metadata round trip tested here.
Stores allowing only scalar metadata may require an adapter and are **not**
claimed compatible without further integration tests.

Expansion validates types, ranges, window lengths and that the retrieved sentence
is still exactly the corresponding substring. Same-source overlapping windows
merge only when overlapping characters agree. Inconsistent overlaps raise before
returning output. Windows from different sources/revisions never merge. A union
over budget stays as separate windows; identical windows deduplicate even when
oversized. Overlap merging repeats to handle bridging hits, and uses the earliest
hit's rank/ordinary metadata for the merged group. All sentence hits, their ranks,
offsets and configured scores remain in `matches`, including repeated hits.
The output window has a new source-addressed ID and `stage: expanded`.

Inputs are never modified; new top-level metadata dictionaries are used. Nested
ordinary metadata is shallow-shared. SHA-256 distinguishes revisions, **not**
source authenticity: this is consistency checking of supplied metadata, not a
signature or a claim that untrusted external metadata is authenticated.

The straightforward merging implementation has quadratic comparisons in recalled
hit count (plus overlap-text work). Do not pass an unbounded corpus as candidates.
Storing overlapping windows also duplicates context in metadata and can dominate
storage for short sentences; measure the tradeoff on the intended workload.

## Evidence and scope

Unit tests cover punctuation/decimals/abbreviations, CJK, CRLF, source-aware IDs,
same-text different-source records, oversized sentences, invalid serialized
metadata, input immutability, consistent overlapping/contained/bridging windows,
score relabeling, and RRF → expansion → context-budget composition.

The integration uses two actual files, whole-file TxtReader, public Knowledge
insertion, an actual SQLite database closed/reopened, and public Knowledge query.
It distinguishes two identical sentence texts whose original voltage conditions
differ, then restores each correct original context. Disabled and sentence-only
pipelines are tested too. Manager lookups, the routing choice and tracing are
mocked; segmentation, extraction, database operations, futures and expansion are
real. The fixture explicitly uses Jieba `top_k=50` for both the baseline and
sentence indexes so its query word is indexed in both paths; the default `top_k=3`
can omit that word from the longer baseline. No default extractor behavior changed.

JUnit properties record original/stored text bytes, stored metadata bytes,
recalled/expanded characters and cl100k_base tokens for the fixture. These are
small-fixture costs, not general compression ratios, latency benchmarks or proof
of improved answer accuracy. Hosted vector services, full app bootstrap and
production-model answer quality are outside this validation.

## 中文摘要

这是入库与召回配套的一项功能：入库按句子建立检索文档，同时保存有限的原文邻域；
召回、融合和重排后扩展回原文。扩展保留条件、指代及来源，不生成或推断缺失内容。
不同来源的相同句子具有不同标识；相同来源的重叠窗口仅在字符一致且预算允许时合并。
发生损坏或内容不一致会明确报错。原句分数移入匹配记录，不再冒充扩展文本的分数；
旧向量和关键词清空。默认查询链路不会改变，必须显式配置才启用。

句子划分是有明确限制的启发式规则，并非完整语言模型。字符预算对单个超长句子为
软上限，标记超限但不丢弃。窗口元数据重复存储上下文，有显著空间开销；扩展后的
上下文也更长，应配合最终模型 token 预算。测试包括真实文件、持久化、重新打开数据库
与公开 Knowledge 调用，不等于所有向量数据库或生产效果都已验证。
