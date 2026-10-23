## ChromaDB

The agentUniverse already integrates ChromaDB-related dependencies, so there is no need for you to install additional packages to utilize ChromaDB's features.
If you wish to gain insights into the underlying principles of ChromaDB, you may visit the  [official ChromaDB website](https://www.trychroma.com/).

### How to Configure ChromaDB Components
```yaml
name: 'chroma_store'
description: 'store based on chroma db'
persist_path: '../../DB/criminal_law.db'
embedding_model: 'dashscope_embedding'
similarity_top_k: 100
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.chroma_store'
  class: 'ChromaStore'
```
- persist_path: The path for persistence storage of the database, utilized for saving and retrieving vector data.
- embedding_model: The model employed to generate embedding vectors, specified here as dashscope_embedding.
- similarity_top_k: The number of most similar results returned during a similarity search.

### Usage
[Knowledge_Define_And_Use](../../../In-Depth_Guides/Tutorials/Knowledge/Knowledge_Define_And_Use.md)