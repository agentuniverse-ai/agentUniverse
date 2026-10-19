## Elasticsearch
如果您希望在agentUniverse中使用Elasticsearch向量数据库，需要遵循以下步骤：

1. 安装Elasticsearch向量数据库
您可以参考[Elasticsearch官方安装文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)了解详细安装说明。推荐通过Docker启动Elasticsearch容器，执行以下命令：

``` shell
$ docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0
```
容器在9200端口提供REST API，为快速体验关闭了安全认证；生产部署请参考官方文档。dense_vector字段的kNN检索要求Elasticsearch 8.x及以上版本。

2. 安装Elasticsearch Python SDK
```
pip install elasticsearch
```

### 如何配置Elasticsearch组件
```yaml
name: 'elasticsearch_store'
description: 'a store based on elasticsearch'
index_name: 'agentuniverse'
distance: 'COSINE'
similarity_top_k: 10
with_vectors: false
connection_args:
  hosts: 'http://localhost:9200'
  # api_key: 'your-elasticsearch-api-key'
  # basic_auth: ['elastic', 'your-password']
embedding_model: 'openai_embedding'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.elasticsearch_store'
  class: 'ElasticsearchStore'
```
- connection_args: 传递给 `elasticsearch.Elasticsearch` 客户端的参数，例如hosts、api_key、basic_auth、cloud_id。
- index_name: 存储文档的Elasticsearch索引；首次写入时会自动创建dense_vector映射。
- distance: dense_vector相似度度量，可选COSINE（默认）、EUCLID、DOT。
- num_candidates: kNN的num_candidates参数；默认为10 x similarity_top_k（Elasticsearch官方推荐值）。
- with_vectors: 为true时查询结果会同时返回向量。
- embedding_model: 用于生成embedding向量的模型，例如openai_embedding。
- similarity_top_k: 相似度检索返回的最相似结果数量。

### 使用
[知识定义与使用](../../原理介绍/知识/知识定义与使用.md)
