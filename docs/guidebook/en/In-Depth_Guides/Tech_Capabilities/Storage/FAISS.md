## FAISS

This page shows how to use FAISS as a vector store in agentUniverse.

### Install
```bash
pip install faiss-cpu   # CPU
# or
pip install faiss-gpu   # GPU
```

### Component YAML Example
```yaml
name: 'faiss_store'
description: 'a store based on faiss'
index_path: './DB/faiss/index.ivf'   # optional; in-memory if omitted
embedding_model: 'dashscope_embedding'
similarity_top_k: 20
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.faiss_store'
  class: 'FaissStore'
```

### Notes
- `index_path`: persist the FAISS index. When set, the same index will be loaded across restarts.
- `embedding_model`: auto-generate vectors when inputs do not provide embeddings.
- `similarity_top_k`: default top-k for search.

### Usage
Same as `ChromaStore`/`MilvusStore`: write `Document`s via import or `Store` API and issue `Query` for similarity search.


