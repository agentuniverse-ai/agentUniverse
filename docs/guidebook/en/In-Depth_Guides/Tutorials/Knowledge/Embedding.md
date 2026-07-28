# Embedding

agentUniverse provides several built-in embedding components used by the Knowledge store and doc processors to vectorise text. Each component is registered with `metadata.type: EMBEDDING` and exposes `get_embeddings(texts, text_type=...)`.

## HuggingFaceEmbedding

`HuggingFaceEmbedding` generates text embeddings using models hosted on the Hugging Face Hub via the `InferenceClient` from `huggingface_hub`. It supports sentence-transformers models, BGE, GTE, and any embedding model exposed through the Hub feature-extraction API. Install the SDK with `pip install huggingface_hub`.

Register a component pointing at `agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.HuggingFaceEmbedding`, then reference it by name from a store or processor (e.g. `embedding_model: huggingface_embedding`). The API key is read from `HUGGINGFACE_API_KEY` (or `HF_TOKEN`).

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
- embedding_model_name: The Hugging Face model repo ID (default `sentence-transformers/all-MiniLM-L6-v2`).
- api_key: Hugging Face API token (env: `HUGGINGFACE_API_KEY` or `HF_TOKEN`).
- timeout: Request timeout in seconds (default 30).
