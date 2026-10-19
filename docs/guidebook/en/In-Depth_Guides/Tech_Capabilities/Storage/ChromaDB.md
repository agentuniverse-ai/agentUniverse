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

### Chroma 1.x upgrade checks

This integration pins ChromaDB 1.5.9. Before upgrading an existing deployment:

1. Stop writers and make a separate backup of the complete persistence directory.
   Perform the first upgrade against a copy, not the only copy of production data.
2. Keep the configured embedding model and vector dimensions unchanged. Reopen
   representative collections and verify IDs, documents, metadata and search results.
3. Restart the application in a new process and repeat the checks. Reusing a client
   in one process is not sufficient evidence of durable persistence.
4. For HTTP deployments, validate against the intended server version separately.
   The local HTTP regression uses a 1.5.9 server; it does not establish compatibility
   with all older servers, authentication setups or reverse proxies.
5. If validation fails, stop the upgraded application and restore the pre-upgrade
   backup with its original environment. Do not assume an upgraded data directory
   can be safely reopened by an older Chroma version.

The process/HTTP regression tests use explicit test vectors and temporary data;
they require no embedding API key or model download:

```shell
python -m pytest tests/test_agentuniverse/unit/base/util/test_chroma_process_integration.py
```
