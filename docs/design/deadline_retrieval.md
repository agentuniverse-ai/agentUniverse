# Bounded deadline retrieval with explicit partial outcomes

`DeadlineRetrievalCoordinator` is an opt-in programmatic fan-out over initialized
synchronous Store objects. It does not change Knowledge.query_knowledge's return
type or its existing wait-for-all behavior. Use it when an application needs to
retain successful channels while reporting slow/failed channels explicitly.

```python
from agentuniverse.agent.action.knowledge.deadline_retrieval import DeadlineRetrievalCoordinator
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor

# Application startup: registered stores and providers must be initialized.
coordinator = DeadlineRetrievalCoordinator(
    {name: StoreManager().get_instance_obj(name, strict=True) for name in ("lexical", "vector")},
    max_workers=2, max_inflight=8, max_documents_per_channel=100,
)
try:
    # Reuse coordinator for many requests. Preserve report status in your API.
    report = coordinator.query(Query(query_str="installation"), budget_seconds=0.5)
    statuses = {name: outcome.status for name, outcome in report.channels.items()}
    fused = ReciprocalRankFusionProcessor(channel_key="recall_channel").process_docs(report.documents)
    response = {"partial": report.partial, "channels": statuses,
                "documents": [document.model_dump() for document in fused]}
finally:
    # Application shutdown, not a fresh executor/context manager per HTTP request.
    coordinator.close()
```

## Status and data contracts

- `success`: a valid list returned within the waiting budget, including an empty
  list. Empty success is not an error or automatically a partial result.
- `error`: ordinary exception or invalid result type. Only the exception class
  name is retained, not provider messages or stack traces.
- `timeout`: the call was not accepted as completed within the budget. Queued work
  is cancelled where possible. `still_running` is a snapshot at report creation,
  not a claim that cancellation stopped a running provider call.
- `cancelled`: work already cancelled externally by coordinator shutdown.

`partial` is true if any channel did not succeed. There are no automatic retries,
silent fallbacks or minimum-success guarantees. A provider that catches failures
and returns [] cannot be distinguished from empty success. Applications must not
discard statuses when returning the flattened documents to a user.

Each call gets an independent deep copy of Query, including keywords/embeddings/
ext_info, so channels cannot mutate another channel's query. Returned Documents
are also deep-copied and stamped with exact channel names under `recall_channel`.
Input documents are not changed. The flattened list preserves configured channel
order and within-channel rank; it is not globally reranked/deduplicated. Existing
RRF may be applied explicitly, without throwing away the report's partial status.
Only the first configured maximum of returned documents is copied per channel.

## Lifetime, admission and timing

The coordinator owns a fixed executor. `max_inflight` bounds all its submitted
unfinished calls across requests, including previous requests' late work. Admission
requires room for **all** channels and otherwise raises RetrievalCapacityError
before submission. A capacity rejection does not submit a partial request. Unusual
executor submission failure can occur after earlier calls started: queued calls are
cancelled and any already-running call remains tracked until completion. Caller
interruption similarly does not detach running work.

At the deadline, completed outcomes are collected, unstarted work is cancelled,
and late results are discarded. Running calls continue consuming in-flight capacity
until completion. `inflight_count` is an instantaneous count; do not treat it as a
reservation for a later request. Callback cleanup runs for success, error and
cancellation. Late calls never append data to a report already returned.

The budget is 0–86400 seconds, measured with a monotonic clock starting at query
entry. Zero budget does not invoke stores. It is a **waiting budget**, not a hard
real-time guarantee: Python scheduling, deep copies, lock acquisition and report
construction can add overhead. Blocking providers holding the GIL can delay the
whole process. The limit does not bound provider allocations or provider-created
threads. Store implementations must be safe for the configured concurrency; use
max_workers=1 or application serialization for non-thread-safe providers.

Python threads cannot be forcibly killed safely. Set finite IO timeouts on every
provider. `close()` stops admission, cancels queued work and waits for running
calls. This can exceed a request's budget or block indefinitely on a stuck provider.
`close(wait_for_running=False)` returns without joining but does NOT stop running
threads; they remain owned/counted and may keep Python alive. A later `close()`
can join them. The context manager waits on exit. The helper never closes the
underlying Store/SDK connections; caller retains their lifecycle ownership.

## Verification and limits

Event-controlled tests prove partial return while a call remains active, capacity
rejection, queued cancellation, stable late-result reports, cleanup after errors,
caller interruption, executor-submit failure and both shutdown modes. Real local
SQLite stores are persisted/reopened, queried and fused with existing RRF. These
are functional tests, not provider latency SLAs or production throughput benchmarks.
No async provider API, distributed cancellation, automatic Knowledge routing,
query paraphrasing or postprocessor timeout is supplied by this helper.

## 中文

本工具提供显式的多 Store 等待预算、部分结果和失败状态，不替换现有 Knowledge
接口。超时不等于线程停止：运行中的旧请求仍计入总在途上限，容量不足则拒绝新请求，
避免每次超时都继续堆积后台任务。尚未启动的任务尽量取消，晚到结果不会改写已返回
报告。返回空结果的成功通道与异常、超时、取消通道分开表示。

必须复用协调器，并为真实提供方配置有限 IO 超时。默认关闭会等待运行中的调用；
非阻塞关闭不会杀死线程。应在线程安全范围内选择并发度，并把 partial/通道状态与
检索内容一起呈现。测试验证资源生命周期，不声称获得严格物理截止或线上性能提升。
