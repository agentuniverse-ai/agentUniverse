# Reproducible Knowledge retrieval evaluation

Use initialized Knowledge objects; this evaluator does not start an application,
load credentials or infer relevance. Supply your own held-out judgments. Example:

```python
import json
from agentuniverse.agent.action.knowledge.retrieval_evaluation import evaluate_retrieval

# baseline and fused are already initialized Knowledge instances.
report = evaluate_retrieval(
    {"baseline": baseline, "rrf": fused},
    [{"query_id": "manual", "query": "AX-12 installation",
      "judgments": {"manual-document-id": 2, "related-id": 1}}],
    k=5,
    baseline="baseline",
    provenance={"code_revision": "record-your-commit", "corpus_revision": "v1",
                "pipeline_configs": {"baseline": "config digest", "rrf": "config digest"}},
)
print(json.dumps(report, indent=2, allow_nan=False))
```

Each pipeline is called through `query_knowledge(query_str=..., similarity_top_k=k)`.
Reported IDs are truncated to k even if a backend returns more. No text or labels
are passed to a judge. Relevance grades are integers 0..30; positive means relevant.
Recall denominator is all positively judged documents, not min(k, relevant).
MRR uses the first positive hit. nDCG uses gain `2**grade - 1` and discount
`log2(rank + 1)`, with the ideal ranking derived from the full supplied judgment set.

Duplicate IDs consume ranks but gain only once. Missing judgments mean nonrelevant.
Queries with no positive labels receive zero; `has_positive_labels` makes that
choice visible. Empty datasets are rejected. Invalid datasets and provenance
fail before querying. Query exceptions produce zero metrics and an error type;
failed queries remain in macro averages. Exception messages are intentionally
omitted. Do not interpret an exception-free report as proof of healthy providers:
Knowledge may itself suppress store failures, which this wrapper cannot observe.

Dataset content/order is fingerprinted using SHA-256. Provenance is explicitly
provided, not automatically verified. Report IDs/provenance can still contain
sensitive information: keep reports local unless cleared for publication.
Latency is wall time around query plus scoring, is not deterministic, and includes
cold caches. There is no warm-up, significance test or production-speed claim.

Defaults bound case/pipeline counts to 1000/20, not memory use within a backend.
Calls are sequential; configure backend timeouts. No background cancellation,
retries or executor shutdown is performed. Callers own pipeline lifetimes.

## Same-run baseline comparisons

Optional `baseline` must name a supplied pipeline and is validated before calls.
The default report remains unchanged when it is omitted. Comparisons include
candidate-minus-baseline metric/latency deltas, first-occurrence document ranks
(null means absent from the returned top-k), and improved/unchanged/regressed
query counts for each relevance metric. Duplicate slots still consume rank.
Failures remain visible on both sides and count as zero, including when both
sides fail; unchanged scores do not mean both pipelines succeeded. Positive
latency delta means slower, not better. There is no statistical significance claim.

From the repository root, run `python -m docs.examples.retrieval_evaluation_demo`.
This prints a three-query hand-authored example with one improved and one regressed
nDCG query plus an unanswerable query. The recorded rankings explain the report
format only: they are not a retrieval algorithm or measured quality improvement.
For actual experiments replace the two fixtures with initialized Knowledge objects,
use corpus-matched document IDs and independent held-out relevance judgments.

## 中文

本评测器针对 Knowledge 公共检索入口，区别于 ContextManager 的合成关键词评测。
输入明确的文档相关性标注，输出 Recall@k、MRR@k、nDCG@k、逐查询错误和耗时。
失败查询和没有正例的查询不会从平均分中消失。不要以小型合成样例宣称生产准确率提升。
测试包含手算对照以及实际 SQLite 持久化、关闭重开后对原始/融合管线的评测。
后续管线对比需使用相同语料、查询及标注，调参集与最终评估集应分离。
可选 baseline 输出逐查询增减、文档首次出现的名次及退步数量；失败不被隐藏。
附带可运行的手工示例仅演示报告解释，不代表实际检索收益。
