# Knowledge query diagnostics

`Knowledge.query_knowledge()` intentionally tolerates failures from individual
stores so healthy retrieval channels can still answer. Applications that need
to observe those partial failures can use the opt-in diagnostics API:

```python
result = knowledge.query_knowledge_with_diagnostics(
    query_str="agent orchestration",
    similarity_top_k=5,
)

for diagnostic in result.diagnostics:
    print(
        diagnostic.store_code,
        diagnostic.succeeded,
        diagnostic.duration_ms,
        diagnostic.document_count,
        diagnostic.error,
    )

documents = result.documents
```

Every routed store produces one diagnostic with success state, elapsed
milliseconds, returned document count, and a concise error when applicable.
`documents` uses the same de-duplication and post-processing path as
`query_knowledge()`. Missing component registrations still raise immediately;
runtime failures from one store remain non-fatal.
