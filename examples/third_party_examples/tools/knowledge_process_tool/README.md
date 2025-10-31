### Enable Knowledge Post-Processing (Rerank/Filter/Merge/Summarize)

You can chain post-retrieval processors in any `Knowledge` config via `post_processors`.

```
post_processors:
  - dashscope_reranker
  - score_threshold_filter
  - merge_by_metadata
  - summarize_docs
```

Fine-tune processors at the agent level under `config.doc_processors`:

```
config:
  doc_processors:
    score_threshold_filter:
      min_score: 0.2
      keep_no_score: true
      top_k: 20
    merge_by_metadata:
      group_keys: ['file_name']
      separator: "\n\n"
      prefer_higher_score: true
    summarize_docs:
      llm: '__default_instance__'
      mode: 'stuff'  # or 'map_reduce'
      return_only_summary: false
```

Requirements:
- Set `DASHSCOPE_API_KEY` for `dashscope_reranker`.
- Ensure an LLM is configured for summarization.