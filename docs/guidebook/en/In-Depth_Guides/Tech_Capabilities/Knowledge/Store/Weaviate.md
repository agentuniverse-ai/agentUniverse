# Weaviate Vector Store

Weaviate is an open-source vector database optimized for semantic search and RAG pipelines. This component provides a `WeaviateStore` that plugs into agentUniverse's knowledge layer.

## Installation

```bash
pip install weaviate-client
```

## Configuration

Create a store component YAML (e.g. `weaviate_store.yaml`):

```yaml
name: weaviate_store
description: Weaviate vector store for knowledge retrieval
url: http://localhost:8080
grpc_port: 50051
api_key: ''
collection_name: AgentuniverseDocument
embedding_model: openai_embedding
dimensions: 1536
distance: cosine
similarity_top_k: 10
max_insert_batch: 500
metadata:
  type: STORE
  module: agentuniverse.agent.action.knowledge.store.weaviate_store
  class: WeaviateStore
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | str | `http://localhost:8080` | Weaviate server URL |
| `grpc_port` | int | `50051` | gRPC port for fast data transfer; set `0` to disable |
| `api_key` | str | `""` | Optional Weaviate API key |
| `collection_name` | str | `AgentuniverseDocument` | Weaviate collection name |
| `embedding_model` | str | `None` | Name of a registered aU embedding component |
| `dimensions` | int | `None` | Vector dimension; inferred from first insert if unset |
| `distance` | str | `cosine` | Distance metric: `cosine`, `dot`, `l2` |
| `similarity_top_k` | int | `10` | Default number of query results |
| `max_insert_batch` | int | `500` | Max documents per batch insert |

## Usage

```python
from agentuniverse.agent.action.knowledge.store.weaviate_store import WeaviateStore
from agentuniverse.agent.action.knowledge.store.document import Document

store = WeaviateStore(
    url="http://localhost:8080",
    collection_name="MyCollection",
    embedding_model="openai_embedding",
    dimensions=1536,
    distance="cosine",
)

# Insert documents
store.insert_document([
    Document(id="doc1", text="Hello world", embedding=[...] * 1536),
])

# Query
from agentuniverse.agent.action.knowledge.store.query import Query
results = store.query(Query(query_str="greeting", embeddings=[[...] * 1536]))
```

## Dimension validation

The store validates that every inserted document's embedding dimension matches the collection's configured dimension (or the dimension of the first inserted document). Mismatched dimensions raise a clear `ValueError` instead of failing at the server with an opaque error.
