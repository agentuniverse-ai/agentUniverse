# Weaviate 向量存储

Weaviate 是一个开源向量数据库，专为语义搜索和 RAG 管道优化。本组件提供 `WeaviateStore`，接入 agentUniverse 的知识层。

## 安装

```bash
pip install weaviate-client
```

## 配置

创建存储组件 YAML（如 `weaviate_store.yaml`）：

```yaml
name: weaviate_store
description: Weaviate 向量存储
url: http://localhost:8080
grpc_port: 50051
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

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | str | `http://localhost:8080` | Weaviate 服务器地址 |
| `grpc_port` | int | `50051` | gRPC 端口（设为 `0` 禁用） |
| `api_key` | str | `""` | 可选的 Weaviate API 密钥 |
| `collection_name` | str | `AgentuniverseDocument` | Weaviate 集合名称 |
| `embedding_model` | str | `None` | 已注册的 aU embedding 组件名称 |
| `dimensions` | int | `None` | 向量维度；未设置时从首个插入文档推断 |
| `distance` | str | `cosine` | 距离度量：`cosine`、`dot`、`l2` |
| `similarity_top_k` | int | `10` | 默认返回结果数 |
| `max_insert_batch` | int | `500` | 每批插入的最大文档数 |

## 使用示例

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

# 插入文档
store.insert_document([
    Document(id="doc1", text="你好世界", embedding=[...] * 1536),
])

# 查询
from agentuniverse.agent.action.knowledge.store.query import Query
results = store.query(Query(query_str="问候", embeddings=[[...] * 1536]))
```

## 维度校验

存储组件会校验每个插入文档的 embedding 维度是否与集合配置的维度一致（或与首个插入文档的维度一致）。维度不匹配时会抛出明确的 `ValueError`，而非在服务端产生不可诊断的错误。
