# LanceDB Vector Store

LanceDB is an embedded (serverless) vector database — no separate server process is required, and data persists to a local directory. This makes it ideal for development, testing, and single-node production deployments.

## Installation

```bash
pip install lancedb
```

## Configuration

```yaml
name: lancedb_store
description: LanceDB embedded vector store
db_path: ./lancedb
table_name: agentuniverse_documents
embedding_model: openai_embedding
dimensions: 1536
distance: cosine
similarity_top_k: 10
max_insert_batch: 500
metadata:
  type: STORE
  module: agentuniverse.agent.action.knowledge.store.lancedb_store
  class: LanceDBStore
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | str | `./lancedb` | Local directory for the database |
| `table_name` | str | `agentuniverse_documents` | LanceDB table name |
| `embedding_model` | str | `None` | Name of a registered aU embedding component |
| `dimensions` | int | `None` | Vector dimension; inferred from first insert if unset |
| `distance` | str | `cosine` | Distance metric: `cosine`, `l2`, `dot` |
| `similarity_top_k` | int | `10` | Default number of query results |
| `max_insert_batch` | int | `500` | Max documents per batch insert |

## Usage

```python
from agentuniverse.agent.action.knowledge.store.lancedb_store import LanceDBStore
from agentuniverse.agent.action.knowledge.store.document import Document

store = LanceDBStore(
    db_path="./my_lancedb",
    table_name="MyCollection",
    dimensions=1536,
    distance="cosine",
)

store.insert_document([
    Document(id="doc1", text="Hello world", embedding=[...] * 1536),
])

from agentuniverse.agent.action.knowledge.store.query import Query
results = store.query(Query(query_str="greeting", embeddings=[[...] * 1536]))
```

## Dimension validation

The store validates that every inserted document's embedding dimension matches the table's configured dimension (or the dimension inferred from the first insert). Mismatched dimensions raise a clear `ValueError`.
