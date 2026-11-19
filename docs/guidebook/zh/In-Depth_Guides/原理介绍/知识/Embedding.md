# Embedding（向量化）

agentUniverse 提供若干内置 embedding 组件，供知识库 store 与文档处理器对文本向量化。每个组件以 `metadata.type: EMBEDDING` 注册，并暴露 `get_embeddings(texts, text_type=...)` 方法。

## SentenceTransformerEmbedding

`SentenceTransformerEmbedding` 使用本地托管的 sentence-transformers 模型（通过 `sentence-transformers` 包）生成文本向量。无需 API Key、无需联网——模型完全在本地运行，非常适合开发、测试、对隐私敏感的部署以及离线场景。安装包：`pip install sentence-transformers`。

注册一个指向 `agentuniverse.agent.action.knowledge.embedding.sentence_transformer_embedding.SentenceTransformerEmbedding` 的组件，然后在 store 或处理器中按名引用（如 `embedding_model: sentence_transformer_embedding`）。

```yaml
name: 'sentence_transformer_embedding'
description: 'local embedding via sentence-transformers'
embedding_model_name: 'all-MiniLM-L6-v2'
device: 'cpu'
normalize_embeddings: true
batch_size: 32
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.sentence_transformer_embedding'
  class: 'SentenceTransformerEmbedding'
```
- embedding_model_name：模型名或路径（默认 `all-MiniLM-L6-v2`）。
- device：运行模型的设备——`cpu`、`cuda` 或 `mps`（默认 `cpu`）。
- normalize_embeddings：为 `true`（默认）时对输出向量做 L2 归一化——推荐用于余弦相似度。
- batch_size：编码时的批大小（默认 32）。
