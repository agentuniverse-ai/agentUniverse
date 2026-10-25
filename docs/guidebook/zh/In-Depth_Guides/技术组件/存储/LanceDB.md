## LanceDB
如果您希望在agentUniverse中使用LanceDB向量数据库，需要遵循以下步骤：

1. 安装LanceDB Python SDK
```
pip install lancedb
```
LanceDB是嵌入式向量数据库：`uri`指向本地目录时无需任何服务进程，数据以Lance列式格式存储在磁盘上。如需使用LanceDB Cloud，请将`uri`设置为`db://`形式的地址并提供`api_key`。

### 如何配置LanceDB组件
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
- uri: LanceDB连接地址；本地目录路径（嵌入式模式，无需服务）或`db://`形式的LanceDB Cloud地址。
- api_key: LanceDB Cloud的API Key，仅云地址需要。
- region: LanceDB Cloud的地域，默认us-east-1。
- table_name: 存储文档的LanceDB表；首次写入时自动创建。
- distance: 检索时使用的向量距离度量，可选COSINE（默认）、EUCLID、DOT。
- with_vectors: 为true时查询结果会同时返回向量。
- embedding_model: 用于生成embedding向量的模型，例如openai_embedding。
- similarity_top_k: 相似度检索返回的最相似结果数量。

### 使用
[知识定义与使用](../../原理介绍/知识/知识定义与使用.md)
