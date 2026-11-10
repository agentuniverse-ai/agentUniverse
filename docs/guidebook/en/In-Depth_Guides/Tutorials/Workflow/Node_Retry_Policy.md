# Workflow Node Retry Policy

Individual workflow nodes can opt into deterministic retries for transient
failures. Existing nodes remain fail-fast because the default is one attempt.

Add `retry_policy` to a node in the workflow graph configuration:

```yaml
graph:
  nodes:
    - id: fetch-data
      type: tool
      retry_policy:
        max_attempts: 4
        initial_delay: 0.5
        backoff_multiplier: 2
        max_delay: 5
      data:
        # existing node configuration
```

`max_attempts` includes the initial call. Delays use exponential backoff and
are capped by `max_delay` when it is set. The original exception is re-raised
after the final attempt. A node that succeeds after retrying adds
`attempt_count` to its output metadata for observability.

Retries are opt-in because tool and agent nodes may perform side effects. Only
enable them when the operation is idempotent or otherwise safe to repeat.
