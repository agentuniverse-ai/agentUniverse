# Embedding

agentUniverse provides several built-in embedding components used by the Knowledge store and doc processors to vectorise text. Each component is registered with `metadata.type: EMBEDDING` and exposes `get_embeddings(texts, text_type=...)`.

## SentenceTransformerEmbedding

`SentenceTransformerEmbedding` generates text embeddings using locally-hosted sentence-transformers models (via the `sentence-transformers` package). No API key or network connection is required — models run entirely on-device, which makes this component ideal for development, testing, privacy-sensitive deployments, and offline use. Install the package with `pip install sentence-transformers`.

Register a component pointing at `agentuniverse.agent.action.knowledge.embedding.sentence_transformer_embedding.SentenceTransformerEmbedding`, then reference it by name from a store or processor (e.g. `embedding_model: sentence_transformer_embedding`).

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
- embedding_model_name: The model name or path (default `all-MiniLM-L6-v2`).
- device: Device to run the model on — `cpu`, `cuda`, or `mps` (default `cpu`).
- normalize_embeddings: When `true` (default), L2-normalise the output vectors — recommended for cosine similarity.
- batch_size: Batch size for encoding (default 32).
