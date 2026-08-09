# Store

`Store`负责对`Document`进行存储，并在知识的检索阶段提供查询能力。`Store`的具体形式可以是多样的，包括关系型数据库、向量数据库、图数据库等形式。因此同一份`Document`也能在不同的`Store`中以不同的形式存储，而具体的检索方式也和`Store`的能力相绑定。

Store定义如下：
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
- `_new_client`和`_new_async_client`用于创建数据库链接，在组件注册阶段会被添加到[post_fork](../../技术组件/服务化/Web_Server.md)执行列表中，保证创建的数据库连接在Gunicorn模式下的子进程中是独立的。
- `query`函数是知识组件在查询时调用的函数，负责根据传入的Query实例在store中查找相关的内容并以document的形式返回
- `Store`的还包括对`Document`类型数据的增删改查，作为知识存储的管理接口。

在编写完对应代码后，可以参考下面的yaml将你的Store注册为aU组件：
```yaml
name: 'sample_store'
description: 'a sample store'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.sample_store'
  class: 'SampleStore'
```
其中metadata的type固定为STORE.

### 关注您定义的Store所在的包路径
在agentUniverse项目的config.toml中需要配置Store配置对应的package, 请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`store`路径或其子路径下。

以示例工程中的配置为例，如下：
```yaml
[CORE_PACKAGE]
store = ['sample_standard_app.intelligence.agentic.knowledge.store']
```

## agentUniverse目前内置Store：
- [Chroma](../../技术组件/存储/ChromaDB.md)
- [Milvus](../../技术组件/存储/Milvus.md)
- [Sqlite](../../技术组件/存储/Sqlite.md)
### RedisVectorStore

`RedisVectorStore` 使用 Redis Stack/RediSearch HNSW 索引提供同步和异步向量增删改查。通过 `pip install 'agentUniverse[store_ext]'` 安装可选依赖，并使用 Redis Stack；不含 Search 模块的普通 Redis 无法使用该组件。

复制 `redis_vector_store.yaml.example`，配置向量维度、距离度量、键前缀，以及需要精确过滤的 TAG 元数据字段。连接凭证也可通过 `REDIS_VECTOR_URL` 注入，避免写入 YAML。

```python
store.upsert_document([Document(id="1", text="hello", metadata={"tenant": "acme"}, embedding=[0.1, 0.2])])
results = store.query(Query(embeddings=[[0.1, 0.2]], similarity_top_k=5), metadata_filter={"tenant": "acme"})
```

支持 `cosine`、`l2`、`inner_product`。元数据过滤仅允许使用 `filter_tag_fields` 中声明的字段；组件会验证标识符并转义 RediSearch TAG 查询值。

## PGVectorStore

`PGVectorStore` 提供基于 PostgreSQL/pgvector 的同步与异步 CRUD、余弦/L2/内积检索、JSONB 包含过滤、可选的自动向量化、维度校验、自动建表和可选 HNSW 索引。安装 `store_ext` extra，并将 `agentuniverse/agent/action/knowledge/store/pgvector_store.yaml.example` 复制到应用配置目录。连接地址可以写在本地配置的 `connection_url` 中，或通过 `PGVECTOR_CONNECTION_URL` 提供；请勿提交数据库凭据。

## MongoDBAtlasStore

`MongoDBAtlasStore` 是基于 MongoDB Atlas Vector Search 的向量存储。通过 ``$vectorSearch`` 聚合管道阶段提供插入、查询、upsert、更新、删除及巡检能力，支持 cosine / euclidean / dotProduct 相似度函数、可配置向量维度、通过已注册 aU embedding 组件按需向量化、可选 metadata 过滤，以及受控的资源使用（`similarity_top_k`）。安装可选依赖 `pip install 'agentUniverse[store_ext]'`（或 `pip install pymongo`），并准备一个配置了 Vector Search 索引的 MongoDB Atlas 集群。

将 `agentuniverse/agent/action/knowledge/store/mongodb_atlas_store.yaml.example` 复制到应用配置目录，加载内置 `mongodb_atlas_store` 组件。在该配置副本中设置 `connection_url`（或通过 `MONGODB_ATLAS_URI` 环境变量提供）；`embedding_model` 指定一个已注册的 aU embedding 组件，用于按需对文档和查询向量化。Atlas Vector Search 索引（默认名 `vector_index`）需通过 Atlas 控制台 / 管理 API 在 `vector_field` 上配置。

```yaml
name: mongodb_atlas_store
description: MongoDB Atlas Vector Search store for knowledge retrieval
connection_url: ''
database_name: agentuniverse
collection_name: documents
embedding_model: openai_embedding
dimensions: 1536
similarity: cosine
similarity_top_k: 10
vector_field: embedding
text_field: text
index_name: vector_index
metadata:
  type: STORE
  module: agentuniverse.agent.action.knowledge.store.mongodb_atlas_store
  class: MongoDBAtlasStore
```
- connection_url: MongoDB 连接串；未设置时回退到 `MONGODB_ATLAS_URI` 环境变量。
- database_name: 存放集合的 MongoDB 数据库。
- collection_name: 存放文档的 MongoDB 集合。
- embedding_model: 用于按需对文档/查询向量化的已注册 aU embedding 组件名。
- dimensions: 向量维度；为 `null` 时由首条插入文档推断。
- similarity: `$vectorSearch` 相似度函数——`cosine`、`euclidean` 或 `dotProduct`。
- similarity_top_k: `query` 默认返回的结果数。
- vector_field: 存储向量 embedding 的字段名。
- text_field: 存储文档文本的字段名。
- index_name: Atlas Vector Search 索引名。

```python
store.upsert_document([Document(id="1", text="hello", metadata={"tenant": "acme"}, embedding=[0.1, 0.2, 0.3])])
results = store.query(Query(embeddings=[[0.1, 0.2, 0.3]], similarity_top_k=5), metadata_filter={"tenant": "acme"})
```
