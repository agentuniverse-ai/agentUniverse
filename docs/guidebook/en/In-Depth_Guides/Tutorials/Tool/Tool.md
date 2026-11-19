# Tool
Just as humans use and create tools to extend their capabilities, enhance their professionalism, and compensate for deficiencies in their innate abilities, intelligent agents can also leverage tools to push the boundaries of their capabilities. 

In complex task scenarios, specialized tools are often needed to improve the performance of agents. These tools can be existing APIs or methods within the task domain or new methods created by users to solve problems.

agentUniverse provides a standardized approach to customizing tools. Combining underlying RPC technological components with standard HTTP protocol, you can register any API or local code snippet as a standard tool for use by agents and other components.

## Resilience wrapper

`ResilientTool` wraps any registered tool with configurable timeouts, idempotency-aware exponential retries, exception allowlists, structured-error retries, fallback values, and a thread-safe circuit breaker. Copy `agentuniverse/agent/action/tool/resilient_tool.yaml.example` into the application and point `target_tool` at an existing component.

Retries are disabled for non-idempotent operations unless `allow_retry_non_idempotent` is explicitly enabled. The circuit opens after `circuit_failure_threshold` terminal failures, rejects calls during the recovery window, then permits one half-open probe. `resilience_state()` exposes counters without changing the wrapped tool result.

```yaml
name: resilient_search
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.resilient_tool
  class: ResilientTool
input_keys: [input]
target_tool: google_search_tool
idempotent: true
max_attempts: 3
timeout_seconds: 10
circuit_failure_threshold: 5
circuit_recovery_seconds: 30
```

`timeout_seconds` is a response deadline. With Python thread-backed execution it stops waiting but cannot forcibly terminate code already running inside the wrapped tool. A deadline failure is therefore never retried automatically, even for an idempotent target: starting another attempt could overlap the still-running worker and duplicate side effects. Native asynchronous targets can propagate cancellation to cancellable I/O. Cancellation of a half-open probe safely reopens the circuit so a later probe is not permanently blocked.

Each accepted wrapper invocation asks `ToolManager` for a fresh target copy. This preserves the framework's copy-per-call isolation when multiple wrapper calls execute concurrently; only the wrapper's circuit and metric state are intentionally shared.

# Conclusion
By now, you should have a basic understanding of the design principles behind tool components. In the next section, we will introduce you to the standard definitions of tool components, how to customize and create your own tools, and how to utilize these tools.
