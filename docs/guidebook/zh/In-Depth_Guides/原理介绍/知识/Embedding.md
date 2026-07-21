# Embedding（向量化）

agentUniverse 提供若干内置 embedding 组件，供知识库 store 与文档处理器对文本向量化。每个组件以 `metadata.type: EMBEDDING` 注册，并暴露 `get_embeddings(texts, text_type=...)` 方法。

## CohereEmbedding

`CohereEmbedding` 使用 Cohere Embed v3 API 生成文本向量。支持多语言模型（`embed-multilingual-v3.0`，默认）和英文优化模型（`embed-english-v3.0`）。无需额外安装（`requests` 已是核心依赖）——只需一个 Cohere API Key。

注册一个指向 `agentuniverse.agent.action.knowledge.embedding.cohere_embedding.CohereEmbedding` 的组件，然后在 store 或处理器中按名引用（如 `embedding_model: cohere_embedding`）。API Key 从 `COHERE_API_KEY` 读取。

```yaml
name: 'cohere_embedding'
description: 'embedding via Cohere Embed v3 API'
embedding_model_name: 'embed-multilingual-v3.0'
api_key: '${COHERE_API_KEY}'
input_type: 'document'
request_timeout: 30
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.cohere_embedding'
  class: 'CohereEmbedding'
```
- embedding_model_name：Cohere embed 模型（默认 `embed-multilingual-v3.0`）。
- api_key：Cohere API Key（环境变量 `COHERE_API_KEY`）。
- input_type：`document` 或 `query`——Cohere 建议明确指定以获得最佳检索质量（默认 `document`）。
- request_timeout：超时秒数（默认 30）。
