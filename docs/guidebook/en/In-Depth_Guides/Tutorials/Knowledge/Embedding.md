# Embedding

The Embedding component is responsible for converting text into vectors, which the Store uses for similarity retrieval. agentUniverse provides the abstract base class `Embedding` and a set of built-in implementations (OpenAI, Gemini, Ollama, DashScope, ...). This document focuses on the **Jina AI Embedding** component.

---

## Jina AI Embedding

`JinaEmbedding` integrates the [Jina AI](https://jina.ai) Embeddings API (the `jina-embeddings-v3` model family) into agentUniverse. Jina Embeddings v3 is a multilingual model with configurable output dimensions and strong performance on retrieval tasks.

Unlike the OpenAI / DashScope embeddings which are consumed through a dedicated SDK, the Jina Embeddings API is a plain JSON-over-HTTPS endpoint with no first-party Python client, so `JinaEmbedding` calls `https://api.jina.ai/v1/embeddings` directly with `requests` and exposes the `get_embeddings` / `async_get_embeddings` methods required by the `Embedding` base class.

### 1. Create the configuration file

Create a YAML file, for example `jina_embedding.yaml`, and paste the following content into it.

```yaml
name: 'jina_embedding'
description: 'embedding use jina ai api'
embedding_model_name: 'jina-embeddings-v3'
api_key: '${JINA_API_KEY}'
api_base: 'https://api.jina.ai/v1/embeddings'
dimensions: 1024
request_timeout: 30
batch_size: 32
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.jina_embedding'
  class: 'JinaEmbedding'
```

**Note:** `api_key` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.
    ```yaml
    api_key: 'jina_***'
    ```
2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax.
    ```yaml
    api_key: '${JINA_API_KEY}'
    ```
3. **Custom function loading** - use the `@FUNC` annotation.

### 2. Configuration parameters

| Parameter             | Description                                                                                  | Default                          |
| --------------------- | -------------------------------------------------------------------------------------------- | -------------------------------- |
| `embedding_model_name`| The Jina embedding model id.                                                                  | `jina-embeddings-v3`             |
| `api_key`             | Jina AI API key. Falls back to the `JINA_API_KEY` env var.                                   | -                                |
| `api_base`            | Jina Embeddings endpoint URL.                                                                | `https://api.jina.ai/v1/embeddings` |
| `dimensions`          | Output vector dimensionality. jina-embeddings-v3 supports 32/64/128/256/512/768/1024.        | `1024`                           |
| `request_timeout`     | Timeout in seconds for the HTTP call. Must be a positive number.                             | `30`                             |
| `batch_size`          | Maximum number of texts sent in a single API call.                                           | `32`                             |

### 3. Environment setup

Required: `JINA_API_KEY`
Optional: none.

#### 3.1 Configure through Python code

```python
import os
os.environ['JINA_API_KEY'] = 'jina_***'
```

#### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory:

```toml
JINA_API_KEY="jina_***"
```

### 4. Obtaining the Jina API key

1. Sign in at [https://jina.ai](https://jina.ai).
2. Navigate to the API key management page and create a new key.
3. Copy the generated key and assign it to `JINA_API_KEY`.

### 5. Using the Embedding in code

```python
from agentuniverse.agent.action.knowledge.embedding.jina_embedding import JinaEmbedding

embedding = JinaEmbedding()

# Synchronous
vectors = embedding.get_embeddings(['hello', 'world'])

# Asynchronous
import asyncio
async def main():
    vecs = await embedding.async_get_embeddings(['hello', 'world'])
    print(len(vecs), len(vecs[0]))
asyncio.run(main())
```

The returned value is a list of float vectors, one per input text, in input order. The vectors can be stored in a `Document.embedding` and queried by any Store implementation.

### 6. Tips

- `jina-embeddings-v3` is multilingual and is a good default for both Chinese and English retrieval.
- For multimodal (image) embeddings use the dedicated Jina CLIP embeddings model instead.
- Keep `dimensions` consistent with what your Store / index expects; changing it after indexing invalidates the existing vectors.
