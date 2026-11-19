## LanceDB
If you wish to utilize the LanceDB vector database within agentUniverse, you need to follow these steps:

1. Install the LanceDB Python SDK
```
pip install lancedb
```
LanceDB is an embedded vector database: when `uri` points at a local directory no server process is needed, the data is stored in Lance columnar format on disk. To use LanceDB Cloud instead, set `uri` to a `db://` uri together with your `api_key`.

### How to Configure LanceDB Components
```yaml
name: 'lancedb_store'
description: 'a store based on lancedb'
uri: './lancedb'
table_name: 'agentuniverse'
distance: 'COSINE'
similarity_top_k: 10
with_vectors: false
embedding_model: 'openai_embedding'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.lancedb_store'
  class: 'LanceDBStore'
```
- uri: The LanceDB connection uri; a local directory path (embedded mode, no server needed) or a `db://` LanceDB Cloud uri.
- api_key: The LanceDB Cloud API key, only needed for cloud uris.
- region: The LanceDB Cloud region, defaults to us-east-1.
- table_name: The LanceDB table that stores the documents; it is created automatically on first insert.
- distance: The vector distance metric used at search time, one of COSINE (default), EUCLID, DOT.
- with_vectors: If true, query results also carry the stored vectors.
- embedding_model: The model employed to generate embedding vectors, for example openai_embedding.
- similarity_top_k: The number of the most similar results returned in a similarity search.

### Usage
[Knowledge_Define_And_Use](../../../In-Depth_Guides/Tutorials/Knowledge/Knowledge_Define_And_Use.md)
