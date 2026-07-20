# Store

`Store` is responsible for storing `Document` objects and providing query capabilities during the knowledge retrieval phase. The specific form of a `Store` can vary, including relational databases, vector databases, graph databases, and more. Therefore, the same `Document` can be stored in different Stores in various formats, and the retrieval methods are tied to the capabilities of the specific `Store`.

The Store is defined as follows:
```python
from typing import Any, List, Optional

from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent_serve.web.post_fork_queue import add_post_fork

class Store(ComponentBase):
    component_type: ComponentEnum = ComponentEnum.STORE
    name: Optional[str] = None
    description: Optional[str] = None
    client: Any = None
    async_client: Any = None

    def _new_client(self) -> Any:
        pass

    def _new_async_client(self) -> Any:
        pass

    def _initialize_by_component_configer(self,
                                         store_configer: ComponentConfiger) \
            -> 'Store':
        if store_configer.name:
            self.name = store_configer.name
        if store_configer.description:
            self.description = store_configer.description
        add_post_fork(self._new_client)
        add_post_fork(self._new_async_client)
        return self

    def query(self, query: Query, **kwargs) -> List[Document]:
        raise NotImplementedError

    def insert_document(self, documents: List[Document], **kwargs):
        raise NotImplementedError

    def delete_document(self, document_id: str, **kwargs):
        raise NotImplementedError

    def upsert_document(self, documents: List[Document], **kwargs):
        raise NotImplementedError

    def update_document(self, documents: List[Document], **kwargs):
        raise NotImplementedError
```
- `_new_client` and `_new_async_client` are used to create database connections. These methods are added to the [post_fork](../../../In-Depth_Guides/Tech_Capabilities/Service/Web_Server.md) execution list during the component registration phase to ensure that the database connections created are independent in Gunicorn mode child processes.
- The `query`function is called by the knowledge component during a query, responsible for searching the store for relevant content based on the passed Query instance and returning the results in the form of Document objects.
- The `Store` also includes CRUD (Create, Read, Update, Delete) operations for Document data, serving as the management interface for knowledge storage.

After writing the code, you can refer to the following YAML configuration to register your Store as an aU component:
```yaml
name: 'sample_store'
description: 'a sample store'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.sample_store'
  class: 'SampleStore'
```
The `metadata.type` must be set to STORE.

### Pay Attention to the Package Path of Your Defined Store
In the config.toml file of the agentUniverse project, you must configure the package path for the Store. Ensure that the package path of the file you created is under the CORE_PACKAGE in the store path or its subpaths.

For example, in the configuration of the sample project:
```yaml
[CORE_PACKAGE]
store = ['sample_standard_app.intelligence.agentic.knowledge.store']
```

## Prebuilt Stores in agentUniverse:
- [Chroma](../../../In-Depth_Guides/Tech_Capabilities/Storage/ChromaDB.md)
- [Milvus](../../../In-Depth_Guides/Tech_Capabilities/Storage/Milvus.md)
- [Sqlite](../../../In-Depth_Guides/Tech_Capabilities/Storage/Sqlite.md)
### RedisVectorStore

`RedisVectorStore` uses Redis Stack/RediSearch HNSW indexes for synchronous and asynchronous vector CRUD and search. Install the optional dependency with `pip install 'agentUniverse[store_ext]'` and run Redis Stack (classic Redis without the Search module is insufficient).

Copy `redis_vector_store.yaml.example` and configure the vector dimension, distance metric, key prefix, and any metadata fields that must be indexed as exact-match TAG fields. Credentials may be supplied through `REDIS_VECTOR_URL` instead of YAML.

```python
store.upsert_document([Document(id="1", text="hello", metadata={"tenant": "acme"}, embedding=[0.1, 0.2])])
results = store.query(Query(embeddings=[[0.1, 0.2]], similarity_top_k=5), metadata_filter={"tenant": "acme"})
```

Supported metrics are `cosine`, `l2`, and `inner_product`. Metadata filters are accepted only for fields declared in `filter_tag_fields`; identifiers and filter values are validated and escaped before constructing RediSearch queries.

## PGVectorStore

`PGVectorStore` adds PostgreSQL/pgvector persistence with synchronous and asynchronous CRUD, cosine/L2/inner-product search, JSONB containment filters, optional managed embeddings, dimension validation, automatic table/extension creation, and an optional HNSW index. Install the `store_ext` extra and copy `agentuniverse/agent/action/knowledge/store/pgvector_store.yaml.example` into the application configuration directory. Set `connection_url` in that copy or use `PGVECTOR_CONNECTION_URL`; never commit credentials.
