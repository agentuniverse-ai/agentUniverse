# Optional weighted, explainable reciprocal rank fusion

Existing pipelines remain unweighted unless configured. The score becomes
`sum(weight[channel] / (k + rank))`; omitted weights default to 1. Weights
are nonnegative finite numbers, matched to exact string channel IDs. Zero
disables a channel entirely (including its choice of representative document).
If every observed channel is disabled, output is empty. Unused configured
channels are ignored. Missing/None/non-string channel IDs retain weight 1;
without `channel_key`, the whole input is a single unweighted channel.

Example component settings (retain the existing RRF YAML metadata):

```yaml
channel_key: recall_channel
channel_weights:
  curated_store: 2.0
  vector_store: 1.0
explain: true
explanation_field: fusion_details
max_explanation_channels: 32
```

Configure this processor in `Knowledge.post_processors`. Knowledge stamps
store names as `recall_channel`; these are store identifiers, not publishers.
No external model, API or new runtime dependency is required.

The shipped component YAML explicitly defaults to empty `channel_weights` and
`explain: false`. Registration tests load that YAML through Configer and the real
DocProcessorManager. Independent manager copies do not share mutable weight maps.

## Controlled counterexample, not a quality benchmark

A two-query, two-SQLite-store fixture is tested through actual managers, BaseRouter
and public Knowledge queries after database close/reopen (only tracing is mocked).
Store A has the labeled useful alpha document; store B has the useful beta document.
Default and explicit unit weights produce the same scores/order. Giving B weight 3
moves beta's useful document to first place but also moves alpha's distractor first.
The fixture's top-one hits remain 1/2: this proves controllable tradeoffs, not a net
relevance gain. Tune on separate training labels, then evaluate on held-out queries;
do not report this hand-authored example as evidence of production improvement.

Each returned explanation records channel, original one-based rank, weight,
and contribution. Duplicates within a channel still consume original positions
but contribute only once. Entries follow channel encounter order and are capped
per output document. `omitted_channels` and `omitted_contribution` summarize
the rest; displayed plus omitted contributions reconcile with the score within
floating-point precision. A zero entry limit provides totals only. Non-string
channel labels are represented as null in explanations, not serialized objects.

Default tie ordering and first-representative semantics are unchanged. Like
existing RRF, output is the representative input object and its metadata is
updated; this feature does not promise input immutability. Explanations are
off by default, so existing metadata is not removed. When enabled, the selected
explanation field is overwritten; it cannot equal the score field. Output
embeddings, text and IDs are unchanged. Score overflow raises before output
metadata writes. Explanation storage is bounded by returned documents times
the configured entry limit; the caller must choose sensible limits.

Weights express retrieval preferences, not calibrated probabilities or proof
of source credibility. A larger weight can promote irrelevant results. Tune
using held-out relevance judgments, not the scoring competition leaderboard.

## 中文说明

本功能在现有 RRF 上增加可选渠道权重及分数解释，不另造融合组件。
默认权重为 1、解释关闭，保持既有排序、去重和代表文档行为。
零权重停用渠道；所有渠道停用时返回空列表。解释超出条数上限的部分
保留贡献总和与渠道数，不能把截断解释误认为完整明细。
通过真实 SQLite 关闭重开及 Knowledge 公共查询链路验证渠道权重，
不代表生产检索质量提升，也不等于完整应用启动或云端 CI 验证。
