## Weaviate
如果您希望在agentUniverse中使用Weaviate向量数据库，需要遵循以下步骤：

1. 安装Weaviate向量数据库
您可以参考[Weaviate官方安装文档](https://weaviate.io/developers/weaviate/installation)了解Weaviate的详细安装与使用说明。推荐通过Docker启动Weaviate容器，执行以下命令：

``` shell
$ docker run -d --name weaviate \
  -p 8080:8080 -p 50051:50051 \
  -e AUTHENTICATION_APIKEY_ENABLED='true' \
  -e AUTHENTICATION_APIKEY_ALLOWED_KEYS='your-weaviate-api-key' \
  -e AUTHENTICATION_APIKEY_USERS='admin@weaviate.io' \
  -e AUTHORIZATION_ADMINREAD_ENABLED='true' \
  cr.weaviate.io/semitechnologies/weaviate:latest
```
上述命令会下载Weaviate镜像并启动容器，REST API服务于8080端口，gRPC API服务于50051端口。更多信息与其他安装方式请参考官方文档。

2. 安装Weaviate Python SDK
```
pip install weaviate-client
```

### 如何配置Weaviate组件
```yaml
name: 'weaviate_store'
description: 'a store based on weaviate'
collection_name: 'agentuniverse'
distance: 'COSINE'
similarity_top_k: 10
with_vectors: false
connection_args:
  http_host: 'localhost'
  http_port: 8080
  http_secure: false
  grpc_host: 'localhost'
  grpc_port: 50051
  grpc_secure: false
api_key: 'your-weaviate-api-key'
embedding_model: 'openai_embedding'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.weaviate_store'
  class: 'WeaviateStore'
```
- connection_args: 通过v4客户端连接Weaviate服务所需的参数：http_host、http_port、http_secure、grpc_host、grpc_port、grpc_secure。
- api_key: 服务端开启API Key认证时使用的凭证；服务端无认证时可删除该配置。
- collection_name: 存储文档的Weaviate collection；首次写入时会按配置的距离度量自动创建。
- distance: collection向量索引使用的距离度量，可选COSINE（默认）、EUCLID、DOT、MANHATTAN、HAMMING。
- with_vectors: 为true时查询结果会同时返回向量。
- embedding_model: 用于生成embedding向量的模型，例如openai_embedding。
- similarity_top_k: 相似度检索返回的最相似结果数量。

### 使用
[知识的定义与使用](../../原理介绍/知识/知识定义与使用.md)
