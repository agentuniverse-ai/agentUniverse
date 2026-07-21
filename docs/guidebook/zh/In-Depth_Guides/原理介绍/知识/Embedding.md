# Embedding（向量化）

agentUniverse 提供若干内置 embedding 组件，供知识库 store 与文档处理器对文本向量化。每个组件以 `metadata.type: EMBEDDING` 注册，并暴露 `get_embeddings(texts, text_type=...)` 方法。

## HuggingFaceEmbedding

`HuggingFaceEmbedding` 通过 `huggingface_hub` 的 `InferenceClient`，使用 Hugging Face Hub 上托管的模型生成文本向量。支持 sentence-transformers 模型、BGE、GTE，以及任何通过 Hub feature-extraction API 暴露的 embedding 模型。安装 SDK：`pip install huggingface_hub`。

注册一个指向 `agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.HuggingFaceEmbedding` 的组件，然后在 store 或处理器中按名引用（如 `embedding_model: huggingface_embedding`）。API Key 从 `HUGGINGFACE_API_KEY`（或 `HF_TOKEN`）读取。

```yaml
name: 'huggingface_embedding'
description: 'embedding via Hugging Face Hub Inference API'
embedding_model_name: 'sentence-transformers/all-MiniLM-L6-v2'
api_key: '${HUGGINGFACE_API_KEY}'
timeout: 30
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.huggingface_embedding'
  class: 'HuggingFaceEmbedding'
```
- embedding_model_name：Hugging Face 模型 repo ID（默认 `sentence-transformers/all-MiniLM-L6-v2`）。
- api_key：Hugging Face API token（环境变量 `HUGGINGFACE_API_KEY` 或 `HF_TOKEN`）。
- timeout：请求超时秒数（默认 30）。
