# Embedding

agentUniverse provides several built-in embedding components used by the Knowledge store and doc processors to vectorise text. Each component is registered with `metadata.type: EMBEDDING` and exposes `get_embeddings(texts, input_type=...)` together with its async counterpart.

## VoyageEmbedding

`VoyageEmbedding` generates text embeddings using the Voyage AI embeddings API (`https://api.voyageai.com/v1/embeddings`). It supports the Voyage AI embedding family, including `voyage-3` (default), `voyage-3-lite`, `voyage-3-large` and `voyage-large-2`. No extra install is required — `requests` is already a core dependency of agentUniverse — only a Voyage AI API key.

Register a component pointing at `agentuniverse.agent.action.knowledge.embedding.voyage_embedding.VoyageEmbedding`, then reference it by name from a store or processor (e.g. `embedding_model: voyage_embedding`). The API key is read from the `VOYAGE_API_KEY` environment variable.

```yaml
name: 'voyage_embedding'
description: 'embedding via Voyage AI embeddings API'
embedding_model_name: 'voyage-3'
input_type: 'document'
request_timeout: 30
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.voyage_embedding'
  class: 'VoyageEmbedding'
```
- embedding_model_name: Voyage AI embedding model (default `voyage-3`).
- input_type: `document` or `query` — Voyage AI recommends specifying this for best retrieval quality (default `document`).
- request_timeout: Timeout in seconds for the HTTP call (default 30). `requests` defaults to no timeout, so without this a stalled Voyage API would hang the whole embed step indefinitely.

Voyage AI recommends telling the API whether each call is embedding documents for storage or a query for retrieval. The `input_type` on the component sets the default; pass `input_type='query'` to `get_embeddings` to override it per call. On timeout the call returns one empty vector per input text so a single slow request does not crash an ingestion pipeline; HTTP errors and non-JSON responses are surfaced as `RuntimeError`, and a missing API key raises `ValueError`.
