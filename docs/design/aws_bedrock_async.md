# AWS Bedrock Async Execution

## Problem and Scope

The native Bedrock LLM `_acall()` and embedding `async_get_embeddings()` called
synchronous Boto3 code directly. The streaming wrapper also advanced a blocking
event iterator on the event loop. As a result, unrelated coroutines could not
make progress during AWS client initialization, requests, or response reads.

This change keeps Boto3 and the existing request/response conversion. Optional
dependency packaging is a separate PR. It does not introduce aioboto3, change
model parameters, fix empty non-stream responses, or migrate LangChain adapters.

## Execution and Ownership

- Non-stream LLM calls and embedding batches use `asyncio.to_thread`, including
  lazy client initialization and embedding response-body reads. Context variables
  are propagated. Embedding order and model-specific keyword arguments are retained.
- Lazy client creation is serialized. LLM clients are created through a private
  Boto3 session rather than the shared default session. Only client creation is
  locked, not inference. Cached clients can serve concurrent requests.
- Async streams open lazily on the first iteration. Both the HTTP request and
  each iterator read run on a dedicated single-worker executor for that stream.
  Opening, reading and closing have one thread owner. There is no prefetch or
  unbounded response queue: the consumer requests one chunk at a time.
- One worker is allocated per active stream. This avoids holding the shared
  asyncio executor while a consumer is idle, but callers should bound their
  overall concurrent streams according to deployment capacity.
- A small synchronous iterator owns the underlying event stream even before
  the text generator starts. Exhaustion, parsing errors and explicit close
  release it once. Embedding response bodies also close on success or parse error.
- The default public `acall()` tracing wrapper forwards `aclose()` in a `finally`
  block, when the iterator supports it, and pops the monitor entry when a started
  stream finishes, fails or closes.
  This is necessary for callers closing the public API rather than `_acall()`.
  Custom tracing plugins remain responsible for forwarding cleanup themselves.

## Cancellation and Compatibility

Cancellation of an awaiting task propagates promptly. It cannot forcibly stop a
Boto3 request already executing in a thread. A cancelled non-stream call or
embedding batch may continue running to completion. For streams, cleanup is
queued after the in-flight opening/read operation, and no subsequent read is
scheduled. The generator is never closed concurrently with an active `next()`.
Outstanding SDK work and process shutdown remain subject to SDK timeout/retry
behavior; this is not hard cancellation of remote inference or its billing.

Streams preserve chunk order, `LLMOutput` values, and existing request/read error
messages. One deliberate timing change is that stream-opening errors surface at
the first iteration, not when awaiting `acall(..., streaming=True)`. Merely
obtaining and closing an unstarted async iterator allocates no AWS resources.

Use explicit cleanup when stopping early (inside an initialized application):

```python
from contextlib import aclosing

async def first_chunk(llm, messages):
    async with aclosing(await llm.acall(messages, streaming=True)) as chunks:
        async for chunk in chunks:
            return chunk.text
    return ""
```

The SDK calls still use the configured AWS account and may incur charges.

## Offline Validation

```bash
python -m pytest -q \
  tests/test_agentuniverse/unit/llm/test_aws_bedrock_async.py \
  tests/test_agentuniverse/unit/base/annotation/test_trace_llm_stream_cleanup.py \
  tests/test_agentuniverse/unit/base/annotation/test_trace.py \
  tests/test_agentuniverse/unit/base/util/monitor/test_monitor.py \
  tests/test_agentuniverse/unit/llm/test_llm_configuration.py
```

Tests use fake clients, blocked sockets and synchronization gates instead of
AWS credentials or real network latency. They verify loop progress during
opening, reading and closing; cancellation at each stage; ordering and context;
empty streams; errors; early close; no prefetch; client initialization races;
and eventual worker shutdown. Generic tracing tests cover iterators with and
without `aclose`, exceptions, cancellation and non-stream results.

Reference: [Python thread offloading](https://docs.python.org/3.10/library/asyncio-task.html#asyncio.to_thread),
[Boto3 client concurrency](https://docs.aws.amazon.com/boto3/latest/guide/clients.html#multithreading-or-multiprocessing-with-clients),
[Botocore event-stream close](https://docs.aws.amazon.com/botocore/latest/reference/eventstream.html).

## 中文说明

原有异步接口直接运行同步 Boto3 请求，会阻塞事件循环。此次修改将普通 LLM 调用及
Embedding 批次放到工作线程；流式请求则由单独的单线程执行器负责创建、按需读取和关闭，
保持输出顺序，不进行无限预取。客户端的延迟创建加锁，LLM 使用独立的 Boto3 Session，
推理请求本身不加锁。普通调用会传播上下文变量，Embedding 保留输入顺序及模型参数。

每个活跃流占用一个线程，调用方应限制总并发数量。公共 `acall()` 的默认监控包装层会
传递关闭操作；自定义监控插件仍需自行传递清理。同步流在结束、解析异常或显式关闭时释放
响应，Embedding 响应体在成功或解析异常时也会释放。

取消协程会及时返回，但无法强行中止已经运行的同步 SDK 请求。普通调用或 Embedding 批次
可能继续完成；流式清理会排在当前创建或读取操作之后，之后不再读取，不会并发关闭正在
执行的生成器。清理和进程退出仍受 SDK 超时及重试行为影响，取消不保证远端推理停止或免除费用。

流式请求改为首次迭代时发起，因此连接错误也在首次迭代时抛出。尚未开始迭代的流不会创建
AWS 资源。提前退出请使用上面的 `contextlib.aclosing` 示例。输出顺序、内容及已有错误信息
保持不变，不包含非流式空响应修复、LangChain 升级或可选依赖配置变更。

以上测试命令无需安装 Boto3，不读取 AWS 凭据，也不访问网络。通过同步门控制模拟阻塞，
验证事件循环响应性、并发、各阶段取消、空流、错误、提前关闭、无预取以及工作线程退出。
