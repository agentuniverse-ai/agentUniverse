# LanceDB 向量存储

LanceDB 是一个嵌入式（无服务器）向量数据库 — 无需独立的服务器进程，数据持久化到本地目录。非常适合开发、测试和单节点生产部署。

## 安装

```bash
pip install lancedb
```

## 配置

```yaml
name: lancedb_store
description: LanceDB 嵌入式向量存储
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

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `db_path` | str | `./lancedb` | 本地数据库目录 |
| `table_name` | str | `agentuniverse_documents` | LanceDB 表名 |
| `embedding_model` | str | `None` | 已注册的 aU embedding 组件名称 |
| `dimensions` | int | `None` | 向量维度；未设置时从首个插入文档推断 |
| `distance` | str | `cosine` | 距离度量：`cosine`、`l2`、`dot` |
| `similarity_top_k` | int | `10` | 默认返回结果数 |
| `max_insert_batch` | int | `500` | 每批插入的最大文档数 |

## 使用示例

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
    Document(id="doc1", text="你好世界", embedding=[...] * 1536),
])

from agentuniverse.agent.action.knowledge.store.query import Query
results = store.query(Query(query_str="问候", embeddings=[[...] * 1536]))
```

## 维度校验

存储组件会校验每个插入文档的 embedding 维度是否与表配置的维度一致（或与首个插入文档的维度一致）。维度不匹配时会抛出明确的 `ValueError`。
