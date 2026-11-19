# Embedding

agentUniverse provides several built-in embedding components used by the Knowledge store and doc processors to vectorise text. Each component is registered with `metadata.type: EMBEDDING` and exposes `get_embeddings(texts, text_type=...)`.

## CohereEmbedding

`CohereEmbedding` generates text embeddings using the Cohere Embed v3 API. It supports the multilingual model (`embed-multilingual-v3.0`, default) and the English-optimised model (`embed-english-v3.0`). No extra install (`requests` is already a core dependency) — only a Cohere API key.

Register a component pointing at `agentuniverse.agent.action.knowledge.embedding.cohere_embedding.CohereEmbedding`, then reference it by name from a store or processor (e.g. `embedding_model: cohere_embedding`). The API key is read from `COHERE_API_KEY`.

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
- embedding_model_name: Cohere embed model (default `embed-multilingual-v3.0`).
- api_key: Cohere API key (env: `COHERE_API_KEY`).
- input_type: `document` or `query` — Cohere recommends specifying this for best retrieval quality (default `document`).
- request_timeout: Timeout in seconds (default 30).
