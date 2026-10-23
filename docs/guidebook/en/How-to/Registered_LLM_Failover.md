# Explicit registered LLM failover / 显式注册模型故障切换

Use a caller-approved sequence of existing registered LLM names:

```python
from agentuniverse.llm.registered_failover import RegisteredLLMFailover

chain = RegisteredLLMFailover(["primary_llm", "backup_llm"])
result = chain.call(messages=[{"role": "user", "content": "Hello"}])
print(result.output.text, result.provider, result.attempts)
# await chain.acall(...) for async calls
# chain.stream(...) or chain.astream(...) for provenance-bearing chunks
```

This API calls actual LLM.call/acall and retains their instrumentation. It is
independent of LiteLLM and tool retry wrappers. Each invocation resolves fresh
registry copies, validates the entire 1–8 name chain before calling, and tries
each at most once. Input kwargs are deep-copied for each attempt. No parameters
are silently dropped; a provider's unsupported parameter/business error normally
propagates. Objects that cannot be deep-copied are outside this API's contract.

Defaults permit built-in ConnectionError, TimeoutError and asyncio.TimeoutError.
SDK exceptions need explicit approval, e.g. `retry_errors=(openai.RateLimitError,)`.
Do not use broad business exception classes. Exception/BaseException and
cancellation types are rejected. All-approved failures raise LLMFailoverExhausted
with attempt records and the last error as cause; other exceptions propagate.
Attempt records contain registered names and error class names, not error text.

Provider configuration still controls internal retries and request timeouts.
There is no background timeout worker, circuit breaker or parallel attempt;
an observed timeout can still mean the remote service did work. This cannot
promise exactly-once remote execution or zero duplicate cost. Configure provider
internal retries deliberately. A registered name identifies that configuration,
not a guarantee of a gateway's internal vendor selection. Caller parameters can
still override provider options according to the underlying LLM's API.

Streaming commits to the provider after **any** emitted chunk, including an
empty or role-only chunk. Later errors propagate and never splice another
model's output. A successful empty stream is accepted and emits no provenance
record. Close/aclose the generator when abandoning it; the wrapper delegates
closure to the returned iterator, but provider/decorator implementations remain
responsible for transport cleanup. Cancellation never triggers failover.

## 中文

显式提供已批准的注册模型名称链；每次调用先验证全部名称，再按顺序各尝试一次。
返回原 LLMOutput、最终注册名称和尝试记录；流式每块也携带该记录。调用使用
现有 LLM.call/acall，不替代现有追踪，不依赖 LiteLLM 或 Tool 重试包装器。

默认只对连接/超时异常切换，SDK 异常类型需另行批准。业务错误、参数不支持和
取消直接传播；参数不会静默丢弃，每次尝试使用输入副本。流中一旦输出任何块，
包括空块，即不再切换。提前结束消费时请 close/aclose；底层提供方仍负责其网络
资源。成功空流不会输出来源记录。注册名表示该模型配置，不保证网关内部供应商。

没有并发尝试或后台超时线程；提供方内部重试和超时仍由配置决定，远端超时仍可能
发生计费/执行，不能保证远端恰好一次。测试使用合成受控提供方，以及两个仅回环
HTTP服务配合真实OpenAI SDK/OpenAIStyleLLM；不使用付费模型或真实账号数据。
